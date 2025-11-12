# dialogos_a_español

Conversor de diálogos narrativos con comillas al formato editorial español con raya de diálogo (—).

**Versión actual:** 1.2.1

---

## 🎯 ¿Qué hace?

Convierte automáticamente diálogos con comillas (`"` `'`) al formato editorial español estándar con rayas de diálogo (—), siguiendo las reglas de la RAE y convenciones editoriales.

**Antes:**
```
"Hola" dijo Juan. "¿Cómo estás?"
```

**Después:**
```
—Hola —dijo Juan. —¿Cómo estás?
```

---

## ✨ Características

- ✅ **Soporte nativo para archivos ODT** (LibreOffice/OpenOffice Writer)
- ✅ **Soporte para archivos TXT** (texto plano)
- ✅ Procesamiento offline, sin internet
- ✅ Sin dependencias externas (solo Python estándar)
- ✅ Manejo de textos muy largos (novelas completas)
- ✅ Soporta comillas rectas ASCII (`"` `'`) y tipográficas (`"` `"` `'` `'`)
- ✅ Aplicación completa de reglas editoriales
- ✅ Log detallado de todos los cambios
- ✅ Preserva estructura y estilos del documento
- ✅ 26 tests automatizados (100% passing)

---

## 📋 Requisitos

- **Python 3.11+**
- Solo librerías estándar (incluidas con Python)

---

## 🚀 Instalación

```bash
git clone <repo-url>
cd dialogos_a_español
```

No se requiere instalación de dependencias adicionales.

---

## 💡 Uso

### Básico

```bash
# Archivo de texto
python -m src.main mi_capitulo.txt

# Archivo ODT (LibreOffice/Writer)
python -m src.main mi_capitulo.odt
```

### Opciones

```bash
# Especificar archivo de salida
python -m src.main input.txt -o salida.txt

# Modo silencioso (sin mensajes)
python -m src.main input.txt --quiet

# Ver versión
python -m src.main --version

# Ayuda
python -m src.main --help
```

### Archivos generados

Cada ejecución genera **dos archivos**:

1. **`{nombre}_convertido.txt`** (o `.odt`) - Texto convertido
2. **`{nombre}_convertido.log.txt`** - Log detallado con:
   - Ubicación de cada cambio
   - Texto original
   - Texto convertido
   - Regla aplicada

---

## 📝 Reglas de Conversión

El conversor implementa todas las reglas editoriales del español:

### D1: Sustitución de delimitadores

Convierte comillas a rayas de diálogo:

```
"Hola, Juan" → —Hola, Juan
```

Soporta:
- Comillas rectas: `"` `'` (ASCII)
- Comillas tipográficas: `"` `"` `'` `'` (Unicode)

### D2: Etiquetas de diálogo

Coloca etiquetas narrativas después de raya con minúscula:

```
"Hola" Dijo Juan → —Hola —dijo Juan
"¿Vienes?" preguntó Ana → —¿Vienes? —preguntó Ana
```

Reconoce **42 verbos dicendi**: dijo, preguntó, respondió, murmuró, gritó, etc.

### D3: Puntuación correcta

Maneja signos de interrogación y exclamación:

```
"¿Qué haces?" dijo → —¿Qué haces? —dijo
"¡Espera!" gritó → —¡Espera! —gritó
```

### D4: Continuación de diálogo

Detecta cuando el mismo personaje sigue hablando:

```
"Hola" dijo Juan. "¿Cómo estás?"
↓
—Hola —dijo Juan. —¿Cómo estás?
```

### D5: Citas internas

Usa comillas latinas para citas dentro de diálogos:

```
"Me dijo 'vendré' pero no vino"
↓
—Me dijo «vendré» pero no vino
```

---

## 📂 Trabajo con ODT (LibreOffice)

### Ventajas

✅ Trabaja directamente con tus documentos  
✅ Preserva toda la estructura del archivo original  
✅ Mantiene estilos del documento (títulos, párrafos, etc.)  
✅ Preserva saltos de línea entre diálogos  
✅ Resultado editable en LibreOffice/Word  

### Flujo de trabajo recomendado

1. **Escribe** en LibreOffice Writer (usa comillas normales)
2. **Guarda** tu documento (`.odt`)
3. **Convierte**: `python -m src.main capitulo_1.odt`
4. **Abre** `capitulo_1_convertido.odt` en LibreOffice
5. **Revisa** los cambios (consulta el `.log.txt` si es necesario)
6. **Continúa** editando normalmente

### ⚠️ Limitación actual (v1.2.1)

En párrafos con saltos de línea internos (line-breaks), se pierde el **formato inline** (negrita, cursiva, subrayado). Esto es una limitación técnica temporal.

**Lo que SÍ se preserva:**
- ✅ Estilos del documento completo
- ✅ Estructura de párrafos
- ✅ Saltos de línea
- ✅ Configuración del documento

**Lo que se pierde temporalmente:**
- ❌ Negrita/cursiva dentro de párrafos largos con line-breaks

**Solución:** Re-aplicar formato inline manualmente donde sea necesario (Ctrl+B para negrita, Ctrl+I para cursiva).

---

## 📊 Ejemplo Completo

### Entrada (`ejemplo.txt`):

```
"Hola, ¿cómo estás?" Preguntó María.

"Bien, gracias." Respondió Juan. "¿Y tú?"

"También bien" dijo María. "Me alegra verte."
```

### Salida (`ejemplo_convertido.txt`):

```
—Hola, ¿cómo estás? —preguntó María.

—Bien, gracias. —respondió Juan. —¿Y tú?

—También bien —dijo María. —Me alegra verte.
```

### Log generado:

```
CAMBIO #1
Ubicación: ~línea 1
Regla aplicada: D2: Etiqueta de diálogo

ORIGINAL:
  "Hola, ¿cómo estás?" Preguntó

CONVERTIDO:
  —Hola, ¿cómo estás? —preguntó
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m unittest discover tests -v

# Test específico
python -m unittest tests.test_converter -v

# Verificación completa del proyecto
./verify.sh
```

**Estado actual:** 26 tests, todos pasan ✅

---

## 📁 Estructura del Proyecto

```
dialogos_a_español/
├── src/
│   ├── __init__.py         # Versión del paquete
│   ├── main.py             # CLI principal
│   ├── converter.py        # Motor de conversión
│   ├── logger.py           # Sistema de logging
│   ├── rules.py            # Reglas de conversión
│   └── odt_handler.py      # Manejo de archivos ODT
├── tests/
│   ├── test_converter.py   # Tests de conversión
│   └── test_odt.py         # Tests de ODT
├── examples/
│   ├── ejemplo.txt         # Ejemplo básico
│   └── ejemplo_largo.txt   # Ejemplo complejo
├── README.md               # Este archivo
├── CHANGELOG.md            # Historial de versiones
├── LICENSE                 # Licencia MIT
└── verify.sh               # Script de verificación
```

---

## 🔧 Uso Programático

También puedes usar el conversor desde tu propio código Python:

```python
from pathlib import Path
from src.converter import DialogConverter

# Convertir texto
converter = DialogConverter()
texto_original = '"Hola" dijo Juan.'
texto_convertido, logger = converter.convert(texto_original)

print(texto_convertido)  # —Hola —dijo Juan.

# Ver estadísticas
stats = logger.get_stats()
print(f"Cambios: {stats['total_changes']}")

# Guardar log
logger.save_to_file(Path('conversion.log.txt'))
```

### Procesar ODT:

```python
from pathlib import Path
from src.odt_handler import ODTProcessor
from src.converter import DialogConverter

# Procesar y guardar ODT
processor = ODTProcessor(Path('entrada.odt'))
converter = DialogConverter()

processor.process_and_save(
    Path('salida.odt'),
    converter.convert
)
```

---

## ❓ Preguntas Frecuentes

### ¿Funciona con archivos de Word (.docx)?

No directamente. Word puede **exportar a ODT**: Archivo → Guardar como → OpenDocument Text (.odt).

Luego procesas el ODT y lo puedes abrir nuevamente en Word.

### ¿Puedo procesar varios archivos a la vez?

Sí, usando un script bash:

```bash
for file in capitulo_*.odt; do
    python -m src.main "$file" --quiet
done
```

### ¿Se puede deshacer la conversión?

No automáticamente, pero el archivo original nunca se modifica. Siempre se crea un archivo nuevo `_convertido`.

### ¿Qué pasa si el conversor se equivoca?

Revisa el archivo `.log.txt` para ver exactamente qué se cambió y dónde. Puedes editar manualmente los casos incorrectos en el archivo convertido.

### ¿Funciona con otros idiomas?

El conversor está optimizado para español, pero puede funcionar con cualquier texto que use comillas. Las etiquetas de diálogo están en español.

---

## 🐛 Problemas Conocidos

1. **Formato inline perdido en párrafos con line-breaks** (v1.2.1)
   - Se preserva estructura pero no negrita/cursiva en párrafos largos
   - Solución temporal: re-aplicar formato manualmente
   - Solución permanente: próxima versión

2. **Casos edge con puntuación compleja**
   - Algunos casos muy específicos pueden necesitar revisión manual
   - Siempre revisar el log para verificar cambios

---

## 🚀 Próximas Versiones

### v2.0 (Planificado)
- Preservación completa de formato inline (bold/italic)
- Soporte para más tipos de comillas
- Modo interactivo para revisar cambios antes de aplicarlos
- Exportación a otros formatos

---

## 🤝 Contribuir

Este es un proyecto funcional pero siempre mejorable. Si encuentras bugs o tienes sugerencias:

1. Prueba con un archivo pequeño primero
2. Revisa el `.log.txt` generado
3. Reporta casos problemáticos con ejemplos específicos

---

## 📄 Licencia

MIT License - Ver archivo `LICENSE` para detalles.

---

## 👤 Autor

Proyecto creado con GitHub Copilot CLI para facilitar la edición de textos narrativos en español.

---

## 📚 Recursos Adicionales

- **RAE**: Normas de puntuación en español
- **Fundéu**: Recomendaciones editoriales
- **LibreOffice**: Editor gratuito compatible con ODT

---

**¿Preguntas?** Revisa el `CHANGELOG.md` para ver el historial completo de cambios y mejoras.
