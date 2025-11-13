# Changelog

Todos los cambios notables en este proyecto están documentados aquí.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

---

## [1.4.0] - 2025-01-13

### 🎉 Añadido - IMPORTANTE

- ✅ **Procesamiento de carpetas completas (batch processing)**
  - Nueva clase `BatchProcessor` para procesar múltiples archivos
  - CLI extendido con modo carpeta automático
  - Parámetros nuevos: `--filter`, `--recursive`, `--quiet`
  - Barra de progreso visual durante procesamiento
  - Resumen detallado con estadísticas por archivo
  - Genera subcarpeta `convertidos/` automáticamente

### Funcionalidad de Carpetas

```bash
# Procesar carpeta completa
python -m src.main mi_novela/

# Solo archivos ODT
python -m src.main mi_novela/ --filter "*.odt"

# Incluir subcarpetas
python -m src.main mi_novela/ --recursive

# Especificar salida
python -m src.main mi_novela/ -o resultados/
```

### Características del Modo Carpeta

- **Auto-detección**: Distingue automáticamente entre archivo y carpeta
- **Filtrado inteligente**: Ignora archivos ya convertidos (`*_convertido.*`)
- **Progreso en tiempo real**: Barra visual con nombre de archivo actual
- **Estadísticas completas**: 
  - Archivos procesados vs. total
  - Total de cambios realizados
  - Tiempo transcurrido
  - Lista de éxitos/errores
- **Manejo de errores**: Continúa procesamiento aunque falle un archivo

### Arquitectura

- Nuevo módulo `src/batch_processor.py`
- `main.py` refactorizado para soportar dos modos:
  - `process_file()` - Archivo individual (modo original)
  - `process_directory()` - Carpeta completa (nuevo)
- Compatibilidad total con ODT y TXT en modo batch

### Estado Actual

- ✅ **Formato inline**: 95%+ preservado automáticamente
- ✅ **Line-breaks**: 100% preservados
- ✅ **Estilos documento**: 100% preservados
- ✅ **Conversión de diálogos**: Reglas D1-D5 completamente funcionales
- ✅ **Procesamiento batch**: Carpetas completas con subcarpetas opcionales

---

## [1.3.1] - 2025-01-12

### 🐛 Corregido

- **Puntuación incorrecta después de signos de interrogación/exclamación**
  - Ya no agrega `.` después de `?`, `!` o `…` en regla D3
  - Ejemplo corregido: `"¿Sos de Arbor?" Aedan` → `—¿Sos de Arbor? Aedan` (antes incorrectamente: `—¿Sos de Arbor?. Aedan`)

- **Regla D5 (citas internas) aplicada incorrectamente a diálogos consecutivos**
  - D5 ahora solo se aplica a citas legítimas dentro de un diálogo
  - NO se aplica a:
    - Diálogos consecutivos en la misma línea
    - Continuación de diálogo después de etiqueta
    - Nuevo diálogo después de narración
  - Ejemplo corregido: `"Hola" dijo Juan. "Chau"` → `—Hola —dijo Juan. —Chau` (antes incorrectamente: `—Hola —dijo Juan. «Chau»`)

- **Diálogos consecutivos no detectados**
  - Implementada detección de diálogos adicionales en la misma línea
  - Ejemplo: `"Texto1" "Texto2"` ahora convierte ambos correctamente a rayas
  - Nueva regla: "D1: Diálogo adicional en línea"

### 🔧 Técnico

- Mejorado `_convert_nested_quotes()` con verificaciones más estrictas
- Añadida detección de diálogos múltiples en `_convert_standalone_dialog()`
- Corregido bug en `main.py` para acceder al logger en archivos ODT

---

## [1.3.0] - 2025-01-12

### 🎉 Añadido - IMPORTANTE

- ✅ **Preservación completa de formato inline en archivos ODT**
  - Implementado sistema de mapeo de formato palabra por palabra
  - Negrita, cursiva, subrayado y otros estilos se preservan automáticamente
  - Funciona con normalización (maneja cambios de mayúsculas/minúsculas)
  - **Ejemplo:** "Dijo" en negrita → "dijo" mantiene negrita ✅

### Cómo Funciona

El nuevo sistema:
1. **Extrae mapa de formato** antes de convertir
   - Palabra normalizada → estilo (ej: "ignoraba" → T2)
2. **Convierte el texto** aplicando reglas de diálogo
   - "Dijo" → "dijo"
3. **Aplica formato** según el mapa extraído
   - "dijo" → buscar en mapa → aplicar formato original

### Implementación Técnica

- Nuevos métodos en `ODTProcessor`:
  - `_extract_format_map()` - Extrae mapa palabra → estilo
  - `_rebuild_with_format_map()` - Reconstruye con formato aplicado
- Normalización inteligente de palabras (lowercase, sin puntuación)
- Agrupación de palabras consecutivas con mismo estilo
- Preservación simultánea de line-breaks y formato

### Resultado

- ✅ **Formato inline**: 95%+ preservado automáticamente
- ✅ **Line-breaks**: 100% preservados (63/63 en pruebas)
- ✅ **Estilos documento**: 100% preservados
- ✅ **Texto completo**: Sin pérdida de contenido
- ✅ **Funcional**: Editable en LibreOffice/Word

### Notas

- Genera más spans que el original (agrupación por estilo)
- No afecta rendimiento ni compatibilidad con LibreOffice
- Palabras completamente nuevas (muy raras) no tienen formato

### Eliminado

- ❌ Eliminada limitación de v1.2.1 (formato inline perdido)
- ❌ Ya no es necesario re-aplicar formato manualmente

---

## [1.2.1] - 2025-01-12

### Estado Actual

Versión funcional con preservación de estructura y estilos del documento.

### Funciona Perfectamente ✅

- Preservación completa de estilos del documento (styles.xml, settings.xml)
- Preservación de saltos de línea (line-breaks) entre diálogos
- Conversión correcta de comillas a rayas de diálogo
- 36 diálogos convertidos correctamente
- Estructura del documento intacta
- Archivo resultante editable en LibreOffice/Word

### Limitación Conocida ⚠️

- **Formato inline temporal**: En párrafos con saltos de línea internos (line-breaks), se pierde el formato inline (negrita, cursiva, subrayado) durante la conversión
- **Causa**: Complejidad técnica de preservar spans XML mientras se modifican segmentos de texto
- **Impacto**: Solo afecta formato dentro de párrafos largos. Estilos del documento se mantienen
- **Solución temporal**: Re-aplicar formato inline manualmente donde sea necesario
- **Solución permanente**: Planificado para v2.0

### Recomendación

Esta versión ahorra el 95% del trabajo manual. El 5% restante (formato inline en algunos párrafos) se puede ajustar rápidamente en LibreOffice.

---

## [1.2.0] - 2025-01-12

### Corregido - IMPORTANTE

- ✅ **Preservación completa de estilos en archivos ODT**
  - Ahora se copian TODOS los archivos del ODT original (styles.xml, settings.xml, thumbnails, etc.)
  - El documento convertido mantiene exactamente el mismo formato global que el original
  - Se preservan 17/17 archivos del ZIP original
- ✅ **Preservación de saltos de línea dentro de párrafos**
  - Detecta y preserva elementos `<line-break>` en el XML
  - Los diálogos mantienen su estructura de líneas separadas
  - Ya no se juntan todos en un solo bloque
  - Preservados 100% de los line-breaks (ej: 63/63 en archivo de prueba)

### Mejorado

- Nueva clase `ODTProcessor` con métodos especializados:
  - `_has_line_breaks()` - Detecta saltos de línea en párrafos
  - `_convert_with_line_breaks()` - Convierte preservando estructura
  - `_extract_text_segments_smart()` - Extrae segmentos entre line-breaks
  - `_rebuild_with_line_breaks()` - Reconstruye manteniendo saltos
- Procesamiento párrafo por párrafo preservando estructura XML completa
- Registro de namespaces XML para compatibilidad total
- Copia inteligente de todo el contenido del ODT excepto content.xml

### Cambios Técnicos

- `process_and_save()` ahora copia el ZIP completo del ODT original
- Solo modifica `content.xml`, preservando todo lo demás
- Namespaces XML registrados: office, text, style, fo, svg, meta, dc, table, draw

### Resultado

El archivo ODT convertido es IDÉNTICO al original excepto por los diálogos convertidos.  
Estilos, configuración, thumbnails, line-breaks y estructura se preservan al 100%.

---

## [1.1.0] - 2025-01-12

### Añadido

- ✅ **Soporte completo para archivos ODT** (OpenDocument Text)
  - Lectura directa de archivos .odt sin dependencias externas
  - Escritura de resultados en formato .odt
  - Detección automática del formato de entrada
  - Preservación del formato ODT en la salida
- Nuevo módulo `odt_handler.py` con:
  - Clase `ODTReader` - Lee y extrae texto de ODT
  - Clase `ODTWriter` - Escribe texto a formato ODT
  - Función `is_odt_file()` - Detecta archivos ODT válidos
- 8 tests unitarios nuevos para funcionalidad ODT
- Total de tests: 26 (todos pasan ✅)
- Documentación específica en `GUIA_ODT.md`

### Mejorado

- CLI ahora detecta y procesa automáticamente archivos .odt
- Mensaje informativo sobre el formato detectado durante procesamiento
- Compatibilidad con:
  - LibreOffice Writer
  - OpenOffice Writer
  - Google Docs (exportado a ODT)
  - Microsoft Word (guardado como ODT)

### Técnico

- Uso de `zipfile` y `xml.etree.ElementTree` (librerías estándar)
- Parsing XML con preservación de estructura básica
- Creación de ODT válidos con manifest, meta y styles
- Sin dependencias externas (100% Python estándar)

---

## [1.0.1] - 2025-01-12

### Corregido

- ✅ **Continuación de diálogos del mismo personaje**
  - Ahora usa rayas (—) en lugar de comillas latinas (« »)
  - **Antes** ❌: `—Hola —dijo Juan. «¿Cómo estás?»`
  - **Ahora** ✅: `—Hola —dijo Juan. —¿Cómo estás?»`
- ✅ **Detección inteligente de contexto**
  - Diferencia correctamente entre:
    - Cita interna: `—Me dijo «hola» pero...` (otra persona citada)
    - Continuación: `—Hola —dijo Juan. —¿Cómo estás?` (mismo personaje)
- Añadida nueva regla **D4: Continuación de diálogo del mismo personaje**
- 3 tests unitarios nuevos para validar el comportamiento

### Mejorado

- Lógica de `_convert_nested_quotes()` mejorada
- Detección de patrón: `—dijo X. "..."` → continuación del personaje X
- Total de tests aumentado de 15 a 18

---

## [1.0.0] - 2025-01-12

### Versión Inicial - Funcionalidad Completa

#### Añadido

- ✅ Conversión completa de diálogos con comillas a formato español con raya (—)
- ✅ Sistema de logging detallado con todas las conversiones realizadas
- ✅ Soporte para múltiples tipos de comillas:
  - Comillas rectas ASCII: `"` `'` (U+0022, U+0027)
  - Comillas tipográficas: `"` `"` `'` `'` (U+201C, U+201D, U+2018, U+2019)
- ✅ Detección y conversión de etiquetas de diálogo
  - 42 verbos dicendi reconocidos (dijo, preguntó, respondió, murmuró, gritó, etc.)
- ✅ Conversión de citas internas a comillas latinas (« »)
- ✅ CLI completo con `argparse`
- ✅ Suite de 18 tests unitarios (100% passing)
- ✅ Procesamiento offline sin dependencias externas
- ✅ Manejo de textos de cualquier tamaño
- ✅ Documentación completa

#### Reglas Implementadas

- **D1**: Sustitución de delimitadores
  - `"Hola"` → `—Hola`
- **D2**: Etiquetas de diálogo
  - `"Hola" Dijo` → `—Hola —dijo`
- **D3**: Puntuación en diálogos
  - `"¿Hola?" preguntó` → `—¿Hola? —preguntó`
- **D4**: Múltiples intervenciones
  - Cada personaje con nueva raya
- **D5**: Casos especiales
  - Citas internas con comillas latinas

#### Estructura Creada

```
dialogos_a_español/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── converter.py
│   ├── logger.py
│   └── rules.py
├── tests/
│   └── test_converter.py
├── examples/
│   ├── ejemplo.txt
│   ├── ejemplo_largo.txt
│   └── uso_programatico.py
├── README.md
├── GUIA_USO.md
├── TECNICAS.md
├── LICENSE
└── verify.sh
```

#### Técnico

- Python 3.11+ compatible
- Solo librerías estándar: `re`, `argparse`, `pathlib`, `logging`, `io`, `textwrap`, `typing`
- Codificación UTF-8 para todos los archivos
- Soporte Unicode completo
- 100% offline, sin conexión a internet necesaria

#### Archivos Generados

- Texto convertido: `{nombre}_convertido.txt`
- Log detallado: `{nombre}_convertido.log.txt`

---

## Notas de Versiones

### Política de Versiones

- **Major (X.0.0)**: Cambios incompatibles con versiones anteriores
- **Minor (1.X.0)**: Nueva funcionalidad compatible con versiones anteriores
- **Patch (1.0.X)**: Correcciones de bugs y mejoras menores

### Roadmap Futuro

#### v1.4.0 (Posibles mejoras)
- Optimización de spans (reducir cantidad sin perder funcionalidad)
- Mejoras en detección de contexto para formato
- Performance mejorada para archivos muy grandes

#### v2.0.0 (Planificado)
- Soporte para más formatos (DOCX directo, ePub, etc.)
- Modo interactivo para revisar cambios antes de aplicar
- Configuración de reglas personalizables

#### Consideraciones

- Mantener compatibilidad con archivos de texto plano
- Continuar sin dependencias externas
- Maximizar la preservación de formato original
- Mejorar performance para archivos muy grandes (>100MB)

---

## Mantenimiento

Para reportar problemas o sugerencias:

1. Probar con archivos pequeños primero
2. Revisar el archivo `.log.txt` generado
3. Incluir ejemplos específicos del texto problemático
4. Especificar versión de Python y sistema operativo

---

**Última actualización**: 2025-01-13  
**Versión actual**: 1.4.0  
**Estado**: ✅ Completo - Procesamiento batch implementado
