"""
Esquemas Pydantic para validación del JSON consolidado
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class CompletenessResult(BaseModel):
    """Resultado del análisis de completitud."""
    summary: Dict[str, Any]
    columns_analysis: Dict[str, Any]
    critical_fields_missing: List[str]
    top_missing_columns: List[Dict[str, Any]]
    evaluation: Dict[str, Any]
    recommendations: List[Dict[str, str]]


class TypologyResult(BaseModel):
    """Resultado del análisis de tipología."""
    summary: Dict[str, Any]
    columns_typology: Dict[str, Any]
    inconsistencies: List[Dict[str, Any]]
    encoding_issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, str]]
    analysis_timestamp: str


class SemanticResult(BaseModel):
    """Resultado del análisis semántico."""
    summary: Dict[str, Any]
    edad_invalida: List[Dict[str, Any]]
    fechas_incoherentes: List[Dict[str, Any]]
    metodos_no_estandarizados: List[Dict[str, Any]]
    distribuciones_atipicas: List[Dict[str, Any]]
    valores_imposibles: List[Dict[str, Any]]
    recommendations: List[Dict[str, str]]
    analysis_timestamp: str


class GeospatialResult(BaseModel):
    """Resultado del análisis geoespacial."""
    summary: Dict[str, Any]
    coordinates_analysis: Optional[Dict[str, Any]]
    address_analysis: Optional[Dict[str, Any]]
    municipality_analysis: Optional[Dict[str, Any]]
    geocoding_capability: Dict[str, Any]
    clustering_potential: Dict[str, Any]
    required_fields: List[str]
    recommendations: List[Dict[str, str]]
    analysis_timestamp: str


class AnonymizationResult(BaseModel):
    """Resultado del análisis de anonimización."""
    summary: Dict[str, Any]
    entities_found: List[Dict[str, Any]]
    columns_with_pii: List[str]
    risk_assessment: Dict[str, Any]
    recommendations: List[Dict[str, str]]
    analysis_timestamp: str


class MLReadinessResult(BaseModel):
    """Resultado del análisis de preparación ML."""
    summary: Dict[str, Any]
    target_column: Optional[str]
    features_analysis: Dict[str, Any]
    balance_analysis: Optional[Dict[str, Any]]
    leakage_risks: List[Dict[str, Any]]
    correlation_analysis: Dict[str, Any]
    ml_viability: Dict[str, Any]
    model_suggestions: List[Dict[str, str]]
    recommendations: List[Dict[str, str]]
    analysis_timestamp: str


class ConsolidatedAnalysis(BaseModel):
    """Resultado consolidado de todos los análisis."""
    metadata: Dict[str, Any] = Field(
        description="Metadatos del dataset analizado"
    )
    completitud: CompletenessResult = Field(
        description="Análisis de completitud de datos"
    )
    tipos: TypologyResult = Field(
        description="Análisis de tipología de variables"
    )
    semantica: SemanticResult = Field(
        description="Análisis de coherencia semántica"
    )
    geoespacial: GeospatialResult = Field(
        description="Análisis de capacidad geoespacial"
    )
    anonimizacion: AnonymizationResult = Field(
        description="Análisis de riesgo de identificación"
    )
    ml: MLReadinessResult = Field(
        description="Análisis de preparación para ML"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "filename": "suicidios_2024.csv",
                    "rows": 1523,
                    "columns": 18,
                    "analysis_date": "2025-11-25T10:30:00Z"
                }
            }
        }
