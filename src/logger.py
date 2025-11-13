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
    
    def _truncate_text(self, text: str, max_length: int = 150) -> str:
        """
        Trunca texto largo mostrando solo el inicio relevante.
        Para logs de conversión, lo importante es ver el CAMBIO, no todo el texto.
        
        Args:
            text: Texto a truncar
            max_length: Longitud máxima (aumentado a 150 para mayor contexto)
            
        Returns:
            Texto truncado mostrando el inicio (donde están los cambios)
        """
        if len(text) <= max_length:
            return text
        
        # Truncar mostrando el inicio (donde suelen estar los cambios)
        # Intentar cortar en un espacio para no partir palabras
        truncate_at = max_length
        
        # Buscar el último espacio antes del límite
        last_space = text.rfind(' ', 0, max_length)
        if last_space > max_length * 0.8:  # Si el espacio está cerca del final
            truncate_at = last_space
        
        truncated = text[:truncate_at]
        
        # Agregar indicador de truncamiento
        if truncate_at < len(text):
            truncated = truncated + "..."
                
        return truncated
    
    def generate_report(self) -> str:
        """
        Genera el reporte completo de cambios.
        
        Returns:
            String con el reporte formateado
        """
        buffer = io.StringIO()
        
        buffer.write("=" * 80 + "\n")
        buffer.write("LOG DE CONVERSIÓN DE DIÁLOGOS A FORMATO ESPAÑOL\n")
        buffer.write("=" * 80 + "\n\n")
        
        buffer.write(f"Total de cambios realizados: {len(self.changes)}\n\n")
        
        if not self.changes:
            buffer.write("No se realizaron cambios.\n")
            return buffer.getvalue()
        
        buffer.write("-" * 80 + "\n\n")
        
        for idx, (line_num, original, converted, rule) in enumerate(self.changes, 1):
            buffer.write(f"CAMBIO #{idx}\n")
            buffer.write(f"Ubicación: ~línea {line_num}\n")
            buffer.write(f"Regla aplicada: {rule}\n\n")
            
            # Truncar textos largos
            original_display = self._truncate_text(original)
            converted_display = self._truncate_text(converted)
            
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
