"""
Interfaz web con Streamlit para conversión de diálogos.
"""

import sys
from pathlib import Path
from typing import Dict, List

import streamlit as st

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.converter import DialogConverter
from src.odt_handler import is_odt_file

# Configuración de página
st.set_page_config(
    page_title="Conversor de Diálogos",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)


def count_words_in_file(file_path: Path) -> int:
    """Cuenta palabras en un archivo."""
    try:
        if is_odt_file(file_path):
            from src.odt_handler import ODTReader

            reader = ODTReader(file_path)
            text = reader.extract_text()
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

        words = text.split()
        return len(words)
    except Exception:
        return 0


def scan_directory(
    directory: Path, pattern: str = "*.*", recursive: bool = False
) -> List[Dict]:
    """Escanea directorio y retorna información de archivos."""
    files_info = []
    extensions = {".odt", ".txt"}

    if recursive:
        iterator = directory.rglob(pattern)
    else:
        iterator = directory.glob(pattern)

    for file_path in iterator:
        if file_path.is_file() and file_path.suffix in extensions:
            if not file_path.stem.endswith("_convertido"):
                word_count = count_words_in_file(file_path)
                files_info.append(
                    {
                        "path": file_path,
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "words": word_count,
                        "type": "ODT" if is_odt_file(file_path) else "TXT",
                    }
                )

    return sorted(files_info, key=lambda x: x["name"])


def format_size(size_bytes: int) -> str:
    """Formatea tamaño en bytes a formato legible."""
    # Trabajamos con un float local para evitar que la división cambie el tipo
    bytes_val = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"


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
                if item.is_dir() and not item.name.startswith("."):
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
            if path.exists() and str(path) not in [
                d.replace("📁 ", "").replace("⬆️ ", "") for d in dirs
            ]:
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
        st.markdown(
            """
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
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
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
        """,
            unsafe_allow_html=True,
        )


def main():
    """Función principal de la aplicación."""

    # Script para leer tema desde localStorage
    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )

    # Configurar tema - intentar recuperar de query params o usar default
    if "theme" not in st.session_state:
        # Intentar leer desde query params (para persistencia)
        query_params = st.query_params
        saved_theme = query_params.get("theme", "dark")
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
            if st.button(
                "🌙 Oscuro",
                use_container_width=True,
                type="primary" if st.session_state.theme == "dark" else "secondary",
            ):
                st.session_state.theme = "dark"
                st.query_params.theme = "dark"
                st.rerun()
        with col2:
            if st.button(
                "☀️ Claro",
                use_container_width=True,
                type="primary" if st.session_state.theme == "light" else "secondary",
            ):
                st.session_state.theme = "light"
                st.query_params.theme = "light"
                st.rerun()

        st.markdown("---")

        # Modo de selección de carpeta
        folder_mode = st.radio(
            "Modo de selección",
            ["Escribir ruta", "Selector de carpetas"],
            horizontal=True,
            label_visibility="collapsed",
        )

        # Selección de carpeta
        if folder_mode == "Selector de carpetas":
            # Obtener directorio actual desde session_state o usar "."
            if "current_folder" not in st.session_state:
                st.session_state["current_folder"] = str(Path(".").resolve())

            current_base = Path(st.session_state["current_folder"])
            if not current_base.exists():
                current_base = Path(".")
                st.session_state["current_folder"] = str(current_base.resolve())

            available_dirs = list_directories(current_base)

            # Mostrar carpeta actual
            st.text("📍 Ubicación actual:")
            st.code(str(current_base.resolve()), language=None)

            # Selector de carpeta
            selected_dir = st.selectbox(
                "Navegar a:",
                options=available_dirs,
                index=0,
                help="Selecciona una carpeta para navegar o usar",
                label_visibility="collapsed",
            )

            # Actualizar carpeta si se seleccionó una diferente
            if not selected_dir.startswith("─"):
                parsed_dir = parse_directory_choice(selected_dir)
                if parsed_dir != str(current_base):
                    st.session_state["current_folder"] = parsed_dir
                    st.rerun()

            input_dir = str(current_base.resolve())

        else:
            # Input de texto tradicional
            input_dir = st.text_input(
                "📂 Carpeta de entrada",
                value=st.session_state.get("input_dir_text", "."),
                help="Ruta a la carpeta con archivos a procesar",
            )
            # Actualizar current_folder cuando se cambia el texto
            if input_dir:
                st.session_state["current_folder"] = input_dir

        # Guardar en session_state
        st.session_state["input_dir_text"] = input_dir

        # Opciones de escaneo
        st.subheader("Opciones de búsqueda")

        file_filter = st.selectbox(
            "Tipo de archivo",
            options=["Todos (*.*)", "Solo ODT (*.odt)", "Solo TXT (*.txt)"],
            index=0,
        )

        recursive = st.checkbox(
            "Incluir subcarpetas", value=False, help="Buscar archivos en subcarpetas"
        )

        # Botón de escaneo
        scan_button = st.button("🔍 Escanear", type="primary", use_container_width=True)

    # Mapeo de filtro
    filter_map = {
        "Todos (*.*)": "*.*",
        "Solo ODT (*.odt)": "*.odt",
        "Solo TXT (*.txt)": "*.txt",
    }
    pattern = filter_map[file_filter]

    # Estado de la aplicación
    if "files_info" not in st.session_state:
        st.session_state.files_info = []
    if "selected_files" not in st.session_state:
        st.session_state.selected_files = set()

    # Escanear directorio
    if scan_button:
        # input_dir puede ser None (streamlit retorna Optional[str])
        input_path = Path(input_dir or ".")

        if not input_path.exists():
            st.error(f"❌ La carpeta '{input_dir}' no existe")
        elif not input_path.is_dir():
            st.error(f"❌ '{input_dir}' no es una carpeta")
        else:
            with st.spinner("Escaneando archivos..."):
                st.session_state.files_info = scan_directory(
                    input_path, pattern, recursive
                )
                # Seleccionar todos por defecto
                st.session_state.selected_files = {
                    f["path"] for f in st.session_state.files_info
                }

                # Limpiar cualquier checkbox previo en session_state
                for k in list(st.session_state.keys()):
                    if str(k).startswith("check_"):
                        try:
                            del st.session_state[k]
                        except Exception:
                            pass

                # Inicializar los checkboxes para que reflejen la selección
                for idx, _ in enumerate(st.session_state.files_info):
                    st.session_state[f"check_{idx}"] = True

            if st.session_state.files_info:
                st.success(
                    f"✅ Encontrados {len(st.session_state.files_info)} archivo(s)"
                )
            else:
                st.warning("⚠️ No se encontraron archivos")

    # Mostrar archivos encontrados
    if st.session_state.files_info:
        st.header("📋 Archivos Encontrados")

        # Estadísticas generales
        total_files = len(st.session_state.files_info)
        total_words = sum(f["words"] for f in st.session_state.files_info)
        total_size = sum(f["size"] for f in st.session_state.files_info)

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

        # Botones para seleccionar/deseleccionar todos
        col_all1, col_all2, col_all3 = st.columns([1, 1, 3])
        with col_all1:
            # Determinar si todos están seleccionados
            all_selected = len(st.session_state.selected_files) == total_files

            # Solo mostrar el botón relevante
            if not all_selected:
                if st.button("Seleccionar todos", key="select_all_button"):
                    st.session_state.selected_files = {
                        f["path"] for f in st.session_state.files_info
                    }

                    # Marcar todos los checkboxes en session_state
                    for idx, _ in enumerate(st.session_state.files_info):
                        st.session_state[f"check_{idx}"] = True
            else:
                if st.button("Deseleccionar todos", key="deselect_all_button"):
                    st.session_state.selected_files = set()

                    # Desmarcar todos los checkboxes en session_state
                    for idx, _ in enumerate(st.session_state.files_info):
                        st.session_state[f"check_{idx}"] = False

        # Mostrar cada archivo
        for idx, file_info in enumerate(st.session_state.files_info):
            col1, col2, col3, col4, col5 = st.columns([1, 4, 1, 1, 1])

            with col1:
                key = f"check_{idx}"

                # Estado previo según selected_files
                was_selected = file_info["path"] in st.session_state.selected_files

                # Crear checkbox sin pasar 'value' si ya existe la clave
                # en session_state
                if key in st.session_state:
                    is_selected = st.checkbox(
                        "Seleccionar", key=key, label_visibility="collapsed"
                    )
                else:
                    # Si la clave no existe, pasar el valor inicial
                    is_selected = st.checkbox(
                        "Seleccionar",
                        value=was_selected,
                        key=key,
                        label_visibility="collapsed",
                    )

                # Actualizar selección si cambió
                if is_selected and not was_selected:
                    st.session_state.selected_files.add(file_info["path"])
                elif not is_selected and was_selected:
                    st.session_state.selected_files.discard(file_info["path"])

            with col2:
                st.text(file_info["name"])

            with col3:
                st.text(file_info["type"])

            with col4:
                st.text(f"{file_info['words']:,} palabras")

            with col5:
                st.text(format_size(file_info["size"]))

        st.markdown("---")

        # Configuración de procesamiento
        st.header("⚙️ Configuración de Procesamiento")

        col1, col2 = st.columns(2)

        with col1:
            # input_dir puede ser None; usar '.' como fallback para Path
            default_output = str(Path(input_dir or ".") / "convertidos")
            output_dir = st.text_input(
                "📁 Carpeta de salida",
                value=default_output,
                help="Carpeta donde se guardarán los archivos convertidos",
            )

        with col2:
            st.write("")  # Espaciado

        # Botón de procesamiento
        if len(st.session_state.selected_files) > 0:
            if st.button(
                "▶️ Iniciar Conversión", type="primary", use_container_width=True
            ):
                process_files(st.session_state.selected_files, Path(output_dir))
        else:
            st.warning("⚠️ Selecciona al menos un archivo para procesar")

    # Mostrar resultados si existen en session_state
    if (
        "processing_results" in st.session_state
        and st.session_state["processing_results"]
    ):
        display_results(
            st.session_state["processing_results"],
            Path(st.session_state["output_directory"]),
        )

    elif "files_info" not in st.session_state:
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
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                converted_text, logger = converter.convert(text)

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(converted_text)

                log_content = logger.generate_report()

            # Guardar log
            log_file = output_dir / f"{file_path.stem}_convertido.log.txt"
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(log_content)

            # Guardar also a structured JSON log for easier programmatic inspection
            # Prepare a variable for the structured JSON log path; keep it
            # initialized so linters / type-checkers don't complain about
            # possibly unbound local variables.
            json_file_path = None

            try:
                json_log_file = output_dir / f"{file_path.stem}_convertido.log.json"
                # converter.logger may not exist for non-ODT flows; guard before saving
                if hasattr(converter, "logger") and converter.logger.changes:
                    converter.logger.save_structured_log(json_log_file)
                    json_file_path = json_log_file
            except Exception:
                # Non-critical: ignore failures saving structured log
                pass

            results.append(
                {
                    "file": file_path.name,
                    "success": True,
                    "changes": len(converter.logger.changes),
                    "output": output_file,
                    "log_file": log_file,
                    "json_log": str(json_file_path) if json_file_path else None,
                }
            )

        except Exception as e:
            results.append({"file": file_path.name, "success": False, "error": str(e)})

    # Completar progreso
    progress_bar.progress(1.0)
    status_text.text("✅ Procesamiento completado")

    # Guardar resultados en session_state para persistencia
    st.session_state["processing_results"] = results
    st.session_state["output_directory"] = str(output_dir)

    # Los resultados se mostrarán automáticamente en el re-run


def display_results(results: List[Dict], output_dir: Path):
    """Muestra los resultados del procesamiento."""
    st.markdown("---")
    st.subheader("📊 Resultados")

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    total_changes = sum(r.get("changes", 0) for r in successful)

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
        sorted_results = sorted(successful, key=lambda x: x["file"])

        for idx, result in enumerate(sorted_results):
            # Usar hash del log_file como key única
            file_key = str(result.get("log_file", idx))

            with st.expander(
                f"📄 {result['file']} ({result['changes']} cambios)",
                expanded=(idx == 0),
            ):
                # Usar el log_file que se guardó durante el procesamiento
                log_file = result.get("log_file")

                if log_file and Path(log_file).exists():
                    # Prefer structured JSON log when available
                    json_log_path = None
                    if result.get("json_log"):
                        try:
                            json_log_str = result.get("json_log")
                            if json_log_str:
                                json_log_path = Path(json_log_str)
                            else:
                                json_log_path = None
                        except Exception:
                            json_log_path = None
                    else:
                        # fallback: replace .log.txt with .log.json if present
                        try:
                            candidate = str(log_file)
                            if candidate.endswith(".log.txt"):
                                candidate_json = (
                                    candidate[: -len(".log.txt")] + ".log.json"
                                )
                                json_log_path = Path(candidate_json)
                        except Exception:
                            json_log_path = None

                    if json_log_path and json_log_path.exists():
                        try:
                            structured = json_log_path.read_text(encoding="utf-8")
                            import json as _json

                            entries = _json.loads(structured)
                        except Exception:
                            entries = None
                    else:
                        entries = None

                    # Leer contenido del textual log for fallback
                    current_log_content = Path(log_file).read_text(encoding="utf-8")

                    # Opciones de visualización (keys únicas por archivo)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        show_full = st.checkbox(
                            "Mostrar todos", value=False, key=f"full_{file_key}"
                        )
                    with col2:
                        max_changes = st.number_input(
                            "Cambios a mostrar",
                            min_value=5,
                            max_value=500,
                            value=50,
                            step=5,
                            disabled=show_full,
                            key=f"max_{file_key}",
                        )
                    with col3:
                        st.download_button(
                            label="Descargar log",
                            data=current_log_content,
                            file_name=Path(log_file).name,
                            mime="text/plain",
                            use_container_width=True,
                            key=f"download_{file_key}",
                        )

                    # Opciones adicionales de visualización
                    col4, col5 = st.columns([1, 2])
                    with col4:
                        show_diff_raw = st.checkbox(
                            "Mostrar diff crudo",
                            value=False,
                            key=f"showdiffraw_{file_key}",
                        )
                    with col5:
                        inline_highlight = st.checkbox(
                            "Resaltar cambios inline",
                            value=True,
                            key=f"inline_{file_key}",
                        )

                    # Parsear cambios del log (scope local para este archivo)
                    def build_inline_diff_html(a: str, b: str) -> str:
                        import difflib

                        theme = st.session_state.get("theme", "dark")
                        if theme == "dark":
                            orig_color = "#ffdede"
                            conv_color = "#d9ffdf"
                        else:
                            orig_color = "#721c24"
                            conv_color = "#0b4118"

                        a_words = [w for w in a.split()]
                        b_words = [w for w in b.split()]
                        matcher = difflib.SequenceMatcher(None, a_words, b_words)
                        parts = []

                        def _make_span(text, bg, color, strike=False):
                            style_parts = [f"background:{bg};", f"color:{color};"]
                            if strike:
                                style_parts.append("text-decoration:line-through;")
                            style_parts.append("padding:2px;")
                            style_parts.append("border-radius:3px;")
                            style_parts.append("margin-right:2px;")
                            style = "".join(style_parts)
                            return f"<span style='{style}'>{text}</span>"

                        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                            if tag == "equal":
                                parts.append(" ".join(a_words[i1:i2]))
                            elif tag == "replace":
                                removed = " ".join(a_words[i1:i2])
                                added = " ".join(b_words[j1:j2])
                                if removed:
                                    parts.append(
                                        _make_span(
                                            removed,
                                            "#4b0f0f",
                                            orig_color,
                                            True,
                                        )
                                    )
                                if added:
                                    parts.append(
                                        _make_span(
                                            added,
                                            "#143e19",
                                            conv_color,
                                        )
                                    )
                            elif tag == "delete":
                                removed = " ".join(a_words[i1:i2])
                                parts.append(
                                    _make_span(removed, "#4b0f0f", orig_color, True)
                                )
                            elif tag == "insert":
                                added = " ".join(b_words[j1:j2])
                                parts.append(
                                    _make_span(
                                        added,
                                        "#143e19",
                                        conv_color,
                                    )
                                )
                        return (
                            '<div style="white-space:pre-wrap;font-family:monospace;">'
                            + " ".join(parts)
                            + "</div>"
                        )

                    def parse_and_display_log(
                        log_text,
                        show_all,
                        max_to_show,
                        show_diff_raw=False,
                        inline_highlight=True,
                    ):
                        """Parse y muestra cambios - función local para aislar scope.

                        Ahora captura bloques completos (preserva saltos de línea)
                        y muestra un diff unificado cuando esté disponible.
                        """
                        all_changes_local = []
                        current_change_local = None
                        section = None

                        for raw in log_text.splitlines():
                            # Detectar inicio de cambio
                            if raw.startswith("CAMBIO #"):
                                if current_change_local:
                                    all_changes_local.append(current_change_local)
                                current_change_local = {
                                    "numero": raw.strip(),
                                    "ubicacion": "",
                                    "regla": "",
                                    "original": [],
                                    "convertido": [],
                                    "diff": [],
                                }
                                section = None
                                continue

                            if current_change_local is None:
                                continue

                            stripped = raw.strip()
                            if stripped.startswith("Línea:"):
                                current_change_local["ubicacion"] = stripped.replace(
                                    "Línea:", ""
                                ).strip()
                                continue
                            if stripped.startswith("Regla:"):
                                current_change_local["regla"] = stripped.replace(
                                    "Regla:", ""
                                ).strip()
                                continue

                            if stripped == "ORIGINAL:":
                                section = "original"
                                continue
                            if stripped == "CONVERTIDO:":
                                section = "convertido"
                                continue
                            if stripped == "DIFF (unified):":
                                section = "diff"
                                continue

                            # Separator line - finalize current change
                            if stripped.startswith("-----"):
                                if current_change_local:
                                    all_changes_local.append(current_change_local)
                                    current_change_local = None
                                section = None
                                continue

                            # Según la sección actual, agregar la línea
                            # (preservando saltos)
                            if section == "original":
                                # Quitar prefijo de dos espacios que el logger añade
                                line_content = raw[2:] if raw.startswith("  ") else raw
                                current_change_local["original"].append(line_content)
                            elif section == "convertido":
                                line_content = raw[2:] if raw.startswith("  ") else raw
                                current_change_local["convertido"].append(line_content)
                            elif section == "diff":
                                line_content = raw[2:] if raw.startswith("  ") else raw
                                current_change_local["diff"].append(line_content)

                        if current_change_local:
                            all_changes_local.append(current_change_local)

                        # Mostrar cambios
                        changes_to_show_local = (
                            all_changes_local
                            if show_all
                            else all_changes_local[:max_to_show]
                        )
                        st.markdown(
                            "**Mostrando "
                            + f"{len(changes_to_show_local)}"
                            + f" de {len(all_changes_local)} cambios**"
                        )

                        for change in changes_to_show_local:
                            with st.container():
                                orig_text = (
                                    "\n".join(change["original"]).strip()
                                    if change["original"]
                                    else "N/A"
                                )
                                conv_text = (
                                    "\n".join(change["convertido"]).strip()
                                    if change["convertido"]
                                    else "N/A"
                                )
                                diff_text = (
                                    "\n".join(change["diff"]).strip()
                                    if change["diff"]
                                    else None
                                )

                                st.markdown(f"**{change['numero']}**")
                                st.markdown(
                                    f"*Línea {change['ubicacion']} • {change['regla']}*"
                                )

                                # Paleta dependiente del tema
                                theme = st.session_state.get("theme", "dark")
                                if theme == "dark":
                                    orig_bg = "#3b2626"
                                    conv_bg = "#12321a"
                                    orig_color = "#ffdede"
                                    conv_color = "#d9ffdf"
                                else:
                                    orig_bg = "#fff5f5"
                                    conv_bg = "#f0fff4"
                                    orig_color = "#721c24"
                                    conv_color = "#0b4118"

                                orig_block = orig_text
                                conv_block = conv_text

                                # Inline highlight helper (word-level)
                                def build_inline_diff_html(a: str, b: str) -> str:
                                    import difflib

                                    def _make_span(text, bg, color, strike=False):
                                        style_parts = [
                                            f"background:{bg};",
                                            f"color:{color};",
                                        ]
                                        if strike:
                                            style_parts.append(
                                                "text-decoration:line-through;"
                                            )
                                        style_parts.append("padding:2px;")
                                        style_parts.append("border-radius:3px;")
                                        style_parts.append("margin-right:2px;")
                                        style = "".join(style_parts)
                                        return f"<span style='{style}'>{text}</span>"

                                    a_words = [w for w in a.split()]
                                    b_words = [w for w in b.split()]
                                    matcher = difflib.SequenceMatcher(
                                        None, a_words, b_words
                                    )
                                    parts = []
                                    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                                        if tag == "equal":
                                            parts.append(" ".join(a_words[i1:i2]))
                                        elif tag == "replace":
                                            removed = " ".join(a_words[i1:i2])
                                            added = " ".join(b_words[j1:j2])
                                            if removed:
                                                parts.append(
                                                    _make_span(
                                                        removed,
                                                        "#4b0f0f",
                                                        orig_color,
                                                        True,
                                                    )
                                                )
                                            if added:
                                                parts.append(
                                                    _make_span(
                                                        added,
                                                        "#143e19",
                                                        conv_color,
                                                    )
                                                )
                                        elif tag == "delete":
                                            removed = " ".join(a_words[i1:i2])
                                            parts.append(
                                                _make_span(
                                                    removed, "#4b0f0f", orig_color, True
                                                )
                                            )
                                        elif tag == "insert":
                                            added = " ".join(b_words[j1:j2])
                                            parts.append(
                                                _make_span(
                                                    added,
                                                    "#143e19",
                                                    conv_color,
                                                )
                                            )
                                    return (
                                        '<div style="white-space:pre-wrap;'
                                        'font-family:monospace;">'
                                        + " ".join(parts)
                                        + "</div>"
                                    )

                                if inline_highlight:
                                    try:
                                        inline_html = build_inline_diff_html(
                                            orig_block, conv_block
                                        )
                                        inline_title = (
                                            "<div style='margin-bottom:6px'>"
                                            "<strong>Inline diff:</strong></div>"
                                        )
                                        st.markdown(
                                            inline_title + inline_html,
                                            unsafe_allow_html=True,
                                        )
                                        # Also show the full original/converted blocks
                                        # below
                                        # for context
                                        orig_style = (
                                            f"<div style='background:{orig_bg};"
                                            f"color:{orig_color};"
                                            "border-radius:6px;padding:10px;white-space:pre-wrap;"
                                            "font-family:monospace;'><strong>Original:</strong>\n"
                                        )
                                        orig_html = orig_style + orig_block + "</div>"
                                        st.markdown(orig_html, unsafe_allow_html=True)
                                        conv_style = (
                                            f"<div style='background:{conv_bg};"
                                            f"color:{conv_color};"
                                            "border-radius:6px;padding:10px;white-space:pre-wrap;"
                                            "font-family:monospace;'><strong>Convertido:</strong>\n"
                                        )
                                        conv_html = conv_style + conv_block + "</div>"
                                        st.markdown(conv_html, unsafe_allow_html=True)
                                    except Exception:
                                        st.markdown(
                                            (
                                                f"<div style='background:{orig_bg};"
                                                f"color:{orig_color};"
                                                "border-radius:6px;padding:10px;white-space:pre-wrap;"
                                                "font-family:monospace;'>"
                                                f"<strong>Original:</strong>\n{orig_block}</div>"
                                            ),
                                            unsafe_allow_html=True,
                                        )
                                        st.markdown(
                                            (
                                                f"<div style='background:{conv_bg};"
                                                f"color:{conv_color};"
                                                "border-radius:6px;padding:10px;white-space:pre-wrap;"
                                                "font-family:monospace;'>"
                                                f"<strong>Convertido:</strong>\n{conv_block}</div>"
                                            ),
                                            unsafe_allow_html=True,
                                        )
                                else:
                                    st.markdown(
                                        (
                                            f"<div style='background:{orig_bg};"
                                            f"color:{orig_color};"
                                            "border-radius:6px;padding:10px;white-space:pre-wrap;"
                                            "font-family:monospace;'><strong>Original:</strong>\n"
                                            + orig_block
                                            + "</div>"
                                        ),
                                        unsafe_allow_html=True,
                                    )
                                    st.markdown(
                                        (
                                            f"<div style='background:{conv_bg};"
                                            f"color:{conv_color};"
                                            "border-radius:6px;padding:10px;white-space:pre-wrap;"
                                            "font-family:monospace;'><strong>Convertido:</strong>\n"
                                            + conv_block
                                            + "</div>"
                                        ),
                                        unsafe_allow_html=True,
                                    )

                                # Mostrar diff unificado solo si el usuario lo pidió
                                if diff_text and show_diff_raw:
                                    st.markdown("**Diff (unified):**")
                                    st.code(diff_text, language="diff")

                                st.markdown("---")

                        return len(all_changes_local)

                    # If we have structured entries prefer them
                    # (use precise spans if available)
                    def build_inline_html_from_spans(
                        orig: str, conv: str, orig_span, conv_span, theme="dark"
                    ) -> str:
                        import html as _html

                        # Colors depending on theme
                        if theme == "dark":
                            orig_color = "#ffdede"
                            conv_color = "#d9ffdf"
                            del_bg = "#4b0f0f"
                            ins_bg = "#143e19"
                        else:
                            orig_color = "#721c24"
                            conv_color = "#0b4118"
                            del_bg = "#f8d7da"
                            ins_bg = "#d4edda"

                        # If spans available, wrap exact substrings
                        # Support one-sided spans (only original or only converted)
                        if orig_span and conv_span:
                            ostart, oend = orig_span
                            cstart, cend = conv_span

                            before_o = _html.escape(orig[:ostart])
                            frag_o = _html.escape(orig[ostart:oend])
                            after_o = _html.escape(orig[oend:])

                            before_c = _html.escape(conv[:cstart])
                            frag_c = _html.escape(conv[cstart:cend])
                            after_c = _html.escape(conv[cend:])

                            parts = []
                            # Original with deletion highlight
                            orig_template = (
                                "<div style='background:transparent;"
                                "color:{color};"
                                ""
                                "white-space:pre-wrap;font-family:monospace;'>"
                                "<strong>Original:</strong><br>"
                                "{before}<span style='background:{del_bg};"
                                "color:{color};text-decoration:line-through;"
                                "padding:2px;border-radius:3px;'>{frag}</span>"
                                "{after}</div>"
                            )
                            parts.append(
                                orig_template.format(
                                    color=orig_color,
                                    before=before_o,
                                    frag=frag_o,
                                    del_bg=del_bg,
                                    after=after_o,
                                )
                            )
                            # Converted with insertion highlight
                            conv_template = (
                                "<div style='background:transparent;color:{color};"
                                "white-space:pre-wrap;font-family:monospace;'>"
                                "<strong>Convertido:</strong><br>"
                                "{before}<span style='background:{ins_bg};"
                                "color:{color};padding:2px;border-radius:3px;'>{frag}</span>{after}</div>"
                            )
                            parts.append(
                                conv_template.format(
                                    color=conv_color,
                                    before=before_c,
                                    frag=frag_c,
                                    ins_bg=ins_bg,
                                    after=after_c,
                                )
                            )

                            return (
                                "<div style='margin-bottom:6px'>"
                                + "".join(parts)
                                + "</div>"
                            )

                        # If one side only is present, highlight that side
                        # and show the other block
                        elif orig_span or conv_span:
                            ostart = oend = cstart = cend = None
                            # default empty values so static analysis
                            # knows they are defined
                            before_c = frag_c = after_c = ""
                            if orig_span:
                                ostart, oend = orig_span
                            if conv_span:
                                cstart, cend = conv_span

                            parts = []
                            if orig_span:
                                before_o = _html.escape(orig[:ostart])
                                frag_o = _html.escape(orig[ostart:oend])
                                after_o = _html.escape(orig[oend:])
                                parts.append(
                                    (
                                        "<div style='background:transparent;'"
                                        "color:{color};"
                                        "white-space:pre-wrap;font-family:monospace;'>"
                                        "<strong>Original:</strong><br>"
                                        "{before}<span style='background:{del_bg};"
                                        "color:{color};text-decoration:line-through;"
                                        "padding:2px;border-radius:3px;'>{frag}</span>"
                                        "{after}</div>"
                                    ).format(
                                        color=orig_color,
                                        before=before_o,
                                        frag=frag_o,
                                        del_bg=del_bg,
                                        after=after_o,
                                    )
                                )

                            if conv_span:
                                before_c = _html.escape(conv[:cstart])
                                frag_c = _html.escape(conv[cstart:cend])
                                after_c = _html.escape(conv[cend:])
                            conv_template = (
                                "<div style='background:transparent;"
                                "color:{color};"
                                "white-space:pre-wrap;font-family:monospace;'>"
                                "<strong>Convertido:</strong><br>"
                                "{before}<span style='background:{ins_bg};"
                                "color:{color};padding:2px;border-radius:3px;'>{frag}</span>{after}</div>"
                            )
                            if conv_span:
                                parts.append(
                                    conv_template.format(
                                        color=conv_color,
                                        before=before_c,
                                        frag=frag_c,
                                        ins_bg=ins_bg,
                                        after=after_c,
                                    )
                                )

                            return (
                                "<div style='margin-bottom:6px'>"
                                + "".join(parts)
                                + "</div>"
                            )

                        # Fallback to word-level diff
                        try:
                            return build_inline_diff_html(orig, conv)
                        except Exception:
                            return (
                                "<div><pre>"
                                + _html.escape(orig)
                                + "\n---\n"
                                + _html.escape(conv)
                                + "</pre></div>"
                            )

                    # If we have structured entries, render them
                    if entries is not None:
                        st.markdown(
                            "**Mostrando "
                            + (
                                f"{min(len(entries), max_changes)}"
                                if not show_full
                                else f"{len(entries)}"
                            )
                            + f" de {len(entries)} cambios (JSON)**"
                        )
                        display_list = entries if show_full else entries[:max_changes]
                        for idx_e, entry in enumerate(display_list, 1):
                            with st.container():
                                st.markdown(f"**CAMBIO #{idx_e}**")
                                st.markdown(
                                    "*Línea ~"
                                    + str(entry.get("line"))
                                    + " • "
                                    + str(entry.get("rule"))
                                    + "*"
                                )

                                orig_text = entry.get("original", "")
                                conv_text = entry.get("converted", "")
                                orig_span = entry.get("original_span")
                                conv_span = entry.get("converted_span")

                                theme = st.session_state.get("theme", "dark")
                                inline_html = build_inline_html_from_spans(
                                    orig_text, conv_text, orig_span, conv_span, theme
                                )
                                # Mostrar la fuente de los spans (útil para depuración)
                                span_source_line = ""
                                if entry.get("original_span_source") or entry.get(
                                    "converted_span_source"
                                ):
                                    span_source_line = (
                                        "(span: orig="
                                        + str(entry.get("original_span_source"))
                                        + ", conv="
                                        + str(entry.get("converted_span_source"))
                                        + ")"
                                    )
                                    st.markdown(
                                        "<small style='color:gray'>"
                                        + span_source_line
                                        + "</small>",
                                        unsafe_allow_html=True,
                                    )
                                st.markdown(inline_html, unsafe_allow_html=True)

                                if entry.get("diff") and show_diff_raw:
                                    st.markdown("**Diff (unified):**")
                                    st.code(entry.get("diff"), language="diff")

                                st.markdown("---")
                    else:
                        # Fallback to the legacy textual parser
                        parse_and_display_log(
                            current_log_content,
                            show_full,
                            max_changes,
                            show_diff_raw,
                            inline_highlight,
                        )

                    # Estadísticas de reglas
                    rules_count = {}
                    for line in current_log_content.split("\n"):
                        if "Regla aplicada:" in line or "Regla:" in line:
                            rule = (
                                line.replace("Regla:", "")
                                .replace("Regla aplicada:", "")
                                .strip()
                            )
                            rules_count[rule] = rules_count.get(rule, 0) + 1

                    if rules_count:
                        st.markdown("### Estadísticas")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Reglas más aplicadas:**")
                            sorted_rules = sorted(
                                rules_count.items(), key=lambda x: x[1], reverse=True
                            )
                            for rule, count in sorted_rules[:5]:
                                st.text(f"{rule}: {count} veces")

                        with col2:
                            st.markdown("**Distribución:**")
                            for rule, count in sorted_rules[:5]:
                                percentage = (count / result["changes"]) * 100
                                st.progress(
                                    percentage / 100, text=f"{rule}: {percentage:.1f}%"
                                )
                else:
                    st.warning("⚠️ No se encontró el archivo de log")


if __name__ == "__main__":
    main()
