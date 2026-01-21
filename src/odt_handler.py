"""
Módulo para trabajar con archivos ODT (OpenDocument Text).
"""

import difflib
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Optional


class ODTProcessor:
    """Procesa archivos ODT preservando estilos y estructura."""

    def __init__(self, filepath: Path):
        """Inicializa el procesador de ODT."""
        self.filepath = filepath
        # Registrar namespaces para preservarlos en el XML
        ET.register_namespace(
            "office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
        )
        ET.register_namespace("text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0")
        ET.register_namespace(
            "style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
        )
        ET.register_namespace(
            "fo", "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
        )
        ET.register_namespace(
            "svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
        )
        ET.register_namespace("meta", "urn:oasis:names:tc:opendocument:xmlns:meta:1.0")
        ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
        ET.register_namespace(
            "table", "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
        )
        ET.register_namespace(
            "draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
        )

    def process_and_save(self, output_path: Path, text_converter_func):
        """
        Procesa el ODT aplicando conversiones y guarda preservando estructura completa.

        Args:
            output_path: Ruta de salida
            text_converter_func: Función que convierte el texto. Recibe str y
                retorna tuple[str, logger]
        """
        try:
            with zipfile.ZipFile(self.filepath, "r") as input_zip:
                with zipfile.ZipFile(
                    output_path, "w", zipfile.ZIP_DEFLATED
                ) as output_zip:
                    # Copiar TODOS los archivos excepto content.xml
                    for item in input_zip.namelist():
                        if item != "content.xml":
                            data = input_zip.read(item)
                            # mimetype debe ir sin comprimir
                            if item == "mimetype":
                                output_zip.writestr(
                                    item, data, compress_type=zipfile.ZIP_STORED
                                )
                            else:
                                output_zip.writestr(item, data)

                    # Procesar content.xml preservando estructura
                    content_xml = input_zip.read("content.xml")
                    root = ET.fromstring(content_xml)

                    # Construir mapa de propiedades de estilos (italic, bold...)
                    # Esto nos permitirá normalizar estilos y evitar crear
                    # cientos de spans distintos que representan lo mismo.
                    self._build_style_properties(root)

                    # Convertir textos párrafo por párrafo
                    self._convert_paragraphs_in_tree(root, text_converter_func)

                    # Guardar content.xml modificado
                    modified_content = ET.tostring(
                        root, encoding="utf-8", xml_declaration=True
                    )
                    output_zip.writestr("content.xml", modified_content)

        except Exception as e:
            raise Exception(f"Error procesando ODT: {e}")

    def _convert_paragraphs_in_tree(self, element, converter_func):
        """Convierte textos párrafo por párrafo preservando estructura."""
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        # Solo procesar párrafos y encabezados
        if tag in ("p", "h"):
            # Verificar si tiene line-breaks internos
            if self._has_line_breaks(element):
                # Procesar preservando line-breaks Y formato inline
                self._convert_with_line_breaks(element, converter_func)
            else:
                # Párrafo simple: preservar formato inline sin line-breaks
                text = self._get_full_text(element)
                if text.strip():
                    converted, _ = converter_func(text)
                    if converted != text:
                        # Reconstruir preservando formato inline
                        self._rebuild_simple_paragraph(element, text, converted)

        # Procesar hijos recursivamente
        for child in element:
            self._convert_paragraphs_in_tree(child, converter_func)

    def _get_full_text(self, element) -> str:
        """Obtiene todo el texto de un párrafo incluyendo spans."""
        parts = []
        if element.text:
            parts.append(element.text)
        for child in element:
            if child.text:
                parts.append(child.text)
            if child.tail:
                parts.append(child.tail)
        return "".join(parts)

    def _set_paragraph_text(self, element, new_text: str):
        """Reemplaza el texto de un párrafo manteniendo la estructura simple."""
        # Guardar los atributos del elemento
        attribs = element.attrib.copy()

        # Limpiar el elemento
        element.clear()

        # Restaurar atributos
        element.attrib.update(attribs)

        # Establecer nuevo texto
        element.text = new_text

    def _rebuild_simple_paragraph(
        self, element, original_text: str, converted_text: str
    ):
        """
        Reconstruye un párrafo simple preservando formato inline.

        Args:
            element: Elemento XML del párrafo
            original_text: Texto original completo
            converted_text: Texto convertido completo
        """
        # Extraer mapa de formato del original
        format_map = self._extract_format_map(element)

        # Si no hay formato especial, usar método simple
        if not format_map or all(not v for v in format_map.values()):
            self._set_paragraph_text(element, converted_text)
            return

        # Aplicar formato usando el mapa
        ns_text = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"

        def normalize_word(word: str) -> str:
            """Normaliza palabra para matching."""
            # Quitar puntuación incluyendo TODAS las comillas (ASCII + tipográficas)
            cleaned = re.sub(
                r'[.,;:!?¿¡"\u2018\u2019\u201C\u201D\'—()\[\]{}]', "", word
            )
            return cleaned.lower().strip()

        def get_word_style(word: str) -> Optional[str]:
            """Obtiene el estilo de una palabra desde el mapa."""
            norm_word = normalize_word(word)
            if norm_word in format_map and format_map[norm_word]:
                return format_map[norm_word][0]["style"]
            return None

        # Guardar atributos
        attribs = element.attrib.copy()
        element.clear()
        element.attrib.update(attribs)

        # Dividir en palabras preservando espacios
        words = re.split(r"(\s+)", converted_text)

        # Reconstruir con formato
        for i, word in enumerate(words):
            if not word:
                continue

            style_name = get_word_style(word) if not word.isspace() else None

            if i == 0:
                # Primera palabra/espacio va en element.text
                if style_name:
                    span = ET.SubElement(element, f"{ns_text}span")
                    span.set(f"{ns_text}style-name", style_name)
                    span.text = word
                else:
                    element.text = word
            else:
                # Resto va en tails o spans
                if style_name:
                    span = ET.SubElement(element, f"{ns_text}span")
                    span.set(f"{ns_text}style-name", style_name)
                    span.text = word
                else:
                    # Agregar al tail del último elemento
                    if len(element) > 0:
                        if element[-1].tail:
                            element[-1].tail += word
                        else:
                            element[-1].tail = word
                    else:
                        if element.text:
                            element.text += word
                        else:
                            element.text = word

    def _has_line_breaks(self, element) -> bool:
        """Verifica si un párrafo tiene saltos de línea internos."""
        for child in element.iter():
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag == "line-break":
                return True
        return False

    def _convert_with_line_breaks(self, element, converter_func):
        """
        Convierte texto preservando line-breaks Y formato (spans, bold, italic).

        NUEVA ESTRATEGIA: Mapeo de formato palabra por palabra
        1. Extraer mapa de formato del original (palabra → estilo)
        2. Convertir el texto
        3. Reconstruir aplicando el formato según el mapa
        """
        # 1. Extraer mapa de formato ANTES de modificar
        format_map = self._extract_format_map(element)

        # 2. Extraer segmentos de texto entre line-breaks Y estilos por token
        segments, token_styles_seq = self._extract_text_segments_and_styles(element)

        # 3. Convertir cada segmento
        converted_segments = []
        for seg in segments:
            if seg.strip():
                converted, _ = converter_func(seg)
                converted_segments.append(converted)
            else:
                converted_segments.append(seg)

        # 4. Reconstruir preservando formato: preferir estilos por índice
        # (token_styles_seq)
        #    y usar format_map consumiendo entradas (pop) como fallback.
        # Pasar además los segmentos originales para permitir alineado token->token
        self._rebuild_with_format_map(
            element,
            converted_segments,
            format_map,
            token_styles_seq=token_styles_seq,
            original_segments=segments,
        )

    def _extract_text_segments_smart(self, element) -> list:
        """
        Extrae segmentos de texto entre line-breaks para saber qué convertir.
        No modifica la estructura, solo lee.
        """
        segments = []
        current_text = []

        def extract_recursive(elem):
            if elem.text:
                current_text.append(elem.text)

            for child in elem:
                child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

                if child_tag == "line-break":
                    # Guardar segmento actual
                    segments.append("".join(current_text))
                    current_text.clear()
                    if child.tail:
                        current_text.append(child.tail)
                else:
                    # Continuar acumulando (recursivo para hijos)
                    extract_recursive(child)
                    if child.tail:
                        current_text.append(child.tail)

        extract_recursive(element)

        # Guardar último segmento
        if current_text:
            segments.append("".join(current_text))

        return segments

    def _split_preserving_spaces(self, text: str) -> list:
        """
        Divide texto en tokens preservando espacios similares a la versión anterior.
        Retorna una lista de tokens donde las palabras y los espacios adyacentes
        se mantienen juntos cuando sea apropiado.
        """
        parts = []
        current_pos = 0

        word_pattern = re.compile(r"\S+")

        for match in word_pattern.finditer(text):
            start, end = match.span()

            # Añadir espacios previos si los hay
            if start > current_pos:
                spaces_before = text[current_pos:start]
                if parts:
                    parts[-1] = parts[-1] + spaces_before
                else:
                    parts.append(spaces_before)

            # Añadir la palabra
            word = text[start:end]
            parts.append(word)
            current_pos = end

        # Añadir espacios finales si los hay
        if current_pos < len(text):
            if parts:
                parts[-1] = parts[-1] + text[current_pos:]
            else:
                parts.append(text[current_pos:])

        return parts

    def _align_token_styles(
        self,
        orig_tokens: list[str],
        orig_styles: list[Optional[str]],
        conv_tokens: list[str],
        unset_value=None,
    ) -> list:
        """Alinea estilos de tokens originales a tokens convertidos.

        Usa SequenceMatcher para encontrar bloques iguales y asigna estilos
        de tokens originales a tokens convertidos. Para bloques reemplazados
        mapea por proporción de índices.
        """
        # Normalizar tokens (strip) para comparar
        orig_norm = [t.strip() for t in orig_tokens]
        conv_norm = [t.strip() for t in conv_tokens]

        matcher = difflib.SequenceMatcher(None, orig_norm, conv_norm)
        result_styles = [unset_value for _ in range(len(conv_tokens))]

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                # Copiar estilos directamente
                for o_idx, c_idx in zip(range(i1, i2), range(j1, j2)):
                    if o_idx < len(orig_styles):
                        result_styles[c_idx] = orig_styles[o_idx]
            else:
                len_orig = i2 - i1
                len_conv = j2 - j1
                if len_conv <= 0:
                    continue
                if len_orig <= 0:
                    # No hay tokens originales correspondentes
                    for c_idx in range(j1, j2):
                        result_styles[c_idx] = None
                    continue
                # Mapear por proporción
                for offset in range(len_conv):
                    # calcular índice proporcional
                    mapped = i1 + int(offset * len_orig / len_conv)
                    if mapped >= i2:
                        mapped = i2 - 1
                    if mapped < len(orig_styles):
                        result_styles[j1 + offset] = orig_styles[mapped]

        return result_styles

    def _extract_text_segments_and_styles(
        self, element
    ) -> tuple[list[str], list[list[Optional[str]]]]:
        """
        Extrae segmentos de texto entre line-breaks y, para cada segmento,
        devuelve la lista de tokens (manteniendo espacios) y una lista de estilos
        por token (None si no hay estilo).

        Returns:
            (segments_texts, segments_token_styles) donde ambos son listas paralelas.
        """
        segments = []
        segments_token_styles = []

        current_chars = []
        current_char_styles = []

        ns_text = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"

        def extract_recursive(elem, current_style=None):
            # Actualizar estilo si el elemento es span
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag == "span":
                style_attr = f"{ns_text}style-name"
                current_style = elem.attrib.get(style_attr, current_style)

            # Texto directo
            if elem.text:
                txt = elem.text
                current_chars.append(txt)
                # Marcar estilo por carácter
                current_char_styles.extend([current_style] * len(txt))

            for child in elem:
                child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

                if child_tag == "line-break":
                    # Guardar segmento actual
                    segments.append("".join(current_chars))
                    segments_token_styles.append([])  # placeholder, rellenaremos luego
                    # Guardar char style snapshot
                    # Convertir current_char_styles a lista y añadir a auxiliar
                    # (almacenaremos el arreglo en paralelo en otra lista)
                    # Para simplificar, almacenamos temporalmente en
                    # segments_token_styles[-1]
                    segments_token_styles[-1] = current_char_styles.copy()

                    # Limpiar acumuladores para el siguiente segmento
                    current_chars.clear()
                    current_char_styles.clear()

                    if child.tail:
                        txt_tail = child.tail
                        current_chars.append(txt_tail)
                        current_char_styles.extend([current_style] * len(txt_tail))
                else:
                    extract_recursive(child, current_style)
                    if child.tail:
                        txt_tail = child.tail
                        current_chars.append(txt_tail)
                        current_char_styles.extend([current_style] * len(txt_tail))

        extract_recursive(element)

        # Guardar último segmento
        if current_chars:
            segments.append("".join(current_chars))
            segments_token_styles.append(current_char_styles.copy())

        # Ahora convertir char-styles en estilos por token para cada segmento
        segments_token_styles_by_token = []
        for seg_text, char_styles in zip(segments, segments_token_styles):
            tokens = self._split_preserving_spaces(seg_text)
            token_styles = []
            pos = 0
            for token in tokens:
                length = len(token)
                # Extraer estilos de los caracteres cubiertos por este token
                slice_styles = char_styles[pos : pos + length]
                # Elegir primer estilo no-None si existe, sino None
                token_style = None
                for s in slice_styles:
                    if s is not None:
                        token_style = s
                        break
                token_styles.append(token_style)
                pos += length

            segments_token_styles_by_token.append(token_styles)

        return segments, segments_token_styles_by_token

    def _build_style_properties(self, root):
        """
        Construye un mapa de propiedades para cada style-name definido en
        automatic-styles del documento. Guarda en `self._style_props` un dict
        style-name -> { 'italic': bool, 'bold': bool }

        También selecciona un style-name canónico para italic si encuentra uno,
        y lo guarda en `self._canonical_style_for`.
        """
        self._style_props = {}
        self._canonical_style_for = {"italic": None, "bold": None}

        # namespaces declared above; no need to reassign here

        # Buscar estilos dentro de automatic-styles
        for elem in root.iter():
            # tag completo como '{ns}style'
            if isinstance(elem.tag, str) and elem.tag.endswith("}style"):
                # Obtener el nombre del estilo
                style_name = None
                for k, v in elem.attrib.items():
                    if k.endswith("}name") or k == "name" or k.endswith(":name"):
                        style_name = v
                        break

                if not style_name:
                    continue

                # Buscar child text:properties dentro de este style
                italic = False
                bold = False
                for child in elem:
                    # child tag localname
                    local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if local == "text-properties":
                        # Revisar atributos fo:font-style y fo:font-weight
                        for ak, av in child.attrib.items():
                            if ak.endswith("}font-style") and av == "italic":
                                italic = True
                            if ak.endswith("}font-weight") and av in ("bold", "700"):
                                bold = True

                self._style_props[style_name] = {"italic": italic, "bold": bold}

                if italic and not self._canonical_style_for["italic"]:
                    self._canonical_style_for["italic"] = style_name
                if bold and not self._canonical_style_for["bold"]:
                    self._canonical_style_for["bold"] = style_name

        # If no canonical italic found, leave None; downstream we skip creating
        # spans for non-meaningful styles.

    def _extract_format_map(self, element) -> dict:
        """
        Extrae un mapa de palabra normalizada → estilo de span.

        Returns:
            Dict con estructura:
            {
                'palabra_normalizada': [
                    {'style': 'T1', 'original': 'Palabra'},
                    ...
                ]
            }
        """
        format_map = {}

        def normalize_word(word: str) -> str:
            """Normaliza palabra para matching (lowercase, sin puntuación)."""
            # Quitar puntuación incluyendo TODAS las comillas (ASCII + tipográficas)
            # U+0022: " | U+0027: ' | U+2018: ' | U+2019: ' | U+201C: " | U+201D: "
            cleaned = re.sub(
                r'[.,;:!?¿¡"\u2018\u2019\u201C\u201D\'—()\[\]{}]', "", word
            )
            return cleaned.lower().strip()

        def extract_words_with_format(elem, current_style=None):
            """Extrae palabras con su estilo asociado."""
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            # Si es un span, capturar el estilo
            if tag == "span":
                ns_text = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
                style_attr = f"{ns_text}style-name"
                current_style = elem.attrib.get(style_attr, None)

            # Procesar texto del elemento
            if elem.text and current_style:
                words = elem.text.split()
                for word in words:
                    norm_word = normalize_word(word)
                    if norm_word:  # Solo si queda algo después de normalizar
                        if norm_word not in format_map:
                            format_map[norm_word] = []
                        format_map[norm_word].append(
                            {"style": current_style, "original": word}
                        )

            # Procesar hijos recursivamente
            for child in elem:
                extract_words_with_format(child, current_style)

                # Procesar tail (texto después del hijo)
                if child.tail and current_style:
                    words = child.tail.split()
                    for word in words:
                        norm_word = normalize_word(word)
                        if norm_word:
                            if norm_word not in format_map:
                                format_map[norm_word] = []
                            format_map[norm_word].append(
                                {"style": current_style, "original": word}
                            )

        extract_words_with_format(element)
        return format_map

    def _rebuild_with_format_map(
        self,
        element,
        segments: list,
        format_map: dict,
        token_styles_seq: Optional[list] = None,
        original_segments: Optional[list] = None,
    ):
        """
        Reconstruye el párrafo con line-breaks Y formato aplicado según mapa.

        Args:
            element: Elemento XML del párrafo
            segments: Lista de segmentos de texto convertido
            format_map: Mapa de palabra normalizada → estilo
            token_styles_seq: (opcional) lista paralela a segments con listas de
                              estilos por token (None donde no había estilo).
        """

        def normalize_word(word: str) -> str:
            """Normaliza palabra para matching."""
            # Quitar puntuación incluyendo TODAS las comillas (ASCII + tipográficas)
            cleaned = re.sub(
                r'[.,;:!?¿¡"\u2018\u2019\u201C\u201D\'—()\[\]{}]', "", word
            )
            return cleaned.lower().strip()

        def get_word_style_from_map_consume(word: str) -> Optional[str]:
            """Obtiene el estilo de una palabra desde el mapa y lo consume (pop).

            Esto ayuda a aplicar estilos repetidos en orden de aparición en el
            documento original, evitando que siempre se use la primera entrada.
            """
            norm_word = normalize_word(word)
            if norm_word in format_map and format_map[norm_word]:
                entry = format_map[norm_word].pop(0)
                return entry.get("style")
            return None

        # Guardar atributos del párrafo
        attribs = element.attrib.copy()

        # Limpiar elemento
        # Antes de limpiar el elemento, hacemos una copia NO consumible del
        # format_map para que podamos tomar decisiones basadas en el mapa
        # original (sin alterar) más abajo en heurísticas de corrección.
        original_format_map = {
            k: [entry.copy() for entry in v] for k, v in format_map.items()
        }

        element.clear()
        element.attrib.update(attribs)

        # Namespaces
        ns_text = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
        
        # Sentinel for unknown style
        UNSET = object()

        # Procesar cada segmento
        for seg_idx, segment_text in enumerate(segments):
            if seg_idx > 0:
                # Añadir line-break entre segmentos
                # (se añade automáticamente al elemento)
                ET.SubElement(element, f"{ns_text}line-break")

            # Dividir el segmento en tokens (palabras y espacios)
            words = self._split_preserving_spaces(segment_text)

            # Separar puntuación inicial (comillas de apertura, rayas) de la
            # palabra para evitar que un carácter de puntuación que llevaba
            # el estilo en el documento original se propague al resto de la
            # palabra cuando la tokenización cambia (p.ej. " → —).
            expanded_words = []
            punct_re = re.compile(
                r'^([\"\u201C\u201E\u2018\u201B\u00AB\u00BB\u2018\u2019\u201D\'"«»—-]+)(.*)$'
            )
            for w in words:
                m = punct_re.match(w)
                if m and m.group(2):
                    # Mantener los espacios/colas en la segunda parte
                    expanded_words.append(m.group(1))
                    expanded_words.append(m.group(2))
                else:
                    expanded_words.append(w)
            words = expanded_words

            # Determinar estilo por token: preferir estilos por token y, si la
            # tokenización cambió entre original y convertido, usar un
            # alineador para mapear estilos desde tokens originales a tokens
            # convertidos. Si aún así no hay estilo, caer al format_map.
            ts_for_segment = None
            if token_styles_seq and seg_idx < len(token_styles_seq):
                ts_for_segment = token_styles_seq[seg_idx]

            # Obtener estilos iniciales para los tokens convertidos
            if (
                ts_for_segment is not None
                and original_segments
                and seg_idx < len(original_segments)
            ):
                # Alinear tokens: tomar tokens del segmento original
                orig_seg_text = original_segments[seg_idx]
                orig_tokens = self._split_preserving_spaces(orig_seg_text)
                converted_tokens = words
                styles_for_tokens = self._align_token_styles(
                    orig_tokens, ts_for_segment, converted_tokens, unset_value=UNSET
                )
            elif ts_for_segment is not None:
                # Sin segmentos originales, intentar usar estilos por índice
                styles_for_tokens = [
                    ts_for_segment[i] if i < len(ts_for_segment) else UNSET
                    for i in range(len(words))
                ]
            else:
                styles_for_tokens = [UNSET for _ in range(len(words))]

            # Para tokens, aplicar FORCED NORMALIZATION para marcadores de diálogo
            # y luego, si no hay estilo asignado,
            # intentar consumir del mapa por palabra.
            for i, token in enumerate(words):
                token_stripped = token.strip()

                # Si no se asignó estilo aún, intentar consumir del mapa por palabra
                # Intentamos esto antes de la "forced normalization" que limpia
                # estilos en tokens seguidores de una raya. De esta forma, si
                # la palabra realmente tenía estilo en el original (mapa), lo
                # conservamos, evitando quitarlo por error (caso "Uno studio...").
                if styles_for_tokens[i] is UNSET:
                    if token_stripped:
                        styles_for_tokens[i] = get_word_style_from_map_consume(
                            token_stripped
                        )
                    else:
                        styles_for_tokens[i] = None

                # FORCED NORMALIZATION: if the previous token is a dash/hyphen
                # (we split leading punctuation earlier), then this token is
                # likely the speaker label (e.g. "Me") and we should not
                # apply the previous span's formatting to it either. Only clear
                # the style if we still don't have one (map or alignment).
                prev_stripped = words[i - 1].strip() if i > 0 else None
                if prev_stripped and (
                    prev_stripped.startswith("—") or prev_stripped.startswith("-")
                ):
                    if styles_for_tokens[i] is UNSET or styles_for_tokens[i] is None:
                        # leave as None (explicit) and continue
                        # Ensure it's None and not UNSET for final processing
                        styles_for_tokens[i] = None
                        continue

                # FORCED NORMALIZATION: si el token empieza con raya (—) o guion (-),
                # no aplicar formato inline bajo ninguna circunstancia.
                if token_stripped and (
                    token_stripped.startswith("—") or token_stripped.startswith("-")
                ):
                    if styles_for_tokens[i] is UNSET or styles_for_tokens[i] is None:
                         styles_for_tokens[i] = None
                         continue

            # Agrupar tokens consecutivos con el mismo estilo
            groups = []
            current_group_style = None
            current_group_tokens = []

            # Heurística adicional: si un token quedó sin estilo y está
            # inmediatamente después de una raya/guion, pero el token
            # siguiente sí tiene estilo, heredamos ese estilo. Esto ayuda
            # a preservar casos como "—Uno studio sui draghi" donde el
            # original tenía la frase completa en un mismo span.
            for idx in range(len(words)):
                prev_str = words[idx - 1].strip() if idx > 0 else None
                if (
                    styles_for_tokens[idx] is None
                    and prev_str
                    and (prev_str.startswith("—") or prev_str.startswith("-"))
                ):
                    # Buscar adelante el primer token con estilo no-None en una
                    # ventana pequeña. Si lo encontramos, heredamos ese estilo.
                    found = None
                    for j in range(idx + 1, min(len(words), idx + 7)):
                        if styles_for_tokens[j] is not None:
                            found = styles_for_tokens[j]
                            break
                    if found:
                        styles_for_tokens[idx] = found

            # Heurística de corrección: en algunos casos el alineador puede
            # asignar un estilo distinto al token inmediatamente después de
            # una puntuación transformada (p.ej. comilla → raya). Si vemos
            # que el token siguiente tiene estilo Y y el token actual tiene
            # estilo X distinto, pero en el mapa original la palabra
            # normalizada del token actual aparece asociada a Y, corregimos
            # el estilo del token actual para coincidir con el siguiente.
            def normalize_word_lookup(w: str) -> str:
                cleaned = re.sub(
                    r'[.,;:!?¿¡"\u2018\u2019\u201C\u201D\'"—()\[\]{}]',
                    "",
                    w,
                )
                return cleaned.lower().strip()

            for idx in range(len(words) - 1):
                prev_str = words[idx - 1].strip() if idx > 0 else None
                if prev_str and (prev_str.startswith("—") or prev_str.startswith("-")):
                    cur_style = styles_for_tokens[idx]
                    next_style = styles_for_tokens[idx + 1]
                    if cur_style != next_style and next_style is not None:
                        # comprobar en el mapa original si la entrada normalizada
                        # del token actual tenía el estilo next_style
                        norm = normalize_word_lookup(words[idx])
                        if norm and norm in original_format_map:
                            styles_list = [
                                e["style"] for e in original_format_map[norm]
                            ]
                            if next_style in styles_list:
                                styles_for_tokens[idx] = next_style

            for token, style in zip(words, styles_for_tokens):
                if style == current_group_style:
                    current_group_tokens.append(token)
                else:
                    if current_group_tokens:
                        groups.append(
                            (current_group_style, "".join(current_group_tokens))
                        )
                    current_group_style = style
                    current_group_tokens = [token]

            if current_group_tokens:
                groups.append((current_group_style, "".join(current_group_tokens)))

            # Crear spans para cada grupo
            for group_idx, (style, text_content) in enumerate(groups):
                if seg_idx == 0 and group_idx == 0:
                    # Primer texto del párrafo
                    if style:
                        span = ET.SubElement(element, f"{ns_text}span")
                        span.attrib[f"{ns_text}style-name"] = style
                        span.text = text_content
                    else:
                        element.text = text_content
                else:
                    # Resto del contenido
                    if style:
                        span = ET.SubElement(element, f"{ns_text}span")
                        span.attrib[f"{ns_text}style-name"] = style
                        span.text = text_content
                    else:
                        # Texto sin estilo - añadir al tail del último elemento
                        if len(element) > 0:
                            last_elem = element[-1]
                            if last_elem.tail:
                                last_elem.tail += text_content
                            else:
                                last_elem.tail = text_content
                        else:
                            if element.text:
                                element.text += text_content
                            else:
                                element.text = text_content

    def _apply_text_changes_inplace(self, element, originals: list, converted: list):
        """
        Aplica cambios de texto preservando estructura.

        NOTA: Por ahora usa el método de reconstrucción que pierde formato inline
        en párrafos con line-breaks. Es una limitación conocida que se mejorará
        en futuras versiones.
        """
        # Usar el método que funciona (aunque pierde formato inline)
        self._rebuild_with_line_breaks(element, converted)

    def _extract_text_segments(self, element) -> list:
        """Extrae segmentos de texto separados por line-breaks."""
        segments = []
        current_segment = []

        # Función recursiva para extraer
        def extract_from_element(elem):
            if elem.text:
                current_segment.append(elem.text)

            for child in elem:
                child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

                if child_tag == "line-break":
                    # Guardar segmento actual y empezar uno nuevo
                    segments.append("".join(current_segment))
                    current_segment.clear()
                    if child.tail:
                        current_segment.append(child.tail)
                else:
                    # Seguir acumulando texto
                    extract_from_element(child)
                    if child.tail:
                        current_segment.append(child.tail)

        extract_from_element(element)

        # Guardar último segmento
        if current_segment:
            segments.append("".join(current_segment))

        return segments

    def _rebuild_with_line_breaks(self, element, segments: list):
        """Reconstruye el párrafo con line-breaks entre segmentos."""
        # Guardar atributos
        attribs = element.attrib.copy()

        # Limpiar elemento
        element.clear()
        element.attrib.update(attribs)

        # Namespace para line-break
        ns_text = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"

        # Reconstruir con line-breaks
        if segments:
            element.text = segments[0]

            for i in range(1, len(segments)):
                # Añadir line-break
                lb = ET.SubElement(element, f"{ns_text}line-break")
                lb.tail = segments[i]


class ODTReader:
    """Lee y extrae texto de archivos ODT."""

    # Namespace para ODT
    NAMESPACES = {
        "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
        "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
        "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    }

    def __init__(self, filepath: Path):
        """
        Inicializa el lector de ODT.

        Args:
            filepath: Ruta al archivo .odt
        """
        self.filepath = filepath

    def extract_text(self) -> str:
        """
        Extrae el texto del archivo ODT.

        Returns:
            Texto completo del documento

        Raises:
            ValueError: Si el archivo no es un ODT válido
        """
        try:
            with zipfile.ZipFile(self.filepath, "r") as odt_zip:
                # El contenido está en content.xml
                if "content.xml" not in odt_zip.namelist():
                    raise ValueError(
                        f"{self.filepath} no parece ser un archivo ODT válido"
                    )

                # Leer el XML
                content_xml = odt_zip.read("content.xml")

                # Parsear XML
                root = ET.fromstring(content_xml)

                # Extraer texto
                text_parts = []
                self._extract_text_recursive(root, text_parts)

                return "\n".join(text_parts)

        except zipfile.BadZipFile:
            raise ValueError(f"{self.filepath} no es un archivo ZIP válido")

    def _extract_text_recursive(self, element, text_parts: list):
        """
        Extrae texto recursivamente del XML.

        Args:
            element: Elemento XML
            text_parts: Lista para acumular partes de texto
        """
        # Obtener el tag sin namespace
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        # Si es un párrafo, añadir su texto
        if tag == "p":
            para_text = self._get_paragraph_text(element)
            if para_text.strip():
                text_parts.append(para_text)

        # Si es un encabezado
        elif tag == "h":
            heading_text = self._get_paragraph_text(element)
            if heading_text.strip():
                text_parts.append(heading_text)

        # Procesar hijos recursivamente
        for child in element:
            self._extract_text_recursive(child, text_parts)

    def _get_paragraph_text(self, element) -> str:
        """
        Obtiene el texto de un párrafo, incluyendo spans y otros elementos inline.
        PRESERVA line-breaks internos como saltos de línea (recursivamente).

        Args:
            element: Elemento de párrafo

        Returns:
            Texto del párrafo con line-breaks convertidos a \n
        """

        def extract_text_recursive(elem):
            """Extrae texto recursivamente preservando line-breaks."""
            parts = []

            # Texto directo del elemento
            if elem.text:
                parts.append(elem.text)

            # Procesar hijos
            for child in elem:
                child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag

                # Si es line-break, agregar salto de línea
                if child_tag == "line-break":
                    parts.append("\n")
                else:
                    # Recursivo para procesar spans que pueden contener line-breaks
                    parts.extend(extract_text_recursive(child))

                # Texto después del elemento (tail)
                if child.tail:
                    parts.append(child.tail)

            return parts

        return "".join(extract_text_recursive(element))


class ODTWriter:
    """Escribe texto a un archivo ODT."""

    def __init__(self, filepath: Path):
        """
        Inicializa el escritor de ODT.

        Args:
            filepath: Ruta donde guardar el archivo .odt
        """
        self.filepath = filepath

    def write_text(self, text: str):
        """
        Escribe texto a un archivo ODT.

        Args:
            text: Texto a escribir
        """
        # Template mínimo de ODT
        mimetype = "application/vnd.oasis.opendocument.text"

        # manifest.xml
        manifest = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
    <manifest:file-entry
        manifest:media-type="application/vnd.oasis.opendocument.text"
        manifest:full-path="/"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="meta.xml"/>
</manifest:manifest>"""

        # meta.xml
        meta = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
  <office:meta>
    <meta:generator>dialogos_a_español 1.0.1</meta:generator>
  </office:meta>
</office:document-meta>"""

        # styles.xml (mínimo)
        styles = """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
  <office:styles/>
  <office:automatic-styles/>
  <office:master-styles/>
</office:document-styles>"""

        # content.xml con el texto
        paragraphs = []
        for line in text.split("\n"):
            escaped_line = self._escape_xml(line)
            paragraphs.append(
                f'    <text:p text:style-name="Standard">{escaped_line}</text:p>'
            )

        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                         xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                         xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0">
  <office:automatic-styles>
    <style:style style:name="Standard" style:family="paragraph"/>
  </office:automatic-styles>
  <office:body>
    <office:text>
{chr(10).join(paragraphs)}
    </office:text>
  </office:body>
</office:document-content>"""

        # Crear archivo ZIP (ODT)
        with zipfile.ZipFile(self.filepath, "w", zipfile.ZIP_DEFLATED) as odt_zip:
            # mimetype debe ser el primer archivo, sin comprimir
            odt_zip.writestr("mimetype", mimetype, compress_type=zipfile.ZIP_STORED)

            # Crear directorio META-INF
            odt_zip.writestr("META-INF/manifest.xml", manifest)

            # Añadir archivos XML
            odt_zip.writestr("meta.xml", meta)
            odt_zip.writestr("styles.xml", styles)
            odt_zip.writestr("content.xml", content)

    def _escape_xml(self, text: str) -> str:
        """
        Escapa caracteres especiales para XML.

        Args:
            text: Texto a escapar

        Returns:
            Texto escapado
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )


def is_odt_file(filepath: Path) -> bool:
    """
    Verifica si un archivo es ODT.

    Args:
        filepath: Ruta del archivo

    Returns:
        True si es ODT
    """
    if not filepath.exists():
        return False

    # Verificar extensión
    if filepath.suffix.lower() != ".odt":
        return False

    # Verificar que sea un ZIP válido con content.xml
    try:
        with zipfile.ZipFile(filepath, "r") as z:
            return "content.xml" in z.namelist()
    except Exception:
        return False
