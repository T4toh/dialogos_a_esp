# Conversor de Diálogos a Español

Como escritor, escribo mis manuscritos (los que están en español) de la manera más cómoda posible y después paso todo a formato estándar español. Suelo usar un prompt pulido para un LLM, pero el resultado usualmente termina plachando (palabras perdidas, cambio de diálogos, cambio de voces, 'vos' pasados a 'ti', etc.). Así que pensé que esto debería poder hacerse de manera programática, cosa que ya existe en internet, pero a mí me gusta invocar a Bender y hacer mi propio script con juego de azar y mujerzuelas. Con esto en mente, escribí (con Claudio) este script.

**Versión:** 2.1.0

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

- ✅ **Interfaz gráfica nativa (Tkinter)** - Sin navegador, sin dependencias
- ✅ Línea de comandos (CLI)
- ✅ Soporte para archivos ODT y TXT
- ✅ Procesamiento por lotes de carpetas completas
- ✅ Preserva formato de documentos ODT (estilos, metadatos)
- ✅ Logs detallados con estadísticas (incluye exportación JSON con offsets y metadatos)
- ✅ **Selección de archivos nativa del sistema operativo**
- ✅ **Sin dependencias externas** (solo Python stdlib)
- ✅ **Distribución como AppImage** con actualizaciones automáticas

---

## Instalación

### 📦 AppImage — Linux (Recomendado)

Descarga el AppImage desde [GitHub Releases](https://github.com/T4toh/dialogos_a_esp/releases/latest), dale permisos y ejecútalo. No requiere instalar nada.

```bash
chmod +x Conversor-Dialogos-*.AppImage
./Conversor-Dialogos-*.AppImage
```

La app avisa automáticamente al arrancar cuando hay una nueva versión disponible.

#### Actualizaciones automáticas

La app usa [AppImageUpdate](https://github.com/AppImage/AppImageUpdate/releases/latest) para descargar solo los bloques que cambiaron (vía zsync), sin re-descargar todo el archivo.

1. Descarga `AppImageUpdate` y colócalo en `$PATH` o en la misma carpeta que el AppImage
2. Al iniciar la app, si hay una nueva versión aparece un banner verde con el botón **"Actualizar ahora"**
3. La actualización se aplica en segundo plano sin cerrar la app

Para actualizar manualmente desde terminal:

```bash
AppImageUpdate Conversor-Dialogos-*.AppImage
```

### 🐍 Desde el código fuente

```bash
git clone https://github.com/T4toh/dialogos_a_esp.git
cd dialogos_a_esp
```

**No requiere dependencias** - Solo Python 3.11+

---

## Uso

### 🖥️ Interfaz Gráfica

```bash
python gui.py
```

**Características:**

- ✨ Interfaz nativa del sistema operativo
- 📁 Selección de archivos/carpetas con diálogos nativos
- 📊 Tabla de archivos con información detallada
- ⚡ Barra de progreso en tiempo real
- 📈 Ventana de resultados con estadísticas
- 🚀 Sin navegador, sin latencia, sin dependencias

**Pasos:**

1. Ejecuta `python gui.py` (o `./start_gui.sh`)
2. Haz clic en "📁 Seleccionar Archivos" o "📂 Seleccionar Carpeta"
3. (Opcional) Cambia la carpeta de salida
4. Haz clic en "▶ Procesar Archivos"
5. Revisa el resumen de resultados
6. Abre la carpeta de salida desde la ventana de resultados

**💡 Tip:** Usa los archivos ODT en `examples/` para probar el conversor con casos reales que incluyen estilos y formato complejo.

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

---

## Testing

Usa los archivos de prueba que prefieras. El conversor genera logs detallados para cada conversión que muestran:

- Todos los cambios realizados línea por línea
- Regla aplicada (D1-D5)
- Texto original vs convertido
- Estadísticas de cambios

**Recomendación:** Prueba con tus propios archivos para validar el comportamiento en casos reales.

---

## Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## Versión

**2.1.0** - Eliminación de interfaz web (Streamlit). Enfoque en GUI nativa (Tkinter) y CLI.

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo de cambios.