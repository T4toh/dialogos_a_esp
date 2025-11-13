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
        # Repetir hasta que no haya más comillas (para líneas con múltiples diálogos)
        max_iterations = 10  # Evitar loops infinitos
        for _ in range(max_iterations):
            prev_line = line
            line = self._convert_dialog_with_tag(line, original_line)
            line = self._convert_standalone_dialog(line, original_line)
            line = self._convert_nested_quotes(line, original_line)
            
            # Si no cambió, ya terminamos
            if line == prev_line:
                break
        
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
                # No agregar punto si ya termina con puntuación
                if content.endswith(('.', '?', '!', '…')):
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
        
        También maneja múltiples diálogos consecutivos en la misma línea.
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
        
        # NUEVO: Comillas que son diálogos adicionales en la misma línea
        # Patrón: después de un espacio o después de narración
        # Ejemplo: "Texto1" "Texto2" o Narración. "Texto"
        # SOLO si NO tiene etiqueta de diálogo antes
        
        # Verificar si hay comillas restantes que NO son citas internas
        # (comillas que están al inicio de una frase o después de narración)
        pattern_additional = re.compile(
            r'(\s+)' + self.QUOTES_PATTERN + r'([^"\u201C\u201D]+)' + self.QUOTES_PATTERN
        )
        
        def replace_additional(match):
            space = match.group(1)
            content = match.group(2)
            
            # Verificar si el contenido parece ser un diálogo completo
            # (empieza con mayúscula o signos de interrogación/exclamación)
            if content.strip() and (content[0].isupper() or content.startswith(('¿', '¡'))):
                result = f'{space}{self.EM_DASH}{content}'
                
                self.logger.log_change(
                    self.current_line,
                    match.group(0),
                    result,
                    'D1: Diálogo adicional en línea'
                )
                return result
            
            # Si no parece diálogo, no tocar
            return match.group(0)
        
        # Solo aplicar si la línea ya tiene rayas (indica que estamos en contexto de diálogos)
        if self.EM_DASH in new_line:
            new_line = pattern_additional.sub(replace_additional, new_line)
        
        return new_line
    
    def _convert_nested_quotes(self, line: str, original: str) -> str:
        """
        Convierte comillas dentro de diálogos a comillas latinas.
        Ejemplo: —Ella me dijo 'te esperaré' → —Ella me dijo «te esperaré»
        
        IMPORTANTE: NO aplica D5 si las comillas son:
        1. Continuación de diálogo después de etiqueta
        2. Nuevo diálogo en la misma línea
        3. Diálogo al inicio de la línea (ya procesado antes)
        
        Solo convierte a latinas si son CITAS DENTRO del diálogo.
        """
        # Solo si la línea ya tiene raya de diálogo
        if self.EM_DASH not in line:
            return line
        
        # NO aplicar D5 si hay comillas que son diálogos independientes
        # Casos donde NO debe aplicarse D5:
        
        # 1. Comillas al inicio después de espacios (es un diálogo nuevo en la línea)
        if re.search(r'^\s*' + self.QUOTES_PATTERN, line):
            return line
        
        # 2. Comillas después de etiqueta de diálogo (continuación)
        # Ejemplo: —dijo pensativa. "Más texto"
        for tag in DIALOG_TAGS:
            if re.search(self.EM_DASH + tag + r'\b[^"]*?[\.,]\s*' + self.QUOTES_PATTERN, line, re.IGNORECASE):
                # Es continuación de diálogo, NO cita interna
                # Ya debería haberse procesado en _convert_dialog_with_tag, pero por las dudas
                return line
        
        # 3. Comillas después de narración con mayúscula (nuevo diálogo)
        # Ejemplo: —Texto. Narración con mayúscula. "Más diálogo"
        if re.search(r'\.\s+[A-ZÁÉÍÓÚÑ][^.]*\s*' + self.QUOTES_PATTERN, line):
            return line
        
        # 4. Múltiples diálogos en la misma línea separados por espacio
        # Ejemplo: "Texto1" "Texto2"
        # Contar comillas: si hay más de 2 pares, probablemente son diálogos consecutivos
        quote_count = len(re.findall(self.QUOTES_PATTERN, line))
        if quote_count >= 4:  # 2 o más pares de comillas
            return line
        
        # Si llegamos acá, son citas internas legítimas
        # SOLO convertir comillas SIMPLES a latinas (citas dentro de diálogo)
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
        
        return new_line
