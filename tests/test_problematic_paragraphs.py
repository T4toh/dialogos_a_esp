import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from src.odt_handler import ODTProcessor


class TestProblematicParagraphs(unittest.TestCase):
    """Detecta párrafos con muchos spans en un ODT convertido y verifica métodos."""

    def setUp(self):
        self.odt_path = Path(
            "examples/1 - La Caballera Esmeralda/1 - Primer Trabajo_convertido.odt"
        )
        if not self.odt_path.exists():
            self.skipTest(f"Archivo de ejemplo no encontrado: {self.odt_path}")

        # namespace usado por el ODT para text
        self.ns_text = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"

        # cargar content.xml
        with zipfile.ZipFile(self.odt_path, "r") as z:
            if "content.xml" not in z.namelist():
                self.skipTest("content.xml no encontrado en el ODT de ejemplo")
            content = z.read("content.xml")
        self.root = ET.fromstring(content)

    def test_extract_and_rebuild_on_problem_paragraphs(self):
        # Buscar párrafos con muchas spans (fragmentación)
        paras = []
        for elem in self.root.iter():
            tag = elem.tag.split("}")[-1] if isinstance(elem.tag, str) else elem.tag
            if tag == "p":
                # contar spans dentro del párrafo
                spans = elem.findall(f".//{self.ns_text}span")
                if len(spans) > 8:
                    paras.append(elem)

        if not paras:
            self.skipTest("No se hallaron párrafos con más de 8 spans en el ODT de ejemplo")

        # Tomar hasta 5 párrafos problemáticos
        paras = paras[:5]

        proc = ODTProcessor(self.odt_path)

        # Construir propiedades de estilo desde root (mimic process_and_save)
        proc._build_style_properties(self.root)

        for p in paras:
            # trabajar sobre copia para no mutar el árbol original
            p_copy = ET.fromstring(ET.tostring(p))

            # Extracción de segmentos y estilos por token
            segments, token_styles_seq = proc._extract_text_segments_and_styles(p_copy)

            # Invariante básica: segmentos y listas de estilos paralelas
            self.assertEqual(len(segments), len(token_styles_seq))

            # Para cada segmento, tokens y estilos deben alinear
            for seg, styles in zip(segments, token_styles_seq):
                tokens = proc._split_preserving_spaces(seg)
                self.assertEqual(len(tokens), len(styles))

            # Contar spans antes
            before_spans = len(p_copy.findall(f".//{self.ns_text}span"))

            # Extraer mapa de formato y reconstruir (operación no transformadora aquí)
            fmt_map = proc._extract_format_map(p_copy)

            # Reconstruir: usamos los mismos segmentos (sin cambios de texto) para
            # verificar que la reconstrucción no aumente la fragmentación.
            proc._rebuild_with_format_map(p_copy, segments, fmt_map, token_styles_seq=token_styles_seq)

            after_spans = len(p_copy.findall(f".//{self.ns_text}span"))

            # Comprobación: la reconstrucción no debe incrementar el número de spans
            self.assertLessEqual(
                after_spans,
                before_spans,
                msg=f"La reconstrucción aumentó spans: antes={before_spans} despues={after_spans}",
            )


if __name__ == "__main__":
    unittest.main()
