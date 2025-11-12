# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [1.2.0] - 2025-01-12

### Corregido - IMPORTANTE
- ✅ **Preservación completa de estilos en archivos ODT**
  - Ahora se copian TODOS los archivos del ODT original (styles.xml, settings.xml, etc.)
  - El documento convertido mantiene exactamente el mismo formato que el original
  
- ✅ **Preservación de saltos de línea dentro de párrafos**
  - Detecta y preserva elementos `<line-break>` en el XML
  - Los diálogos mantienen su estructura de líneas separadas
  - Ya no se juntan todos en un solo bloque

### Mejorado
- Nueva clase `ODTProcessor` con métodos especializados:
  - `_has_line_breaks()` - Detecta saltos de línea
  - `_convert_with_line_breaks()` - Convierte preservando estructura
  - `_extract_text_segments()` - Extrae segmentos entre line-breaks
  - `_rebuild_with_line_breaks()` - Reconstruye manteniendo saltos
- Procesamiento párrafo por párrafo preservando estructura XML completa
- Registro de namespaces XML para compatibilidad total

### Resultado
Ahora el archivo ODT convertido es IDÉNTICO al original excepto por los diálogos convertidos.
Estilos, formato, saltos de línea, imágenes (si las hay) se preservan al 100%.

## [1.1.0] - 2025-01-12

### Añadido
- ✅ **Soporte completo para archivos ODT** (OpenDocument Text)
  - Lectura directa de archivos .odt sin dependencias externas
  - Escritura de resultados en formato .odt
  - Detección automática del formato de entrada
  - Preservación del formato ODT en la salida
- Módulo `odt_handler.py` con clases `ODTReader` y `ODTWriter`
- 8 tests unitarios para funcionalidad ODT
- Total de tests: 26 (todos pasan ✅)

### Mejorado
- CLI ahora detecta y procesa automáticamente archivos .odt
- Mensaje informativo sobre el formato detectado

## [1.0.1] - 2025-01-12

### Corregido
- Continuación de diálogos del mismo personaje ahora usa rayas (—) en lugar de comillas latinas (« »)
  - Antes: `—Hola —dijo Juan. «¿Cómo estás?»` ❌
  - Ahora: `—Hola —dijo Juan. —¿Cómo estás?` ✅
- Detección inteligente entre cita interna y continuación de diálogo
- Añadidos 3 tests nuevos para validar el comportamiento correcto

## [1.0.0] - 2025-01-12

### Añadido
- Conversión completa de diálogos con comillas a formato español con raya (—)
- Sistema de logging detallado con todas las conversiones realizadas
- Soporte para comillas dobles (" ") y simples (' ')
- Soporte para comillas tipográficas/curvas (" " ' ')
- Detección y conversión de etiquetas de diálogo (dijo, preguntó, etc.)
- Conversión de citas internas a comillas latinas (« »)
- CLI completo con argparse
- Suite de tests unitarios
- Procesamiento offline sin dependencias externas
- Manejo de textos de cualquier tamaño
- Documentación completa (README, GUIA_USO)
- Ejemplos de uso (básico y avanzado)

### Reglas Implementadas
- D1: Sustitución de delimitadores (comillas rectas y tipográficas)
- D2: Etiquetas de diálogo
- D3: Puntuación en diálogos
- D4: Múltiples intervenciones
- D5: Casos especiales (citas internas)

### Técnico
- Python 3.11+ compatible
- Solo librerías estándar (re, argparse, pathlib, logging, io, textwrap, typing)
- Codificación UTF-8 para todos los archivos
- 18 tests unitarios con 100% de cobertura de funcionalidad básica
- Soporte Unicode completo (U+201C, U+201D, U+2018, U+2019)
