#!/bin/bash
# build_appimage.sh - Construye el AppImage del Conversor de Diálogos
#
# Requisitos:
#   - python3 (3.11+) con tkinter y pip
#   - wget o curl
#   - zsyncmake (paquete 'zsync' en la mayoría de distros)
#
# Uso:
#   ./build_appimage.sh              # Construye la versión actual
#   ./build_appimage.sh --clean      # Limpia artefactos previos antes de construir

set -euo pipefail

# ─── Configuración ────────────────────────────────────────────────────────────

REPO_OWNER="T4toh"
REPO_NAME="dialogos_a_esp"
ARCH="x86_64"

# Leer versión desde el código fuente
VERSION=$(python3 -c "import sys; sys.path.insert(0, '.'); from src import __version__; print(__version__)")
APP_NAME="Conversor-Dialogos"
APPIMAGE_NAME="${APP_NAME}-${VERSION}-${ARCH}.AppImage"

APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"

TOOLS_DIR=".appimage-tools"
BUILD_DIR=".appimage-build"

# ─── Colores para output ───────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log_info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ─── Limpiar artefactos previos ────────────────────────────────────────────────
if [[ "${1:-}" == "--clean" ]]; then
    log_info "Limpiando artefactos previos..."
    rm -rf "${BUILD_DIR}" dist build __pycache__ *.spec "${APP_NAME}-"*.AppImage "${APP_NAME}-"*.AppImage.zsync
    log_ok "Limpieza completada"
    shift
fi

# ─── Verificar dependencias ────────────────────────────────────────────────────
log_info "Verificando dependencias del sistema..."

if ! command -v zsyncmake &>/dev/null; then
    log_error "zsyncmake no encontrado. Instálalo:"
    echo "  Debian/Ubuntu: sudo apt-get install zsync"
    echo "  Arch:          sudo pacman -S zsync"
    echo "  Fedora:        sudo dnf install zsync"
    exit 1
fi

if ! python3 -c "import tkinter" 2>/dev/null; then
    log_error "tkinter no encontrado. Instálalo:"
    echo "  Debian/Ubuntu: sudo apt-get install python3-tk"
    echo "  Arch:          sudo pacman -S tk"
    echo "  Fedora:        sudo dnf install python3-tkinter"
    exit 1
fi

DOWNLOADER=""
if command -v wget &>/dev/null; then
    DOWNLOADER="wget -q --show-progress -O"
elif command -v curl &>/dev/null; then
    DOWNLOADER="curl -L --progress-bar -o"
else
    log_error "Necesitas wget o curl instalado."
    exit 1
fi

log_ok "Dependencias OK (zsyncmake, tkinter, ${DOWNLOADER%% *})"

# ─── Instalar PyInstaller si no está disponible ────────────────────────────────
if ! python3 -m PyInstaller --version &>/dev/null 2>&1; then
    log_info "Instalando PyInstaller..."
    python3 -m pip install pyinstaller --quiet 2>/dev/null \
        || python3 -m pip install pyinstaller --quiet --break-system-packages
    log_ok "PyInstaller instalado"
else
    log_ok "PyInstaller $(python3 -m PyInstaller --version) disponible"
fi

# ─── Preparar directorio de herramientas ──────────────────────────────────────
mkdir -p "${TOOLS_DIR}" "${BUILD_DIR}"

# Función helper: ejecuta un AppImage desde /tmp para evitar noexec en el fs del repo
# APPIMAGE_EXTRACT_AND_RUN=1 permite correrlo sin FUSE (necesario en CI/contenedores)
run_appimage() {
    local src="$1"
    shift
    local tmp
    tmp=$(mktemp /tmp/appimage-tool-XXXXX)
    cp "${src}" "${tmp}"
    chmod +x "${tmp}"
    APPIMAGE_EXTRACT_AND_RUN=1 "${tmp}" "$@"
    local rc=$?
    rm -f "${tmp}"
    return ${rc}
}

# Descargar appimagetool si no está en caché
APPIMAGETOOL="${TOOLS_DIR}/appimagetool"
if [[ ! -s "${APPIMAGETOOL}" ]]; then
    log_info "Descargando appimagetool..."
    $DOWNLOADER "${APPIMAGETOOL}" "${APPIMAGETOOL_URL}"
    if [[ ! -s "${APPIMAGETOOL}" ]]; then
        log_error "Fallo al descargar appimagetool (archivo vacío)"
        exit 1
    fi
    log_ok "appimagetool descargado"
fi

# ─── Bundlear app con PyInstaller ─────────────────────────────────────────────
log_info "Bundleando aplicación con PyInstaller..."

# Limpiar builds previos de PyInstaller
rm -rf dist build __pycache__

python3 -m PyInstaller \
    --noconfirm \
    --windowed \
    --onedir \
    --name "conversor-dialogos" \
    --add-data "src:src" \
    --add-data "icon.png:." \
    --hidden-import "tkinter" \
    --hidden-import "tkinter.ttk" \
    --hidden-import "tkinter.filedialog" \
    --hidden-import "tkinter.messagebox" \
    gui.py \
    2>&1 | grep -E "^\[|\bWARN\b|\bERROR\b|Building|completed" || true

if [[ ! -d "dist/conversor-dialogos" ]]; then
    log_error "PyInstaller no generó la carpeta dist/conversor-dialogos"
    exit 1
fi
log_ok "Bundle creado en dist/conversor-dialogos"

# ─── Construir AppDir ─────────────────────────────────────────────────────────
APPDIR="${BUILD_DIR}/AppDir"
log_info "Construyendo AppDir en ${APPDIR}..."

rm -rf "${APPDIR}"
mkdir -p "${APPDIR}/usr/bin" "${APPDIR}/usr/share/applications" "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

# Copiar bundle de PyInstaller
cp -r dist/conversor-dialogos/* "${APPDIR}/usr/bin/"

# Copiar .desktop e icono
cp AppDir/conversor-dialogos.desktop "${APPDIR}/conversor-dialogos.desktop"
cp AppDir/conversor-dialogos.desktop "${APPDIR}/usr/share/applications/"
cp AppDir/conversor-dialogos.png "${APPDIR}/conversor-dialogos.png"
cp AppDir/conversor-dialogos.png "${APPDIR}/usr/share/icons/hicolor/256x256/apps/"

# Crear AppRun para bundle PyInstaller (el ejecutable está en usr/bin/)
cat > "${APPDIR}/AppRun" << 'APPRUN_EOF'
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "${0}")")"
exec "${APPDIR}/usr/bin/conversor-dialogos" "$@"
APPRUN_EOF
chmod +x "${APPDIR}/AppRun"

log_ok "AppDir preparado"

# ─── Generar AppImage ─────────────────────────────────────────────────────────
log_info "Generando ${APPIMAGE_NAME}..."

# Update info para AppImageUpdate con zsync en GitHub Releases
UPDATE_INFO="gh-releases-zsync|${REPO_OWNER}|${REPO_NAME}|latest|${APP_NAME}-*-${ARCH}.AppImage.zsync"

ARCH="${ARCH}" run_appimage "${APPIMAGETOOL}" \
    --updateinformation "${UPDATE_INFO}" \
    "${APPDIR}" \
    "${APPIMAGE_NAME}" \
    2>&1

chmod +x "${APPIMAGE_NAME}"
log_ok "AppImage generada: ${APPIMAGE_NAME}"

# ─── Generar .zsync ───────────────────────────────────────────────────────────
log_info "Generando ${APPIMAGE_NAME}.zsync para actualizaciones delta..."
zsyncmake "${APPIMAGE_NAME}" -o "${APPIMAGE_NAME}.zsync" 2>&1
log_ok "Archivo zsync generado: ${APPIMAGE_NAME}.zsync"

# ─── Limpiar artefactos temporales de PyInstaller ─────────────────────────────
rm -rf dist build __pycache__ *.spec

# ─── Resumen ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Build completado: v${VERSION}${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  📦 AppImage:  ${APPIMAGE_NAME}  ($(du -sh "${APPIMAGE_NAME}" | cut -f1))"
echo -e "  🔄 Zsync:     ${APPIMAGE_NAME}.zsync"
echo ""
echo -e "  Para probar:"
echo -e "    ./${APPIMAGE_NAME}"
echo ""
echo -e "  Para publicar en GitHub Releases:"
echo -e "    gh release create v${VERSION} ${APPIMAGE_NAME} ${APPIMAGE_NAME}.zsync"
echo ""
