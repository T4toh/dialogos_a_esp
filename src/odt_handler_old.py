"""
Módulo para trabajar con archivos ODT (OpenDocument Text).
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


class ODTReader:
    """Lee y extrae texto de archivos ODT."""
    
    # Namespace para ODT
    NAMESPACES = {
        'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
        'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
        'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0'
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
            with zipfile.ZipFile(self.filepath, 'r') as odt_zip:
                # El contenido está en content.xml
                if 'content.xml' not in odt_zip.namelist():
                    raise ValueError(f"{self.filepath} no parece ser un archivo ODT válido")
                
                # Leer el XML
                content_xml = odt_zip.read('content.xml')
                
                # Parsear XML
                root = ET.fromstring(content_xml)
                
                # Extraer texto
                text_parts = []
                self._extract_text_recursive(root, text_parts)
                
                return '\n'.join(text_parts)
                
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
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        
        # Si es un párrafo, añadir su texto
        if tag == 'p':
            para_text = self._get_paragraph_text(element)
            if para_text.strip():
                text_parts.append(para_text)
        
        # Si es un encabezado
        elif tag == 'h':
            heading_text = self._get_paragraph_text(element)
            if heading_text.strip():
                text_parts.append(heading_text)
        
        # Procesar hijos recursivamente
        for child in element:
            self._extract_text_recursive(child, text_parts)
    
    def _get_paragraph_text(self, element) -> str:
        """
        Obtiene el texto de un párrafo, incluyendo spans y otros elementos inline.
        
        Args:
            element: Elemento de párrafo
            
        Returns:
            Texto del párrafo
        """
        text_parts = []
        
        # Texto directo del elemento
        if element.text:
            text_parts.append(element.text)
        
        # Procesar elementos hijos (spans, etc)
        for child in element:
            if child.text:
                text_parts.append(child.text)
            if child.tail:
                text_parts.append(child.tail)
        
        return ''.join(text_parts)


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
        mimetype = 'application/vnd.oasis.opendocument.text'
        
        # manifest.xml
        manifest = '''<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <manifest:file-entry manifest:media-type="application/vnd.oasis.opendocument.text" manifest:full-path="/"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="content.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="styles.xml"/>
  <manifest:file-entry manifest:media-type="text/xml" manifest:full-path="meta.xml"/>
</manifest:manifest>'''
        
        # meta.xml
        meta = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
  <office:meta>
    <meta:generator>dialogos_a_español 1.0.1</meta:generator>
  </office:meta>
</office:document-meta>'''
        
        # styles.xml (mínimo)
        styles = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
  <office:styles/>
  <office:automatic-styles/>
  <office:master-styles/>
</office:document-styles>'''
        
        # content.xml con el texto
        paragraphs = []
        for line in text.split('\n'):
            escaped_line = self._escape_xml(line)
            paragraphs.append(f'    <text:p text:style-name="Standard">{escaped_line}</text:p>')
        
        content = f'''<?xml version="1.0" encoding="UTF-8"?>
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
</office:document-content>'''
        
        # Crear archivo ZIP (ODT)
        with zipfile.ZipFile(self.filepath, 'w', zipfile.ZIP_DEFLATED) as odt_zip:
            # mimetype debe ser el primer archivo, sin comprimir
            odt_zip.writestr('mimetype', mimetype, compress_type=zipfile.ZIP_STORED)
            
            # Crear directorio META-INF
            odt_zip.writestr('META-INF/manifest.xml', manifest)
            
            # Añadir archivos XML
            odt_zip.writestr('meta.xml', meta)
            odt_zip.writestr('styles.xml', styles)
            odt_zip.writestr('content.xml', content)
    
    def _escape_xml(self, text: str) -> str:
        """
        Escapa caracteres especiales para XML.
        
        Args:
            text: Texto a escapar
            
        Returns:
            Texto escapado
        """
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))


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
    if filepath.suffix.lower() != '.odt':
        return False
    
    # Verificar que sea un ZIP válido con content.xml
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            return 'content.xml' in z.namelist()
    except:
        return False
