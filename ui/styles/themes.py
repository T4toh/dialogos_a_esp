"""
Temas y estilos personalizados para la aplicación.
"""

import streamlit as st


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


def get_theme_colors(theme: str = "dark") -> dict:
    """Retorna los colores del tema para uso en componentes."""
    if theme == "dark":
        return {
            "orig_bg": "#3b2626",
            "conv_bg": "#12321a",
            "orig_color": "#ffdede",
            "conv_color": "#d9ffdf",
            "del_bg": "#4b0f0f",
            "ins_bg": "#143e19",
        }
    else:
        return {
            "orig_bg": "#fff5f5",
            "conv_bg": "#f0fff4",
            "orig_color": "#721c24",
            "conv_color": "#0b4118",
            "del_bg": "#f8d7da",
            "ins_bg": "#d4edda",
        }
