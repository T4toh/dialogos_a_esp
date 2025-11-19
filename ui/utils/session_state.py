"""
Gestión del estado de la sesión de Streamlit.
"""

import streamlit as st


def initialize_session_state():
    """Inicializa las variables de estado de la sesión."""
    # Tema
    if "theme" not in st.session_state:
        query_params = st.query_params
        saved_theme = query_params.get("theme", "dark")
        st.session_state.theme = saved_theme

    # Archivos
    if "files_info" not in st.session_state:
        st.session_state.files_info = []

    if "selected_files" not in st.session_state:
        st.session_state.selected_files = set()

    # Carpeta actual
    if "current_folder" not in st.session_state:
        from pathlib import Path

        st.session_state.current_folder = str(Path(".").resolve())

    # Input de directorio
    if "input_dir_text" not in st.session_state:
        st.session_state.input_dir_text = "."


def update_theme(theme: str):
    """Actualiza el tema de la aplicación."""
    st.session_state.theme = theme
    st.query_params.theme = theme


def get_selected_files() -> set:
    """Obtiene los archivos seleccionados."""
    return st.session_state.get("selected_files", set())


def set_selected_files(files: set):
    """Actualiza los archivos seleccionados."""
    st.session_state.selected_files = files


def get_files_info() -> list:
    """Obtiene la información de archivos escaneados."""
    return st.session_state.get("files_info", [])


def set_files_info(files_info: list):
    """Actualiza la información de archivos escaneados."""
    st.session_state.files_info = files_info


def clear_file_checkboxes():
    """Limpia los checkboxes de archivos del estado."""
    for k in list(st.session_state.keys()):
        if str(k).startswith("check_"):
            try:
                del st.session_state[k]
            except Exception:
                pass
