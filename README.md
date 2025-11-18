# Conversor de Diálogos a Español

Como escritor, escribo mis manuscritos (los que están en español) de la manera más cómoda posible y después paso todo a formato estándar español. Suelo usar un prompt pulido para un LLM, pero el resultado usualmente termina plachando (palabras perdidas, cambio de diálogos, cambio de voces, 'vos' pasados a 'ti', etc.). Así que pensé que esto debería poder hacerse de manera programática, cosa que ya existe en internet, pero a mí me gusta invocar a Bender y hacer mi propio script con juego de azar y mujerzuelas. Con esto en mente, escribí (con Claudio) este script. Yo estoy cómodo con la consola, pero agregué un Streamlit muy básico que usa el script para hacer los trabajos de manera más visual. En el front tiene un par de defectos, pero hace su trabajo. Por ejemplo, el explorador de carpetas deja mucho que desear.

**Versión:** 1.6.2

---

## ¿Qué hace?

**Antes:**

```text
"Hola" dijo Juan. "¿Cómo estás?"
```

**Después:**

```text
—Hola —dijo Juan. —¿Cómo estás?
```

---

## Características

- ✅ Interfaz web visual con explorador de logs
- ✅ Línea de comandos (CLI)
- ✅ Soporte para archivos ODT y TXT
- ✅ Procesamiento por lotes de carpetas completas
- ✅ Preserva formato de documentos ODT (estilos, metadatos)
- ✅ Logs detallados con estadísticas (incluye exportación JSON con offsets y metadatos)
- ✅ Modo oscuro/claro persistente
- ✅ Sin dependencias externas (solo stdlib + Streamlit para web)

---

## Instalación

```bash
git clone <repo-url>
cd dialogos_a_español
```

### Para usar la interfaz web

```bash
# Instalar Streamlit
pip install streamlit

# O con el script (instala automáticamente)
./start_web.sh
```

---

## Uso

### 🖥️ Interfaz Web (Recomendado)

```bash
./start_web.sh
```

Se abre en tu navegador: `http://localhost:8501`

**Características:**

- Navegador visual de carpetas
- Contador de palabras por archivo
- Selección múltiple con checkboxes
- Barra de progreso en tiempo real
- **📄 Visualizador de logs**: Explora todos los cambios realizados - El visor prefiere logs JSON estructurados cuando están disponibles y muestra la fuente del span para inspección rápida.
- **📊 Estadísticas**: Conteo de reglas aplicadas
- Descarga logs individuales
- Modo oscuro/claro persistente

**Pasos:**

1. Selecciona una carpeta (selector visual o escribir ruta)
2. Haz clic en "🔍 Escanear"
3. Selecciona los archivos que quieres procesar
4. Configura carpeta de salida (opcional)
5. Haz clic en "▶️ Iniciar Conversión"
6. **Explora los cambios**: Visualizador integrado de logs con cada cambio detallado
7. Descarga logs individuales o copia la ruta de salida

---

### 💻 Línea de Comandos

#### Archivo individual

```bash
# Archivo de texto
python -m src.main mi_archivo.txt

# Archivo ODT
python -m src.main mi_archivo.odt
```

#### Carpeta completa

```bash
# Procesar todos los archivos
python -m src.main mi_carpeta/

# Solo archivos ODT
python -m src.main mi_carpeta/ --filter "*.odt"

# Incluir subcarpetas
python -m src.main mi_carpeta/ --recursive

# Especificar carpeta de salida
python -m src.main mi_carpeta/ -o resultados/
```

#### Opciones

```bash
-o, --output PATH    # Archivo/carpeta de salida
--filter PATTERN     # Patrón de archivos (ej: "*.odt")
--recursive          # Incluir subcarpetas
-q, --quiet          # Modo silencioso
--version            # Ver versión
--help               # Ayuda
```

---

## Archivos Generados

Cada conversión genera **dos archivos**:

1. **`archivo_convertido.txt`** (o `.odt`) - Texto convertido
2. **`archivo_convertido.log.txt`** - Log detallado con:

   - Total de cambios realizados
   - Línea aproximada de cada cambio
   - Regla aplicada (D1, D2, D3, D4, D5)
   - Texto original y convertido lado a lado

3. **`archivo_convertido.log.json`** - Log estructurado (opcional). Contiene:
   - `original` / `converted`: bloque completo
   - `original_fragment` / `converted_fragment`: fragmento asociado
   - `original_span` / `converted_span`: offsets en el bloque
   - `original_span_source` / `converted_span_source`: cómo se encontró el span (`exact`, `fuzzy`, `raw`, `full_text`, `full_converted`, `normalized`)

Nota: si el JSON está presente, el visor de Streamlit lo usará para resaltado 1:1; si no, se ejecutará el fallback de diffs por palabras.

**Tip:** La interfaz web muestra estos logs de forma visual con búsqueda y filtros.

---

## Reglas de Conversión

El conversor aplica las reglas editoriales del español según la **Real Academia Española (RAE)**:

**📖 Referencia oficial:** [RAE - Uso de la raya en diálogos](https://www.rae.es/dpd/raya)

### Reglas implementadas

- **D1**: Sustitución de comillas → `"Hola"` → `—Hola`
- **D2**: Etiquetas de diálogo → `"Hola" dijo` → `—Hola —dijo`
- **D3**: Narración después de diálogo → `"Está bien." Cerró la puerta` → `—Está bien. —Cerró la puerta`
- **D4**: Continuación de diálogo → Detecta mismo personaje
- **D5**: Citas internas → Usa comillas latinas `« »`

### Ejemplos según RAE

- `"¡Qué le vamos a hacer!" exclamó` → `—¡Qué le vamos a hacer! —exclamó`
- `"Cortesía." dijo` → `—Cortesía. —dijo`
- `"Es una demo." El hombre agregó. "¿Y ahora?"` → `—Es una demo. —El hombre agregó. —¿Y ahora?`

### Soporta

- Comillas rectas: `"` `'`
- Comillas tipográficas: `"` `"` `'` `'`
- 42 verbos dicendi reconocidos

---

## Requisitos

- Python 3.11+
- Streamlit (solo para interfaz web)

---

## Tests

Para ejecutar todos los tests y una comprobación rápida de estilo (ruff) hemos añadido un script práctico en la raíz del proyecto.

```bash
./run_all_tests.sh
```

Este script ejecuta un `ruff check` rápido si `ruff` está instalado y luego ejecuta
`python -m unittest discover tests -v`.

Última ejecución conocida: 29 tests (1 skip) ✅

Nuevas pruebas: se añadió test para suprimir D1-no-op (`tests/test_converter.py::test_noop_d1_diálogo_adicional_suppressed`) y se integraron tests para la búsqueda de spans en la línea convertida `post_process_line_spans`.

---

## Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## Versión

**1.6.2** - Mejoras en detectado y logging de spans, supresión de D1 no-op

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo de cambios.

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo de cambios.
