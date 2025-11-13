# Changelog

Historial de cambios del proyecto.

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
**Versión actual:** 1.4.0
