"""
Tests para el conversor de diálogos.
"""

import unittest
from src.converter import DialogConverter


class TestDialogConverter(unittest.TestCase):
    """Tests para DialogConverter."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.converter = DialogConverter()
    
    def test_simple_dialog_double_quotes(self):
        """Test: Conversión de diálogo simple con comillas dobles."""
        input_text = '"Hola, Juan"'
        expected = '—Hola, Juan'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_simple_dialog_single_quotes(self):
        """Test: Conversión de diálogo simple con comillas simples."""
        input_text = "'Hola, Juan'"
        expected = '—Hola, Juan'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_dialog_with_tag(self):
        """Test: Diálogo con etiqueta narrativa."""
        input_text = '"Hola" dijo Juan.'
        expected = '—Hola —dijo Juan.'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_dialog_with_question(self):
        """Test: Diálogo con pregunta."""
        input_text = '"¿Cómo estás?" preguntó Ana.'
        expected = '—¿Cómo estás? —preguntó Ana.'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_dialog_with_exclamation(self):
        """Test: Diálogo con exclamación."""
        input_text = '"¡Qué sorpresa!" exclamó María.'
        expected = '—¡Qué sorpresa! —exclamó María.'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_dialog_with_comma(self):
        """Test: Diálogo con coma antes de etiqueta."""
        input_text = '"No puedo creerlo," dijo Juan.'
        expected = '—No puedo creerlo —dijo Juan.'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_dialog_followed_by_narration(self):
        """Test: Diálogo seguido de narración."""
        input_text = '"Está bien." Cerró la puerta.'
        expected = '—Está bien. Cerró la puerta.'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_nested_quotes(self):
        """Test: Citas dentro de diálogos."""
        input_text = '—Ella me dijo \'te esperaré\''
        expected = '—Ella me dijo «te esperaré»'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_multiline_dialogs(self):
        """Test: Múltiples líneas con diálogos."""
        input_text = '''"Hola" dijo Juan.
"Adiós" respondió María.'''
        expected = '''—Hola —dijo Juan.
—Adiós —respondió María.'''
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_mixed_quotes(self):
        """Test: Mezcla de comillas dobles y simples."""
        input_text = '''"Hola" dijo Juan.
'Adiós' respondió María.'''
        expected = '''—Hola —dijo Juan.
—Adiós —respondió María.'''
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_no_changes_without_quotes(self):
        """Test: Texto sin comillas no se modifica."""
        input_text = 'Juan caminaba por el parque.'
        expected = 'Juan caminaba por el parque.'
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
        input_text = '\u201CHola\u201D dijo Juan.'  # "Hola" dijo Juan.
        expected = '—Hola —dijo Juan.'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_typographic_single_quotes(self):
        """Test: Comillas tipográficas simples ('')."""
        input_text = '\u2018Hola\u2019 dijo María.'  # 'Hola' dijo María.
        expected = '—Hola —dijo María.'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_mixed_typographic_quotes(self):
        """Test: Mezcla de comillas rectas y tipográficas."""
        input_text = '''"Hola" dijo Juan.
\u201CAdiós\u201D respondió María.'''
        expected = '''—Hola —dijo Juan.
—Adiós —respondió María.'''
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_dialog_continuation_same_speaker(self):
        """Test: Continuación de diálogo del mismo personaje."""
        input_text = '"Hola" dijo Juan. "¿Cómo estás?"'
        expected = '—Hola —dijo Juan. —¿Cómo estás?'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_long_dialog_continuation(self):
        """Test: Diálogo largo con continuación."""
        input_text = '"Reunión familiar…" Dijo jocoso Bastien. "Miralo a Chispita, con una princesa en la cama."'
        expected = '—Reunión familiar… —dijo jocoso Bastien. —Miralo a Chispita, con una princesa en la cama.'
        result, _ = self.converter.convert(input_text)
        self.assertEqual(result, expected)
    
    def test_quote_within_dialog_vs_continuation(self):
        """Test: Cita interna vs continuación de diálogo."""
        # Cita interna (debe usar « »)
        input_text1 = '"Me dijo \'vendré mañana\' pero no vino" murmuró Pedro.'
        expected1 = '—Me dijo «vendré mañana» pero no vino —murmuró Pedro.'
        result1, _ = self.converter.convert(input_text1)
        self.assertEqual(result1, expected1)
        
        # Continuación de diálogo (debe usar —)
        input_text2 = '"Hola" dijo Ana. "¿Cómo estás?"'
        expected2 = '—Hola —dijo Ana. —¿Cómo estás?'
        result2, _ = self.converter.convert(input_text2)
        self.assertEqual(result2, expected2)


if __name__ == '__main__':
    unittest.main()
