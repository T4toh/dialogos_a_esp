# Changelog

Historial de cambios del proyecto.

---

## [1.6.0] - 2025-01-14

### Agregado
- **REGLAS_RAE.md**: Documentación completa de reglas RAE para diálogos con raya
  - 5 reglas principales (D1-D5) explicadas en detalle con ejemplos
  - 42 verbos de dicción listados y categorizados
  - Ejemplos correctos e incorrectos de puntuación según RAE
  - Estado de implementación actual de cada regla
- **MEJORAS_DIALOGOS.md**: Lista de mejoras pendientes para el parser

### Corregido
- **Puntuación antes de verbos de dicción**: Corrección automática según RAE
  - Detecta y corrige: `"texto." verbo` → `"texto", verbo`
  - Ejemplo: `"Buenos días, Adi." dijo` → `—Buenos días, Adi —dijo` (sin punto antes de raya)
  - Regla RAE: usar coma (no punto) antes de cerrar comillas si sigue verbo de dicción
  - No afecta signos fuertes (¿?¡!) que son correctos según RAE
- **Bug crítico en batch processing**: Logs acumulados entre archivos
  - Cada archivo ahora crea su propio `DialogConverter()` independiente
  - Anteriormente el logger acumulaba cambios de todos los archivos procesados
  - Logs en interfaz web ahora muestran contenido correcto por archivo

### Cambiado
- **Limpieza general del código** (pasó linting ruff):
  - Type hints: Agregado `Optional[str]` donde funciones retornan `None`
  - Excepciones: `except:` → `except Exception:` (no bare except)
  - Imports: Eliminados duplicados (3x `re` en odt_handler) y no usados
  - Variables: Removidas asignaciones sin uso (`container_key`, etc.)
  - Whitespace: 127 líneas limpiadas automáticamente
- **Documentación mejorada**:
  - `.github/copilot-instructions.md`: Sección "Code Quality Standards" con reglas de linting
  - README.md: Info del visualizador de logs y estadísticas integrados

---

## [1.5.2] - 2025-01-13

### Eliminado

- **Botón "Abrir Carpeta de Resultados" en interfaz web**
  - Funcionalidad inconsistente entre sistemas operativos
  - Reemplazado por mostrar la ruta de resultados directamente
  - Los usuarios pueden copiar la ruta y abrirla manualmente

---

## [1.5.1] - 2025-01-13

### Corregido

- **Truncamiento de logs mejorado para coherencia**
  - Problema: Original y convertido se truncaban en puntos diferentes
  - Ejemplo: Original mostraba "...Técnica Arca..." pero convertido "...después de ..."
  - Causa: Algoritmo usaba posición de comillas, que difiere entre `"` y `—`
  - Solución: Truncamiento simple desde el inicio, cortando en espacio
  - Límite aumentado a 150 caracteres (antes 100)
  - Ahora ambos textos se truncan en el MISMO punto lógico

### Mejorado

- **Legibilidad de logs**
  - Textos cortos (<150 chars) se muestran completos
  - Textos largos se truncan en el último espacio antes de 150 chars
  - No parte palabras en medio
  - Original y convertido siempre alineados

### Confirmado

- **Formato inline (itálicas/negritas) SÍ se preserva en ODT**
  - El problema reportado era SOLO en los logs
  - El ODT convertido tiene "Técnica Arcana" completo con formato
  - Los logs solo mostraban truncamiento confuso

---

## [1.5.0] - 2025-01-13

### ⚠️ CORRECCIÓN CRÍTICA

- **Line-breaks internos en ODT ahora se preservan correctamente**
  - Bug crítico: Párrafos con `<text:line-break/>` se pegaban sin saltos de línea
  - Antes: Todo el capítulo en 12 líneas pegadas
  - Ahora: 386 líneas correctamente separadas
  - Afectaba archivos ODT creados en LibreOffice con Shift+Enter
  
### Corregido

- **ODTReader._get_paragraph_text() reescrito**
  - Ahora es recursivo para procesar line-breaks dentro de spans
  - Convierte `<text:line-break/>` a `\n` correctamente
  - Preserva estructura de párrafos largos con saltos internos
  
### Impacto

- **Antes (v1.4.4):**
  ```
  ...peinado.Técnica Arcana."Me contó...
  ```
  (Todo pegado, ilegible)

- **Ahora (v1.5.0):**
  ```
  ...peinado.
  —Buenos días, Adi. —dijo llena de energía.
  Sus cabellos castaños...
  ```
  (Correctamente separado)

### Tests

- 27/27 tests pasando ✓
- Probado con novela completa de ejemplo
- Line-breaks preservados en lectura Y escritura

---

## [1.4.4] - 2025-01-13

### Mejorado

- **Logs de conversión con truncamiento inteligente**
  - Textos largos ahora se truncan a ~100 caracteres
  - Muestra el contexto relevante (inicio del diálogo) en lugar del medio
  - Los logs son mucho más legibles para textos largos
  - Ejemplo: Texto de 259 caracteres se muestra como `"Inicio del texto...`
  - Mejora significativa en la usabilidad del archivo `.log.txt`

### Técnico

- `src/logger.py`: Nueva función `_truncate_text()` con lógica contextual
- Detecta posición de comillas y centra el truncamiento alrededor de ellas
- Máximo 100 caracteres por entrada de log (configurable)

---

## [1.4.3] - 2025-01-13

### Añadido

- **Soporte para narración compleja entre diálogos (RAE 2.3.d)**
  - Ejemplo: `"Demo." El hombre agregó. "¿Y ahora?"` → `—Demo. —El hombre agregó. —¿Y ahora?`
  - Ahora detecta correctamente narración sin verbo de lengua
  - Agrega raya de apertura antes de narración con mayúscula
  - Test específico agregado para caso complejo

- **Link a reglas RAE en README**
  - Referencia oficial: https://www.rae.es/dpd/raya
  - Ejemplos según RAE en la documentación
  - Explicación clara de cada regla implementada

### Corregido

- **Raya de apertura en narración sin verbo de lengua**
  - Antes: `"Está bien." Cerró la puerta` → `—Está bien. Cerró la puerta` ❌
  - Ahora: `"Está bien." Cerró la puerta` → `—Está bien. —Cerró la puerta` ✓
  - Cumple con RAE 2.3.d

### Tests

- 27/27 tests pasando ✓
- Nuevo test: `test_complex_narration_interruption`
- Test actualizado: `test_dialog_followed_by_narration`

---

## [1.4.2] - 2025-01-13

### Corregido

- **Cumplimiento total de reglas RAE para puntuación en diálogos**
  - `"Cortesía." dijo` ahora produce `—Cortesía. —dijo.` (mantiene el punto del diálogo)
  - Antes quitaba incorrectamente el punto: `—Cortesía —dijo.` ❌
  - Ahora sigue la norma RAE: mantener puntuación original del diálogo ✓
  - Referencia: https://www.rae.es/dpd/raya
  
### Ejemplos RAE implementados

- `"¡Qué le vamos a hacer!" exclamó` → `—¡Qué le vamos a hacer! —exclamó`
- `"Espero que salga bien" dijo` → `—Espero que salga bien —dijo`
- `"¿Qué hora es?" preguntó` → `—¿Qué hora es? —preguntó`
- `"No lo sé." contestó` → `—No lo sé. —contestó`

---

## [1.4.1] - 2025-01-13

### Corregido

- **Pérdida de formato inline en archivos ODT**
  - Negrita, cursiva, subrayado ahora se preservan en TODOS los párrafos
  - Antes solo se preservaba en párrafos con line-breaks
  - Usa mapeo de formato palabra por palabra para todos los casos
  - Ejemplo: "Técnica Arcana" en itálicas se mantiene en itálicas

### Técnico

- `src/odt_handler.py`: `_convert_paragraphs_in_tree()` siempre usa mapeo de formato

---

## [1.4.0] - 2025-01-13

### Añadido

- **Interfaz web con Streamlit**
  - Navegador visual de carpetas con ⬆️ (padre) y 📁 (subcarpetas)
  - Accesos rápidos a carpetas comunes (Inicio, Documentos, Escritorio)
  - Contador de palabras por archivo
  - Selección interactiva con checkboxes
  - Barra de progreso en tiempo real
  - Botón para abrir carpeta de resultados en explorador
  - Modo oscuro/claro con persistencia
  - Scripts de inicio: `start_web.sh` y `start_web.bat`

- **Procesamiento de carpetas (batch)**
  - Procesar múltiples archivos a la vez
  - Filtros por tipo de archivo (`*.odt`, `*.txt`)
  - Búsqueda recursiva en subcarpetas
  - Estadísticas completas del procesamiento
  - Genera subcarpeta `convertidos/` automáticamente

### Mejorado

- Botón "Abrir Carpeta" funciona en Windows, macOS y Linux
- Tema claro completamente legible (contraste corregido)
- Barra superior de Streamlit estilizada para ambos temas
- CSS mejorado para todos los elementos de la interfaz

---

## [1.3.1] - 2025-01-12

### Corregido

- Puntuación incorrecta después de signos de interrogación/exclamación
- Regla D5 (citas internas) ya no se aplica incorrectamente a diálogos consecutivos
- Diálogos consecutivos ahora se detectan correctamente

---

## [1.3.0] - 2025-01-12

### Añadido

- **Preservación completa de formato inline en archivos ODT**
  - Negrita, cursiva, subrayado se preservan automáticamente
  - Sistema de mapeo de formato palabra por palabra
  - Funciona con normalización (maneja cambios de mayúsculas/minúsculas)

---

## [1.2.1] - 2025-01-12

### Mejorado

- Preservación de estilos del documento ODT (styles.xml, settings.xml)
- Preservación de saltos de línea (line-breaks) entre diálogos
- 100% de line-breaks preservados

### Limitación

- Formato inline temporal en párrafos con line-breaks (resuelto en 1.3.0)

---

## [1.2.0] - 2025-01-12

### Añadido

- Preservación completa de estilos en archivos ODT
- Copia de todos los archivos del ODT original (17/17 archivos)
- Preservación de saltos de línea dentro de párrafos

---

## [1.1.0] - 2025-01-12

### Añadido

- **Soporte completo para archivos ODT** (OpenDocument Text)
- Lectura directa de archivos .odt sin dependencias externas
- Módulo `odt_handler.py` con clases ODTReader y ODTWriter
- 8 tests unitarios nuevos para funcionalidad ODT
- Documentación en `GUIA_ODT.md`

---

## [1.0.1] - 2025-01-12

### Corregido

- Continuación de diálogos del mismo personaje ahora usa rayas (—) en lugar de comillas latinas
- Detección inteligente de contexto: diferencia entre cita interna y continuación
- Nueva regla D4: Continuación de diálogo del mismo personaje

---

## [1.0.0] - 2025-01-12

### Versión Inicial

- Conversión completa de diálogos con comillas a formato español con raya (—)
- Sistema de logging detallado
- Soporte para comillas ASCII y tipográficas
- 42 verbos dicendi reconocidos
- 5 reglas de conversión implementadas (D1-D5)
- CLI completo con argparse
- 18 tests unitarios
- Sin dependencias externas
- Documentación completa

---

**Última actualización:** 2025-01-13  
**Versión actual:** 1.5.2
