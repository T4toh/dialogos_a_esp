"""
Interfaz web con Streamlit para conversión de diálogos.
"""

import streamlit as st
import sys
from pathlib import Path
import time
import subprocess
from typing import List, Dict, Tuple

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.converter import DialogConverter
from src.batch_processor import BatchProcessor
from src.odt_handler import is_odt_file


# Configuración de página
st.set_page_config(
    page_title="Conversor de Diálogos",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)


def format_log_for_display(log_content: str, show_full: bool, max_changes: int = None, total_changes: int = 0) -> str:
    """Formatea el log para mejor visualización en markdown."""
    lines = log_content.split('\n')
    formatted = []
    changes_shown = 0
    current_change = []
    in_change = False
    
    for line in lines:
        # Detectar inicio de cambio
        if line.startswith("CAMBIO #"):
            if current_change and (show_full or changes_shown < max_changes):
                # Renderizar cambio anterior
                formatted.append(format_single_change(current_change))
                changes_shown += 1
            current_change = [line]
            in_change = True
            
            # Si alcanzamos el límite, detenemos
            if not show_full and max_changes and changes_shown >= max_changes:
                break
        elif in_change:
            current_change.append(line)
    
    # Agregar último cambio
    if current_change and (show_full or changes_shown < max_changes):
        formatted.append(format_single_change(current_change))
        changes_shown += 1
    
    # Agregar mensaje si está truncado
    if not show_full and max_changes and changes_shown < total_changes:
        formatted.append(f"\n---\n\n💡 **Mostrando {changes_shown} de {total_changes} cambios**. Marca *'Mostrar log completo'* para ver todos.\n")
    
    return '\n'.join(formatted)


def format_single_change(change_lines: List[str]) -> str:
    """Formatea un cambio individual como tarjeta."""
    if not change_lines:
        return ""
    
    # Extraer información
    header = change_lines[0]  # CAMBIO #N
    location = ""
    rule = ""
    original = []
    converted = []
    
    section = None
    for line in change_lines[1:]:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("-" * 10):  # Ignorar separadores
            continue
        
        # Detectar línea
        if line_stripped.startswith("Línea"):
            location = line_stripped.replace("Línea:", "").replace("Línea", "").strip()
        # Detectar regla
        elif line_stripped.startswith("Regla:"):
            rule = line_stripped.replace("Regla:", "").strip()
        # Detectar sección original (mayúsculas o minúsculas)
        elif line_stripped.upper().startswith("ORIGINAL:"):
            section = "original"
        # Detectar sección convertido (mayúsculas o minúsculas)
        elif line_stripped.upper().startswith("CONVERTIDO:"):
            section = "converted"
        # Agregar contenido a la sección actual
        elif section == "original":
            original.append(line_stripped)
        elif section == "converted":
            converted.append(line_stripped)
    
    # Construir markdown como tarjeta
    md = f"<div style='border: 1px solid #444; border-radius: 8px; padding: 16px; margin: 12px 0; background-color: rgba(28, 131, 225, 0.05);'>\n\n"
    md += f"**{header}** | Línea {location}\n\n"
    md += f"*{rule}*\n\n"
    
    # Mostrar original y convertido sin truncar
    original_text = ' '.join(original) if original else 'N/A'
    converted_text = ' '.join(converted) if converted else 'N/A'
    
    md += "<table style='width: 100%; border-collapse: collapse;'>\n"
    md += "<tr>\n"
    md += f"<td style='width: 50%; padding: 8px; vertical-align: top;'><strong>Original:</strong><br/><code>{original_text}</code></td>\n"
    md += f"<td style='width: 50%; padding: 8px; vertical-align: top;'><strong>Convertido:</strong><br/><code>{converted_text}</code></td>\n"
    md += "</tr>\n"
    md += "</table>\n\n"
    md += "</div>\n\n"
    
    return md


def count_words_in_file(file_path: Path) -> int:
    """Cuenta palabras en un archivo."""
    try:
        if is_odt_file(file_path):
            from src.odt_handler import ODTReader
            reader = ODTReader(file_path)
            text = reader.extract_text()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        words = text.split()
        return len(words)
    except:
        return 0


def scan_directory(directory: Path, pattern: str = "*.*", recursive: bool = False) -> List[Dict]:
    """Escanea directorio y retorna información de archivos."""
    files_info = []
    extensions = {'.odt', '.txt'}
    
    if recursive:
        iterator = directory.rglob(pattern)
    else:
        iterator = directory.glob(pattern)
    
    for file_path in iterator:
        if file_path.is_file() and file_path.suffix in extensions:
            if not file_path.stem.endswith('_convertido'):
                word_count = count_words_in_file(file_path)
                files_info.append({
                    'path': file_path,
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'words': word_count,
                    'type': 'ODT' if is_odt_file(file_path) else 'TXT'
                })
    
    return sorted(files_info, key=lambda x: x['name'])


def format_size(size_bytes: int) -> str:
    """Formatea tamaño en bytes a formato legible."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"



def list_directories(base_path: Path, max_depth: int = 2) -> List[str]:
    """Lista directorios disponibles desde un path base."""
    dirs = []
    
    try:
        base_path = base_path.resolve()
        
        # Añadir el directorio actual
        dirs.append(str(base_path))
        
        # Añadir directorio padre
        if base_path.parent != base_path:
            dirs.append(f"⬆️ {base_path.parent}")
        
        # Añadir subdirectorios del directorio actual
        try:
            for item in sorted(base_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    dirs.append(f"📁 {item}")
        except PermissionError:
            pass
        
        # Separador
        if len(dirs) > 1:
            dirs.append("─" * 50)
        
        # Añadir directorios comunes del usuario
        home = Path.home()
        common_dirs = [
            ("🏠 Inicio", home),
            ("📄 Documentos", home / "Documents"),
            ("📄 Documentos", home / "Documentos"),
            ("🖥️ Escritorio", home / "Desktop"),
            ("🖥️ Escritorio", home / "Escritorio"),
            ("⬇️ Descargas", home / "Downloads"),
            ("⬇️ Descargas", home / "Descargas"),
        ]
        
        for label, path in common_dirs:
            if path.exists() and str(path) not in [d.replace("📁 ", "").replace("⬆️ ", "") for d in dirs]:
                dirs.append(f"{label}: {path}")
        
    except Exception:
        dirs = ["."]
    
    return dirs


def parse_directory_choice(choice: str) -> str:
    """Extrae la ruta del directorio de la elección."""
    if choice.startswith("─"):
        return "."
    
    # Remover emojis y etiquetas
    choice = choice.replace("📁 ", "").replace("⬆️ ", "")
    
    # Si tiene formato "Etiqueta: path"
    if ": " in choice:
        choice = choice.split(": ", 1)[1]
    
    return choice.strip()


def apply_custom_theme(theme: str):
    """Aplica tema personalizado mediante CSS y guarda en localStorage."""
    
    # JavaScript para persistir tema en localStorage
    theme_script = f"""
    <script>
        // Guardar tema en localStorage
        localStorage.setItem('dialogos_theme', '{theme}');
        
        // Aplicar tema inmediatamente
        document.documentElement.setAttribute('data-theme', '{theme}');
    </script>
    """
    st.markdown(theme_script, unsafe_allow_html=True)
    
    if theme == "light":
        st.markdown("""
        <style>
            /* Tema Claro - Completo y legible */
            :root {
                --background-color: #ffffff;
                --secondary-background-color: #f0f2f6;
                --text-color: #262730;
                --primary-color: #1f77b4;
            }
            
            /* Fondo principal */
            .stApp {
                background-color: #ffffff !important;
            }
            
            /* Header/Toolbar de Streamlit */
            header[data-testid="stHeader"] {
                background-color: #ffffff !important;
                border-bottom: 1px solid #e5e7eb !important;
            }
            
            /* Iconos del toolbar */
            header[data-testid="stHeader"] svg {
                fill: #262730 !important;
                color: #262730 !important;
            }
            
            /* Botones del toolbar */
            header[data-testid="stHeader"] button {
                color: #262730 !important;
            }
            
            /* Menú hamburguesa */
            [data-testid="stToolbar"] {
                background-color: #ffffff !important;
            }
            
            [data-testid="stToolbar"] button {
                color: #262730 !important;
            }
            
            /* Sidebar */
            section[data-testid="stSidebar"] {
                background-color: #f0f2f6 !important;
            }
            
            section[data-testid="stSidebar"] * {
                color: #262730 !important;
            }
            
            /* Botones - fondo blanco, texto negro, borde */
            .stButton > button {
                background-color: #ffffff !important;
                color: #262730 !important;
                border: 1px solid #d1d5db !important;
            }
            
            .stButton > button:hover {
                background-color: #f3f4f6 !important;
                border-color: #1f77b4 !important;
            }
            
            .stButton > button[kind="primary"] {
                background-color: #1f77b4 !important;
                color: #ffffff !important;
                border-color: #1f77b4 !important;
            }
            
            .stButton > button[kind="secondary"] {
                background-color: #f0f2f6 !important;
                color: #262730 !important;
                border: 1px solid #d1d5db !important;
            }
            
            /* Inputs de texto */
            .stTextInput > div > div > input {
                background-color: #ffffff !important;
                color: #262730 !important;
                border-color: #d1d5db !important;
            }
            
            /* Selectbox y dropdown */
            .stSelectbox > div > div {
                background-color: #ffffff !important;
                color: #262730 !important;
            }
            
            .stSelectbox [data-baseweb="select"] > div {
                background-color: #ffffff !important;
                color: #262730 !important;
            }
            
            /* Opciones del dropdown */
            [role="listbox"] {
                background-color: #ffffff !important;
            }
            
            [role="option"] {
                background-color: #ffffff !important;
                color: #262730 !important;
            }
            
            [role="option"]:hover {
                background-color: #f0f2f6 !important;
            }
            
            /* Radio buttons */
            .stRadio > div {
                color: #262730 !important;
            }
            
            /* Checkboxes */
            .stCheckbox > label {
                color: #262730 !important;
            }
            
            /* Texto general */
            .stMarkdown {
                color: #262730 !important;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #262730 !important;
            }
            
            p, span, label, div {
                color: #262730 !important;
            }
            
            /* Métricas */
            [data-testid="stMetricValue"] {
                color: #262730 !important;
            }
            
            [data-testid="stMetricLabel"] {
                color: #6b7280 !important;
            }
            
            /* Code blocks */
            code {
                background-color: #f0f2f6 !important;
                color: #262730 !important;
            }
            
            /* Mensajes */
            .stSuccess {
                background-color: #d1fae5 !important;
                color: #065f46 !important;
            }
            
            .stInfo {
                background-color: #dbeafe !important;
                color: #1e40af !important;
            }
            
            .stWarning {
                background-color: #fef3c7 !important;
                color: #92400e !important;
            }
            
            .stError {
                background-color: #fee2e2 !important;
                color: #991b1b !important;
            }
            
            /* Progress bar */
            .stProgress > div > div {
                background-color: #1f77b4 !important;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            /* Tema Oscuro - Forzar todos los elementos */
            :root {
                --background-color: #0e1117;
                --secondary-background-color: #262730;
                --text-color: #fafafa;
                --primary-color: #3b82f6;
            }
            
            .stApp {
                background-color: #0e1117 !important;
                color: #fafafa !important;
            }
            
            /* Header/Toolbar de Streamlit */
            header[data-testid="stHeader"] {
                background-color: #0e1117 !important;
                border-bottom: 1px solid #262730 !important;
            }
            
            /* Iconos del toolbar */
            header[data-testid="stHeader"] svg {
                fill: #fafafa !important;
                color: #fafafa !important;
            }
            
            /* Botones del toolbar */
            header[data-testid="stHeader"] button {
                color: #fafafa !important;
            }
            
            /* Menú hamburguesa */
            [data-testid="stToolbar"] {
                background-color: #0e1117 !important;
            }
            
            [data-testid="stToolbar"] button {
                color: #fafafa !important;
            }
            
            section[data-testid="stSidebar"] {
                background-color: #262730 !important;
            }
            
            .stApp > header {
                background-color: transparent !important;
            }
            
            .stMarkdown, .stText, p, span, div {
                color: #fafafa !important;
            }
            
            .stButton > button {
                color: #fafafa !important;
            }
            
            .stTextInput > div > div > input {
                background-color: #262730 !important;
                color: #fafafa !important;
            }
            
            .stSelectbox > div > div {
                background-color: #262730 !important;
                color: #fafafa !important;
            }
            
            /* Métricas */
            [data-testid="stMetricValue"] {
                color: #fafafa !important;
            }
            
            /* Code blocks */
            code {
                background-color: #262730 !important;
                color: #fafafa !important;
            }
        </style>
        """, unsafe_allow_html=True)


def main():
    """Función principal de la aplicación."""
    
    # Script para leer tema desde localStorage
    st.markdown("""
    <script>
        // Intentar leer tema guardado
        const savedTheme = localStorage.getItem('dialogos_theme');
        if (savedTheme) {
            // Enviar evento personalizado a Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                key: 'theme_from_storage',
                value: savedTheme
            }, '*');
        }
    </script>
    """, unsafe_allow_html=True)
    
    # Configurar tema - intentar recuperar de query params o usar default
    if 'theme' not in st.session_state:
        # Intentar leer desde query params (para persistencia)
        query_params = st.query_params
        saved_theme = query_params.get('theme', 'dark')
        st.session_state.theme = saved_theme
    
    apply_custom_theme(st.session_state.theme)
    
    # Header
    st.title("📝 Conversor de Diálogos a Español")
    st.markdown("Convierte diálogos con comillas al formato español con raya (—)")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selector de tema
        st.subheader("🎨 Apariencia")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌙 Oscuro", use_container_width=True, 
                        type="primary" if st.session_state.theme == "dark" else "secondary"):
                st.session_state.theme = "dark"
                st.query_params.theme = "dark"
                st.rerun()
        with col2:
            if st.button("☀️ Claro", use_container_width=True,
                        type="primary" if st.session_state.theme == "light" else "secondary"):
                st.session_state.theme = "light"
                st.query_params.theme = "light"
                st.rerun()
        
        st.markdown("---")
        
        # Modo de selección de carpeta
        folder_mode = st.radio(
            "Modo de selección",
            ["Escribir ruta", "Selector de carpetas"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Selección de carpeta
        if folder_mode == "Selector de carpetas":
            # Obtener directorio actual desde session_state o usar "."
            if 'current_folder' not in st.session_state:
                st.session_state['current_folder'] = str(Path('.').resolve())
            
            current_base = Path(st.session_state['current_folder'])
            if not current_base.exists():
                current_base = Path('.')
                st.session_state['current_folder'] = str(current_base.resolve())
            
            available_dirs = list_directories(current_base)
            
            # Mostrar carpeta actual
            st.text(f"📍 Ubicación actual:")
            st.code(str(current_base.resolve()), language=None)
            
            # Selector de carpeta
            selected_dir = st.selectbox(
                "Navegar a:",
                options=available_dirs,
                index=0,
                help="Selecciona una carpeta para navegar o usar",
                label_visibility="collapsed"
            )
            
            # Actualizar carpeta si se seleccionó una diferente
            if not selected_dir.startswith("─"):
                parsed_dir = parse_directory_choice(selected_dir)
                if parsed_dir != str(current_base):
                    st.session_state['current_folder'] = parsed_dir
                    st.rerun()
            
            input_dir = str(current_base.resolve())
            
        else:
            # Input de texto tradicional
            input_dir = st.text_input(
                "📂 Carpeta de entrada",
                value=st.session_state.get('input_dir_text', '.'),
                help="Ruta a la carpeta con archivos a procesar"
            )
            # Actualizar current_folder cuando se cambia el texto
            if input_dir:
                st.session_state['current_folder'] = input_dir
        
        # Guardar en session_state
        st.session_state['input_dir_text'] = input_dir
        
        # Opciones de escaneo
        st.subheader("Opciones de búsqueda")
        
        file_filter = st.selectbox(
            "Tipo de archivo",
            options=["Todos (*.*)", "Solo ODT (*.odt)", "Solo TXT (*.txt)"],
            index=0
        )
        
        recursive = st.checkbox(
            "Incluir subcarpetas",
            value=False,
            help="Buscar archivos en subcarpetas"
        )
        
        # Botón de escaneo
        scan_button = st.button("🔍 Escanear", type="primary", use_container_width=True)
    
    # Mapeo de filtro
    filter_map = {
        "Todos (*.*)": "*.*",
        "Solo ODT (*.odt)": "*.odt",
        "Solo TXT (*.txt)": "*.txt"
    }
    pattern = filter_map[file_filter]
    
    # Estado de la aplicación
    if 'files_info' not in st.session_state:
        st.session_state.files_info = []
    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = set()
    
    # Escanear directorio
    if scan_button:
        input_path = Path(input_dir)
        
        if not input_path.exists():
            st.error(f"❌ La carpeta '{input_dir}' no existe")
        elif not input_path.is_dir():
            st.error(f"❌ '{input_dir}' no es una carpeta")
        else:
            with st.spinner("Escaneando archivos..."):
                st.session_state.files_info = scan_directory(input_path, pattern, recursive)
                st.session_state.selected_files = {f['path'] for f in st.session_state.files_info}
            
            if st.session_state.files_info:
                st.success(f"✅ Encontrados {len(st.session_state.files_info)} archivo(s)")
            else:
                st.warning("⚠️ No se encontraron archivos")
    
    # Mostrar archivos encontrados
    if st.session_state.files_info:
        st.header("📋 Archivos Encontrados")
        
        # Estadísticas generales
        total_files = len(st.session_state.files_info)
        total_words = sum(f['words'] for f in st.session_state.files_info)
        total_size = sum(f['size'] for f in st.session_state.files_info)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Archivos", total_files)
        with col2:
            st.metric("Palabras totales", f"{total_words:,}")
        with col3:
            st.metric("Tamaño total", format_size(total_size))
        with col4:
            selected_count = len(st.session_state.selected_files)
            st.metric("Seleccionados", selected_count)
        
        st.markdown("---")
        
        # Tabla de archivos con checkboxes
        st.subheader("Seleccionar archivos a procesar")
        
        # Checkbox para seleccionar/deseleccionar todos
        col_all1, col_all2 = st.columns([1, 5])
        with col_all1:
            select_all = st.checkbox("Todos", value=len(st.session_state.selected_files) == total_files)
            if select_all:
                st.session_state.selected_files = {f['path'] for f in st.session_state.files_info}
            elif not select_all and len(st.session_state.selected_files) == total_files:
                st.session_state.selected_files = set()
        
        # Mostrar cada archivo
        for idx, file_info in enumerate(st.session_state.files_info):
            col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 1, 1])
            
            with col1:
                is_selected = file_info['path'] in st.session_state.selected_files
                if st.checkbox("Seleccionar", value=is_selected, key=f"check_{idx}", label_visibility="collapsed"):
                    st.session_state.selected_files.add(file_info['path'])
                else:
                    st.session_state.selected_files.discard(file_info['path'])
            
            with col2:
                st.text(file_info['name'])
            
            with col3:
                st.text(file_info['type'])
            
            with col4:
                st.text(f"{file_info['words']:,} palabras")
            
            with col5:
                st.text(format_size(file_info['size']))
        
        st.markdown("---")
        
        # Configuración de procesamiento
        st.header("⚙️ Configuración de Procesamiento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_output = str(Path(input_dir) / "convertidos")
            output_dir = st.text_input(
                "📁 Carpeta de salida",
                value=default_output,
                help="Carpeta donde se guardarán los archivos convertidos"
            )
        
        with col2:
            st.write("")  # Espaciado
        
        # Botón de procesamiento
        if len(st.session_state.selected_files) > 0:
            if st.button("▶️ Iniciar Conversión", type="primary", use_container_width=True):
                process_files(st.session_state.selected_files, Path(output_dir))
        else:
            st.warning("⚠️ Selecciona al menos un archivo para procesar")
    
    # Mostrar resultados si existen en session_state
    if 'processing_results' in st.session_state and st.session_state['processing_results']:
        display_results(st.session_state['processing_results'], Path(st.session_state['output_directory']))
    
    elif 'files_info' not in st.session_state:
        # Mensaje inicial solo si no hay archivos escaneados ni resultados
        st.info("👆 Selecciona una carpeta y haz clic en 'Escanear' para comenzar")


def process_files(selected_files: set, output_dir: Path):
    """Procesa los archivos seleccionados."""
    
    # Crear carpeta de salida
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Contenedor para resultados
    st.header("🚀 Procesando Archivos")
    
    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Resultados
    results = []
    total_files = len(selected_files)
    
    for idx, file_path in enumerate(selected_files, 1):
        # Actualizar progreso
        progress = idx / total_files
        progress_bar.progress(progress)
        status_text.text(f"Procesando {idx}/{total_files}: {file_path.name}")
        
        try:
            # CREAR NUEVO CONVERTIDOR POR CADA ARCHIVO
            converter = DialogConverter()
            
            # Determinar archivo de salida
            output_file = output_dir / f"{file_path.stem}_convertido{file_path.suffix}"
            
            # Leer y convertir
            if is_odt_file(file_path):
                from src.odt_handler import ODTProcessor
                processor = ODTProcessor(file_path)
                processor.process_and_save(output_file, converter.convert)
                log_content = converter.logger.generate_report()
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                converted_text, logger = converter.convert(text)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(converted_text)
                
                log_content = logger.generate_report()
            
            # Guardar log
            log_file = output_dir / f"{file_path.stem}_convertido.log.txt"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(log_content)
            
            results.append({
                'file': file_path.name,
                'success': True,
                'changes': len(converter.logger.changes),
                'output': output_file,
                'log_file': log_file
            })
            
        except Exception as e:
            results.append({
                'file': file_path.name,
                'success': False,
                'error': str(e)
            })
    
    # Completar progreso
    progress_bar.progress(1.0)
    status_text.text("✅ Procesamiento completado")
    
    # Guardar resultados en session_state para persistencia
    st.session_state['processing_results'] = results
    st.session_state['output_directory'] = str(output_dir)
    
    # Los resultados se mostrarán automáticamente en el re-run


def display_results(results: List[Dict], output_dir: Path):
    """Muestra los resultados del procesamiento."""
    st.markdown("---")
    st.subheader("📊 Resultados")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    total_changes = sum(r.get('changes', 0) for r in successful)
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Exitosos", len(successful))
    with col2:
        st.metric("❌ Fallidos", len(failed))
    with col3:
        st.metric("🔄 Cambios totales", f"{total_changes:,}")
    
    # Detalles de archivos procesados
    if successful:
        st.success("Archivos procesados correctamente:")
        for result in successful:
            st.text(f"✓ {result['file']} → {result['changes']} cambios")
    
    if failed:
        st.error("Archivos con errores:")
        for result in failed:
            st.text(f"✗ {result['file']} → {result.get('error', 'Error desconocido')}")
    
    # Mostrar ruta de salida
    st.markdown("---")
    st.info(f"📁 **Archivos guardados en:** `{output_dir}`")
    
    # Visor de logs
    if successful:
        st.markdown("---")
        st.header("📄 Explorador de Cambios")
        st.markdown("Revisa los cambios realizados en cada archivo")
        
        # Iterar sobre todos los archivos procesados (ordenados alfabéticamente)
        sorted_results = sorted(successful, key=lambda x: x['file'])
        
        for idx, result in enumerate(sorted_results):
            # Usar hash del log_file como key única
            file_key = str(result.get('log_file', idx))
            
            with st.expander(f"📄 {result['file']} ({result['changes']} cambios)", expanded=(idx == 0)):
                # Contenedor con key única para evitar caché de Streamlit
                container_key = f"log_container_{hash(file_key)}"
                
                # Usar el log_file que se guardó durante el procesamiento
                log_file = result.get('log_file')
                
                if log_file and Path(log_file).exists():
                    # Leer contenido del log
                    current_log_content = Path(log_file).read_text(encoding='utf-8')
                    
                    # Opciones de visualización (keys únicas por archivo)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        show_full = st.checkbox("Mostrar todos", value=False, key=f"full_{file_key}")
                    with col2:
                        max_changes = st.number_input(
                            "Cambios a mostrar", 
                            min_value=5, 
                            max_value=500, 
                            value=50,
                            step=5,
                            disabled=show_full,
                            key=f"max_{file_key}"
                        )
                    with col3:
                        st.download_button(
                            label="Descargar log",
                            data=current_log_content,
                            file_name=Path(log_file).name,
                            mime="text/plain",
                            use_container_width=True,
                            key=f"download_{file_key}"
                        )
                    
                    # Parsear cambios del log (scope local para este archivo)
                    def parse_and_display_log(log_text, show_all, max_to_show):
                        """Parse y muestra cambios - función local para aislar scope."""
                        all_changes_local = []
                        current_change_local = None
                        
                        for line in log_text.split('\n'):
                            if line.startswith("CAMBIO #"):
                                if current_change_local:
                                    all_changes_local.append(current_change_local)
                                current_change_local = {
                                    'numero': line.strip(),
                                    'ubicacion': '',
                                    'regla': '',
                                    'original': [],
                                    'convertido': [],
                                    'section': None
                                }
                            elif current_change_local:
                                line_stripped = line.strip()
                                if line_stripped.startswith("Línea:"):
                                    current_change_local['ubicacion'] = line_stripped.replace("Línea:", "").strip()
                                elif line_stripped.startswith("Regla:"):
                                    current_change_local['regla'] = line_stripped.replace("Regla:", "").strip()
                                elif line_stripped == "ORIGINAL:":
                                    current_change_local['section'] = 'original'
                                elif line_stripped == "CONVERTIDO:":
                                    current_change_local['section'] = 'convertido'
                                elif line.startswith("---"):
                                    continue
                                elif current_change_local['section'] == 'original' and line_stripped:
                                    current_change_local['original'].append(line_stripped)
                                elif current_change_local['section'] == 'convertido' and line_stripped:
                                    current_change_local['convertido'].append(line_stripped)
                        
                        if current_change_local:
                            all_changes_local.append(current_change_local)
                        
                        # Mostrar cambios
                        changes_to_show_local = all_changes_local if show_all else all_changes_local[:max_to_show]
                        st.markdown(f"**Mostrando {len(changes_to_show_local)} de {len(all_changes_local)} cambios**")
                        
                        for change in changes_to_show_local:
                            with st.container():
                                orig_text = ' '.join(change['original']) if change['original'] else 'N/A'
                                conv_text = ' '.join(change['convertido']) if change['convertido'] else 'N/A'
                                
                                st.markdown(f"**{change['numero']}**")
                                st.markdown(f"*Línea {change['ubicacion']} • {change['regla']}*")
                                st.markdown("**Original:**")
                                st.code(orig_text, language=None)
                                st.markdown("**Convertido:**")
                                st.code(conv_text, language=None)
                                st.markdown("---")
                        
                        return len(all_changes_local)
                    
                    # Llamar a la función
                    total_changes_in_file = parse_and_display_log(current_log_content, show_full, max_changes)
                    
                    # Estadísticas de reglas
                    rules_count = {}
                    for line in current_log_content.split('\n'):
                        if 'Regla aplicada:' in line or 'Regla:' in line:
                            rule = line.replace("Regla:", "").replace("Regla aplicada:", "").strip()
                            rules_count[rule] = rules_count.get(rule, 0) + 1
                    
                    if rules_count:
                        st.markdown("### Estadísticas")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Reglas más aplicadas:**")
                            sorted_rules = sorted(rules_count.items(), key=lambda x: x[1], reverse=True)
                            for rule, count in sorted_rules[:5]:
                                st.text(f"{rule}: {count} veces")
                        
                        with col2:
                            st.markdown("**Distribución:**")
                            for rule, count in sorted_rules[:5]:
                                percentage = (count / result['changes']) * 100
                                st.progress(percentage / 100, text=f"{rule}: {percentage:.1f}%")
                else:
                    st.warning("⚠️ No se encontró el archivo de log")


if __name__ == '__main__':
    main()
