"""
Página de conversión por lotes.
Maneja el procesamiento de múltiples archivos.
"""

from pathlib import Path

import streamlit as st

from src.converter import DialogConverter
from src.odt_handler import ODTProcessor, is_odt_file


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
    results = []
    total_files = len(selected_files)

    for idx, file_path in enumerate(selected_files, 1):
        # Actualizar progreso
        progress = idx / total_files
        progress_bar.progress(progress)
        status_text.text(f"Procesando {idx}/{total_files}: {file_path.name}")

        try:
            # CREAR NUEVO CONVERTIDOR POR CADA ARCHIVO
            converter = DialogConverter()

            # Determinar archivo de salida
            output_file = output_dir / f"{file_path.stem}_convertido{file_path.suffix}"

            # Leer y convertir
            if is_odt_file(file_path):
                processor = ODTProcessor(file_path)
                processor.process_and_save(output_file, converter.convert)
                log_content = converter.logger.generate_report()
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                converted_text, logger = converter.convert(text)

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(converted_text)

                log_content = logger.generate_report()

            # Guardar log
            log_file = output_dir / f"{file_path.stem}_convertido.log.txt"
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(log_content)

            # Guardar log estructurado JSON
            json_file_path = None
            try:
                json_log_file = output_dir / f"{file_path.stem}_convertido.log.json"
                if hasattr(converter, "logger") and converter.logger.changes:
                    converter.logger.save_structured_log(json_log_file)
                    json_file_path = json_log_file
            except Exception:
                # Non-critical: ignore failures saving structured log
                pass

            results.append(
                {
                    "file": file_path.name,
                    "success": True,
                    "changes": len(converter.logger.changes),
                    "output": output_file,
                    "log_file": log_file,
                    "json_log": str(json_file_path) if json_file_path else None,
                }
            )

        except Exception as e:
            results.append({"file": file_path.name, "success": False, "error": str(e)})

    # Completar progreso
    progress_bar.progress(1.0)
    status_text.text("✅ Procesamiento completado")

    # Guardar resultados en session_state para persistencia
    st.session_state["processing_results"] = results
    st.session_state["output_directory"] = str(output_dir)
