# Reglas RAE para Diálogos con Raya

Este documento detalla las reglas oficiales de la RAE para el uso de la raya (—) en diálogos narrativos.

**Referencia oficial:** [RAE - Uso de la raya](https://www.rae.es/dpd/raya)

---

## Regla D1: Sustitución básica de comillas → raya

**Aplicación:** Diálogos simples sin etiquetas de narrador.

### Ejemplos

```
"Hola"          → —Hola
"¿Cómo estás?"  → —¿Cómo estás?
«Buenos días»   → —Buenos días
```

### Notas importantes

- La raya va **pegada** al texto (sin espacio)
- No se cierra con segunda raya salvo que haya inciso del narrador
- Aplica a cualquier tipo de comillas: `"` `"` `«` `»`

---

## Regla D2: Diálogo con etiqueta de narrador (verbo de dicción)

**Aplicación:** Cuando el diálogo va seguido de un verbo que indica habla (dijo, preguntó, exclamó, etc.)

### D2.1: Etiqueta después del diálogo CON COMA

**CRÍTICO:** Cuando hay **coma** antes del verbo, NO se añade punto.

```
"Hola", dijo Juan.          → —Hola —dijo Juan.
"Buenos días", dijo Ana.    → —Buenos días —dijo Ana.
"¿Vienes?", preguntó.       → —¿Vienes? —preguntó.
```

**REGLA:** `"texto", verbo` → `—texto —verbo` (sin punto después de texto)

### D2.2: Etiqueta después del diálogo CON PUNTO

```
"Hola." Dijo Juan.          → —Hola. —Dijo Juan.
"Buenos días." Respondió.   → —Buenos días. —Respondió.
```

**REGLA:** `"texto." Verbo` → `—texto. —Verbo` (mantener punto)

### D2.3: Etiqueta después de signos de interrogación/exclamación

```
"¡Qué sorpresa!" exclamó Ana.     → —¡Qué sorpresa! —exclamó Ana.
"¿Por qué?" preguntó Juan.        → —¿Por qué? —preguntó Juan.
```

**REGLA:** Los signos fuertes (¿?¡!) NO se reemplazan por coma

---

## Regla D3: Inciso del narrador con continuación

**Aplicación:** Cuando el narrador interrumpe el diálogo y el personaje continúa hablando.

### Ejemplos

```
"Lo principal", añadió Pilar, "es sentirse viva".
→ —Lo principal —añadió Pilar—, es sentirse viva.

"Esto que has hecho", gritó, "es una locura!"
→ —Esto que has hecho —gritó— es una locura!
```

### Estructura

1. **Primera raya**: Abre el diálogo
2. **Segunda raya**: Cierra primera parte y abre inciso del narrador
3. **Tercera raya**: Cierra inciso del narrador
4. Continuación del diálogo (sin cuarta raya)

### Puntuación crítica

- La puntuación ANTES del inciso se mantiene
- La puntuación DESPUÉS del inciso se mantiene
- Ejemplo: `"texto", narrador, "continuación"` → `—texto —narrador—, continuación`

---

## Regla D4: Narración después del diálogo (sin verbo de dicción)

**Aplicación:** Cuando después del diálogo hay narración que NO es verbo de habla.

```
"No se moleste." Cerró la puerta.
→ —No se moleste. —Cerró la puerta.

"Me voy ya." Se puso en pie.
→ —Me voy ya. —Se puso en pie.
```

**REGLA:** El punto se mantiene, y la narración lleva raya de apertura.

---

## Regla D5: Comillas internas (citas dentro del diálogo)

**Aplicación:** Cuando un personaje cita a otro dentro de su diálogo.

```
"Me dijo: 'volvé pronto'"       → —Me dijo: «volvé pronto»
"El letrero decía 'cerrado'"    → —El letrero decía «cerrado»
```

**REGLA:** Las comillas internas se convierten a comillas latinas `« »`

---

## Verbos de dicción reconocidos (42 verbos)

Lista de verbos que indican habla y activan la regla D2:

### Verbos básicos

- dijo, dice, decir
- preguntó, pregunta, preguntar
- respondió, responde, responder
- exclamó, exclama, exclamar
- gritó, grita, gritar

### Verbos de afirmación

- afirmó, aseguró, confirmó, declaró, manifestó

### Verbos de sugerencia

- añadió, agregó, continuó, prosiguió, siguió

### Verbos de actitud

- murmuró, susurró, suspiró, balbuceó
- insistió, replicó, objetó, protestó

### Verbos de intensidad

- chilló, bramó, rugió, vociferó

### Verbos de comunicación

- comentó, observó, indicó, señaló, apuntó
- advirtió, reconoció, confesó, admitió
- propuso, sugirió, ofreció

**Ver lista completa en:** `src/rules.py`

---

## Puntuación: Reglas críticas

### 1. Punto antes de verbo de dicción

❌ **INCORRECTO:**

```
"Buenos días, Adi." dijo llena de energía.
→ —Buenos días, Adi. —dijo llena de energía.
```

✅ **CORRECTO:**

```
"Buenos días, Adi", dijo llena de energía.
→ —Buenos días, Adi —dijo llena de energía.
```

**REGLA:** Si hay verbo de dicción después, usar **coma** (no punto) antes de cerrar comillas.

### 2. Coma en incisos intercalados

```
"Lo principal", añadió, "es esto".
→ —Lo principal —añadió—, es esto.
```

La coma después del inciso se mantiene.

### 3. Signos de interrogación/exclamación

```
"¡Hola!", gritó.     → —¡Hola! —gritó.
"¿Vienes?", dijo.    → —¿Vienes? —dijo.
```

Los signos fuertes reemplazan la coma/punto pero la estructura se mantiene.

---

## Espaciado

### Reglas de espacios

1. **Raya pegada al diálogo:** `—Hola` (sin espacio)
2. **Espacio antes de verbo:** `—Hola —dijo` (con espacio antes de "dijo")
3. **Raya pegada a puntuación:** `—dijo—,` (sin espacio antes de coma)

### Ejemplos

```
✅ —Hola —dijo Juan.
❌ — Hola — dijo Juan.
❌ —Hola— dijo Juan.

✅ —Lo principal —añadió—, es esto.
❌ —Lo principal —añadió— , es esto.
```

---

## Estado de implementación

### ✅ Implementado

- [x] D1: Sustitución básica de comillas
- [x] D2: Etiquetas con verbos de dicción
  - [x] Corrección automática de puntuación (coma vs punto)
- [x] D3: Incisos del narrador con continuación (CON verbo)
  - [x] Con coma: `"texto1", verbo, "texto2"` → `—texto1 —verbo—, texto2`
  - [x] Con punto: `"texto1", verbo. "texto2"` → `—texto1 —verbo—. texto2`
- [x] D4: Narración intermedia con continuación (SIN verbo)
  - [x] `"texto1." Narración. "texto2"` → `—texto1. —Narración—. texto2`
- [x] D5: Comillas internas a latinas
- [x] Reconocimiento de 44 verbos de dicción (agregado `agregó/agrega`)
- [x] Normalización de comillas (« » " " ' ' → " ')

### ⚠️ Nota importante

**Input correcto** según RAE para diálogos con continuación:

```
"Es normal", agregó sonriente. "Bastien ya debe estar esperándonos."
```

NO (punto antes de verbo):

```
"Es normal." Agregó sonriente. "Bastien ya debe estar esperándonos."
```

El conversor **autocorrige** puntos → comas cuando detecta verbo de dicción, pero funciona mejor con input ya correcto.

### ❌ Pendiente

- [ ] Detección de diálogos con etiqueta ANTES: `Juan dijo: "Hola"`
- [ ] Múltiples diálogos en una línea (se procesa pero puede mejorar)
- [ ] Validación de espaciado exacto

---

## Referencias

- [RAE - Raya](https://www.rae.es/dpd/raya)
- [Fundéu - Uso de la raya](https://www.fundeu.es/consulta/raya-en-dialogos/)
- Ortografía de la lengua española (RAE/ASALE, 2010)
