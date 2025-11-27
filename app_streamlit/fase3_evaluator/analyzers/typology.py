"""
Analizador de Tipología de Variables
Identifica tipos reales, detecta errores de tipado y codificaciones inconsistentes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re


def analyze_typology(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analiza la tipología de variables en el DataFrame.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con análisis de tipos de datos
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío")
    
    columns_typology = {}
    inconsistencies = []
    encoding_issues = []
    
    for col in df.columns:
        analysis = _analyze_column_type(df, col)
        columns_typology[col] = analysis
        
        # Detectar inconsistencias
        if analysis["has_inconsistency"]:
            inconsistencies.append({
                "column": col,
                "expected": analysis["inferred_type"],
                "found": analysis["detected_types"],
                "inconsistency_rate": analysis["inconsistency_rate"],
                "examples": analysis["inconsistent_examples"][:3]
            })
        
        # Detectar problemas de encoding
        if analysis["encoding_issue"]:
            encoding_issues.append({
                "column": col,
                "issue": analysis["encoding_issue"],
                "examples": analysis["encoding_examples"][:3]
            })
    
    # Resumen general
    summary = _generate_typology_summary(columns_typology, inconsistencies, encoding_issues)
    
    # Recomendaciones
    recommendations = _generate_typology_recommendations(
        inconsistencies, 
        encoding_issues,
        columns_typology
    )
    
    return {
        "summary": summary,
        "columns_typology": columns_typology,
        "inconsistencies": inconsistencies,
        "encoding_issues": encoding_issues,
        "recommendations": recommendations,
        "analysis_timestamp": datetime.now().isoformat()
    }


def _analyze_column_type(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Analiza en detalle el tipo de una columna.
    
    Returns:
        Diccionario con análisis completo del tipo
    """
    col_data = df[column].dropna()
    
    if len(col_data) == 0:
        return {
            "pandas_dtype": str(df[column].dtype),
            "inferred_type": "empty",
            "detected_types": [],
            "has_inconsistency": False,
            "inconsistency_rate": 0.0,
            "inconsistent_examples": [],
            "encoding_issue": None,
            "encoding_examples": []
        }
    
    # Tipo pandas actual
    pandas_dtype = str(df[column].dtype)
    
    # Inferir tipo real examinando los datos
    type_counts = {}
    inconsistent_examples = []
    
    for idx, value in col_data.items():
        detected_type = _detect_value_type(value)
        type_counts[detected_type] = type_counts.get(detected_type, 0) + 1
        
        # Guardar ejemplos de valores inconsistentes
        if len(type_counts) > 1 and len(inconsistent_examples) < 10:
            inconsistent_examples.append({
                "row": int(idx),
                "value": str(value)[:50],  # Truncar si es muy largo
                "detected_type": detected_type
            })
    
    # Tipo más frecuente
    inferred_type = max(type_counts, key=type_counts.get) if type_counts else "unknown"
    
    # Calcular inconsistencia
    total_non_null = len(col_data)
    main_type_count = type_counts.get(inferred_type, 0)
    inconsistency_rate = 1.0 - (main_type_count / total_non_null)
    has_inconsistency = inconsistency_rate > 0.05  # >5% de valores inconsistentes
    
    # Detectar problemas de encoding
    encoding_issue, encoding_examples = _detect_encoding_issues(col_data)
    
    return {
        "pandas_dtype": pandas_dtype,
        "inferred_type": inferred_type,
        "detected_types": list(type_counts.keys()),
        "type_distribution": {k: int(v) for k, v in type_counts.items()},
        "has_inconsistency": has_inconsistency,
        "inconsistency_rate": float(inconsistency_rate),
        "inconsistent_examples": inconsistent_examples[:5],
        "encoding_issue": encoding_issue,
        "encoding_examples": encoding_examples,
        "total_non_null": int(total_non_null)
    }


def _detect_value_type(value: Any) -> str:
    """
    Detecta el tipo real de un valor individual.
    
    Returns:
        String con el tipo detectado
    """
    # None/NaN
    if pd.isna(value):
        return "null"
    
    # Datetime
    if isinstance(value, (pd.Timestamp, datetime)):
        return "datetime"
    
    # Boolean
    if isinstance(value, (bool, np.bool_)):
        return "boolean"
    
    # Numeric
    if isinstance(value, (int, np.integer)):
        return "integer"
    
    if isinstance(value, (float, np.floating)):
        # Verificar si es entero disfrazado de float
        if value.is_integer():
            return "integer"
        return "float"
    
    # String - verificar contenido
    if isinstance(value, str):
        value_stripped = value.strip()
        
        # Booleano como string
        if value_stripped.lower() in ['true', 'false', 'verdadero', 'falso', 'sí', 'si', 'no', 't', 'f']:
            return "string_boolean"
        
        # Número como string
        if re.match(r'^-?\d+$', value_stripped):
            return "string_integer"
        
        if re.match(r'^-?\d+[.,]\d+$', value_stripped):
            return "string_float"
        
        # Fecha como string
        if _looks_like_date(value_stripped):
            return "string_datetime"
        
        # Categórico (valores repetidos y cortos)
        if len(value_stripped) < 50:
            return "string_categorical"
        
        return "string_text"
    
    return "unknown"


def _looks_like_date(value: str) -> bool:
    """
    Detecta si un string parece una fecha.
    
    Returns:
        True si parece una fecha
    """
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
        r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
    ]
    
    return any(re.match(pattern, value) for pattern in date_patterns)


def _detect_encoding_issues(series: pd.Series) -> Tuple[str, List[Dict]]:
    """
    Detecta problemas de encoding en una serie de strings.
    
    Returns:
        Tupla (tipo_de_issue, ejemplos)
    """
    if not pd.api.types.is_string_dtype(series):
        return None, []
    
    examples = []
    issues_found = set()
    
    for idx, value in series.items():
        if not isinstance(value, str):
            continue
        
        # Caracteres raros de UTF-8 mal decodificado
        if any(char in value for char in ['Ã', 'Â', '©', 'º', 'ª']):
            if 'Ã±' in value or 'Ã©' in value or 'Ã³' in value:
                issues_found.add("utf8_latin1_mix")
                if len(examples) < 5:
                    examples.append({
                        "row": int(idx),
                        "value": value[:50],
                        "issue": "Posible mezcla UTF-8/Latin-1"
                    })
        
        # Caracteres de escape no procesados
        if '\\x' in value or '\\u' in value:
            issues_found.add("escaped_characters")
            if len(examples) < 5:
                examples.append({
                    "row": int(idx),
                    "value": value[:50],
                    "issue": "Caracteres de escape sin procesar"
                })
    
    if issues_found:
        return ", ".join(issues_found), examples
    
    return None, []


def _generate_typology_summary(
    columns_typology: Dict,
    inconsistencies: List[Dict],
    encoding_issues: List[Dict]
) -> Dict[str, Any]:
    """
    Genera resumen del análisis de tipología.
    """
    total_columns = len(columns_typology)
    
    # Contar tipos inferidos
    type_distribution = {}
    for col_data in columns_typology.values():
        inferred = col_data["inferred_type"]
        type_distribution[inferred] = type_distribution.get(inferred, 0) + 1
    
    return {
        "total_columns": total_columns,
        "inconsistencies_count": len(inconsistencies),
        "encoding_issues_count": len(encoding_issues),
        "type_distribution": type_distribution,
        "quality_score": _calculate_typology_score(
            total_columns,
            len(inconsistencies),
            len(encoding_issues)
        )
    }


def _calculate_typology_score(
    total_cols: int,
    inconsistencies_count: int,
    encoding_issues_count: int
) -> float:
    """
    Calcula score de calidad tipológica (0-100).
    """
    score = 100.0
    
    # Penalización por inconsistencias
    if total_cols > 0:
        inconsistency_rate = inconsistencies_count / total_cols
        score -= inconsistency_rate * 40  # Hasta -40 puntos
    
    # Penalización por encoding
    if total_cols > 0:
        encoding_rate = encoding_issues_count / total_cols
        score -= encoding_rate * 30  # Hasta -30 puntos
    
    return max(0.0, score)


def _generate_typology_recommendations(
    inconsistencies: List[Dict],
    encoding_issues: List[Dict],
    columns_typology: Dict
) -> List[Dict[str, str]]:
    """
    Genera recomendaciones basadas en problemas de tipología.
    """
    recommendations = []
    
    # Recomendaciones por inconsistencias
    for issue in inconsistencies[:3]:  # Top 3
        col = issue["column"]
        expected = issue["expected"]
        
        # Determinar acción según el tipo de inconsistencia
        if "string_integer" in issue["found"] and expected == "integer":
            action = f"Convertir valores string a enteros: pd.to_numeric(df['{col}'], errors='coerce')"
        elif "string_float" in issue["found"] and expected in ["float", "integer"]:
            action = f"Convertir valores string a numéricos, considerar separador decimal regional"
        elif "string_datetime" in issue["found"]:
            action = f"Convertir a datetime: pd.to_datetime(df['{col}'], format='...', errors='coerce')"
        else:
            action = f"Estandarizar tipo de dato y limpiar valores inconsistentes"
        
        recommendations.append({
            "priority": "alta",
            "field": col,
            "issue": f"Tipo inconsistente: {issue['inconsistency_rate']*100:.1f}% de valores no coinciden",
            "action": action,
            "impact": "Alto - Impide análisis cuantitativos correctos"
        })
    
    # Recomendaciones por encoding
    for issue in encoding_issues[:3]:  # Top 3
        col = issue["column"]
        
        recommendations.append({
            "priority": "media",
            "field": col,
            "issue": f"Problemas de codificación de caracteres: {issue['issue']}",
            "action": f"Recodificar a UTF-8: df['{col}'] = df['{col}'].str.encode('latin1').str.decode('utf8')",
            "impact": "Medio - Afecta análisis de texto y búsquedas"
        })
    
    # Detectar columnas que deberían ser categóricas
    potential_categorical = [
        col for col, data in columns_typology.items()
        if data["inferred_type"] in ["string_categorical", "string_text"]
        and data["total_non_null"] > 50
        and len(set([ex["value"] for ex in data.get("inconsistent_examples", [])])) < 20
    ]
    
    if potential_categorical:
        recommendations.append({
            "priority": "baja",
            "field": ", ".join(potential_categorical[:3]),
            "issue": "Columnas string que parecen categóricas",
            "action": "Convertir a tipo 'category' para optimizar memoria y análisis",
            "impact": "Bajo - Mejora eficiencia y claridad"
        })
    
    return recommendations
