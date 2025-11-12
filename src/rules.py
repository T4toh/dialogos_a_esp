"""
Definición de reglas y patrones para la conversión de diálogos.
"""

import re
from typing import Pattern

# Etiquetas de diálogo comunes (verbos dicendi)
DIALOG_TAGS = [
    'dijo', 'dice', 'preguntó', 'pregunta', 'respondió', 'responde',
    'contestó', 'contesta', 'murmuró', 'murmura', 'susurró', 'susurra',
    'gritó', 'grita', 'exclamó', 'exclama', 'añadió', 'añade',
    'continuó', 'continúa', 'repuso', 'repone', 'replicó', 'replica',
    'insistió', 'insiste', 'afirmó', 'afirma', 'negó', 'niega',
    'comentó', 'comenta', 'explicó', 'explica', 'señaló', 'señala',
    'indicó', 'indica', 'mencionó', 'menciona', 'expresó', 'expresa',
    'aseguró', 'asegura', 'declaró', 'declara', 'manifestó', 'manifiesta',
    'sugirió', 'sugiere', 'propuso', 'propone', 'ordenó', 'ordena',
    'pidió', 'pide', 'rogó', 'ruega', 'suplicó', 'suplica',
    'bramó', 'brama', 'gimió', 'gime', 'sollozó', 'solloza',
    'balbuceó', 'balbucea', 'tartamudeó', 'tartamudea'
]

# Patrones de regex compilados
class Patterns:
    """Patrones de expresiones regulares para detección de diálogos."""
    
    # Diálogo con comillas dobles
    DOUBLE_QUOTES: Pattern = re.compile(
        r'"([^"]+)"(\s*)([A-ZÁÉÍÓÚa-záéíóúñÑ])',
        re.MULTILINE | re.DOTALL
    )
    
    # Diálogo con comillas simples
    SINGLE_QUOTES: Pattern = re.compile(
        r"'([^']+)'(\s*)([A-ZÁÉÍÓÚa-záéíóúñÑ])",
        re.MULTILINE | re.DOTALL
    )
    
    # Diálogo simple al inicio de línea
    DIALOG_START: Pattern = re.compile(
        r'^"([^"]+)"',
        re.MULTILINE
    )
    
    # Diálogo simple con comillas simples al inicio
    DIALOG_START_SINGLE: Pattern = re.compile(
        r"^'([^']+)'",
        re.MULTILINE
    )
    
    # Comillas dobles standalone (sin continuación)
    STANDALONE_DOUBLE: Pattern = re.compile(
        r'"([^"]+)"(?=\s*$|\s*\n)',
        re.MULTILINE
    )
    
    # Comillas simples standalone
    STANDALONE_SINGLE: Pattern = re.compile(
        r"'([^']+)'(?=\s*$|\s*\n)",
        re.MULTILINE
    )

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
    tags = '|'.join(DIALOG_TAGS)
    return f'({tags})'
