"""
Capa de Integración y Orquestación
Ejecuta analizadores en paralelo y anonimiza datos
"""

from .orchestrator import (
    run_parallel_analysis,
    run_single_analyzer,
    get_analysis_summary
)
from .anonymizer import (
    anonymize_dataframe,
    generate_anonymization_report,
    validate_anonymization
)
from .schema import ConsolidatedAnalysis

__all__ = [
    "run_parallel_analysis",
    "run_single_analyzer",
    "get_analysis_summary",
    "anonymize_dataframe",
    "generate_anonymization_report",
    "validate_anonymization",
    "ConsolidatedAnalysis"
]
