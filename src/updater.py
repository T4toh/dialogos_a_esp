"""
src/updater.py - Módulo de auto-actualización para AppImage.

Solo activo cuando la app se ejecuta como AppImage (variable de entorno $APPIMAGE).
Usa AppImageUpdate para descargar solo los bloques cambiados vía zsync.
"""

import os
import shutil
import subprocess
from typing import Optional


# URL de descarga de AppImageUpdate para mostrar al usuario si no lo tiene
APPIMAGEUPDATE_DOWNLOAD_URL = (
    "https://github.com/AppImage/AppImageUpdate/releases/latest"
)


def is_running_as_appimage() -> bool:
    """Devuelve True si la app está ejecutándose como AppImage."""
    return "APPIMAGE" in os.environ


def get_appimage_path() -> Optional[str]:
    """Devuelve la ruta al AppImage actual, o None si no aplica."""
    return os.environ.get("APPIMAGE")


def find_appimageupdate() -> Optional[str]:
    """
    Busca el ejecutable AppImageUpdate.
    Busca primero junto al AppImage, luego en $PATH.
    """
    appimage_path = get_appimage_path()
    if appimage_path:
        # Buscar AppImageUpdate en el mismo directorio que el AppImage
        appimage_dir = os.path.dirname(appimage_path)
        candidate = os.path.join(appimage_dir, "AppImageUpdate")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return shutil.which("AppImageUpdate")


def check_for_updates() -> dict:
    """
    Comprueba si hay una actualización disponible sin descargar nada.

    Returns:
        dict con claves:
          - 'available' (bool): hay actualización
          - 'tool_found' (bool): AppImageUpdate está instalado
          - 'is_appimage' (bool): se está ejecutando como AppImage
          - 'error' (str | None): mensaje de error si falló el check
    """
    result = {
        "available": False,
        "tool_found": False,
        "is_appimage": is_running_as_appimage(),
        "error": None,
    }

    if not result["is_appimage"]:
        return result

    tool = find_appimageupdate()
    if not tool:
        result["error"] = "AppImageUpdate no encontrado"
        return result

    result["tool_found"] = True
    appimage_path = get_appimage_path()

    try:
        # --check-for-update: sale con código 1 si hay update, 0 si no hay
        proc = subprocess.run(
            [tool, "--check-for-update", appimage_path],
            capture_output=True,
            text=True,
            timeout=15,
        )
        result["available"] = proc.returncode == 1
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout al comprobar actualizaciones"
    except Exception as e:
        result["error"] = str(e)

    return result


def apply_update() -> dict:
    """
    Descarga y aplica la actualización usando AppImageUpdate.
    Bloquea hasta que termina (llamar desde un hilo separado).

    Returns:
        dict con claves:
          - 'success' (bool)
          - 'output' (str): salida del proceso
          - 'error' (str | None)
    """
    result = {"success": False, "output": "", "error": None}

    if not is_running_as_appimage():
        result["error"] = "No se está ejecutando como AppImage"
        return result

    tool = find_appimageupdate()
    if not tool:
        result["error"] = (
            f"AppImageUpdate no encontrado.\n"
            f"Descárgalo en: {APPIMAGEUPDATE_DOWNLOAD_URL}"
        )
        return result

    appimage_path = get_appimage_path()

    try:
        proc = subprocess.run(
            [tool, appimage_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        result["output"] = proc.stdout + proc.stderr
        result["success"] = proc.returncode == 0
        if not result["success"]:
            result["error"] = f"AppImageUpdate salió con código {proc.returncode}"
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout al descargar la actualización"
    except Exception as e:
        result["error"] = str(e)

    return result
