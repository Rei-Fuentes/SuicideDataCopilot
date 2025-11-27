"""
CUIDAR IA - Policy Copilot
Punto de entrada principal de la aplicación Streamlit

Este archivo sirve como punto de entrada para la aplicación siguiendo
la estructura estándar de proyectos ML.
"""

import sys
from pathlib import Path

# Agregar el directorio app al path para imports
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Importar y ejecutar la aplicación principal
from app import main

if __name__ == "__main__":
    # La aplicación se ejecuta automáticamente cuando Streamlit carga este archivo
    pass
