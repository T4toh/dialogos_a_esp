"""
Componente del sidebar con configuración y navegación.
"""

from pathlib import Path

import streamlit as st

from ..utils.file_utils import list_directories, parse_directory_choice
from ..utils.session_state import update_theme


def render_sidebar() -> dict:
    """
    Renderiza el sidebar completo con todas las opciones.

    Returns:
        dict: Configuración seleccionada con las claves:
            - input_dir: str
            - pattern: str
            - recursive: bool
            - scan_clicked: bool
    """
    with st.sidebar:
        st.header("⚙️ Configuración")

        # Selector de tema
        st.subheader("🎨 Apariencia")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "🌙 Oscuro",
                use_container_width=True,
                type="primary" if st.session_state.theme == "dark" else "secondary",
            ):
                update_theme("dark")
                st.rerun()
        with col2:
            if st.button(
                "☀️ Claro",
                use_container_width=True,
                type="primary" if st.session_state.theme == "light" else "secondary",
            ):
                update_theme("light")
                st.rerun()

        st.markdown("---")

        # Modo de selección de carpeta
        folder_mode = st.radio(
            "Modo de selección",
            ["Escribir ruta", "Selector de carpetas"],
            horizontal=True,
            label_visibility="collapsed",
        )

        # Selección de carpeta
        if folder_mode == "Selector de carpetas":
            input_dir = _render_folder_selector()
        else:
            input_dir = _render_text_input()

        # Guardar en session_state
        st.session_state["input_dir_text"] = input_dir

        # Opciones de escaneo
        st.subheader("Opciones de búsqueda")

        file_filter = st.selectbox(
            "Tipo de archivo",
            options=["Todos (*.*)", "Solo ODT (*.odt)", "Solo TXT (*.txt)"],
            index=1,
        )

        recursive = st.checkbox(
            "Incluir subcarpetas", value=False, help="Buscar archivos en subcarpetas"
        )

        # Botón de escaneo
        scan_button = st.button("🔍 Escanear", type="primary", use_container_width=True)

    # Mapeo de filtro
    filter_map = {
        "Todos (*.*)": "*.*",
        "Solo ODT (*.odt)": "*.odt",
        "Solo TXT (*.txt)": "*.txt",
    }
    pattern = filter_map[file_filter]

    return {
        "input_dir": input_dir,
        "pattern": pattern,
        "recursive": recursive,
        "scan_clicked": scan_button,
    }


def _render_folder_selector() -> str:
    """Renderiza el selector de carpetas visual."""
    # Obtener directorio actual desde session_state o usar "."
    if "current_folder" not in st.session_state:
        st.session_state["current_folder"] = str(Path(".").resolve())

    current_base = Path(st.session_state["current_folder"])
    if not current_base.exists():
        current_base = Path(".")
        st.session_state["current_folder"] = str(current_base.resolve())

    available_dirs = list_directories(current_base)

    # Mostrar carpeta actual
    st.text("📍 Ubicación actual:")
    st.code(str(current_base.resolve()), language=None)

    # Selector de carpeta
    selected_dir = st.selectbox(
        "Navegar a:",
        options=available_dirs,
        index=0,
        help="Selecciona una carpeta para navegar o usar",
        label_visibility="collapsed",
    )

    # Actualizar carpeta si se seleccionó una diferente
    if not selected_dir.startswith("─"):
        parsed_dir = parse_directory_choice(selected_dir)
        if parsed_dir != str(current_base):
            st.session_state["current_folder"] = parsed_dir
            st.rerun()

    return str(current_base.resolve())


def _render_text_input() -> str:
    """Renderiza el input de texto para la ruta."""
    input_dir = st.text_input(
        "📂 Carpeta de entrada",
        value=st.session_state.get("input_dir_text", "."),
        help="Ruta a la carpeta con archivos a procesar",
    )
    # Actualizar current_folder cuando se cambia el texto
    if input_dir:
        st.session_state["current_folder"] = input_dir

    return input_dir
