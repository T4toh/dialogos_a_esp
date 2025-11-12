# Características Técnicas - dialogos_a_español

## Arquitectura del Proyecto

### Módulos Principales

#### 1. `src/main.py` - CLI Principal
- **Responsabilidad**: Interfaz de línea de comandos
- **Componentes**:
  - ArgumentParser para manejo de argumentos
  - Validación de archivos de entrada/salida
  - Coordinación del flujo principal
- **Dependencias**: argparse, pathlib, sys

#### 2. `src/converter.py` - Motor de Conversión
- **Responsabilidad**: Lógica de conversión de diálogos
- **Clase principal**: `DialogConverter`
- **Métodos clave**:
  - `convert()`: Conversión completa de texto
  - `_convert_line()`: Procesamiento línea por línea
  - `_convert_dialog_with_tag()`: Regla D2
  - `_convert_standalone_dialog()`: Regla D1
  - `_convert_nested_quotes()`: Regla D5
- **Dependencias**: re, typing

#### 3. `src/logger.py` - Sistema de Logging
- **Responsabilidad**: Registro detallado de cambios
- **Clase principal**: `ConversionLogger`
- **Métodos clave**:
  - `log_change()`: Registra un cambio
  - `generate_report()`: Genera reporte formateado
  - `save_to_file()`: Guarda log en archivo
  - `get_stats()`: Estadísticas de conversión
- **Dependencias**: typing, pathlib, io

#### 4. `src/rules.py` - Definición de Reglas
- **Responsabilidad**: Patrones y reglas de conversión
- **Componentes**:
  - `DIALOG_TAGS`: Lista de etiquetas de diálogo
  - `Patterns`: Expresiones regulares compiladas
  - Funciones auxiliares para detección
- **Dependencias**: re, typing

## Patrones de Diseño Utilizados

### 1. Single Responsibility Principle (SRP)
Cada módulo tiene una responsabilidad clara y única:
- `main.py`: CLI
- `converter.py`: Conversión
- `logger.py`: Logging
- `rules.py`: Reglas

### 2. Strategy Pattern
Las diferentes estrategias de conversión (D1-D5) se aplican secuencialmente según el contexto.

### 3. Template Method Pattern
El método `convert()` define el flujo general, delegando detalles a métodos específicos.

## Expresiones Regulares Utilizadas

### Patrón 1: Diálogos con Etiqueta
```python
r'"([^"]+)"\s+(' + '|'.join(DIALOG_TAGS) + r')\b'
```
Captura: `"texto" verbo`

### Patrón 2: Diálogos con Puntuación y Etiqueta
```python
r'"([^"]+)"([,.\s]+)([A-ZÁÉÍÓÚÑ][a-záéíóúñ]*)\b'
```
Captura: `"texto", Palabra` o `"texto." Palabra`

### Patrón 3: Diálogos Standalone
```python
r'^(\s*)"([^"]+)"'
```
Captura: `"texto"` al inicio de línea

### Patrón 4: Citas Internas
```python
r"'([^']+)'"
```
Captura: `'texto'` dentro de un diálogo ya convertido

## Flujo de Procesamiento

```
┌─────────────────┐
│  Archivo Input  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Leer UTF-8    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Split por \n   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Para cada línea:       │
│  1. Verificar vacía     │
│  2. Aplicar D2          │
│  3. Aplicar D1          │
│  4. Aplicar D5          │
│  5. Registrar cambios   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│   Join con \n   │
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│  Guardar archivos:   │
│  - texto_conv.txt    │
│  - texto_conv.log.txt│
└──────────────────────┘
```

## Manejo de Casos Especiales

### 1. Mayúsculas en Etiquetas
```python
if is_dialog_tag(word):
    result = f'{EM_DASH}{content} {EM_DASH}{word.lower()}'
```

### 2. Puntuación al Final del Diálogo
```python
if content.endswith(('?', '!', '.')):
    result = f'{EM_DASH}{content} {EM_DASH}{tag.lower()}'
elif content.endswith(','):
    content_clean = content.rstrip(',').strip()
    result = f'{EM_DASH}{content_clean} {EM_DASH}{tag.lower()}'
```

### 3. Citas Internas
Solo se convierten si la línea ya tiene raya de diálogo:
```python
if EM_DASH not in line:
    return line
```

## Optimizaciones

### 1. Compilación de Regex
Las expresiones regulares se compilan una sola vez en `rules.py`.

### 2. Procesamiento Línea por Línea
Evita cargar todo el texto en memoria para análisis complejos.

### 3. Detección Temprana de Cambios
```python
if original != line:
    return result
```

### 4. UTF-8 Nativo
Uso de encoding UTF-8 en todas las operaciones de I/O.

## Rendimiento

### Complejidad Temporal
- **Por línea**: O(n * m) donde n = longitud de línea, m = número de patrones
- **Total**: O(L * n * m) donde L = número de líneas

### Complejidad Espacial
- **Almacenamiento**: O(L) para líneas convertidas
- **Logger**: O(C) donde C = número de cambios
- **Total**: O(L + C)

### Benchmarks Aproximados
- **Archivo pequeño** (< 1 KB): ~0.001s
- **Archivo mediano** (~10 KB): ~0.01s
- **Archivo grande** (~1 MB): ~1s
- **Archivo muy grande** (~10 MB): ~10s

## Extensibilidad

### Añadir Nuevas Etiquetas
Editar `src/rules.py`:
```python
DIALOG_TAGS = [
    'dijo', 'preguntó',
    'tu_nueva_etiqueta',  # ← Añadir aquí
]
```

### Añadir Nuevas Reglas
En `src/converter.py`:
```python
def _convert_my_rule(self, line: str, original: str) -> str:
    # Tu lógica aquí
    pass

# Y llamarla en _convert_line():
line = self._convert_my_rule(line, original_line)
```

### Personalizar el Log
Editar `src/logger.py`, método `generate_report()`:
```python
buffer.write("MI FORMATO PERSONALIZADO\n")
```

## Testing

### Cobertura de Tests
- ✓ Conversión básica (comillas dobles/simples)
- ✓ Etiquetas de diálogo
- ✓ Puntuación (?, !, .)
- ✓ Comas antes de etiquetas
- ✓ Narración después de diálogo
- ✓ Citas internas
- ✓ Múltiples líneas
- ✓ Mezcla de comillas
- ✓ Logging de cambios

### Ejecutar Tests
```bash
python -m unittest tests.test_converter -v
```

## Limitaciones Técnicas

### 1. Análisis de Contexto
El conversor analiza línea por línea, sin contexto entre líneas.

### 2. Etiquetas Predefinidas
Solo reconoce etiquetas en `DIALOG_TAGS`. Verbos no listados requieren adición manual.

### 3. Diálogos Complejos
Diálogos con estructura narrativa compleja pueden requerir revisión manual.

### 4. Encoding
Asume UTF-8. Archivos en otros encodings deben convertirse previamente.

## Seguridad

### 1. No Hay Ejecución de Código
Solo procesamiento de texto, sin eval() ni exec().

### 2. Validación de Entrada
Verificación de existencia de archivos antes de procesar.

### 3. Manejo de Excepciones
Try-except en puntos críticos con mensajes claros.

### 4. Sin Conexiones Externas
Operación completamente offline.

## Mantenimiento

### Actualizar Dependencias
No aplica - solo usa librerías estándar.

### Agregar Tests
Crear nuevos métodos en `tests/test_converter.py`:
```python
def test_mi_caso(self):
    input_text = "..."
    expected = "..."
    result, _ = self.converter.convert(input_text)
    self.assertEqual(result, expected)
```

## Licencia
MIT - Ver archivo `LICENSE` para detalles completos.
