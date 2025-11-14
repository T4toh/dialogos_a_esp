"""
Sistema de logging para registrar todos los cambios realizados.
"""

from typing import List, Tuple
from pathlib import Path
import io


class ConversionLogger:
    """Registra y formatea los cambios realizados durante la conversión."""
    
    def __init__(self):
        self.changes: List[Tuple[int, str, str, str]] = []
        self.line_number = 0
        
    def log_change(self, line_num: int, original: str, converted: str, rule: str):
        """
        Registra un cambio realizado.
        
        Args:
            line_num: Número de línea (aproximado)
            original: Texto original
            converted: Texto convertido
            rule: Regla aplicada
        """
        self.changes.append((line_num, original, converted, rule))
    
    def _format_text(self, text: str) -> str:
        """
        Formatea texto para el log sin truncar.
        
        Args:
            text: Texto a formatear
            
        Returns:
            Texto formateado
        """
        # Solo limpiar espacios extras pero mantener contenido completo
        return ' '.join(text.split())
    
    def generate_report(self) -> str:
        """
        Genera el reporte completo de cambios.
        
        Returns:
            String con el reporte formateado
        """
        buffer = io.StringIO()
        
        buffer.write("LOG DE CONVERSIÓN DE DIÁLOGOS A FORMATO ESPAÑOL\n")
        buffer.write("=" * 80 + "\n\n")
        
        buffer.write(f"Total de cambios realizados: {len(self.changes)}\n\n")
        
        if not self.changes:
            buffer.write("No se realizaron cambios.\n")
            return buffer.getvalue()
        
        for idx, (line_num, original, converted, rule) in enumerate(self.changes, 1):
            buffer.write(f"CAMBIO #{idx}\n")
            buffer.write(f"Línea: ~{line_num}\n")
            buffer.write(f"Regla: {rule}\n\n")
            
            # Formatear sin truncar
            original_display = self._format_text(original)
            converted_display = self._format_text(converted)
            
            buffer.write("ORIGINAL:\n")
            buffer.write(f"  {original_display}\n\n")
            
            buffer.write("CONVERTIDO:\n")
            buffer.write(f"  {converted_display}\n\n")
            
            buffer.write("-" * 80 + "\n\n")
        
        return buffer.getvalue()
    
    def save_to_file(self, filepath: Path):
        """
        Guarda el log en un archivo.
        
        Args:
            filepath: Ruta del archivo de log
        """
        report = self.generate_report()
        filepath.write_text(report, encoding='utf-8')
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas de la conversión.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'total_changes': len(self.changes),
            'rules_applied': list(set(rule for _, _, _, rule in self.changes))
        }
