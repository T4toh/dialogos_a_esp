# Uso de la Raya en Diálogos - RAE

## Fuente

**Diccionario panhispánico de dudas (DPD)** - Real Academia Española
URL: [https://www.rae.es/dpd/raya](https://www.rae.es/dpd/raya)
Consulta: 14 de noviembre de 2025

---

## Definición

La raya (―) es un signo de puntuación representado por un trazo horizontal de mayor longitud que el guion (-) y el signo menos (−).

---

## Usos en Textos Narrativos (2.3)

La raya se utiliza para introducir o enmarcar los comentarios y precisiones del narrador a las intervenciones de los personajes.

### Regla 2.3.a: Sin continuación del diálogo

No se escribe raya de cierre si tras el comentario del narrador no sigue hablando inmediatamente el personaje:

```text
—Espero que todo salga bien ―dijo Azucena con gesto ilusionado.
A la mañana siguiente, Azucena se levantó nerviosa.
```

### Regla 2.3.b: Con continuación del diálogo

Se escriben dos rayas cuando las palabras del narrador interrumpen la intervención del personaje y esta continúa inmediatamente después:

```text
—Lo principal es sentirse viva ―añadió Pilar―. Afortunada o desafortunada, pero viva.
```

### Regla 2.3.c: Verbos de lengua

Cuando el comentario va introducido por un verbo de lengua (decir, añadir, asegurar, preguntar, exclamar, reponer, etc.), su intervención se inicia en minúscula:

```text
―¡Qué le vamos a hacer! ―exclamó resignada doña Patro.
```

Si la intervención continúa tras las palabras del narrador, los signos de puntuación se colocan tras la raya que cierra el inciso:

```text
―Está bien ―dijo Carlos―; lo haré, pero que sea la última vez que me lo pides.
```

### Regla 2.3.d: Sin verbo de lengua

Cuando el comentario del narrador no se introduce con un verbo de lengua y el parlamento precedente constituye un enunciado completo, las palabras del personaje deben cerrarse con punto y el inciso del narrador debe iniciarse con mayúscula:

```text
―No se moleste. ―Cerró la puerta y salió de mala gana.
```

Si tras el comentario continúa el parlamento, la raya de cierre va seguida de punto:

```text
―Me voy ya. ―Se puso en pie con gesto decidido―. No hace falta que me acompañe. Conozco el camino.
```

### Regla 2.3.e: Inciso en mitad de enunciado

Si el comentario se intercala en mitad de un enunciado, el texto del inciso se inicia con minúscula:

```text
―¡Esto que has hecho ―gritó― es una auténtica locura!
―Solo nos queda esto ―le enseñó unos pocos billetes― para el resto del viaje.
```

### Regla 2.3.f: Dos puntos tras inciso

Si el signo de puntuación tras el inciso son los dos puntos, estos se escriben tras la raya de cierre:

```text
―Anoche estuve en una fiesta ―me confesó, y añadió―: Conocí a personas muy interesantes.
```

---

## Usos como Signo Simple (3.1): Diálogos

En la reproducción escrita de un diálogo, la raya precede a la intervención de cada uno de los interlocutores, sin que se mencione el nombre de estos:

```text
―¿Cuándo volverás?
―No tengo ni idea.
―¡No tardes mucho!
```

**Nota:** No debe dejarse espacio de separación entre la raya y el comienzo de cada una de las intervenciones.

---

## Aplicación al Conversor de Diálogos

### Reglas Implementadas

#### D1: Sustitución básica de comillas

```text
"Hola" → —Hola
"¿Cómo estás?" → —¿Cómo estás?
```

**Implementación en código:**

- **Función:** `_convert_standalone_dialog()`
- **Patrones:** `pattern1` y `pattern2` (inicio de línea)
- **Archivo:** `src/converter.py` líneas ~430-470

#### D2: Diálogo con etiqueta narrativa

```text
"Hola", dijo Juan. → —Hola —dijo Juan.
"¿Vienes?", preguntó. → —¿Vienes? —preguntó.
"Buenos días, Adi.", dijo llena de energía. → —Buenos días, Adi —dijo llena de energía.
```

**Nota:** Cuando hay verbo de lengua inmediatamente después del diálogo, se elimina el punto final del diálogo.

**Implementación en código:**

- **Función:** `_convert_dialog_with_tag()`
- **Patrones:** `pattern1`, `pattern2`, `pattern3`
- **Archivo:** `src/converter.py` líneas ~290-420
- **Verbos:** Lista `DIALOG_TAGS` en `src/rules.py`

#### D3: Inciso del narrador (con verbo)

```text
"Lo principal", añadió Pilar, "es sentirse viva".
→ —Lo principal —añadió Pilar—, es sentirse viva.
```

**Implementación en código:**

- **Función:** `_convert_dialog_with_interruption()`
- **Patrones:** `pattern1` (coma), `pattern2` (punto)
- **Archivo:** `src/converter.py` líneas ~120-220

#### D4: Narración intermedia (sin verbo)

```text
"No se moleste." Cerró la puerta.
→ —No se moleste. —Cerró la puerta.
```

```text
"Con suerte solo terminás recargando arcanismos." Amelia estaba mirando su escritorio con curiosidad. "Uno studio sui draghi de Gerardo di Trivia. ¿Dragones? Adi…"
→ —Con suerte solo terminás recargando arcanismos —Amelia estaba mirando su escritorio con curiosidad—. Uno studio sui draghi de Gerardo di Trivia. ¿Dragones? Adi…
```

**Implementación en código:**

- **Función:** `_convert_dialog_with_narration()`
- **Patrón:** Regex que detecta `"texto1" narración. "texto2"`
- **Archivo:** `src/converter.py` líneas ~230-280
- **Nota:** Aplica primero para evitar conflictos con otras reglas

#### D5: Comillas internas

```text
"Me dijo: 'te esperaré'" → —Me dijo: «te esperaré»
```

**Implementación en código:**

- **Función:** `_convert_nested_quotes()`
- **Patrón:** Comillas simples dentro de texto con rayas
- **Archivo:** `src/converter.py` líneas ~520-580

### Funciones Auxiliares

#### Corrección automática de puntuación

- **Función:** `_fix_punctuation_before_dialog_tag()`
- **Propósito:** Corrige `"texto." verbo` → `"texto", verbo`
- **Archivo:** `src/converter.py` líneas ~100-120

#### Normalización de comillas

- **Función:** `_normalize_quotes()`
- **Propósito:** Convierte `«»` `""` `''` → `""` `''`
- **Archivo:** `src/converter.py` líneas ~35-50

### Orden de Ejecución

```python
# En _convert_line() - src/converter.py líneas ~85-105
line = self._fix_punctuation_before_dialog_tag(line)  # PASO 0

for _ in range(max_iterations):
    line = self._convert_dialog_with_narration(line, original_line)    # D4 (primero)
    line = self._convert_dialog_with_interruption(line, original_line) # D3
    line = self._convert_dialog_with_tag(line, original_line)          # D2
    line = self._convert_standalone_dialog(line, original_line)        # D1
    line = self._convert_nested_quotes(line, original_line)            # D5
```

### Verbos de Dicción Reconocidos

Lista completa de verbos que activan la regla D2:

#### Básicos

- decir, dijo, dicen, dijeron
- preguntar, preguntó, preguntan, preguntaron
- responder, respondió, responden, respondieron
- exclamar, exclamó, exclaman, exclamaron
- gritar, gritó, gritan, gritaron

#### De afirmación

- afirmar, aseguró, afirman, aseguraron
- declarar, declaró, declaran, declararon
- manifestar, manifestó, manifiestan, manifestaron

#### De sugerencia

- añadir, agregó, añaden, agregaron
- continuar, prosiguió, continúan, prosiguieron

#### De actitud

- murmurar, susurró, murmuran, susurraron
- insistir, replicó, insisten, replicaron

#### De intensidad

- chillar, bramó, chillan, bramaron

#### De comunicación

- comentar, observó, comentan, observaron
- indicar, indicó, indican, indicaron
- advertir, reconoció, advierten, reconocieron
- proponer, sugirió, proponen, sugirieron

**Archivo:** `src/rules.py` - lista `DIALOG_TAGS`

---

## Espaciado y Puntuación

### Reglas de espacios

1. **Raya pegada al diálogo:** `—Hola` (sin espacio)
2. **Espacio antes de verbo:** `—Hola —dijo` (con espacio antes de "dijo")
3. **Raya pegada a puntuación:** `—dijo—,` (sin espacio antes de coma)
4. **Narración entre diálogos:** Segundo diálogo sin raya de apertura: `—Texto1 —Narración—. Texto2`

### Ejemplos correctos

```text
✅ —Hola —dijo Juan.
❌ — Hola — dijo Juan.
❌ —Hola— dijo Juan.
✅ —Lo principal —añadió—, es esto.
❌ —Lo principal —añadió— , es esto.
✅ —Con suerte solo terminás recargando arcanismos —Amelia estaba mirando su escritorio con curiosidad—. Uno studio sui draghi de Gerardo di Trivia. ¿Dragones? Adi…
❌ —Con suerte solo terminás recargando arcanismos. —Amelia estaba mirando su escritorio con curiosidad—. —Uno studio sui draghi de Gerardo di Trivia. ¿Dragones? Adi…
```

---

## Referencias Adicionales

- [RAE - Raya](https://www.rae.es/dpd/raya)
- [Fundéu - Uso de la raya](https://www.fundeu.es/consulta/raya-en-dialogos/)
- Ortografía de la lengua española (RAE/ASALE, 2010)

---

_Este documento resume las reglas oficiales de la RAE para el uso de la raya en diálogos narrativos, extraídas del Diccionario panhispánico de dudas._
