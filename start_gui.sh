#!/bin/bash
# Script de inicio para la GUI de Tkinter

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado"
    echo "Por favor instala Python 3.11 o superior"
    exit 1
fi

# Verificar versión de Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION encontrado, pero se requiere Python $REQUIRED_VERSION o superior"
    exit 1
fi

# Ejecutar GUI
echo "🚀 Iniciando Conversor de Diálogos..."
python3 gui.py
