"""
Tests para el conversor de diálogos.
"""

import unittest
from typing import Tuple, cast

from src.converter import DialogConverter


class TestDialogConverter(unittest.TestCase):
    """Tests para DialogConverter."""

    def setUp(self):
        """Configuración antes de cada test."""
        self.converter = DialogConverter()

    def test_simple_dialog_double_quotes(self):
        """Test: Conversión de diálogo simple con comillas dobles."""
        input_text = '"Hola, Juan"'
        expected = "—Hola, Juan"
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_simple_dialog_single_quotes(self):
        """Test: Conversión de diálogo simple con comillas simples."""
        input_text = "'Hola, Juan'"
        expected = "—Hola, Juan"
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_dialog_with_tag(self):
        """Test: Diálogo con etiqueta narrativa."""
        input_text = '"Hola" dijo Juan.'
        expected = "—Hola —dijo Juan."
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_dialog_with_question(self):
        """Test: Diálogo con pregunta."""
        input_text = '"¿Cómo estás?" preguntó Ana.'
        expected = "—¿Cómo estás? —preguntó Ana."
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_dialog_with_exclamation(self):
        """Test: Diálogo con exclamación."""
        input_text = '"¡Qué sorpresa!" exclamó María.'
        expected = "—¡Qué sorpresa! —exclamó María."
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_dialog_with_comma(self):
        """Test: Diálogo con coma antes de etiqueta."""
        input_text = '"No puedo creerlo," dijo Juan.'
        expected = "—No puedo creerlo —dijo Juan."
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_dialog_followed_by_narration(self):
        """Test: Diálogo seguido de narración (RAE 2.3.d)."""
        input_text = '"Está bien." Cerró la puerta.'
        expected = "—Está bien. —Cerró la puerta."
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_nested_quotes(self):
        """Test: Citas dentro de diálogos."""
        input_text = "—Ella me dijo 'te esperaré'"
        expected = "—Ella me dijo «te esperaré»"
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_multiline_dialogs(self):
        """Test: Múltiples líneas con diálogos."""
        input_text = """"Hola" dijo Juan.
"Adiós" respondió María."""
        expected = """—Hola —dijo Juan.
—Adiós —respondió María."""
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_mixed_quotes(self):
        """Test: Mezcla de comillas dobles y simples."""
        input_text = """"Hola" dijo Juan.
'Adiós' respondió María."""
        expected = """—Hola —dijo Juan.
—Adiós —respondió María."""
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_no_changes_without_quotes(self):
        """Test: Texto sin comillas no se modifica."""
        input_text = "Juan caminaba por el parque."
        expected = "Juan caminaba por el parque."
        result, logger = self.converter.convert(input_text)
        self.assertEqual(result, expected)
        self.assertEqual(len(logger.changes), 0)

    def test_logger_records_changes(self):
        """Test: El logger registra los cambios."""
        input_text = '"Hola" dijo Juan.'
        _, logger = self.converter.convert(input_text)
        self.assertGreater(len(logger.changes), 0)

    def test_typographic_double_quotes(self):
        """Test: Comillas tipográficas dobles ("")."""
        input_text = "\u201cHola\u201d dijo Juan."  # "Hola" dijo Juan.
        expected = "—Hola —dijo Juan."
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_typographic_single_quotes(self):
        """Test: Comillas tipográficas simples ('')."""
        input_text = "\u2018Hola\u2019 dijo María."  # 'Hola' dijo María.
        expected = "—Hola —dijo María."
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_mixed_typographic_quotes(self):
        """Test: Mezcla de comillas rectas y tipográficas."""
        input_text = """"Hola" dijo Juan.
\u201cAdiós\u201d respondió María."""
        expected = """—Hola —dijo Juan.
—Adiós —respondió María."""
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_dialog_continuation_same_speaker(self):
        """Test: Continuación de diálogo del mismo personaje."""
        input_text = '"Hola" dijo Juan. "¿Cómo estás?"'
        expected = "—Hola —dijo Juan. —¿Cómo estás?"
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_complex_narration_interruption(self):
        """Test: Diálogo interrumpido por narración compleja (RAE 2.3.d)."""
        input_text = (
            '"Es una demostración de capacidad, querida." El hombre agregó al '
            'instante. "¿Cómo es la educación en este lugar, director?"'
        )
        expected = (
            "—Es una demostración de capacidad, querida. "
            "—El hombre agregó al instante. "
            "—¿Cómo es la educación en este lugar, director?"
        )
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_long_dialog_continuation(self):
        """Test: Diálogo largo con continuación."""
        input_text = (
            '"Reunión familiar…" Dijo jocoso Bastien. '
            '"Miralo a Chispita, con una princesa en la cama."'
        )
        expected = (
            "—Reunión familiar… —dijo jocoso Bastien. "
            "—Miralo a Chispita, con una princesa en la cama."
        )
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)

    def test_structured_log_spans_for_examples(self):
        """Verifica que el log estructurado incluya spans consistentes."""
        text = (
            '"Nada…" dijo.\n"Me contó un pajarito, sí, me dijo"\n"Vestite..." y se fue'
        )
        _, logger = self.converter.convert(text)

        # Guardar en un path temporal.
        # En memoria sería ideal, pero usamos tmp por simplicidad.
        import json
        from pathlib import Path

        p = Path("tmp_test_structured.json")
        try:
            logger.save_structured_log(p)
            data = json.loads(p.read_text(encoding="utf-8"))

            # Deben existir 3 entradas
            self.assertEqual(len(data), 3)

            for entry in data:
                # Fragmentos y spans deben existir y coincidir
                self.assertIsNotNone(entry.get("original_fragment"))
                span_value = entry.get("original_span")
                if span_value is None:
                    self.fail("original_span is None")
                # Inform the type checker that this is an (int, int) pair.
                span = cast(Tuple[int, int], span_value)
                s, e = span
                self.assertEqual(entry["original"][s:e], entry["original_fragment"])

        finally:
            try:
                p.unlink()
            except Exception:
                pass

    def test_fuzzy_span_fallback(self):
        """Verifica que cuando el fragmento contiene más texto que el 'original'
        (por ejemplo por oraciones contiguas con puntos suspensivos) la
        detección de span hace fallback por coincidencia más larga."""
        text = '"Nada que ocultar… espero." dijo alguien.'
        _, logger = self.converter.convert(text)

        # Buscar entrada con D1 o similar
        found = False
        for rec in logger.changes:
            if "Nada que ocultar" in rec.get("original", ""):
                found = True
                # Debe existir un fragment con el que coincida
                self.assertIsNotNone(rec.get("original_fragment"))
                # Y el span debe existir (fuzzy fallback podrá rellenarlo)
                span_value = rec.get("original_span")
                if span_value is None:
                    self.fail("original_span is None")
                self.assertIsInstance(span_value, list)
                # Cast to a fixed two-int tuple for static checkers, then unpack.
                span = cast(Tuple[int, int], tuple(span_value))
                s, e = span
                self.assertGreater(e - s, 0)
                break

        self.assertTrue(
            found,
            "No se encontró la entrada que contiene 'Nada que ocultar'"
            " en logger.changes",
        )

    def test_full_text_span_for_multisentence_fragment(self):
        """
        Verifica que cuando _get_sentence_context corta la oración,
        el 'full_text' se use como fallback.
        """
        text = '"No… sí… capaz." Dijo alguien.'
        _, logger = self.converter.convert(text)

        found = False
        for rec in logger.changes:
            if "No…" in rec.get("original", ""):
                found = True
                # full_text fallback should put 'capaz' in original
                self.assertIn("capaz", rec.get("original", ""))
                self.assertIsNotNone(rec.get("original_span"))
                break

        self.assertTrue(found, "No se encontró la entrada esperada en logger.changes")

    def test_converted_span_present_for_tag(self):
        """Verifica que para etiquetas de diálogo encontremos un converted_span.

        Evita casos donde solo aparece una "borrada" en la interfaz.
        """
        text = '"No… sí… capaz." Dijo alguien.'
        _, logger = self.converter.convert(text)

        # Encontrar la entrada D2
        found = False
        for rec in logger.changes:
            if rec.get("rule", "").startswith("D2") and "No…" in rec.get(
                "original", ""
            ):
                found = True
                self.assertIsNotNone(
                    rec.get("converted_span"), "Converted span no debe ser None"
                )
                break

        self.assertTrue(found, "No se encontró entrada D2 para la frase esperada")

    def test_noop_d1_diálogo_adicional_suppressed(self):
        """
        Asegura que los registros D1 no-op (sin cambio)
        no se guarden en el logger.
        """

        text = '"Hola" dijo Juan. "Tengo…"'
        _, logger = self.converter.convert(text)

        # Buscar D1 entries
        rule_name = "D1: Diálogo adicional en línea"
        d1_entries = [r for r in logger.changes if r.get("rule") == rule_name]

        for rec in d1_entries:
            self.assertNotEqual(
                rec.get("original", "").strip(),
                rec.get("converted", "").strip(),
                "Found a D1 entry with no-op conversion; should be suppressed",
            )

    def test_quote_within_dialog_vs_continuation(self):
        """Test: Cita interna vs continuación de diálogo."""
        # Cita interna (debe usar « »)
        input_text1 = "\"Me dijo 'vendré mañana' pero no vino\" murmuró Pedro."
        expected1 = "—Me dijo «vendré mañana» pero no vino —murmuró Pedro."
        result1, _ = self.converter.convert(input_text1)
        self.assertEqual(result1, expected1)

        # Continuación de diálogo (debe usar —)
        input_text2 = '"Hola" dijo Ana. "¿Cómo estás?"'
        expected2 = "—Hola —dijo Ana. —¿Cómo estás?"
        result2, _ = self.converter.convert(input_text2)
        self.assertEqual(result2, expected2)

    def test_plural_dialog_tags(self):
        """Test: Verbos de diálogo en plural."""
        text = '"Hola" dijeron los niños.'
        result, _ = self.converter.convert(text)
        self.assertEqual(result, "—Hola —dijeron los niños.")

    def test_missing_space_before_dialog_tag_with_period(self):
        """Test: Falta espacio antes de verbo con punto."""
        text = '"Se mudaron hace poco."Dijo sonriente Yiri.'
        result, _ = self.converter.convert(text)
        self.assertEqual(result, "—Se mudaron hace poco —dijo sonriente Yiri.")

    def test_missing_space_before_dialog_tag_with_comma(self):
        """Test: Falta espacio antes de verbo con coma."""
        text = '"Hola",Dijo Juan.'
        result, _ = self.converter.convert(text)
        self.assertEqual(result, "—Hola —dijo Juan.")

    def test_missing_space_before_dialog_tag_no_punctuation(self):
        """Test: Falta espacio antes de verbo sin puntuación."""
        text = '"Hola"Dijo Juan.'
        result, _ = self.converter.convert(text)
        self.assertEqual(result, "—Hola —dijo Juan.")

    def test_missing_space_multiple_cases(self):
        """Test: Múltiples casos de espacios faltantes."""
        text = '"Yo conozco mejor a mi hermanito."Dijo divertida Amelia.'
        result, _ = self.converter.convert(text)
        self.assertEqual(
            result, "—Yo conozco mejor a mi hermanito —dijo divertida Amelia."
        )

    def test_missing_space_not_dialog_tag(self):
        """Test: No insertar espacio si no es verbo de dicción."""
        # "Texto"Palabra donde Palabra NO es verbo de dicción
        text = '"Hola"Mundo'
        result, _ = self.converter.convert(text)
        # No debería cambiar porque "Mundo" no es verbo de dicción
        self.assertEqual(result, '—Hola"Mundo')


if __name__ == "__main__":
    unittest.main()
