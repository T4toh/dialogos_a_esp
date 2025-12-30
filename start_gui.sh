#!/bin/bash
# Script de inicio para la GUI de Tkinter

echo "🚀 Conversor de Diálogos - GUI Tkinter"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo ""
    
    # Detectar distribución y dar instrucciones
    if command -v pacman &> /dev/null; then
        echo "📦 Instalación para Arch Linux:"
        echo "   sudo pacman -S python"
    elif command -v apt-get &> /dev/null; then
        echo "📦 Instalación para Debian/Ubuntu:"
        echo "   sudo apt-get update"
        echo "   sudo apt-get install python3 python3-tk"
    elif command -v dnf &> /dev/null; then
        echo "📦 Instalación para Fedora/RHEL:"
        echo "   sudo dnf install python3 python3-tkinter"
    elif command -v yum &> /dev/null; then
        echo "📦 Instalación para CentOS/RHEL:"
        echo "   sudo yum install python3 python3-tkinter"
    else
        echo "📦 Instala Python 3.11+ desde https://www.python.org"
    fi
    exit 1
fi

# Verificar versión de Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

echo "✅ Python $PYTHON_VERSION encontrado"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "⚠️  Se requiere Python $REQUIRED_VERSION o superior"
    echo "   Actualiza tu versión de Python"
    exit 1
fi

# Verificar tkinter
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo ""
    echo "❌ Tkinter no está instalado"
    echo ""
    
    # Instrucciones específicas por distribución
    if command -v pacman &> /dev/null; then
        echo "📦 Instalación para Arch Linux:"
        echo "   sudo pacman -S tk"
    elif command -v apt-get &> /dev/null; then
        echo "📦 Instalación para Debian/Ubuntu:"
        echo "   sudo apt-get install python3-tk"
    elif command -v dnf &> /dev/null; then
        echo "📦 Instalación para Fedora/RHEL:"
        echo "   sudo dnf install python3-tkinter"
    elif command -v yum &> /dev/null; then
        echo "📦 Instalación para CentOS/RHEL:"
        echo "   sudo yum install python3-tkinter"
    else
        echo "📦 Instala el paquete tkinter para Python 3"
    fi
    exit 1
fi

# Todo listo
echo "✅ Tkinter está disponible"
echo ""
echo "🎨 Abriendo interfaz gráfica..."
echo ""

# Ejecutar GUI
python3 gui.py
