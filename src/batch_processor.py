"""
Procesador de lotes para múltiples archivos.
"""

import time
from pathlib import Path
from typing import List, Dict, Optional
from .converter import DialogConverter
from .odt_handler import is_odt_file


class BatchProcessor:
    """Procesa múltiples archivos en una carpeta."""
    
    def __init__(self, converter: DialogConverter):
        self.converter = converter
    
    def process_directory(
        self, 
        input_dir: Path, 
        output_dir: Optional[Path] = None,
        pattern: str = "*.*",
        recursive: bool = False
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
            return {'success': False, 'files_processed': 0}
        
        # Información inicial
        print(f"\nProcesando carpeta: {input_dir}")
        print(f"Encontrados: {len(files)} archivo(s)")
        print(f"Salida: {output_dir}\n")
        
        # Procesar archivos
        start_time = time.time()
        results = []
        
        for idx, file_path in enumerate(files, 1):
            self._show_progress(idx, len(files), file_path.name)
            
            try:
                # Determinar archivo de salida
                output_file = output_dir / f"{file_path.stem}_convertido{file_path.suffix}"
                
                # Leer archivo
                if is_odt_file(file_path):
                    from .odt_handler import ODTReader, ODTProcessor
                    reader = ODTReader(file_path)
                    text = reader.extract_text()
                    is_odt = True
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    is_odt = False
                
                # Convertir
                converted_text, logger = self.converter.convert(text)
                changes = logger.changes
                
                # Guardar
                if is_odt:
                    processor = ODTProcessor(file_path)
                    processor.process_and_save(
                        output_file,
                        self.converter.convert
                    )
                else:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(converted_text)
                
                # Guardar log
                log_file = output_dir / f"{file_path.stem}_convertido.log.txt"
                log_content = logger.generate_report()
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                results.append({
                    'file': file_path.name,
                    'success': True,
                    'changes': len(changes),
                    'output': output_file
                })
                
            except Exception as e:
                results.append({
                    'file': file_path.name,
                    'success': False,
                    'error': str(e)
                })
        
        # Limpiar línea de progreso
        print()  # Nueva línea después de la barra
        
        # Tiempo total
        elapsed_time = time.time() - start_time
        
        # Generar resumen
        self._show_summary(results, elapsed_time, output_dir)
        
        return {
            'success': True,
            'files_processed': len([r for r in results if r['success']]),
            'total_files': len(files),
            'results': results,
            'elapsed_time': elapsed_time
        }
    
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
        extensions = {'.odt', '.txt'}
        
        if recursive:
            iterator = directory.rglob(pattern)
        else:
            iterator = directory.glob(pattern)
        
        for file_path in iterator:
            if file_path.is_file() and file_path.suffix in extensions:
                # Ignorar archivos ya convertidos
                if not file_path.stem.endswith('_convertido'):
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
        bar = '█' * filled + '░' * (bar_length - filled)
        
        # Truncar nombre de archivo si es muy largo
        max_filename_len = 30
        if len(filename) > max_filename_len:
            display_name = filename[:27] + '...'
        else:
            display_name = filename
        
        print(
            f'\r[{bar}] {current}/{total} ({percent*100:.0f}%) - {display_name}',
            end='',
            flush=True
        )
    
    def _show_summary(self, results: List[Dict], elapsed_time: float, output_dir: Path):
        """
        Genera y muestra resumen final del procesamiento.
        
        Args:
            results: Lista de resultados por archivo
            elapsed_time: Tiempo total transcurrido
            output_dir: Carpeta de salida
        """
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        total_changes = sum(r.get('changes', 0) for r in successful)
        
        print("\n" + "━" * 80)
        
        if successful:
            print("\n✅ Archivos procesados correctamente:")
            for result in successful:
                changes = result.get('changes', 0)
                print(f"   ✓ {result['file']:<40} → {changes:>5} cambios")
        
        if failed:
            print("\n❌ Archivos con errores:")
            for result in failed:
                error = result.get('error', 'Error desconocido')
                print(f"   ✗ {result['file']:<40} → {error}")
        
        print("\n" + "━" * 80)
        print("✅ Procesamiento completado\n")
        print(f"   Archivos procesados: {len(successful)}/{len(results)}")
        print(f"   Total de cambios:    {total_changes:,}")
        print(f"   Tiempo transcurrido: {elapsed_time:.1f}s")
        print(f"\n   Archivos generados en: {output_dir}")
        print("━" * 80)
