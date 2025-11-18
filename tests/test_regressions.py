import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from src.converter import DialogConverter
from src.odt_handler import ODTProcessor


class TestRegressions(unittest.TestCase):
    """Tests específicos para regressiones reportadas."""

    def test_dialogue_marker_full_block_logged(self):
        """
        Verifica que el logger registre el bloque completo
        (original y convertido).
        """
        converter = DialogConverter()

        input_text = '"Buenos días, Adi." Dijo llena de energía.'
        expected = "—Buenos días, Adi —dijo llena de energía."

        result, logger = converter.convert(input_text)

        # Resultado de conversión
        self.assertEqual(result, expected)

        # Logger debe tener al menos un cambio y el cambio debe contener
        # el bloque original y el bloque convertido completos
        self.assertGreaterEqual(len(logger.changes), 1)
        found = False
        for rec in logger.changes:
            original = rec.get("original")
            converted = rec.get("converted")
            if original and "Buenos días" in original:
                self.assertIn("Buenos días, Adi.", original)
                self.assertTrue(converted and "—Buenos días" in converted)
                found = True
                break

        self.assertTrue(found, "No se encontró el cambio esperado en el logger")

    def test_leading_token_style_preserved_in_rebuild(self):
        """
        Verifica que al reconstruir con format_map la primera palabra
        conserve su estilo.

        Simulamos un párrafo donde la totalidad del texto original está
        dentro de un span (p.ej. itálica). Luego aplicamos una conversión
        que añade una raya inicial y reconstruimos con
        `_rebuild_with_format_map`. El primer token legible (p.ej. 'Uno')
        debe aparecer en un span con el mismo style-name que el original.
        """
        # Construir un párrafo XML con un span que contiene todo el texto
        ns_text = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
        p = ET.Element(f"{ns_text}p")
        span = ET.SubElement(p, f"{ns_text}span")
        span.set(f"{ns_text}style-name", "T_Italic")
        span.text = "Uno studio sui draghi"

        proc = ODTProcessor(Path("."))

        # Extraer mapa de formato desde el elemento
        fmt_map = proc._extract_format_map(p)

        # Simular segmento convertido que añade la raya al inicio
        segments = ["—Uno studio sui draghi"]

        # Llamar a la reconstrucción
        proc._rebuild_with_format_map(
            p,
            segments,
            fmt_map,
            token_styles_seq=None,
            original_segments=["Uno studio sui draghi"],
        )

        # Buscar spans en el resultado y verificar que exista un span cuyo
        # style-name sea T_Italic y cuyo texto contenga 'Uno'
        spans = p.findall(f".//{ns_text}span")
        self.assertTrue(
            len(spans) >= 1, "No se encontraron spans en el párrafo reconstruido"
        )

        matched = False
        for s in spans:
            if s.attrib.get(f"{ns_text}style-name") == "T_Italic" and (
                s.text and "Uno" in s.text
            ):
                matched = True
                break

        self.assertTrue(matched, "La primera palabra no preservó el estilo esperado")


if __name__ == "__main__":
    unittest.main()
