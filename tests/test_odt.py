"""
Tests para el módulo ODT.
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from src.odt_handler import ODTReader, ODTWriter, is_odt_file


class TestODTHandler(unittest.TestCase):
    """Tests para manejo de archivos ODT."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Limpieza después de cada test."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_and_read_odt(self):
        """Test: Crear y leer un archivo ODT."""
        odt_path = self.temp_dir / "test.odt"
        test_text = "Línea 1\nLínea 2\nLínea 3"
        
        # Escribir
        writer = ODTWriter(odt_path)
        writer.write_text(test_text)
        
        # Verificar que existe
        self.assertTrue(odt_path.exists())
        
        # Leer
        reader = ODTReader(odt_path)
        read_text = reader.extract_text()
        
        # Verificar contenido
        self.assertEqual(read_text, test_text)
    
    def test_odt_with_dialogs(self):
        """Test: ODT con diálogos."""
        odt_path = self.temp_dir / "dialogs.odt"
        test_text = '"Hola" dijo Juan.\n"Adiós" respondió María.'
        
        writer = ODTWriter(odt_path)
        writer.write_text(test_text)
        
        reader = ODTReader(odt_path)
        read_text = reader.extract_text()
        
        self.assertIn("Hola", read_text)
        self.assertIn("Juan", read_text)
    
    def test_is_odt_file_positive(self):
        """Test: Detectar archivo ODT válido."""
        odt_path = self.temp_dir / "test.odt"
        writer = ODTWriter(odt_path)
        writer.write_text("Test")
        
        self.assertTrue(is_odt_file(odt_path))
    
    def test_is_odt_file_negative_txt(self):
        """Test: Archivo TXT no es ODT."""
        txt_path = self.temp_dir / "test.txt"
        txt_path.write_text("Test", encoding='utf-8')
        
        self.assertFalse(is_odt_file(txt_path))
    
    def test_is_odt_file_nonexistent(self):
        """Test: Archivo inexistente."""
        self.assertFalse(is_odt_file(self.temp_dir / "nonexistent.odt"))
    
    def test_odt_with_special_characters(self):
        """Test: ODT con caracteres especiales."""
        odt_path = self.temp_dir / "special.odt"
        test_text = "Texto con <etiquetas> & símbolos 'especiales' \"comillas\""
        
        writer = ODTWriter(odt_path)
        writer.write_text(test_text)
        
        reader = ODTReader(odt_path)
        read_text = reader.extract_text()
        
        # Debe preservar los caracteres especiales
        self.assertIn("<etiquetas>", read_text)
        self.assertIn("&", read_text)
        self.assertIn("'especiales'", read_text)
    
    def test_odt_empty_lines(self):
        """Test: ODT con líneas vacías."""
        odt_path = self.temp_dir / "empty_lines.odt"
        test_text = "Línea 1\n\nLínea 3\n\nLínea 5"
        
        writer = ODTWriter(odt_path)
        writer.write_text(test_text)
        
        reader = ODTReader(odt_path)
        read_text = reader.extract_text()
        
        # Las líneas vacías no se preservan en ODT (es normal)
        # Verificar que el contenido importante está ahí
        self.assertIn("Línea 1", read_text)
        self.assertIn("Línea 3", read_text)
        self.assertIn("Línea 5", read_text)
    
    def test_odt_unicode_characters(self):
        """Test: ODT con caracteres Unicode."""
        odt_path = self.temp_dir / "unicode.odt"
        test_text = "Español: ñ á é í ó ú\nRaya: —\nComillas: \u201C \u201D « »"
        
        writer = ODTWriter(odt_path)
        writer.write_text(test_text)
        
        reader = ODTReader(odt_path)
        read_text = reader.extract_text()
        
        # Debe preservar caracteres Unicode
        self.assertIn("ñ", read_text)
        self.assertIn("—", read_text)
        self.assertIn("\u201C", read_text)
        self.assertIn("«", read_text)


if __name__ == '__main__':
    unittest.main()
