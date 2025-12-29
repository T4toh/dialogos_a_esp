@echo off
REM Script de inicio para la GUI de Tkinter (Windows)

echo Iniciando Conversor de Dialogos...
python gui.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo Error al iniciar la aplicacion.
    echo Verifica que Python 3.11+ este instalado.
    pause
)
