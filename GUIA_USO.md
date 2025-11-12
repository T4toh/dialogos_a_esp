# Guía de Uso - dialogos_a_español

## Inicio Rápido

### 1. Instalación
No requiere instalación de dependencias. Solo necesitas Python 3.11+.

```bash
cd dialogos_a_español
```

### 2. Uso básico desde línea de comandos

```bash
# Sintaxis básica
python -m src.main archivo_entrada.txt

# El comando anterior genera:
#   - archivo_entrada_convertido.txt
#   - archivo_entrada_convertido.log.txt
```

### 3. Especificar archivo de salida

```bash
python -m src.main input.txt -o mi_salida.txt

# Genera:
#   - mi_salida.txt
#   - mi_salida.log.txt
```

### 4. Modo silencioso (sin estadísticas)

```bash
python -m src.main input.txt --quiet
# o
python -m src.main input.txt -q
```

## Uso Programático

También puedes usar el conversor directamente en tu código Python:

```python
from pathlib import Path
from src.converter import DialogConverter

# Leer texto
texto = Path("mi_archivo.txt").read_text(encoding='utf-8')

# Crear conversor y procesar
converter = DialogConverter()
texto_convertido, logger = converter.convert(texto)

# Guardar resultados
Path("salida.txt").write_text(texto_convertido, encoding='utf-8')
logger.save_to_file(Path("salida.log.txt"))

# Ver estadísticas
stats = logger.get_stats()
print(f"Cambios realizados: {stats['total_changes']}")
```

## Ejemplos de Conversión

### Ejemplo 1: Diálogo simple

**Entrada:**
```
"Hola, Juan"
```

**Salida:**
```
—Hola, Juan
```

### Ejemplo 2: Diálogo con etiqueta

**Entrada:**
```
"Hola" dijo María.
```

**Salida:**
```
—Hola —dijo María.
```

### Ejemplo 3: Diálogo con pregunta

**Entrada:**
```
"¿Cómo estás?" preguntó Juan.
```

**Salida:**
```
—¿Cómo estás? —preguntó Juan.
```

### Ejemplo 4: Diálogo con coma

**Entrada:**
```
"No puedo creerlo," dijo Ana.
```

**Salida:**
```
—No puedo creerlo —dijo Ana.
```

### Ejemplo 5: Diálogo seguido de narración

**Entrada:**
```
"Está bien." Cerró la puerta.
```

**Salida:**
```
—Está bien. Cerró la puerta.
```

### Ejemplo 6: Citas internas

**Entrada:**
```
"Ella me dijo 'te esperaré' pero no vino"
```

**Salida:**
```
—Ella me dijo «te esperaré» pero no vino
```

### Ejemplo 7: Múltiples diálogos

**Entrada:**
```
"Hola" dijo Juan.
"Adiós" respondió María.
```

**Salida:**
```
—Hola —dijo Juan.
—Adiós —respondió María.
```

## Formato del Log

El archivo `.log.txt` generado contiene:

```
================================================================================
LOG DE CONVERSIÓN DE DIÁLOGOS A FORMATO ESPAÑOL
================================================================================

Total de cambios realizados: 15

--------------------------------------------------------------------------------

CAMBIO #1
Ubicación: ~línea 3
Regla aplicada: D2: Etiqueta de diálogo

ORIGINAL:
  "Hola, María" dijo

CONVERTIDO:
  —Hola, María —dijo

--------------------------------------------------------------------------------
```

## Reglas Aplicadas

El conversor implementa estas categorías de reglas:

- **D1**: Sustitución de delimitadores (comillas → rayas)
- **D2**: Etiquetas de diálogo (con minúscula)
- **D3**: Puntuación en diálogos
- **D4**: Múltiples intervenciones
- **D5**: Casos especiales (citas internas)

## Consejos

1. **Textos largos**: El conversor procesa archivos de cualquier tamaño sin problemas.

2. **Backup**: El archivo original nunca se modifica. Siempre se crea un archivo nuevo.

3. **Revisión**: Revisa el archivo `.log.txt` para ver todos los cambios realizados.

4. **Encoding**: Todos los archivos se procesan con UTF-8 para soportar caracteres especiales.

5. **Offline**: No requiere conexión a internet ni servicios externos.

## Pruebas

Ejecuta los tests para verificar que todo funciona:

```bash
python -m unittest tests.test_converter -v
```

## Probando con los Ejemplos Incluidos

```bash
# Ejemplo corto
python -m src.main examples/ejemplo.txt

# Ejemplo largo
python -m src.main examples/ejemplo_largo.txt

# Uso programático
python examples/uso_programatico.py
```

## Solución de Problemas

### Error: "El archivo no existe"
Verifica que la ruta del archivo sea correcta.

```bash
# Usa rutas absolutas o relativas correctas
python -m src.main /ruta/completa/archivo.txt
```

### Error: "UnicodeDecodeError"
El archivo debe estar en UTF-8. Conviértelo:

```bash
iconv -f ISO-8859-1 -t UTF-8 archivo.txt > archivo_utf8.txt
python -m src.main archivo_utf8.txt
```

### Los cambios no son los esperados
Revisa el archivo `.log.txt` para ver exactamente qué reglas se aplicaron y por qué.

## Limitaciones Conocidas

1. **Contexto limitado**: El conversor analiza línea por línea, por lo que puede no detectar contextos narrativos muy complejos.

2. **Etiquetas personalizadas**: Solo reconoce las etiquetas de diálogo más comunes (dijo, preguntó, etc.). Si usas verbos muy específicos, pueden no ser reconocidos.

3. **Diálogos multi-párrafo**: Diálogos que abarcan múltiples párrafos pueden requerir revisión manual.

## Personalización

Si necesitas añadir más etiquetas de diálogo, edita `src/rules.py`:

```python
DIALOG_TAGS = [
    'dijo', 'dice', 'preguntó', 'pregunta',
    # Añade tus etiquetas aquí:
    'susurró', 'gritó', 'chilló', ...
]
```

## Más Información

- Consulta el `README.md` para información general
- Revisa `tests/test_converter.py` para ver ejemplos de uso
- Lee el código fuente en `src/` para entender el funcionamiento interno
