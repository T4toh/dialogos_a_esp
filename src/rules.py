"""
Definición de reglas y patrones para la conversión de diálogos.
"""

import re
from typing import Pattern

# Etiquetas de diálogo comunes (verbos dicendi)
DIALOG_TAGS = [
    "dijo",
    "dice",
    "dijeron",  # Plural de dijo
    "dicen",  # Plural de dice
    "preguntó",
    "pregunta",
    "preguntaron",  # Plural de preguntó
    "preguntan",  # Plural de pregunta
    "respondió",
    "responde",
    "respondieron",  # Plural de respondió
    "responden",  # Plural de responde
    "contestó",
    "contesta",
    "contestaron",  # Plural de contestó
    "contestan",  # Plural de contesta
    "murmuró",
    "murmura",
    "murmuraron",  # Plural de murmuró
    "murmuran",  # Plural de murmura
    "susurró",
    "susurra",
    "susurraron",  # Plural de susurró
    "susurran",  # Plural de susurra
    "gritó",
    "grita",
    "gritaron",  # Plural de gritó
    "gritan",  # Plural de grita
    "exclamó",
    "exclama",
    "exclamaron",  # Plural de exclamó
    "exclaman",  # Plural de exclama
    "añadió",
    "añade",
    "añadieron",  # Plural de añadió
    "añaden",  # Plural de añade
    "agregó",  # Sinónimo de añadió
    "agrega",
    "agregaron",  # Plural de agregó
    "agregan",  # Plural de agrega
    "continuó",
    "continúa",
    "continuaron",  # Plural de continuó
    "continúan",  # Plural de continúa
    "repuso",
    "repone",
    "repusieron",  # Plural de repuso
    "reponen",  # Plural de repone
    "replicó",
    "replica",
    "replicaron",  # Plural de replicó
    "replican",  # Plural de replica
    "insistió",
    "insiste",
    "insistieron",  # Plural de insistió
    "insisten",  # Plural de insiste
    "afirmó",
    "afirma",
    "afirmaron",  # Plural de afirmó
    "afirman",  # Plural de afirma
    "negó",
    "niega",
    "negaron",  # Plural de negó
    "niegan",  # Plural de niega
    "comentó",
    "comenta",
    "comentaron",  # Plural de comentó
    "comentan",  # Plural de comenta
    "explicó",
    "explica",
    "explicaron",  # Plural de explicó
    "explican",  # Plural de explica
    "señaló",
    "señala",
    "señalaron",  # Plural de señaló
    "señalan",  # Plural de señala
    "indicó",
    "indica",
    "indicaron",  # Plural de indicó
    "indican",  # Plural de indica
    "mencionó",
    "menciona",
    "mencionaron",  # Plural de mencionó
    "mencionan",  # Plural de menciona
    "expresó",
    "expresa",
    "expresaron",  # Plural de expresó
    "expresan",  # Plural de expresa
    "aseguró",
    "asegura",
    "aseguraron",  # Plural de aseguró
    "aseguran",  # Plural de asegura
    "declaró",
    "declara",
    "declararon",  # Plural de declaró
    "declaran",  # Plural de declara
    "manifestó",
    "manifiesta",
    "manifestaron",  # Plural de manifestó
    "manifiestan",  # Plural de manifiesta
    "sugirió",
    "sugiere",
    "sugirieron",  # Plural de sugirió
    "sugieren",  # Plural de sugiere
    "propuso",
    "propone",
    "propusieron",  # Plural de propuso
    "proponen",  # Plural de propone
    "ordenó",
    "ordena",
    "ordenaron",  # Plural de ordenó
    "ordenan",  # Plural de ordena
    "pidió",
    "pide",
    "pidieron",  # Plural de pidió
    "piden",  # Plural de pide
    "rogó",
    "ruega",
    "rogaron",  # Plural de rogó
    "ruegan",  # Plural de ruega
    "suplicó",
    "suplica",
    "suplicaron",  # Plural de suplicó
    "suplican",  # Plural de suplica
    "bramó",
    "brama",
    "bramaron",  # Plural de bramó
    "braman",  # Plural de brama
    "gimió",
    "gime",
    "gimieron",  # Plural de gimió
    "gimen",  # Plural de gime
    "sollozó",
    "solloza",
    "sollozaron",  # Plural de sollozó
    "sollozan",  # Plural de solloza
    "balbuceó",
    "balbucea",
    "balbucearon",  # Plural de balbuceó
    "balbucean",  # Plural de balbucea
    "tartamudeó",
    "tartamudea",
    "tartamudearon",  # Plural de tartamudeó
    "tartamudean",  # Plural de tartamudea
    "aportó",
    "aporta",
    "aportaron",  # Plural de aportó
    "aportan",  # Plural de aporta
]


# Patrones de regex compilados
class Patterns:
    """Patrones de expresiones regulares para detección de diálogos."""

    # Diálogo con comillas dobles
    DOUBLE_QUOTES: Pattern = re.compile(
        r'"([^"]+)"(\s*)([A-ZÁÉÍÓÚa-záéíóúñÑ])', re.MULTILINE | re.DOTALL
    )

    # Diálogo con comillas simples
    SINGLE_QUOTES: Pattern = re.compile(
        r"'([^']+)'(\s*)([A-ZÁÉÍÓÚa-záéíóúñÑ])", re.MULTILINE | re.DOTALL
    )

    # Diálogo simple al inicio de línea
    DIALOG_START: Pattern = re.compile(r'^"([^"]+)"', re.MULTILINE)

    # Diálogo simple con comillas simples al inicio
    DIALOG_START_SINGLE: Pattern = re.compile(r"^'([^']+)'", re.MULTILINE)

    # Comillas dobles standalone (sin continuación)
    STANDALONE_DOUBLE: Pattern = re.compile(r'"([^"]+)"(?=\s*$|\s*\n)', re.MULTILINE)

    # Comillas simples standalone
    STANDALONE_SINGLE: Pattern = re.compile(r"'([^']+)'(?=\s*$|\s*\n)", re.MULTILINE)


def is_dialog_tag(word: str) -> bool:
    """
    Verifica si una palabra es una etiqueta de diálogo.

    Args:
        word: Palabra a verificar

    Returns:
        True si es una etiqueta de diálogo
    """
    return word.lower() in DIALOG_TAGS


def build_dialog_tag_pattern() -> str:
    """
    Construye un patrón regex para detectar etiquetas de diálogo.

    Returns:
        Patrón regex como string
    """
    tags = "|".join(DIALOG_TAGS)
    return f"({tags})"
