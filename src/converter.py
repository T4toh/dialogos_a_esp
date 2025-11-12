"""
Lógica principal de conversión de diálogos.
"""

import re
from typing import Tuple, List
from .logger import ConversionLogger
from .rules import is_dialog_tag, DIALOG_TAGS


class DialogConverter:
    """Conversor de diálogos de comillas a formato español con rayas."""
    
    # Raya de diálogo (em dash)
    EM_DASH = '—'
    
    # Comillas a detectar (rectas y tipográficas)
    QUOTES_PATTERN = r'["\u201C\u201D]'  # " y " "
    SINGLE_QUOTES_PATTERN = r"['\u2018\u2019]"  # ' y ' '
    
    def __init__(self):
        self.logger = ConversionLogger()
        self.current_line = 0
    
    def convert(self, text: str) -> Tuple[str, ConversionLogger]:
        """
        Convierte un texto completo.
        
        Args:
            text: Texto de entrada con comillas
            
        Returns:
            Tupla (texto_convertido, logger)
        """
        lines = text.split('\n')
        converted_lines = []
        
        for line_num, line in enumerate(lines, 1):
            self.current_line = line_num
            converted_line = self._convert_line(line)
            converted_lines.append(converted_line)
        
        return '\n'.join(converted_lines), self.logger
    
    def _convert_line(self, line: str) -> str:
        """
        Convierte una línea de texto.
        
        Args:
            line: Línea de texto
            
        Returns:
            Línea convertida
        """
        if not line.strip():
            return line
        
        original_line = line
        
        # Aplicar conversiones en orden de prioridad
        line = self._convert_dialog_with_tag(line, original_line)
        line = self._convert_standalone_dialog(line, original_line)
        line = self._convert_nested_quotes(line, original_line)
        
        return line
    
    def _convert_dialog_with_tag(self, line: str, original: str) -> str:
        """
        Convierte diálogos con etiqueta narrativa.
        Ejemplo: "Hola" dijo Juan. → —Hola —dijo Juan.
        """
        # Patrón para diálogos con etiqueta
        # Captura: comillas + contenido + comillas + espacio + posible puntuación + etiqueta
        
        # Patrón 1: "texto" verbo (comillas tipográficas y rectas)
        pattern1 = re.compile(
            self.QUOTES_PATTERN + r'([^"\u201C\u201D]+)' + self.QUOTES_PATTERN + r'\s+(' + '|'.join(DIALOG_TAGS) + r')\b',
            re.IGNORECASE
        )
        
        def replace1(match):
            content = match.group(1)
            tag = match.group(2)
            
            # Verificar puntuación al final del contenido
            if content.endswith(('?', '!', '.')):
                result = f'{self.EM_DASH}{content} {self.EM_DASH}{tag.lower()}'
            elif content.endswith(','):
                # Quitar coma del final
                content_clean = content.rstrip(',').strip()
                result = f'{self.EM_DASH}{content_clean} {self.EM_DASH}{tag.lower()}'
            else:
                result = f'{self.EM_DASH}{content} {self.EM_DASH}{tag.lower()}'
            
            if original != line:
                return result
            
            self.logger.log_change(
                self.current_line,
                match.group(0),
                result,
                'D2: Etiqueta de diálogo'
            )
            return result
        
        new_line = pattern1.sub(replace1, line)
        
        # Patrón 2: "texto", verbo o "texto." Verbo (comillas tipográficas y rectas)
        pattern2 = re.compile(
            self.QUOTES_PATTERN + r'([^"\u201C\u201D]+)' + self.QUOTES_PATTERN + r'([,.\s]+)([A-ZÁÉÍÓÚÑ][a-záéíóúñ]*)\b'
        )
        
        def replace2(match):
            content = match.group(1)
            punct = match.group(2)
            word = match.group(3)
            
            # Verificar si la palabra es etiqueta de diálogo
            if is_dialog_tag(word):
                # Es etiqueta de diálogo
                if content.endswith(('.', '?', '!')):
                    result = f'{self.EM_DASH}{content} {self.EM_DASH}{word.lower()}'
                elif content.endswith(','):
                    content_clean = content.rstrip(',').strip()
                    result = f'{self.EM_DASH}{content_clean} {self.EM_DASH}{word.lower()}'
                else:
                    result = f'{self.EM_DASH}{content} {self.EM_DASH}{word.lower()}'
                
                self.logger.log_change(
                    self.current_line,
                    match.group(0),
                    result,
                    'D2: Etiqueta de diálogo con mayúscula'
                )
                return result
            else:
                # No es etiqueta, es narración nueva
                if content.endswith('.'):
                    result = f'{self.EM_DASH}{content} {word}'
                else:
                    result = f'{self.EM_DASH}{content}. {word}'
                
                self.logger.log_change(
                    self.current_line,
                    match.group(0),
                    result,
                    'D3: Diálogo seguido de narración'
                )
                return result
        
        if new_line == line:
            new_line = pattern2.sub(replace2, new_line)
        
        # Patrón 3: Comillas simples con etiqueta (simples tipográficas y rectas)
        pattern3 = re.compile(
            self.SINGLE_QUOTES_PATTERN + r"([^'\u2018\u2019]+)" + self.SINGLE_QUOTES_PATTERN + r'\s+(' + '|'.join(DIALOG_TAGS) + r')\b',
            re.IGNORECASE
        )
        
        def replace3(match):
            content = match.group(1)
            tag = match.group(2)
            
            if content.endswith(('?', '!', '.')):
                result = f'{self.EM_DASH}{content} {self.EM_DASH}{tag.lower()}'
            elif content.endswith(','):
                content_clean = content.rstrip(',').strip()
                result = f'{self.EM_DASH}{content_clean} {self.EM_DASH}{tag.lower()}'
            else:
                result = f'{self.EM_DASH}{content} {self.EM_DASH}{tag.lower()}'
            
            self.logger.log_change(
                self.current_line,
                match.group(0),
                result,
                'D2: Etiqueta de diálogo (comillas simples)'
            )
            return result
        
        new_line = pattern3.sub(replace3, new_line)
        
        return new_line
    
    def _convert_standalone_dialog(self, line: str, original: str) -> str:
        """
        Convierte diálogos sin etiqueta (standalone).
        Ejemplo: "Hola, Juan" → —Hola, Juan
        """
        # Solo al inicio de línea o después de espacios (comillas tipográficas y rectas)
        pattern1 = re.compile(r'^(\s*)' + self.QUOTES_PATTERN + r'([^"\u201C\u201D]+)' + self.QUOTES_PATTERN)
        
        def replace1(match):
            indent = match.group(1)
            content = match.group(2)
            result = f'{indent}{self.EM_DASH}{content}'
            
            self.logger.log_change(
                self.current_line,
                match.group(0),
                result,
                'D1: Sustitución de delimitadores'
            )
            return result
        
        new_line = pattern1.sub(replace1, line)
        
        # Comillas simples al inicio (simples tipográficas y rectas)
        pattern2 = re.compile(r"^(\s*)" + self.SINGLE_QUOTES_PATTERN + r"([^'\u2018\u2019]+)" + self.SINGLE_QUOTES_PATTERN)
        
        def replace2(match):
            indent = match.group(1)
            content = match.group(2)
            result = f'{indent}{self.EM_DASH}{content}'
            
            self.logger.log_change(
                self.current_line,
                match.group(0),
                result,
                'D1: Sustitución de delimitadores (comillas simples)'
            )
            return result
        
        if new_line == line:
            new_line = pattern2.sub(replace2, new_line)
        
        # Comillas dobles restantes (no procesadas) - tipográficas y rectas
        pattern3 = re.compile(self.QUOTES_PATTERN + r'([^"\u201C\u201D]+)' + self.QUOTES_PATTERN)
        
        def replace3(match):
            content = match.group(1)
            result = f'{self.EM_DASH}{content}'
            
            self.logger.log_change(
                self.current_line,
                match.group(0),
                result,
                'D1: Sustitución de delimitadores (restantes)'
            )
            return result
        
        # Solo aplicar si no hay rayas ya
        if self.EM_DASH not in new_line:
            new_line = pattern3.sub(replace3, new_line)
        
        return new_line
    
    def _convert_nested_quotes(self, line: str, original: str) -> str:
        """
        Convierte comillas dentro de diálogos a comillas latinas.
        Ejemplo: —Ella me dijo 'te esperaré' → —Ella me dijo «te esperaré»
        
        IMPORTANTE: No convierte comillas que son continuación del diálogo después de etiqueta.
        Ejemplo: —Hola —dijo Juan. "¿Cómo estás?" → —Hola —dijo Juan. —¿Cómo estás?
        """
        # Solo si la línea ya tiene raya de diálogo
        if self.EM_DASH not in line:
            return line
        
        # Verificar si hay etiqueta de diálogo seguida de más diálogo
        # Patrón: —texto —verbo. "más diálogo"
        # Esto indica continuación del mismo personaje, NO cita interna
        has_continuation = False
        for tag in DIALOG_TAGS:
            # Buscar patrón: —verbo seguido de punto/coma y comillas
            if re.search(self.EM_DASH + tag + r'\b[^.]*[\.,]\s*' + self.QUOTES_PATTERN, line, re.IGNORECASE):
                has_continuation = True
                break
        
        # Si hay continuación de diálogo, convertir esas comillas a rayas, no a latinas
        if has_continuation:
            # Convertir comillas después de etiqueta de diálogo a rayas
            pattern_continuation = re.compile(
                r'(' + self.EM_DASH + r'(?:' + '|'.join(DIALOG_TAGS) + r')\b[^.]*?[\.,]\s*)' +
                self.QUOTES_PATTERN + r'([^"\u201C\u201D]+)' + self.QUOTES_PATTERN,
                re.IGNORECASE
            )
            
            def replace_continuation(match):
                prefix = match.group(1)
                content = match.group(2)
                result = f'{prefix}{self.EM_DASH}{content}'
                
                self.logger.log_change(
                    self.current_line,
                    match.group(0),
                    result,
                    'D4: Continuación de diálogo del mismo personaje'
                )
                return result
            
            line = pattern_continuation.sub(replace_continuation, line)
            return line
        
        # Si no hay continuación, son citas internas → convertir a comillas latinas
        # Buscar comillas simples dentro de diálogos con raya (tipográficas y rectas)
        pattern = re.compile(self.SINGLE_QUOTES_PATTERN + r"([^'\u2018\u2019]+)" + self.SINGLE_QUOTES_PATTERN)
        
        def replace(match):
            content = match.group(1)
            result = f'«{content}»'
            
            self.logger.log_change(
                self.current_line,
                match.group(0),
                result,
                'D5: Cita interna con comillas latinas'
            )
            return result
        
        new_line = pattern.sub(replace, line)
        
        # También convertir comillas dobles internas (tipográficas y rectas)
        pattern2 = re.compile(self.QUOTES_PATTERN + r'([^"\u201C\u201D]+)' + self.QUOTES_PATTERN)
        
        def replace2(match):
            content = match.group(1)
            result = f'«{content}»'
            
            self.logger.log_change(
                self.current_line,
                match.group(0),
                result,
                'D5: Cita interna con comillas latinas'
            )
            return result
        
        new_line = pattern2.sub(replace2, new_line)
        
        return new_line
