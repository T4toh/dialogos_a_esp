"""
Componente para selección y visualización de archivos.
"""

from pathlib import Path
from typing import Tuple

import streamlit as st

from ..utils.file_utils import format_size


def render_file_table(files_info: list) -> Tuple[set, str]:
    """
    Renderiza la tabla de archivos con opciones de selección.

    Args:
        files_info: Lista de diccionarios con información de archivos

    Returns:
        Tuple[set, str]: (archivos_seleccionados, directorio_salida)
    """
    if not files_info:
        return set(), ""

    st.header("📋 Archivos Encontrados")

    # Estadísticas generales
    total_files = len(files_info)
    total_words = sum(f["words"] for f in files_info)
    total_size = sum(f["size"] for f in files_info)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Archivos", total_files)
    with col2:
        st.metric("Palabras totales", f"{total_words:,}")
    with col3:
        st.metric("Tamaño total", format_size(total_size))
    with col4:
        selected_count = len(st.session_state.selected_files)
        st.metric("Seleccionados", selected_count)

    st.markdown("---")

    # Tabla de archivos con checkboxes
    st.subheader("Seleccionar archivos a procesar")

    # Botones para seleccionar/deseleccionar todos
    _render_select_all_buttons(files_info, total_files)

    # Mostrar cada archivo
    for idx, file_info in enumerate(files_info):
        _render_file_row(idx, file_info)

    st.markdown("---")

    # Configuración de procesamiento
    output_dir = _render_processing_config()

    # Botón de procesamiento
    process_clicked = False
    if len(st.session_state.selected_files) > 0:
        if st.button("▶️ Iniciar Conversión", type="primary", use_container_width=True):
            process_clicked = True
    else:
        st.warning("⚠️ Selecciona al menos un archivo para procesar")

    return st.session_state.selected_files, output_dir, process_clicked


def _render_select_all_buttons(files_info: list, total_files: int):
    """Renderiza botones para seleccionar/deseleccionar todos."""
    col_all1, col_all2, col_all3 = st.columns([1, 1, 3])
    with col_all1:
        # Determinar si todos están seleccionados
        all_selected = len(st.session_state.selected_files) == total_files

        # Solo mostrar el botón relevante
        if not all_selected:
            if st.button("Seleccionar todos", key="select_all_button"):
                st.session_state.selected_files = {f["path"] for f in files_info}

                # Marcar todos los checkboxes en session_state
                for idx, _ in enumerate(files_info):
                    st.session_state[f"check_{idx}"] = True
        else:
            if st.button("Deseleccionar todos", key="deselect_all_button"):
                st.session_state.selected_files = set()

                # Desmarcar todos los checkboxes en session_state
                for idx, _ in enumerate(files_info):
                    st.session_state[f"check_{idx}"] = False


def _render_file_row(idx: int, file_info: dict):
    """Renderiza una fila de archivo con checkbox."""
    col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 1, 1])

    with col1:
        key = f"check_{idx}"

        # Estado previo según selected_files
        was_selected = file_info["path"] in st.session_state.selected_files

        # Crear checkbox sin pasar 'value' si ya existe la clave en session_state
        if key in st.session_state:
            is_selected = st.checkbox(
                "Seleccionar", key=key, label_visibility="collapsed"
            )
        else:
            # Si la clave no existe, pasar el valor inicial
            is_selected = st.checkbox(
                "Seleccionar",
                value=was_selected,
                key=key,
                label_visibility="collapsed",
            )

        # Actualizar selección si cambió
        if is_selected and not was_selected:
            st.session_state.selected_files.add(file_info["path"])
        elif not is_selected and was_selected:
            st.session_state.selected_files.discard(file_info["path"])

    with col2:
        st.text(file_info["name"])

    with col3:
        st.text(file_info["type"])

    with col4:
        st.text(f"{file_info['words']:,} palabras")

    with col5:
        st.text(format_size(file_info["size"]))


def _render_processing_config() -> str:
    """Renderiza la configuración de procesamiento."""
    st.header("⚙️ Configuración de Procesamiento")

    col1, col2 = st.columns(2)

    with col1:
        # input_dir puede ser None; usar '.' como fallback para Path
        input_dir = st.session_state.get("input_dir_text", ".")
        default_output = str(Path(input_dir or ".") / "convertidos")
        output_dir = st.text_input(
            "📁 Carpeta de salida",
            value=default_output,
            help="Carpeta donde se guardarán los archivos convertidos",
        )

    with col2:
        st.write("")  # Espaciado

    return output_dir
