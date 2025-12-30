@echo off
REM Script para crear ejecutable standalone de la GUI con PyInstaller (Windows)

echo 🔨 Generador de Ejecutable - Conversor de Dialogos
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no esta instalado
    echo    Descarga Python desde https://www.python.org
    pause
    exit /b 1
)

REM Verificar PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 PyInstaller no esta instalado
    echo.
    set /p INSTALL="¿Deseas instalarlo? (s/n): "
    
    if /i "%INSTALL%"=="s" (
        echo 📥 Instalando PyInstaller...
        python -m pip install pyinstaller
        
        if errorlevel 1 (
            echo ❌ Error al instalar PyInstaller
            pause
            exit /b 1
        )
        echo ✅ PyInstaller instalado
    ) else (
        echo Instala PyInstaller con: python -m pip install pyinstaller
        pause
        exit /b 0
    )
)

echo.
echo 🔨 Compilando ejecutable...
echo.

REM Crear ejecutable con PyInstaller
python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "Conversor-Dialogos" ^
    --add-data "src;src" ^
    --hidden-import "tkinter" ^
    --hidden-import "tkinter.ttk" ^
    --hidden-import "tkinter.filedialog" ^
    --hidden-import "tkinter.messagebox" ^
    gui.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Ejecutable creado exitosamente!
    echo.
    echo 📁 Ubicacion: .\dist\Conversor-Dialogos.exe
    echo.
    echo 💡 Puedes copiar este archivo .exe a cualquier Windows sin instalar nada
    echo.
) else (
    echo.
    echo ❌ Error al crear el ejecutable
)

pause
