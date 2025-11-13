@echo off
REM Script de inicio para la interfaz Streamlit en Windows

echo.
echo 🚀 Iniciando Conversor de Diálogos (Interfaz Web)
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python 3 no está instalado
    echo    Instala Python 3.11+ desde https://www.python.org
    pause
    exit /b 1
)

REM Verificar si Streamlit está instalado
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo 📦 Streamlit no está instalado. Instalando...
    echo.
    
    python -m pip install streamlit
    
    if errorlevel 1 (
        echo.
        echo ❌ Error instalando Streamlit
        echo.
        echo Instala manualmente:
        echo   pip install streamlit
        pause
        exit /b 1
    )
    
    echo.
    echo ✅ Streamlit instalado correctamente
    echo.
)

REM Iniciar Streamlit
echo 🌐 Abriendo aplicación en el navegador...
echo    URL: http://localhost:8501
echo.
echo 💡 Presiona Ctrl+C para detener el servidor
echo.

streamlit run app.py
