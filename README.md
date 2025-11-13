# Conversor de Diálogos a Español

Convierte diálogos con comillas al formato editorial español con raya (—).

**Versión:** 1.4.0

---

## ¿Qué hace?

**Antes:**
```
"Hola" dijo Juan. "¿Cómo estás?"
```

**Después:**
```
—Hola —dijo Juan. —¿Cómo estás?
```

---

## Características

- ✅ Interfaz web visual (Streamlit)
- ✅ Línea de comandos (CLI)
- ✅ Soporte para archivos ODT y TXT
- ✅ Procesamiento de carpetas completas
- ✅ Preserva formato de documentos ODT
- ✅ Modo oscuro/claro

---

## Instalación

```bash
git clone <repo-url>
cd dialogos_a_español
```

### Para usar la interfaz web:

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
- Contador de palabras
- Selección de archivos con checkboxes
- Barra de progreso
- Abrir carpeta de resultados
- Modo oscuro/claro

**Pasos:**
1. Selecciona una carpeta (selector visual o escribir ruta)
2. Haz clic en "🔍 Escanear"
3. Selecciona los archivos que quieres procesar
4. Configura carpeta de salida (opcional)
5. Haz clic en "▶️ Iniciar Conversión"
6. Abre la carpeta de resultados con el botón

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
2. **`archivo_convertido.log.txt`** - Log detallado con todos los cambios

---

## Reglas de Conversión

El conversor aplica las reglas editoriales del español:

- **D1**: Sustitución de comillas → `"Hola"` → `—Hola`
- **D2**: Etiquetas de diálogo → `"Hola" dijo` → `—Hola —dijo`
- **D3**: Puntuación correcta → `"¿Hola?" preguntó` → `—¿Hola? —preguntó`
- **D4**: Continuación de diálogo → Detecta mismo personaje
- **D5**: Citas internas → Usa comillas latinas `« »`

Soporta:
- Comillas rectas: `"` `'`
- Comillas tipográficas: `"` `"` `'` `'`
- 42 verbos dicendi reconocidos

---

## Requisitos

- Python 3.11+
- Streamlit (solo para interfaz web)

---

## Tests

```bash
python -m unittest discover tests -v
```

26 tests - 100% passing ✅

---

## Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## Versión

**1.4.0** - Interfaz web, procesamiento batch, modo oscuro/claro

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo de cambios.
