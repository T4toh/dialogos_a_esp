"""
Procesador de lotes para múltiples archivos.
"""

import shutil
from pathlib import Path
from typing import Callable, Dict, List, Optional

from .converter import DialogConverter
from .odt_handler import ODTProcessor, is_odt_file


class BatchProcessor:
    """Procesa múltiples archivos en una carpeta."""

    def __init__(self, converter: DialogConverter):
        self.converter = converter

    def process_directory(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
        pattern: str = "*.*",
        recursive: bool = False,
    ) -> Dict:
        """
        Procesa todos los archivos de una carpeta.

        Args:
            input_dir: Carpeta de entrada
            output_dir: Carpeta de salida (default: input_dir/convertidos)
            pattern: Patrón de archivos a procesar
            recursive: Procesar subcarpetas

        Returns:
            Dict con resultados del procesamiento
        """
        # Configurar carpeta de salida
        if output_dir is None:
            output_dir = input_dir / "convertidos"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Encontrar archivos
        files = self.find_files(input_dir, pattern, recursive)

        if not files:
            print(f"\n❌ No se encontraron archivos en: {input_dir}")
            return {"success": False, "files_processed": 0}

        # Información inicial
        print(f"\nProcesando carpeta: {input_dir}")
        print(f"Encontrados: {len(files)} archivo(s)")
        print(f"Salida: {output_dir}\n")

        # Procesar archivos
        results = self.process_files(
            files, output_dir, progress_callback=self._show_progress
        )

        # Limpiar línea de progreso
        print()  # Nueva línea después de la barra

        # Generar resumen
        self._show_summary(results, output_dir)

        return {
            "success": True,
            "files_processed": len([r for r in results if r["success"]]),
            "total_files": len(files),
            "results": results,
        }

    def process_files(
        self,
        files: List[Path],
        output_dir: Path,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> List[Dict]:
        """
        Procesa una lista de archivos.

        Args:
            files: Lista de archivos a procesar
            output_dir: Carpeta de salida
            progress_callback: Función de callback para progreso (current, total, filename)

        Returns:
            Lista de resultados
        """
        results = []

        for idx, file_path in enumerate(files, 1):
            if progress_callback:
                progress_callback(idx, len(files), file_path.name)

            try:
                # CREAR NUEVO CONVERTIDOR POR CADA ARCHIVO
                converter = DialogConverter()

                # Determinar archivo de salida
                output_file = (
                    output_dir / f"{file_path.stem}_convertido{file_path.suffix}"
                )

                # Procesar según tipo
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

                # Copiar archivo original para debug
                original_copy = (
                    output_dir / f"{file_path.stem}_original{file_path.suffix}"
                )
                shutil.copy2(file_path, original_copy)

                # Guardar log estructurado JSON (si hay cambios)
                json_log_path = None
                try:
                    if converter.logger.changes:
                        json_log_path = (
                            output_dir / f"{file_path.stem}_convertido.log.json"
                        )
                        converter.logger.save_structured_log(json_log_path)
                except Exception:
                    pass

                results.append(
                    {
                        "file": file_path.name,
                        "success": True,
                        "changes": len(converter.logger.changes),
                        "output": output_file,
                        "log_file": log_file,
                        "json_log": str(json_log_path) if json_log_path else None,
                    }
                )

            except Exception as e:
                results.append(
                    {"file": file_path.name, "success": False, "error": str(e)}
                )

        return results

    def find_files(self, directory: Path, pattern: str, recursive: bool) -> List[Path]:
        """
        Encuentra archivos .odt y .txt en la carpeta.

        Args:
            directory: Carpeta a buscar
            pattern: Patrón de archivos
            recursive: Buscar en subcarpetas

        Returns:
            Lista de archivos encontrados
        """
        files = []

        # Extensiones soportadas
        extensions = {".odt", ".txt"}

        if recursive:
            iterator = directory.rglob(pattern)
        else:
            iterator = directory.glob(pattern)

        for file_path in iterator:
            if file_path.is_file() and file_path.suffix in extensions:
                # Ignorar archivos ya convertidos
                if not file_path.stem.endswith("_convertido"):
                    files.append(file_path)

        return sorted(files)

    def _show_progress(self, current: int, total: int, filename: str):
        """
        Muestra barra de progreso.

        Args:
            current: Número de archivo actual
            total: Total de archivos
            filename: Nombre del archivo actual
        """
        percent = current / total
        bar_length = 40
        filled = int(bar_length * percent)
        bar = "█" * filled + "░" * (bar_length - filled)

        # Truncar nombre de archivo si es muy largo
        max_filename_len = 30
        if len(filename) > max_filename_len:
            display_name = filename[:27] + "..."
        else:
            display_name = filename

        print(
            f"\r[{bar}] {current}/{total} ({percent * 100:.0f}%) - {display_name}",
            end="",
            flush=True,
        )

    def _show_summary(self, results: List[Dict], output_dir: Path):
        """
        Genera y muestra resumen final del procesamiento.

        Args:
            results: Lista de resultados por archivo
            output_dir: Carpeta de salida
        """
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        total_changes = sum(r.get("changes", 0) for r in successful)

        print("\n" + "━" * 80)

        if successful:
            print("\n✅ Archivos procesados correctamente:")
            for result in successful:
                changes = result.get("changes", 0)
                print(f"   ✓ {result['file']:<40} → {changes:>5} cambios")

        if failed:
            print("\n❌ Archivos con errores:")
            for result in failed:
                error = result.get("error", "Error desconocido")
                print(f"   ✗ {result['file']:<40} → {error}")

        print("\n" + "━" * 80)
        print("✅ Procesamiento completado\n")
        print(f"   Archivos procesados: {len(successful)}/{len(results)}")
        print(f"   Total de cambios:    {total_changes:,}")
        print(f"\n   Archivos generados en: {output_dir}")
        print("━" * 80)
