#!/bin/bash
# Script para crear ejecutable standalone de la GUI con PyInstaller

echo "🔨 Generador de Ejecutable - Conversor de Diálogos"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

PYTHON_CMD="python3"

# Verificar PyInstaller
if ! $PYTHON_CMD -c "import PyInstaller" 2>/dev/null; then
    echo "📦 PyInstaller no está instalado"
    echo ""
    read -p "¿Deseas instalarlo? (s/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        echo "📥 Instalando PyInstaller..."
        $PYTHON_CMD -m pip install --user pyinstaller
        
        if [ $? -ne 0 ]; then
            echo "❌ Error al instalar PyInstaller"
            echo "   Intenta: $PYTHON_CMD -m pip install --user pyinstaller"
            exit 1
        fi
        echo "✅ PyInstaller instalado"
    else
        echo "Instala PyInstaller con: $PYTHON_CMD -m pip install --user pyinstaller"
        exit 0
    fi
fi

echo ""
echo "🔨 Compilando ejecutable..."
echo ""

# Crear ejecutable con PyInstaller
$PYTHON_CMD -m PyInstaller \
    --onefile \
    --windowed \
    --name "Conversor-Dialogos" \
    --add-data "src:src" \
    --hidden-import "tkinter" \
    --hidden-import "tkinter.ttk" \
    --hidden-import "tkinter.filedialog" \
    --hidden-import "tkinter.messagebox" \
    gui.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Ejecutable creado exitosamente!"
    echo ""
    echo "📁 Ubicación: ./dist/Conversor-Dialogos"
    echo ""
    echo "💡 Puedes copiar este archivo a cualquier Linux con las mismas librerías del sistema"
    echo "   (requiere Tkinter instalado en el sistema destino)"
    echo ""
    
    # Mostrar tamaño
    SIZE=$(du -h dist/Conversor-Dialogos | cut -f1)
    echo "📊 Tamaño: $SIZE"
else
    echo ""
    echo "❌ Error al crear el ejecutable"
    exit 1
fi
