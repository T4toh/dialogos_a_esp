# dialogos_a_español

Conversor de diálogos narrativos con comillas al formato editorial español con raya de diálogo (—).

## Características

- ✅ Procesamiento offline, sin dependencias externas
- ✅ Manejo de textos muy largos
- ✅ **Soporte nativo para archivos ODT** (OpenDocument Text)
- ✅ Conversión automática de comillas (" ", ' ') a rayas de diálogo (—)
- ✅ Soporte para comillas rectas ASCII (" ') y tipográficas (" " ' ')
- ✅ Aplicación completa de reglas editoriales en español
- ✅ Generación de log detallado con cada cambio realizado
- ✅ Preservación del texto original (solo cambios necesarios)

## Requisitos

- Python 3.11+
- Solo librerías estándar (sin dependencias externas)

## Instalación

```bash
git clone <repo-url>
cd dialogos_a_español
```

## Uso

```bash
# Convertir un archivo de texto
python -m src.main input.txt

# Convertir un archivo ODT (LibreOffice/OpenOffice)
python -m src.main mi_documento.odt

# Especificar archivo de salida
python -m src.main input.txt -o output.txt

# Ver ayuda
python -m src.main --help
```

## Archivos generados

- `{nombre}_convertido.txt` o `.odt`: Texto con diálogos convertidos
- `{nombre}_convertido.log.txt`: Log detallado de cambios

## Reglas aplicadas

El conversor implementa el protocolo completo de conversión:

### D1: Sustitución de delimitadores
- Comillas dobles/simples → raya de diálogo (—)
- Soporta comillas rectas: `"` `'`
- Soporta comillas tipográficas: `"` `"` `'` `'`
- `"Hola, Juan"` → `—Hola, Juan`

### D2: Etiquetas de diálogo
- `"Te dije que no" Dijo Pedro.` → `—Te dije que no —dijo Pedro.`

### D3: Puntuación
- `"¿Qué haces?" dijo Marta.` → `—¿Qué haces? —dijo Marta.`

### D4: Múltiples intervenciones
- Cada personaje inicia con nueva raya
- **Continuación del mismo personaje**: usa raya (—)
  - `"Hola" dijo Juan. "¿Cómo estás?"` → `—Hola —dijo Juan. —¿Cómo estás?`

### D5: Casos especiales
- Citas dentro de diálogos usan comillas latinas (« »)
  - `"Dijo 'hola'"` → `—Dijo «hola»`
- Distingue entre cita interna y continuación de diálogo

## Estructura del proyecto

```
dialogos_a_español/
├── src/
│   ├── __init__.py
│   ├── main.py           # CLI principal
│   ├── converter.py      # Lógica de conversión
│   ├── logger.py         # Sistema de logging
│   └── rules.py          # Definición de reglas
├── tests/
│   └── test_converter.py
├── examples/
│   └── ejemplo.txt
└── README.md
```

## Licencia

MIT
