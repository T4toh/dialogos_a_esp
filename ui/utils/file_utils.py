"""
Utilidades para manejo de archivos y directorios.
Funciones extraídas de app.py para mejor organización.
"""

import re
from pathlib import Path
from typing import Dict, List


def count_words_in_file(file_path: Path) -> int:
    """Cuenta palabras en un archivo."""
    try:
        from src.odt_handler import ODTReader, is_odt_file

        if is_odt_file(file_path):
            reader = ODTReader(file_path)
            text = reader.extract_text()
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

        words = text.split()
        return len(words)
    except Exception:
        return 0


def scan_directory(
    directory: Path, pattern: str = "*.*", recursive: bool = False
) -> List[Dict]:
    """Escanea directorio y retorna información de archivos."""
    from src.odt_handler import is_odt_file

    files_info = []
    extensions = {".odt", ".txt"}

    if recursive:
        iterator = directory.rglob(pattern)
    else:
        iterator = directory.glob(pattern)

    for file_path in iterator:
        if file_path.is_file() and file_path.suffix in extensions:
            if not file_path.stem.endswith("_convertido"):
                word_count = count_words_in_file(file_path)
                files_info.append(
                    {
                        "path": file_path,
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "words": word_count,
                        "type": "ODT" if is_odt_file(file_path) else "TXT",
                    }
                )

    def natural_sort_key(s):
        """Clave de ordenamiento natural para strings con números."""
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split(r"(\d+)", s["name"])
        ]

    return sorted(files_info, key=natural_sort_key)


def format_size(size_bytes: int) -> str:
    """Formatea tamaño en bytes a formato legible."""
    # Trabajamos con un float local para evitar que la división cambie el tipo
    bytes_val = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"


def list_directories(base_path: Path, max_depth: int = 2) -> List[str]:
    """Lista directorios disponibles desde un path base."""
    dirs = []

    try:
        base_path = base_path.resolve()

        # Añadir el directorio actual
        dirs.append(str(base_path))

        # Añadir directorio padre
        if base_path.parent != base_path:
            dirs.append(f"⬆️ {base_path.parent}")

        # Añadir subdirectorios del directorio actual
        try:
            for item in sorted(base_path.iterdir()):
                if item.is_dir() and not item.name.startswith("."):
                    dirs.append(f"📁 {item}")
        except PermissionError:
            pass

        # Separador
        if len(dirs) > 1:
            dirs.append("─" * 50)

        # Añadir directorios comunes del usuario
        home = Path.home()
        common_dirs = [
            ("🏠 Inicio", home),
            ("📄 Documentos", home / "Documents"),
            ("📄 Documentos", home / "Documentos"),
            ("🖥️ Escritorio", home / "Desktop"),
            ("🖥️ Escritorio", home / "Escritorio"),
            ("⬇️ Descargas", home / "Downloads"),
            ("⬇️ Descargas", home / "Descargas"),
        ]

        for label, path in common_dirs:
            if path.exists() and str(path) not in [
                d.replace("📁 ", "").replace("⬆️ ", "") for d in dirs
            ]:
                dirs.append(f"{label}: {path}")

    except Exception:
        dirs = ["."]

    return dirs


def parse_directory_choice(choice: str) -> str:
    """Extrae la ruta del directorio de la elección."""
    if choice.startswith("─"):
        return "."

    # Remover emojis y etiquetas
    choice = choice.replace("📁 ", "").replace("⬆️ ", "")

    # Si tiene formato "Etiqueta: path"
    if ": " in choice:
        choice = choice.split(": ", 1)[1]

    return choice.strip()
