"""
src/updater.py - Módulo de auto-actualización para AppImage.

Solo activo cuando la app se ejecuta como AppImage (variable de entorno $APPIMAGE).
Usa la API de GitHub para detectar nuevas versiones y las descarga directamente,
sin depender de herramientas externas como AppImageUpdate.
"""

import os
import shutil
import ssl
import urllib.request
import json
from typing import Optional

from src import __version__

GITHUB_REPO = "T4toh/dialogos_a_esp"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"

# URL de descarga de AppImageUpdate (para compatibilidad, ya no requerido)
APPIMAGEUPDATE_DOWNLOAD_URL = GITHUB_RELEASES_URL


def is_running_as_appimage() -> bool:
    """Devuelve True si la app está ejecutándose como AppImage."""
    return "APPIMAGE" in os.environ


def get_appimage_path() -> Optional[str]:
    """Devuelve la ruta al AppImage actual, o None si no aplica."""
    return os.environ.get("APPIMAGE")


def find_appimageupdate() -> Optional[str]:
    """Busca AppImageUpdate en el directorio del AppImage o en $PATH (opcional)."""
    appimage_path = get_appimage_path()
    if appimage_path:
        candidate = os.path.join(os.path.dirname(appimage_path), "AppImageUpdate")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return shutil.which("AppImageUpdate")


def _make_ssl_context() -> ssl.SSLContext:
    """
    Crea un contexto SSL que usa los certificados del sistema operativo.
    Dentro de un AppImage, Python no encuentra sus propios certs bundleados,
    pero los del sistema (/etc/ssl/certs) sí están disponibles.
    """
    ctx = ssl.create_default_context()
    # Rutas estándar de certificados en Linux
    system_ca_paths = [
        "/etc/ssl/certs/ca-certificates.crt",   # Debian/Ubuntu/Arch
        "/etc/pki/tls/certs/ca-bundle.crt",     # Fedora/RHEL
        "/etc/ssl/ca-bundle.pem",               # openSUSE
    ]
    for path in system_ca_paths:
        if os.path.isfile(path):
            ctx.load_verify_locations(cafile=path)
            return ctx
    # Si no encontramos certs del sistema, deshabilitar verificación
    # (mejor que crashear, muestra error descriptivo al usuario)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _fetch_latest_release() -> dict:
    """
    Consulta la API de GitHub y devuelve info de la última release.
    Lanza excepción si falla la conexión.
    """
    req = urllib.request.Request(
        GITHUB_API_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "dialogos-updater"},
    )
    with urllib.request.urlopen(req, timeout=10, context=_make_ssl_context()) as resp:
        return json.loads(resp.read().decode())


def check_for_updates() -> dict:
    """
    Comprueba si hay una actualización disponible comparando versiones con GitHub.

    Returns:
        dict con claves:
          - 'available' (bool): hay actualización
          - 'latest_version' (str | None): versión más reciente en GitHub
          - 'download_url' (str | None): URL directa del nuevo AppImage
          - 'is_appimage' (bool): se está ejecutando como AppImage
          - 'error' (str | None): mensaje de error si falló el check
    """
    result = {
        "available": False,
        "latest_version": None,
        "download_url": None,
        "is_appimage": is_running_as_appimage(),
        "error": None,
    }

    try:
        release = _fetch_latest_release()
        tag = release.get("tag_name", "").lstrip("v")
        result["latest_version"] = tag

        # Comparación simple de versiones (ej: "2.1.1" > "2.1.0")
        def parse(v: str):
            return tuple(int(x) for x in v.split(".") if x.isdigit())

        if parse(tag) > parse(__version__):
            result["available"] = True
            # Buscar el asset .AppImage para x86_64
            for asset in release.get("assets", []):
                name = asset.get("name", "")
                if name.endswith(".AppImage") and "x86_64" in name and not name.endswith(".zsync"):
                    result["download_url"] = asset["browser_download_url"]
                    break

    except Exception as e:
        result["error"] = str(e)

    return result


def apply_update(download_url: str, progress_callback=None) -> dict:
    """
    Descarga el nuevo AppImage y reemplaza el actual.
    Llama a progress_callback(bytes_done, total_bytes) durante la descarga.
    Bloquea hasta que termina (llamar desde un hilo separado).

    Returns:
        dict con claves:
          - 'success' (bool)
          - 'error' (str | None)
    """
    result = {"success": False, "error": None}

    appimage_path = get_appimage_path()
    if not appimage_path:
        result["error"] = "No se está ejecutando como AppImage"
        return result

    tmp_path = appimage_path + ".new"

    try:
        req = urllib.request.Request(
            download_url,
            headers={"User-Agent": "dialogos-updater"},
        )
        with urllib.request.urlopen(req, timeout=120, context=_make_ssl_context()) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            done = 0
            chunk = 65536
            with open(tmp_path, "wb") as f:
                while True:
                    data = resp.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    done += len(data)
                    if progress_callback:
                        progress_callback(done, total)

        # Dar permisos de ejecución y reemplazar el AppImage actual
        os.chmod(tmp_path, 0o755)
        shutil.move(tmp_path, appimage_path)
        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return result
