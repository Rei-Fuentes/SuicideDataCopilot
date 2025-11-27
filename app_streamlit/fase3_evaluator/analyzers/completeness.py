"""
Analizador de Completitud de Datos
Evalúa valores faltantes, patrones de ausencia y campos críticos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

from config import settings, CRITICAL_FIELDS_SUICIDE_DATA


def analyze_completeness(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analiza la completitud de una base de datos.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con resultados del análisis de completitud
        
    Raises:
        ValueError: Si el DataFrame está vacío
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío")
    
    total_cells = df.size
    missing_cells = df.isna().sum().sum()
    missing_percentage = (missing_cells / total_cells) * 100
    
    # Análisis por columna
    columns_analysis = {}
    critical_fields_missing = []
    
    for col in df.columns:
        missing_count = df[col].isna().sum()
        missing_rate = missing_count / len(df)
        
        # Detectar patrones de ausencia
        pattern = _detect_missing_pattern(df, col)
        
        columns_analysis[col] = {
            "missing_count": int(missing_count),
            "missing_rate": float(missing_rate),
            "total_records": len(df),
            "pattern": pattern,
            "is_critical": _is_critical_field(col)
        }
        
        # Verificar campos críticos
        if _is_critical_field(col) and missing_rate > settings.COMPLETENESS_CRITICAL_THRESHOLD:
            critical_fields_missing.append(col)
    
    # Top 5 columnas con más valores faltantes
    top_missing = sorted(
        [(col, data["missing_rate"]) for col, data in columns_analysis.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    # Evaluación general
    evaluation = _evaluate_completeness(missing_percentage, len(critical_fields_missing))
    
    return {
        "summary": {
            "total_cells": int(total_cells),
            "missing_cells": int(missing_cells),
            "missing_percentage": float(missing_percentage),
            "total_columns": len(df.columns),
            "total_rows": len(df),
            "analysis_timestamp": datetime.now().isoformat()
        },
        "columns_analysis": columns_analysis,
        "critical_fields_missing": critical_fields_missing,
        "top_missing_columns": [
            {"column": col, "missing_rate": float(rate)} 
            for col, rate in top_missing
        ],
        "evaluation": evaluation,
        "recommendations": _generate_completeness_recommendations(
            missing_percentage,
            critical_fields_missing,
            columns_analysis
        )
    }


def _detect_missing_pattern(df: pd.DataFrame, column: str) -> str:
    """
    Detecta patrones en los valores faltantes de una columna.
    
    Returns:
        Descripción del patrón detectado
    """
    if df[column].isna().sum() == 0:
        return "sin_valores_faltantes"
    
    if df[column].isna().all():
        return "columna_completamente_vacia"
    
    # Detectar si los valores faltantes están concentrados
    missing_mask = df[column].isna()
    
    # Patrón temporal (si hay índice datetime o columna de fecha)
    if pd.api.types.is_datetime64_any_dtype(df.index):
        # Agrupar por mes y ver si hay concentración
        monthly_missing = df[missing_mask].groupby(df.index.to_period('M')).size()
        if len(monthly_missing) > 0:
            total_missing = missing_mask.sum()
            max_monthly = monthly_missing.max()
            if max_monthly / total_missing > 0.5:
                return f"concentrado_temporal (50%+ en un mes)"
    
    # Patrón de bloques consecutivos
    consecutive_missing = missing_mask.astype(int).diff().ne(0).cumsum()
    if len(consecutive_missing[missing_mask].unique()) < 5 and missing_mask.sum() > 10:
        return "bloques_consecutivos"
    
    # Patrón aleatorio
    return "aleatorio"


def _is_critical_field(column_name: str) -> bool:
    """
    Determina si un campo es crítico para análisis de suicidio.
    
    Returns:
        True si el campo es crítico
    """
    column_lower = column_name.lower().strip()
    
    # Verificar contra lista de campos críticos
    for critical in CRITICAL_FIELDS_SUICIDE_DATA:
        if critical.lower() in column_lower:
            return True
    
    # Verificar palabras clave adicionales
    critical_keywords = [
        "fecha", "edad", "sexo", "genero", "metodo", "municipio", 
        "localidad", "tipo", "intento", "consumado", "fallec"
    ]
    
    return any(keyword in column_lower for keyword in critical_keywords)


def _evaluate_completeness(missing_percentage: float, critical_missing_count: int) -> Dict[str, Any]:
    """
    Evalúa el nivel de completitud general.
    
    Returns:
        Diccionario con evaluación y score
    """
    # Score de completitud (0-100, inverso al % de faltantes)
    score = max(0, 100 - missing_percentage)
    
    # Penalización por campos críticos faltantes
    if critical_missing_count > 0:
        penalty = min(30, critical_missing_count * 10)  # Hasta -30 puntos
        score = max(0, score - penalty)
    
    # Determinar nivel
    if score >= 90:
        level = "excelente"
        message = "La base tiene excelente completitud"
    elif score >= 75:
        level = "bueno"
        message = "La completitud es buena pero mejorable"
    elif score >= 60:
        level = "aceptable"
        message = "La completitud es aceptable pero requiere atención"
    elif score >= 40:
        level = "deficiente"
        message = "La completitud es deficiente"
    else:
        level = "critico"
        message = "La completitud es crítica - datos no confiables"
    
    return {
        "score": float(score),
        "level": level,
        "message": message,
        "critical_issues_count": critical_missing_count,
        "meets_threshold": score >= (settings.COMPLETENESS_THRESHOLD * 100)
    }


def _generate_completeness_recommendations(
    missing_percentage: float,
    critical_fields: List[str],
    columns_analysis: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Genera recomendaciones específicas basadas en el análisis.
    
    Returns:
        Lista de recomendaciones con prioridad y acción
    """
    recommendations = []
    
    # Recomendación crítica: campos críticos faltantes
    if critical_fields:
        recommendations.append({
            "priority": "critica",
            "field": ", ".join(critical_fields),
            "issue": f"Campo(s) crítico(s) con >30% de datos faltantes",
            "action": "Recuperar estos datos de fuentes primarias (registros hospitalarios, policiales, registro civil)",
            "impact": "Alto - Sin estos datos, análisis de riesgo y patrones serán poco confiables"
        })
    
    # Recomendación alta: completitud general baja
    if missing_percentage > 20:
        recommendations.append({
            "priority": "alta",
            "field": "general",
            "issue": f"Completitud general del {100 - missing_percentage:.1f}% (objetivo: >85%)",
            "action": "Implementar protocolos de registro obligatorio en el punto de captura",
            "impact": "Medio - Limita análisis estadísticos robustos"
        })
    
    # Detectar columnas con patrones temporales
    temporal_issues = [
        col for col, data in columns_analysis.items()
        if "temporal" in data["pattern"] and data["missing_rate"] > 0.1
    ]
    
    if temporal_issues:
        recommendations.append({
            "priority": "media",
            "field": ", ".join(temporal_issues[:3]),
            "issue": "Datos faltantes concentrados en períodos específicos",
            "action": "Revisar cambios en protocolos de registro o problemas sistémicos en esos períodos",
            "impact": "Medio - Puede sesgar análisis de tendencias temporales"
        })
    
    # Columnas completamente vacías
    empty_cols = [
        col for col, data in columns_analysis.items()
        if data["pattern"] == "columna_completamente_vacia"
    ]
    
    if empty_cols:
        recommendations.append({
            "priority": "baja",
            "field": ", ".join(empty_cols),
            "issue": "Columna(s) sin ningún dato registrado",
            "action": "Eliminar estas columnas o iniciar su captura sistemática",
            "impact": "Bajo - No aportan información actualmente"
        })
    
    return recommendations


# ==================== FUNCIONES AUXILIARES PARA VISUALIZACIÓN ====================

def get_missing_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara datos para heatmap de valores faltantes.
    
    Returns:
        DataFrame con máscara booleana de valores faltantes
    """
    return df.isna().astype(int)


def get_completeness_by_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula porcentaje de completitud por columna.
    
    Returns:
        DataFrame con columnas y su % de completitud
    """
    completeness = ((1 - df.isna().mean()) * 100).sort_values()
    return pd.DataFrame({
        'columna': completeness.index,
        'completitud': completeness.values
    })
