"""
Aplicación principal de Streamlit.
Punto de entrada de la interfaz web.
"""

from pathlib import Path

import streamlit as st

from .components.file_selector import render_file_table
from .components.results_display import display_results
from .components.sidebar import render_sidebar
from .pages.batch_converter import process_files
from .styles.themes import apply_custom_theme
from .utils.file_utils import scan_directory
from .utils.session_state import (
    clear_file_checkboxes,
    initialize_session_state,
    set_files_info,
    set_selected_files,
)


def main():
    """Función principal de la aplicación."""
    # Configuración de página
    st.set_page_config(
        page_title="Conversor de Diálogos",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Script para leer tema desde localStorage
    st.markdown(
        """
    <script>
        // Intentar leer tema guardado
        const savedTheme = localStorage.getItem('dialogos_theme');
        if (savedTheme) {
            // Enviar evento personalizado a Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                key: 'theme_from_storage',
                value: savedTheme
            }, '*');
        }
    </script>
    """,
        unsafe_allow_html=True,
    )

    # Inicializar estado de sesión
    initialize_session_state()

    # Aplicar tema
    apply_custom_theme(st.session_state.theme)

    # Header
    st.title("📝 Conversor de Diálogos a Español")
    st.markdown("Convierte diálogos con comillas al formato español con raya (—)")

    # Renderizar sidebar y obtener configuración
    config = render_sidebar()

    # Procesar escaneo si se hizo clic
    if config["scan_clicked"]:
        _handle_scan(config)

    # Mostrar archivos encontrados y permitir selección
    if st.session_state.files_info:
        selected_files, output_dir, process_clicked = render_file_table(
            st.session_state.files_info
        )

        # Procesar archivos si se hizo clic
        if process_clicked:
            process_files(selected_files, Path(output_dir))

    # Mostrar resultados si existen
    if (
        "processing_results" in st.session_state
        and st.session_state["processing_results"]
    ):
        display_results(
            st.session_state["processing_results"],
            Path(st.session_state["output_directory"]),
        )
    elif not st.session_state.files_info:
        # Mensaje inicial solo si no hay archivos escaneados ni resultados
        st.info("👆 Selecciona una carpeta y haz clic en 'Escanear' para comenzar")


def _handle_scan(config: dict):
    """Maneja el escaneo de archivos."""
    input_path = Path(config["input_dir"] or ".")

    if not input_path.exists():
        st.error(f"❌ La carpeta '{config['input_dir']}' no existe")
    elif not input_path.is_dir():
        st.error(f"❌ '{config['input_dir']}' no es una carpeta")
    else:
        with st.spinner("Escaneando archivos..."):
            files_info = scan_directory(
                input_path, config["pattern"], config["recursive"]
            )
            set_files_info(files_info)

            # Seleccionar todos por defecto
            set_selected_files({f["path"] for f in files_info})

            # Limpiar checkboxes previos
            clear_file_checkboxes()

            # Inicializar los checkboxes para que reflejen la selección
            for idx, _ in enumerate(files_info):
                st.session_state[f"check_{idx}"] = True

        if files_info:
            st.success(f"✅ Encontrados {len(files_info)} archivo(s)")
        else:
            st.warning("⚠️ No se encontraron archivos")


if __name__ == "__main__":
    main()
