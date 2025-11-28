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

# Ejecutar el módulo main directamente
import runpy
runpy.run_module("main", run_name="__main__")
