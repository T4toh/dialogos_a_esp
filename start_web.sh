#!/bin/bash
# Script de inicio para la interfaz Streamlit

echo "🚀 Iniciando Conversor de Diálogos (Interfaz Web)"
echo ""

# Verificar Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    echo "   Instala Python 3.11+ desde https://www.python.org"
    exit 1
fi

# Usar python o python3
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Verificar versión de Python
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Verificar si Streamlit está instalado
if ! $PYTHON_CMD -c "import streamlit" 2>/dev/null; then
    echo ""
    echo "📦 Streamlit no está instalado"
    echo ""
    echo "Opciones de instalación:"
    echo ""
    
    # Detectar distribución
    if command -v dnf &> /dev/null; then
        # Fedora/RHEL
        echo "🔧 Instalación para Fedora/RHEL:"
        echo "   sudo dnf install python3-pip"
        echo "   $PYTHON_CMD -m pip install --user streamlit"
    elif command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        echo "🔧 Instalación para Debian/Ubuntu:"
        echo "   sudo apt-get install python3-pip"
        echo "   $PYTHON_CMD -m pip install --user streamlit"
    elif command -v pacman &> /dev/null; then
        # Arch
        echo "🔧 Instalación para Arch Linux:"
        echo "   sudo pacman -S python-pip"
        echo "   $PYTHON_CMD -m pip install --user streamlit"
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL antiguo
        echo "🔧 Instalación para CentOS/RHEL:"
        echo "   sudo yum install python3-pip"
        echo "   $PYTHON_CMD -m pip install --user streamlit"
    else
        echo "🔧 Instalación genérica:"
        echo "   Instala pip para tu distribución"
        echo "   $PYTHON_CMD -m pip install --user streamlit"
    fi
    
    echo ""
    echo "O alternativamente:"
    echo "   $PYTHON_CMD -m ensurepip --user"
    echo "   $PYTHON_CMD -m pip install --user streamlit"
    echo ""
    echo "Después ejecuta nuevamente: ./start_web.sh"
    exit 1
fi

# Iniciar Streamlit
echo ""
echo "✅ Streamlit está instalado"
echo ""
echo "🌐 Abriendo aplicación en el navegador..."
echo "   URL: http://localhost:8501"
echo ""
echo "💡 Presiona Ctrl+C para detener el servidor"
echo ""

# Intentar ejecutar streamlit de varias formas
if command -v streamlit &> /dev/null; then
    streamlit run app.py
elif [ -f "$HOME/.local/bin/streamlit" ]; then
    "$HOME/.local/bin/streamlit" run app.py
else
    $PYTHON_CMD -m streamlit run app.py
fi

