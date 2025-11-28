"""
Lógica principal de conversión de diálogos.
"""

import re
from typing import Tuple

from .logger import ConversionLogger
from .rules import DIALOG_TAGS, is_dialog_tag


class DialogConverter:
    """Conversor de diálogos de comillas a formato español con rayas."""

    # Raya de diálogo (em dash)
    EM_DASH = "—"

    # Comillas a detectar (rectas y tipográficas)
    QUOTES_PATTERN = r'["\u201C\u201D]'  # " y " "
    SINGLE_QUOTES_PATTERN = r"['\u2018\u2019]"  # ' y ' '

    # Comillas españolas (latinas)
    LATIN_QUOTES = ("«", "»")

    def __init__(self):
        self.logger = ConversionLogger()
        self.current_line = 0

    def _get_sentence_context(self, full_line: str, match) -> str:
        """
        Extrae la oración (bloque) completa en `full_line` que contiene la
        coincidencia `match`. Intenta separar por puntos, signos de pregunta
        o exclamación y devuelve el segmento que contiene la coincidencia.
        Si no se encuentra, devuelve la línea completa.
        """
        try:
            start, end = match.span()
        except Exception:
            # Si no es un objeto re.Match, devolver full_line
            return full_line

        # Patrón simple para oraciones: captura hasta un terminador o fin de línea
        sentence_pattern = re.compile(r".+?(?:[\.\?!…](?=\s|$)|$)")
        for m in sentence_pattern.finditer(full_line):
            s0, s1 = m.span()
            if s0 <= start < s1:
                return full_line[s0:s1].strip()

        return full_line.strip()

    def convert(self, text: str) -> Tuple[str, ConversionLogger]:
        """
        Convierte un texto completo.

        Args:
            text: Texto de entrada con comillas

        Returns:
            Tupla (texto_convertido, logger)
        """
        # PASO 0: Normalizar comillas
        text = self._normalize_quotes(text)

        # PASO 1: Normalizar espacios antes de verbos de dicción
        text = self._normalize_spacing_before_tags(text)

        lines = text.split("\n")
        converted_lines = []

        for line_num, line in enumerate(lines, 1):
            self.current_line = line_num
            converted_line = self._convert_line(line)
            # After finishing modifications to the line, attempt to post-process
            # spans so converted fragments are located against the final
            # converted line. This reduces deletion-only diffs.
            try:
                self.logger.post_process_line_spans(line_num, converted_line)
            except Exception:
                # Non-fatal; logging enrichment is optional
                pass
            converted_lines.append(converted_line)

        return "\n".join(converted_lines), self.logger

    def _normalize_quotes(self, text: str) -> str:
        """
        Normaliza todos los tipos de comillas a un formato estándar.

        Convierte:
        - Comillas españolas « » → " " (para detección consistente)
        - Comillas tipográficas curvas " " → " "
        - Comillas simples ' ' → '

        Args:
            text: Texto original

        Returns:
            Texto con comillas normalizadas
        """
        # Comillas españolas (latinas) → comillas rectas
        text = text.replace("«", '"').replace("»", '"')

        # Comillas tipográficas inglesas → comillas rectas
        text = text.replace('"', '"').replace('"', '"')

        # Comillas simples tipográficas → comillas simples rectas
        text = text.replace(""", "'").replace(""", "'")

        return text

    def _normalize_spacing_before_tags(self, text: str) -> str:
        """
        Normaliza espacios faltantes antes de verbos de dicción.

        Corrige: "texto"Verbo → "texto" Verbo

        Args:
            text: Texto con comillas normalizadas

        Returns:
            Texto con espacios corregidos
        """
        # Patrón: comilla + puntuación opcional + comilla + mayúscula
        # Detecta casos como: "texto"Dijo, "texto."Dijo, "texto",Dijo
        # Nota: En este punto las comillas ya están normalizadas a comillas rectas
        pattern = re.compile(r'"([.,]?)"([A-ZÁÉÍÓÚÑ]\w+)', flags=re.UNICODE)

        # Track changes for logging
        changes_made = []

        def add_space(match):
            punct = match.group(1)  # Puntuación opcional (. o ,)
            word = match.group(2)  # Palabra que sigue

            # Verificar si la palabra es verbo de dicción
            if is_dialog_tag(word):
                # Insertar espacio antes del verbo
                original = match.group(0)
                result = f'"{punct}" {word}'

                # Track this change
                changes_made.append(
                    {"original": original, "converted": result, "word": word}
                )

                return result

            # No es verbo, dejar como está
            return match.group(0)

        result_text = pattern.sub(add_space, text)

        # Log the normalization changes
        if changes_made:
            # Create a summary log entry for all spacing normalizations
            for change in changes_made:
                # Log each normalization change
                # We use line 0 as a placeholder since this is text-level normalization
                self.logger.log_change(
                    line_num=0,
                    original=change["original"],
                    converted=change["converted"],
                    rule="N1: Normalización de espacio antes de verbo de dicción",
                    original_fragment=change["original"],
                    converted_fragment=change["converted"],
                )

        return result_text

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

        # PASO 0: Normalizar puntuación incorrecta antes de verbos de dicción
        line = self._fix_punctuation_before_dialog_tag(line)

        # Aplicar conversiones en orden de prioridad
        # Repetir hasta que no haya más comillas (para líneas con múltiples diálogos)
        max_iterations = 10  # Evitar loops infinitos
        for _ in range(max_iterations):
            prev_line = line
            line = self._convert_dialog_with_narration(
                line, original_line
            )  # D4: Narración sin verbo (primero para detectar narración completa)
            line = self._convert_dialog_with_interruption(
                line, original_line
            )  # D3: Incisos con verbo
            line = self._convert_dialog_with_tag(line, original_line)  # D2
            line = self._convert_standalone_dialog(line, original_line)  # D1
            line = self._convert_nested_quotes(line, original_line)  # D5

            # Si no cambió, ya terminamos
            if line == prev_line:
                break

        return line

    def _fix_punctuation_before_dialog_tag(self, line: str) -> str:
        """
        Corrige puntuación incorrecta antes de verbos de dicción.

        Según RAE: "texto", verbo (NO "texto." verbo)

        Args:
            line: Línea original

        Returns:
            Línea con puntuación corregida
        """
        # Patrón: "texto1." Verbo resto. "texto2"
        # Detecta continuación del personaje con inciso del narrador
        pattern = re.compile(
            r'"([^"]+)\.\s*"\s+('
            + "|".join(DIALOG_TAGS)
            + r')\b([^"]*?)\.\s+"([^"]+)"',
            re.IGNORECASE,
        )

        def replace_punct(match):
            content1 = match.group(1).strip()
            verb = match.group(2)
            verb_rest = match.group(3).strip()
            content2 = match.group(4).strip()

            # Verificar si el contenido termina en signos fuertes
            if content1.endswith(("?", "!", "…")):
                # No cambiar: los signos fuertes son correctos
                return match.group(0)

            # Cambiar a formato de inciso: "texto1", verbo resto. "texto2"
            if verb_rest:
                return f'"{content1}", {verb} {verb_rest}. "{content2}"'
            else:
                return f'"{content1}", {verb}. "{content2}"'

        return pattern.sub(replace_punct, line)

    def _convert_dialog_with_interruption(self, line: str, original: str) -> str:
        """
        Convierte diálogos con inciso del narrador (D3).

        Ejemplo: "Lo principal", añadió, "es esto" → —Lo principal —añadió—, es esto

        Args:
            line: Línea a convertir
            original: Línea original para logging

        Returns:
            Línea convertida
        """
        # Patrón 1: "texto1", verbo, "texto2" (con coma)
        pattern1 = re.compile(
            r'"([^"]+)",\s+(' + "|".join(DIALOG_TAGS) + r')\b([^,]*),\s+"([^"]+)"',
            re.IGNORECASE,
        )

        def replace_interruption1(match):
            text1 = match.group(1).strip()
            verb = match.group(2).lower()
            verb_rest = match.group(3).strip()
            text2 = match.group(4).strip()

            # Estructura RAE: —texto1 —verbo resto—, texto2
            if verb_rest:
                result = (
                    f"{self.EM_DASH}{text1} "
                    f"{self.EM_DASH}{verb} {verb_rest}{self.EM_DASH}, "
                    f"{text2}"
                )
            else:
                result = (
                    f"{self.EM_DASH}{text1} {self.EM_DASH}{verb}{self.EM_DASH}, {text2}"
                )

            if original != line:
                return result

            sentence = self._get_sentence_context(line, match)
            converted_sentence = sentence.replace(match.group(0), result, 1)
            self.logger.log_change(
                self.current_line,
                sentence,
                converted_sentence,
                "D3: Inciso del narrador con continuación",
                match.group(0),
                result,
                full_text=original,
                full_converted=converted_sentence,
            )
            return result

        line = pattern1.sub(replace_interruption1, line)

        # Patrón 2: "texto1", verbo resto. "texto2" (con punto)
        pattern2 = re.compile(
            r'"([^"]+)",\s+(' + "|".join(DIALOG_TAGS) + r')\b([^"]*?)\.\s+"([^"]+)"',
            re.IGNORECASE,
        )

        def replace_interruption2(match):
            text1 = match.group(1).strip()
            verb = match.group(2).lower()
            verb_rest = match.group(3).strip()
            text2 = match.group(4).strip()

            # Estructura RAE: —texto1 —verbo resto—. texto2
            if verb_rest:
                result = (
                    f"{self.EM_DASH}{text1} "
                    f"{self.EM_DASH}{verb} {verb_rest}{self.EM_DASH}. "
                    f"{text2}"
                )
            else:
                result = (
                    f"{self.EM_DASH}{text1} {self.EM_DASH}{verb}{self.EM_DASH}. {text2}"
                )

            if original != line:
                return result

            sentence = self._get_sentence_context(line, match)
            converted_sentence = sentence.replace(match.group(0), result, 1)
            self.logger.log_change(
                self.current_line,
                sentence,
                converted_sentence,
                "D3: Inciso del narrador con continuación (punto)",
                match.group(0),
                result,
                full_text=original,
                full_converted=converted_sentence,
            )
            return result

        return pattern2.sub(replace_interruption2, line)

    def _convert_dialog_with_narration(self, line: str, original: str) -> str:
        """
        Convierte diálogos con narración intermedia (D4).

        RAE 2.3.b: "texto1." Narración (sin verbo). "texto2"
        → —texto1. —Narración—. texto2

        Ejemplo: "Hola." Cerró la puerta. "Adiós." → —Hola. —Cerró la puerta—. Adiós.

        Args:
            line: Línea a convertir
            original: Línea original para logging

        Returns:
            Línea convertida
        """
        # Patrón: "texto1." Narración. "texto2"
        # donde Narración NO contiene verbos de dicción
        pattern = re.compile(
            r'"([^"]+)"\s+([A-ZÁÉÍÓÚÑ][^"]*?)\.\s+"([^"]+)"', re.IGNORECASE
        )

        def replace_narration(match):
            text1 = match.group(1).strip()
            narration = match.group(2).strip()
            text2 = match.group(3).strip()

            # Verificar que NO haya verbo de dicción en la narración
            words = narration.split()
            for word in words:
                if is_dialog_tag(word):
                    # Hay verbo de dicción, no aplicar esta regla
                    return match.group(0)

            # Limpiar puntuación final de text1 (ya viene con punto del patrón)
            text1 = text1.rstrip(".")

            # Estructura RAE: —texto1 —Narración—. texto2
            # Para narración intermedia entre diálogos, texto1 NO lleva punto final
            result = (
                f"{self.EM_DASH}{text1} "
                f"{self.EM_DASH}{narration}{self.EM_DASH}. "
                f"{text2}"
            )

            if original != line:
                return result

            sentence = self._get_sentence_context(line, match)
            converted_sentence = sentence.replace(match.group(0), result, 1)
            self.logger.log_change(
                self.current_line,
                sentence,
                converted_sentence,
                "D4: Narración intermedia con continuación",
                match.group(0),
                result,
                full_text=original,
                full_converted=converted_sentence,
            )
            return result

        return pattern.sub(replace_narration, line)

    def _convert_dialog_with_tag(self, line: str, original: str) -> str:
        """
        Convierte diálogos con etiqueta narrativa.
        Ejemplo: "Hola" dijo Juan. → —Hola —dijo Juan.
        """
        # Patrón para diálogos con etiqueta
        # Captura: comillas + contenido + comillas + espacio
        # + posible puntuación + etiqueta

        # Patrón 1: "texto" verbo (comillas tipográficas y rectas)
        pattern1 = re.compile(
            self.QUOTES_PATTERN
            + r'([^"\u201C\u201D]+)'
            + self.QUOTES_PATTERN
            + r"\s+("
            + "|".join(DIALOG_TAGS)
            + r")\b",
            re.IGNORECASE,
        )

        def replace1(match):
            content = match.group(1)
            tag = match.group(2)

            # Regla RAE: cuando hay verbo de lengua, quitar punto final del diálogo
            if content.endswith("."):
                # Quitar punto final cuando hay verbo de lengua
                content_clean = content.rstrip(".").strip()
                result = f"{self.EM_DASH}{content_clean} {self.EM_DASH}{tag.lower()}"
            elif content.endswith(("?", "!")):
                # Mantener signos de interrogación/exclamación
                result = f"{self.EM_DASH}{content} {self.EM_DASH}{tag.lower()}"
            elif content.endswith(","):
                # Quitar coma del final
                content_clean = content.rstrip(",").strip()
                result = f"{self.EM_DASH}{content_clean} {self.EM_DASH}{tag.lower()}"
            else:
                result = f"{self.EM_DASH}{content} {self.EM_DASH}{tag.lower()}"

            if original != line:
                return result

            sentence = self._get_sentence_context(line, match)
            converted_sentence = sentence.replace(match.group(0), result, 1)
            self.logger.log_change(
                self.current_line,
                sentence,
                converted_sentence,
                "D2: Etiqueta de diálogo",
                match.group(0),
                result,
                full_text=original,
                full_converted=converted_sentence,
            )
            return result

        new_line = pattern1.sub(replace1, line)

        # Patrón 2: "texto", verbo o "texto." Verbo (comillas tipográficas y rectas)
        pattern2 = re.compile(
            self.QUOTES_PATTERN
            + r'([^"\u201C\u201D]+)'
            + self.QUOTES_PATTERN
            + r"([,.\s]+)([A-ZÁÉÍÓÚÑ][a-záéíóúñ]*)\b"
        )

        def replace2(match):
            content = match.group(1)
            word = match.group(3)

            # Verificar si la palabra es etiqueta de diálogo
            if is_dialog_tag(word):
                # Regla RAE: cuando hay verbo de lengua, quitar punto final del diálogo
                if content.endswith("."):
                    # Quitar punto final cuando hay verbo de lengua
                    content_clean = content.rstrip(".").strip()
                    result = (
                        f"{self.EM_DASH}{content_clean} {self.EM_DASH}{word.lower()}"
                    )
                elif content.endswith(("?", "!")):
                    # Mantener signos de interrogación/exclamación
                    result = f"{self.EM_DASH}{content} {self.EM_DASH}{word.lower()}"
                elif content.endswith(","):
                    content_clean = content.rstrip(",").strip()
                    result = (
                        f"{self.EM_DASH}{content_clean} {self.EM_DASH}{word.lower()}"
                    )
                else:
                    result = f"{self.EM_DASH}{content} {self.EM_DASH}{word.lower()}"

                sentence = self._get_sentence_context(line, match)
                converted_sentence = sentence.replace(match.group(0), result, 1)
                self.logger.log_change(
                    self.current_line,
                    sentence,
                    converted_sentence,
                    "D2: Etiqueta de diálogo con mayúscula",
                    match.group(0),
                    result,
                    full_text=original,
                    full_converted=converted_sentence,
                )
                return result
            else:
                # No es etiqueta, es narración nueva (RAE 2.3.d)
                # Según RAE: debe iniciarse con mayúscula y llevar raya de apertura
                if content.endswith((".", "?", "!", "…")):
                    result = f"{self.EM_DASH}{content} {self.EM_DASH}{word}"
                else:
                    result = f"{self.EM_DASH}{content}. {self.EM_DASH}{word}"

                sentence = self._get_sentence_context(line, match)
                converted_sentence = sentence.replace(match.group(0), result, 1)
                self.logger.log_change(
                    self.current_line,
                    sentence,
                    converted_sentence,
                    "D3: Diálogo seguido de narración",
                    match.group(0),
                    result,
                    full_text=original,
                    full_converted=converted_sentence,
                )
                return result

        if new_line == line:
            new_line = pattern2.sub(replace2, new_line)

        # Patrón 3: Comillas simples con etiqueta (simples tipográficas y rectas)
        pattern3 = re.compile(
            self.SINGLE_QUOTES_PATTERN
            + r"([^'\u2018\u2019]+)"
            + self.SINGLE_QUOTES_PATTERN
            + r"\s+("
            + "|".join(DIALOG_TAGS)
            + r")\b",
            re.IGNORECASE,
        )

        def replace3(match):
            content = match.group(1)
            tag = match.group(2)

            # Regla RAE: cuando hay verbo de lengua, quitar punto final del diálogo
            if content.endswith("."):
                # Quitar punto final cuando hay verbo de lengua
                content_clean = content.rstrip(".").strip()
                result = f"{self.EM_DASH}{content_clean} {self.EM_DASH}{tag.lower()}"
            elif content.endswith(("?", "!")):
                # Mantener signos de interrogación/exclamación
                result = f"{self.EM_DASH}{content} {self.EM_DASH}{tag.lower()}"
            elif content.endswith(","):
                content_clean = content.rstrip(",").strip()
                result = f"{self.EM_DASH}{content_clean} {self.EM_DASH}{tag.lower()}"
            else:
                result = f"{self.EM_DASH}{content} {self.EM_DASH}{tag.lower()}"

            sentence = self._get_sentence_context(line, match)
            converted_sentence = sentence.replace(match.group(0), result, 1)
            self.logger.log_change(
                self.current_line,
                sentence,
                converted_sentence,
                "D2: Etiqueta de diálogo (comillas simples)",
                match.group(0),
                result,
                full_text=original,
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
        pattern1 = re.compile(
            r"^(\s*)"
            + self.QUOTES_PATTERN
            + r'([^"\u201C\u201D]+)'
            + self.QUOTES_PATTERN
        )

        def replace1(match):
            indent = match.group(1)
            content = match.group(2)
            result = f"{indent}{self.EM_DASH}{content}"

            sentence = self._get_sentence_context(line, match)
            converted_sentence = sentence.replace(match.group(0), result, 1)
            self.logger.log_change(
                self.current_line,
                sentence,
                converted_sentence,
                "D1: Sustitución de delimitadores",
                match.group(0),
                result,
                full_text=original,
                full_converted=converted_sentence,
            )
            return result

        new_line = pattern1.sub(replace1, line)

        # Comillas simples al inicio (simples tipográficas y rectas)
        pattern2 = re.compile(
            r"^(\s*)"
            + self.SINGLE_QUOTES_PATTERN
            + r"([^'\u2018\u2019]+)"
            + self.SINGLE_QUOTES_PATTERN
        )

        def replace2(match):
            indent = match.group(1)
            content = match.group(2)
            result = f"{indent}{self.EM_DASH}{content}"

            sentence = self._get_sentence_context(line, match)
            converted_sentence = sentence.replace(match.group(0), result, 1)
            self.logger.log_change(
                self.current_line,
                sentence,
                converted_sentence,
                "D1: Sustitución de delimitadores (comillas simples)",
                match.group(0),
                result,
                full_text=original,
                full_converted=converted_sentence,
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
            r"(\s+)"
            + self.QUOTES_PATTERN
            + r'([^"\u201C\u201D]+)'
            + self.QUOTES_PATTERN
        )

        def replace_additional(match):
            space = match.group(1)
            content = match.group(2)

            # Verificar si el contenido parece ser un diálogo completo
            # (empieza con mayúscula o signos de interrogación/exclamación)
            if content.strip() and (
                content[0].isupper() or content.startswith(("¿", "¡"))
            ):
                result = f"{space}{self.EM_DASH}{content}"

                sentence = self._get_sentence_context(line, match)
                converted_sentence = sentence.replace(match.group(0), result, 1)
                self.logger.log_change(
                    self.current_line,
                    sentence,
                    converted_sentence,
                    "D1: Diálogo adicional en línea",
                    match.group(0),
                    result,
                    full_text=original,
                    full_converted=converted_sentence,
                )
                return result

            # Si no parece diálogo, no tocar
            return match.group(0)

        # Solo aplicar si la línea ya tiene rayas (indica
        # que estamos en contexto de diálogos)
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
        if re.search(r"^\s*" + self.QUOTES_PATTERN, line):
            return line

        # 2. Comillas después de etiqueta de diálogo (continuación)
        # Ejemplo: —dijo pensativa. "Más texto"
        for tag in DIALOG_TAGS:
            if re.search(
                self.EM_DASH + tag + r'\b[^"]*?[\.,]\s*' + self.QUOTES_PATTERN,
                line,
                re.IGNORECASE,
            ):
                # Es continuación de diálogo, NO cita interna
                # Ya debería haberse procesado en
                # _convert_dialog_with_tag, pero por las dudas
                return line

        # 3. Comillas después de narración con mayúscula (nuevo diálogo)
        # Ejemplo: —Texto. Narración con mayúscula. "Más diálogo"
        if re.search(r"\.\s+[A-ZÁÉÍÓÚÑ][^.]*\s*" + self.QUOTES_PATTERN, line):
            return line

        # 4. Múltiples diálogos en la misma línea separados por espacio
        # Ejemplo: "Texto1" "Texto2"
        # Contar comillas: si hay más de 2 pares,
        # probablemente son diálogos consecutivos
        quote_count = len(re.findall(self.QUOTES_PATTERN, line))
        if quote_count >= 4:  # 2 o más pares de comillas
            return line

        # Si llegamos acá, son citas internas legítimas
        # SOLO convertir comillas SIMPLES a latinas (citas dentro de diálogo)
        pattern = re.compile(
            self.SINGLE_QUOTES_PATTERN
            + r"([^'\u2018\u2019]+)"
            + self.SINGLE_QUOTES_PATTERN
        )

        def replace(match):
            content = match.group(1)
            result = f"«{content}»"

            sentence = self._get_sentence_context(line, match)
            converted_sentence = sentence.replace(match.group(0), result, 1)
            self.logger.log_change(
                self.current_line,
                sentence,
                converted_sentence,
                "D5: Cita interna con comillas latinas",
                match.group(0),
                result,
                full_text=original,
                full_converted=converted_sentence,
            )
            return result

        new_line = pattern.sub(replace, line)

        return new_line
