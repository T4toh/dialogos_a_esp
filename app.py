"""
Punto de entrada para la aplicación Streamlit.
Wrapper para mantener compatibilidad con scripts existentes.

NOTA: El código de la interfaz se ha reorganizado en el módulo ui/
para mejor mantenibilidad. Este archivo solo importa y ejecuta la app.
"""

from ui.app import main

if __name__ == "__main__":
    main()
