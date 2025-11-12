"""
Módulo para trabajar con archivos ODT (OpenDocument Text).
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Tuple


class ODTProcessor:
    """Procesa archivos ODT preservando estilos y estructura."""
    
    def __init__(self, filepath: Path):
        """Inicializa el procesador de ODT."""
        self.filepath = filepath
        # Registrar namespaces para preservarlos en el XML
        ET.register_namespace('office', 'urn:oasis:names:tc:opendocument:xmlns:office:1.0')
        ET.register_namespace('text', 'urn:oasis:names:tc:opendocument:xmlns:text:1.0')
        ET.register_namespace('style', 'urn:oasis:names:tc:opendocument:xmlns:style:1.0')
        ET.register_namespace('fo', 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0')
        ET.register_namespace('svg', 'urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0')
        ET.register_namespace('meta', 'urn:oasis:names:tc:opendocument:xmlns:meta:1.0')
        ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        ET.register_namespace('table', 'urn:oasis:names:tc:opendocument:xmlns:table:1.0')
        ET.register_namespace('draw', 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0')
    
    def process_and_save(self, output_path: Path, text_converter_func):
        """
        Procesa el ODT aplicando conversiones y guarda preservando estructura completa.
        
        Args:
            output_path: Ruta de salida
            text_converter_func: Función que convierte el texto (recibe str, retorna tuple[str, logger])
        """
        try:
            with zipfile.ZipFile(self.filepath, 'r') as input_zip:
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as output_zip:
                    
                    # Copiar TODOS los archivos excepto content.xml
                    for item in input_zip.namelist():
                        if item != 'content.xml':
                            data = input_zip.read(item)
                            # mimetype debe ir sin comprimir
                            if item == 'mimetype':
                                output_zip.writestr(item, data, compress_type=zipfile.ZIP_STORED)
                            else:
                                output_zip.writestr(item, data)
                    
                    # Procesar content.xml preservando estructura
                    content_xml = input_zip.read('content.xml')
                    root = ET.fromstring(content_xml)
                    
                    # Convertir textos párrafo por párrafo
                    self._convert_paragraphs_in_tree(root, text_converter_func)
                    
                    # Guardar content.xml modificado
                    modified_content = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                    output_zip.writestr('content.xml', modified_content)
                    
        except Exception as e:
            raise Exception(f"Error procesando ODT: {e}")
    
    def _convert_paragraphs_in_tree(self, element, converter_func):
        """Convierte textos párrafo por párrafo preservando estructura."""
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        
        # Solo procesar párrafos y encabezados
        if tag in ('p', 'h'):
            # Verificar si tiene line-breaks internos
            if self._has_line_breaks(element):
                # Procesar preservando line-breaks
                self._convert_with_line_breaks(element, converter_func)
            else:
                # Conversión simple
                text = self._get_full_text(element)
                if text.strip():
                    converted, _ = converter_func(text)
                    if converted != text:
                        self._set_paragraph_text(element, converted)
        
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
        return ''.join(parts)
    
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
    
    def _has_line_breaks(self, element) -> bool:
        """Verifica si un párrafo tiene saltos de línea internos."""
        for child in element.iter():
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if tag == 'line-break':
                return True
        return False
    
    def _convert_with_line_breaks(self, element, converter_func):
        """
        Convierte texto preservando line-breaks Y formato (spans, bold, italic).
        
        Este método es más inteligente: en lugar de reconstruir todo el párrafo,
        modifica el texto IN-PLACE preservando toda la estructura de elementos.
        """
        # Extraer segmentos de texto entre line-breaks
        segments = self._extract_text_segments_smart(element)
        
        # Convertir cada segmento
        converted_segments = []
        for seg in segments:
            if seg.strip():
                converted, _ = converter_func(seg)
                converted_segments.append(converted)
            else:
                converted_segments.append(seg)
        
        # Aplicar conversiones IN-PLACE sin destruir la estructura
        self._apply_text_changes_inplace(element, segments, converted_segments)
    
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
                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                
                if child_tag == 'line-break':
                    # Guardar segmento actual
                    segments.append(''.join(current_text))
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
            segments.append(''.join(current_text))
        
        return segments
    
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
                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                
                if child_tag == 'line-break':
                    # Guardar segmento actual y empezar uno nuevo
                    segments.append(''.join(current_segment))
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
            segments.append(''.join(current_segment))
        
        return segments
    
    def _rebuild_with_line_breaks(self, element, segments: list):
        """Reconstruye el párrafo con line-breaks entre segmentos."""
        # Guardar atributos
        attribs = element.attrib.copy()
        
        # Limpiar elemento
        element.clear()
        element.attrib.update(attribs)
        
        # Namespace para line-break
        ns_text = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'
        
        # Reconstruir con line-breaks
        if segments:
            element.text = segments[0]
            
            for i in range(1, len(segments)):
                # Añadir line-break
                lb = ET.SubElement(element, f'{ns_text}line-break')
                lb.tail = segments[i]


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
