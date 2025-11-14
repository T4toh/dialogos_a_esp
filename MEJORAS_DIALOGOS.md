# Mejoras necesarias para la conversión correcta de diálogos (RAE)

Este documento resume los ajustes pendientes para convertir diálogos con
rayas según las reglas de la RAE. Incluye solo aspectos lingüísticos y
normativos, no temas de Python, ODT ni estructura interna del proyecto.

## 1. Normalización de comillas

Para detectar correctamente diálogos, primero debe normalizarse
cualquier tipo de comillas al conjunto estándar:

- Comillas españolas: « »
- Comillas inglesas: " "
- Comillas rectas: " "

Acciones necesarias:

- Unificar todas las variantes a un formato único antes de procesar.
- Evitar falsos positivos con comillas internas a diálogos.

## 2. Reemplazo básico de comillas → raya

Si una línea contiene un parlamento entre comillas y no pertenece a
estructuras complejas:

"Hola" → ---Hola\
"Hola" → ---Hola\
«Hola» → ---Hola

Reglas:

- La raya va pegada al texto (sin espacio).
- No debe cerrarse la intervención con una segunda raya salvo que haya
  inciso del narrador.

## 3. Manejo correcto de verbos de dicción

Palabras que indican que alguien habla: dijo, preguntó, exclamó,
respondió, añadió, replicó, murmuró, comentó, aseguró...

### 3.1. Parlamentos con etiqueta detrás

"Hola", dijo Juan. → ---Hola ---dijo Juan.

### 3.2. Parlamentos con etiqueta delante

Juan dijo: "Hola." → Juan dijo: ---Hola.

### 3.3. Etiquetas después de signos fuertes

"¡Qué locura!", exclamó Ana. → ---¡Qué locura! ---exclamó Ana.

## 4. Interrupción por narrador (incisos)

### 4.1. Intervención + continuación inmediata

"Lo principal es sentirse viva", añadió Pilar, "afortunada o
desafortunada". → ---Lo principal es sentirse viva ---añadió Pilar---,
afortunada o desafortunada.

Reglas clave:

- Si el narrador interrumpe y el personaje continúa, deben usarse dos
  rayas.
- La continuación debe mantener la puntuación después de la raya de
  cierre.

## 5. Inciso final

"Espero que todo salga bien", dijo Azucena. → ---Espero que todo salga
bien ---dijo Azucena.

## 6. Incisos sin verbo de dicción

"No se moleste." Cerró la puerta y salió. → ---No se moleste. ---Cerró
la puerta y salió.

"Me voy ya." Se puso en pie. "No hace falta que me acompañe." → ---Me
voy ya. ---Se puso en pie---. No hace falta que me acompañe.

## 7. Puntuación en incisos intercalados

"¡Esto que has hecho", gritó, "es una locura!" → ---¡Esto que has hecho
---gritó--- es una locura!

"Solo nos queda esto", le enseñó unos billetes, "para el resto." →
---Solo nos queda esto ---le enseñó unos billetes--- para el resto.

## 8. Dos puntos tras el inciso

"Anoche estuve en una fiesta", me confesó, "y añadió: Conocí a gente". →
---Anoche estuve en una fiesta ---me confesó---: Conocí a gente...

## 9. Diálogos sin menciones

---¿Cuándo volverás?\
---No tengo idea.\
---¡No tardes!

## 10. Comillas internas dentro del diálogo

"Me dijo: 'volvé pronto'" → ---Me dijo: «volvé pronto»

## 11. Normalización de guiones

Convertir - y -- a --- solo en contextos dialogales.

## 12. Múltiples diálogos en una línea

"Hola" "¿Cómo estás?" → ---Hola ---¿Cómo estás?

## 13. Diálogo + narración en la misma línea

"Hola" dijo mientras sonreía y agregó "¿vienes?". → ---Hola ---dijo
mientras sonreía--- ¿vienes?

## 14. Espaciado exacto

- Sin espacio entre raya y parlamento: ---Hola
- Un espacio entre raya y narración: ---Hola ---dijo Juan.
- Sin espacio si tras la raya viene puntuación: ---dijo Juan---.
