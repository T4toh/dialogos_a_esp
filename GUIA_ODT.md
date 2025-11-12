# Guía de Uso con Archivos ODT

## 📄 ¿Qué es ODT?

ODT (OpenDocument Text) es el formato estándar de documentos de texto de:
- **LibreOffice Writer**
- **OpenOffice Writer**
- **Google Docs** (puede exportar a ODT)
- **Microsoft Word** (puede abrir y guardar como ODT)

## ✨ Ventajas de Usar ODT

1. **Sin conversión manual** - Trabaja directamente con tus documentos
2. **Preserva el formato** - El resultado es también un ODT editable
3. **Flujo de trabajo natural** - Editas en tu procesador favorito
4. **Sin dependencias** - Solo usa librerías estándar de Python

## 🚀 Uso Básico

### Conversión Simple

```bash
# Tu archivo en LibreOffice/Writer
python -m src.main mi_novela.odt

# Genera automáticamente:
#   - mi_novela_convertido.odt
#   - mi_novela_convertido.log.txt
```

### Especificar Salida

```bash
python -m src.main borrador.odt -o novela_final.odt
```

## 📋 Flujo de Trabajo Recomendado

### 1. Escribir en tu Editor Favorito

Escribe tu texto en **LibreOffice Writer**, **Google Docs**, etc.
Usa comillas normales como escribes habitualmente:

```
"Hola" dijo Juan.
"¿Cómo estás?" preguntó María.
```

### 2. Guardar como ODT

- **LibreOffice**: Ya usa ODT por defecto
- **Google Docs**: Archivo → Descargar → OpenDocument (.odt)
- **Word**: Guardar como → Tipo: OpenDocument Text (.odt)

### 3. Convertir con el Script

```bash
python -m src.main mi_capitulo.odt
```

### 4. Abrir el Resultado

Abre `mi_capitulo_convertido.odt` en tu editor:

```
—Hola —dijo Juan.
—¿Cómo estás? —preguntó María.
```

### 5. Revisar y Continuar Editando

El archivo convertido es un **ODT normal**, puedes:
- ✅ Editarlo en LibreOffice/Word
- ✅ Aplicar estilos y formato
- ✅ Exportar a PDF
- ✅ Compartir con editores

## 📊 Comparación: TXT vs ODT

| Característica | TXT | ODT |
|---------------|-----|-----|
| Formato preservado | ❌ Solo texto plano | ✅ Mantiene formato |
| Editable en Word/Writer | ⚠️ Limitado | ✅ Totalmente |
| Estilos y fuentes | ❌ No | ✅ Sí |
| Fácil revisión | ⚠️ Básico | ✅ Completo |
| Exportar a PDF | ❌ Difícil | ✅ Directo |

## 🔧 Características Técnicas

### Lo que SE Preserva

✅ Contenido de texto  
✅ Párrafos  
✅ Saltos de línea  
✅ Caracteres especiales (ñ, á, —, « », etc.)

### Lo que NO se Preserva (por ahora)

❌ Formato de texto (negrita, cursiva, etc.)  
❌ Estilos personalizados  
❌ Imágenes  
❌ Tablas  

**Nota**: El conversor se enfoca en el **contenido textual**. Los estilos
se pueden aplicar después de la conversión en tu editor.

## 💡 Ejemplos de Uso

### Ejemplo 1: Novela Completa

```bash
# Tienes: novela_borrador.odt (escrito en LibreOffice)
python -m src.main novela_borrador.odt

# Resultado: novela_borrador_convertido.odt
# Listo para editar/publicar
```

### Ejemplo 2: Múltiples Capítulos

```bash
# Convertir todos los capítulos
for file in capitulo_*.odt; do
    python -m src.main "$file" -q
done

# Cada uno genera su _convertido.odt
```

### Ejemplo 3: Workflow con Google Docs

1. Escribes en **Google Docs**
2. Descargas como ODT
3. Conviertes con el script
4. Subes el convertido de vuelta a Google Docs
5. Continúas editando con el formato correcto

## 🐛 Solución de Problemas

### "El archivo no parece ser un ODT válido"

**Causa**: El archivo está corrupto o no es realmente ODT  
**Solución**: 
- Abre y guarda el archivo en LibreOffice
- Verifica que la extensión sea `.odt` (no `.doc` o `.docx`)

### "Faltan párrafos en el resultado"

**Causa**: Párrafos vacíos no se preservan  
**Solución**: 
- Es comportamiento normal en ODT
- Añade manualmente separadores si los necesitas

### "Las comillas no se convirtieron"

**Causa**: Pueden ser caracteres especiales no soportados  
**Solución**:
- Revisa el archivo `.log.txt` para ver qué se detectó
- El conversor soporta: " " ' ' " ' (ASCII y tipográficas)

## 📝 Notas Importantes

### LibreOffice vs Word

- **LibreOffice**: Soporte nativo completo de ODT ✅
- **Word**: Soporte básico de ODT (puede perder algo de formato) ⚠️

**Recomendación**: Usa LibreOffice para mejor compatibilidad.

### Codificación

Todos los archivos ODT usan **UTF-8** internamente, así que:
- ✅ Soporta todos los idiomas
- ✅ Caracteres especiales sin problemas
- ✅ Emojis (aunque no son comunes en narrativa)

### Tamaño de Archivos

Los archivos ODT convertidos pueden ser:
- Ligeramente más grandes (por el formato XML)
- Pero siguen siendo pequeños (compresión ZIP interna)

Un documento de 100 páginas típicamente ocupa menos de 100KB.

## 🎯 Mejores Prácticas

### 1. Haz Backup

Siempre guarda una copia de tu original:
```bash
cp mi_novela.odt mi_novela_backup.odt
python -m src.main mi_novela.odt
```

### 2. Revisa el Log

El archivo `.log.txt` te muestra **cada cambio**:
```
CAMBIO #1
Ubicación: ~línea 15
Regla aplicada: D2: Etiqueta de diálogo

ORIGINAL:
  "Hola" dijo Juan

CONVERTIDO:
  —Hola —dijo Juan
```

### 3. Proceso Iterativo

1. Convierte un capítulo
2. Revisa el resultado
3. Ajusta tu escritura si es necesario
4. Convierte el resto

### 4. Usa Control de Versiones

```bash
# Mantén versiones
mi_novela_v1.odt
mi_novela_v1_convertido.odt
mi_novela_v2.odt
mi_novela_v2_convertido.odt
```

## 🚀 Flujo de Trabajo Profesional

```
┌─────────────────┐
│ Escribir en     │
│ LibreOffice     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Guardar como    │
│ capitulo_1.odt  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Convertir:      │
│ python -m ...   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Revisar log     │
│ y resultado     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Editar en       │
│ LibreOffice     │
│ (aplicar estilos)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Exportar a PDF  │
│ para publicar   │
└─────────────────┘
```

## ✅ Checklist Pre-Conversión

Antes de convertir un documento ODT grande:

- [ ] Hice backup del original
- [ ] Probé con un capítulo pequeño primero
- [ ] Revisé que el archivo abre correctamente en LibreOffice
- [ ] Sé dónde encontrar los archivos convertidos
- [ ] Tengo espacio en disco para los resultados

## 🆘 Ayuda Rápida

```bash
# Ver si el archivo es ODT válido
python3 -c "from src.odt_handler import is_odt_file; from pathlib import Path; print(is_odt_file(Path('archivo.odt')))"

# Extraer texto de un ODT (sin convertir)
python3 -c "from src.odt_handler import ODTReader; from pathlib import Path; print(ODTReader(Path('archivo.odt')).extract_text())"

# Ver versión del conversor
python -m src.main --version
```

## 📚 Recursos Adicionales

- **README.md** - Información general del proyecto
- **GUIA_USO.md** - Guía completa de uso con ejemplos
- **CHANGELOG.md** - Historial de versiones

---

**¿Tienes un problema?** Revisa el archivo `.log.txt` generado, contiene información
detallada de cada cambio realizado.

**¿Encontraste un caso que no se maneja bien?** Añade un ejemplo en los issues del proyecto.
