"""
Página de conversión por lotes.
Maneja el procesamiento de múltiples archivos.
"""

from pathlib import Path

import streamlit as st

from src.batch_processor import BatchProcessor
from src.converter import DialogConverter


def process_files(selected_files: set, output_dir: Path):
    """
    Procesa los archivos seleccionados.

    Args:
        selected_files: Set de Path con archivos a procesar
        output_dir: Path del directorio de salida
    """
    # Crear carpeta de salida
    output_dir.mkdir(parents=True, exist_ok=True)

    # Contenedor para resultados
    st.header("🚀 Procesando Archivos")

    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Resultados
    # Callback para actualizar progreso
    def update_progress(current, total, filename):
        progress = current / total
        progress_bar.progress(progress)
        status_text.text(f"Procesando {current}/{total}: {filename}")

    try:
        # Instanciar procesador
        converter = DialogConverter()
        batch = BatchProcessor(converter)

        # Ejecutar procesamiento
        results = batch.process_files(
            files=list(selected_files),
            output_dir=output_dir,
            progress_callback=update_progress,
        )

    except Exception as e:
        st.error(f"Error durante el procesamiento: {e}")
        results = []

    # Completar progreso
    progress_bar.progress(1.0)
    status_text.text("✅ Procesamiento completado")

    # Guardar resultados en session_state para persistencia
    st.session_state["processing_results"] = results
    st.session_state["output_directory"] = str(output_dir)
