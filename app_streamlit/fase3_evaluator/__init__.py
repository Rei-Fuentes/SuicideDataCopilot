"""
CUIDAR IA - Fase 3: Evaluador Automático de Bases de Datos
Módulo principal de evaluación de calidad de datos para prevención del suicidio
"""

__version__ = "0.1.0"
__author__ = "Reiner Fuentes Ferrada"

from .analyzers import (
    analyze_completeness,
    analyze_typology,
    analyze_semantic,
    analyze_geospatial,
    analyze_anonymization,
    analyze_ml_readiness
)

from .integration import run_parallel_analysis, anonymize_dataframe
from .agent import generate_diagnosis

__all__ = [
    "analyze_completeness",
    "analyze_typology",
    "analyze_semantic",
    "analyze_geospatial",
    "analyze_anonymization",
    "analyze_ml_readiness",
    "run_parallel_analysis",
    "anonymize_dataframe",
    "generate_diagnosis"
]
