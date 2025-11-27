"""
Analizador de Coherencia Semántica
Detecta edades imposibles, fechas incoherentes, métodos no estandarizados
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re

from config import settings


def analyze_semantic(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analiza la coherencia semántica de los datos.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con análisis semántico
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío")
    
    results = {
        "edad_invalida": [],
        "fechas_incoherentes": [],
        "metodos_no_estandarizados": [],
        "distribuciones_atipicas": [],
        "valores_imposibles": []
    }
    
    # Detectar columnas relevantes
    edad_col = _find_column(df, ["edad", "age"])
    fecha_cols = _find_columns(df, ["fecha", "date"])
    metodo_col = _find_column(df, ["metodo", "method", "medio"])
    sexo_col = _find_column(df, ["sexo", "genero", "gender", "sex"])
    
    # Análisis de edad
    if edad_col:
        results["edad_invalida"] = _analyze_age(df, edad_col)
    
    # Análisis de fechas
    if len(fecha_cols) >= 1:
        results["fechas_incoherentes"] = _analyze_dates(df, fecha_cols)
    
    # Análisis de métodos
    if metodo_col:
        results["metodos_no_estandarizados"] = _analyze_methods(df, metodo_col)
    
    # Análisis de distribuciones
    if edad_col:
        results["distribuciones_atipicas"] = _analyze_distributions(df, edad_col, sexo_col)
    
    # Análisis de valores imposibles en otras columnas
    results["valores_imposibles"] = _analyze_impossible_values(df)
    
    # Resumen y score
    summary = _generate_semantic_summary(results)
    recommendations = _generate_semantic_recommendations(results)
    
    return {
        "summary": summary,
        "edad_invalida": results["edad_invalida"],
        "fechas_incoherentes": results["fechas_incoherentes"],
        "metodos_no_estandarizados": results["metodos_no_estandarizados"],
        "distribuciones_atipicas": results["distribuciones_atipicas"],
        "valores_imposibles": results["valores_imposibles"],
        "recommendations": recommendations,
        "analysis_timestamp": datetime.now().isoformat()
    }


def _find_column(df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
    """Encuentra una columna que contenga alguna keyword."""
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in keywords):
            return col
    return None


def _find_columns(df: pd.DataFrame, keywords: List[str]) -> List[str]:
    """Encuentra todas las columnas que contengan alguna keyword."""
    found = []
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in keywords):
            found.append(col)
    return found


def _analyze_age(df: pd.DataFrame, col: str) -> List[Dict[str, Any]]:
    """
    Analiza coherencia de edad.
    
    Returns:
        Lista de problemas detectados
    """
    issues = []
    
    # Convertir a numérico si es string
    age_series = pd.to_numeric(df[col], errors='coerce')
    
    for idx, age in age_series.items():
        if pd.isna(age):
            continue
        
        # Edad negativa
        if age < settings.SEMANTIC_AGE_MIN:
            issues.append({
                "row": int(idx),
                "value": float(age),
                "issue": "Edad negativa",
                "severity": "critica"
            })
        
        # Edad imposible (>120 años)
        elif age > settings.SEMANTIC_AGE_MAX:
            issues.append({
                "row": int(idx),
                "value": float(age),
                "issue": f"Edad superior a {settings.SEMANTIC_AGE_MAX} años",
                "severity": "critica"
            })
        
        # Edad atípica pero posible (>100 años)
        elif age > 100:
            issues.append({
                "row": int(idx),
                "value": float(age),
                "issue": "Edad muy alta (>100 años) - verificar",
                "severity": "advertencia"
            })
    
    return issues


def _analyze_dates(df: pd.DataFrame, date_cols: List[str]) -> List[Dict[str, Any]]:
    """
    Analiza coherencia entre fechas.
    
    Returns:
        Lista de incoherencias detectadas
    """
    issues = []
    
    # Convertir columnas a datetime
    date_data = {}
    for col in date_cols:
        try:
            date_data[col] = pd.to_datetime(df[col], errors='coerce')
        except:
            continue
    
    if len(date_data) < 2:
        return issues
    
    # Buscar pares de fechas relacionadas
    for col1 in date_data:
        for col2 in date_data:
            if col1 >= col2:  # Evitar duplicados
                continue
            
            # Verificar coherencia temporal
            col1_lower = col1.lower()
            col2_lower = col2.lower()
            
            # Casos específicos
            if ("nacimiento" in col1_lower and "defuncion" in col2_lower) or \
               ("defuncion" in col2_lower and "nacimiento" in col1_lower):
                issues.extend(_check_birth_death_coherence(df, col1, col2, date_data))
            
            elif ("evento" in col1_lower and "notificacion" in col2_lower) or \
                 ("notificacion" in col2_lower and "evento" in col1_lower):
                issues.extend(_check_event_notification_coherence(df, col1, col2, date_data))
    
    # Fechas futuras
    today = pd.Timestamp.now()
    for col, dates in date_data.items():
        future_dates = df[dates > today]
        for idx in future_dates.index:
            issues.append({
                "row": int(idx),
                "columns": [col],
                "issue": f"Fecha futura en '{col}': {dates[idx].strftime('%Y-%m-%d')}",
                "severity": "alta"
            })
    
    return issues


def _check_birth_death_coherence(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    date_data: Dict[str, pd.Series]
) -> List[Dict]:
    """Verifica coherencia entre fecha de nacimiento y muerte."""
    issues = []
    
    birth_col = col1 if "nacimiento" in col1.lower() else col2
    death_col = col2 if "nacimiento" in col1.lower() else col1
    
    birth_dates = date_data[birth_col]
    death_dates = date_data[death_col]
    
    for idx in df.index:
        if pd.isna(birth_dates[idx]) or pd.isna(death_dates[idx]):
            continue
        
        # Muerte antes de nacimiento
        if death_dates[idx] < birth_dates[idx]:
            issues.append({
                "row": int(idx),
                "columns": [birth_col, death_col],
                "issue": f"Fecha de muerte anterior a fecha de nacimiento",
                "severity": "critica"
            })
    
    return issues


def _check_event_notification_coherence(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    date_data: Dict[str, pd.Series]
) -> List[Dict]:
    """Verifica coherencia entre fecha de evento y notificación."""
    issues = []
    
    event_col = col1 if "evento" in col1.lower() else col2
    notif_col = col2 if "evento" in col1.lower() else col1
    
    event_dates = date_data[event_col]
    notif_dates = date_data[notif_col]
    
    for idx in df.index:
        if pd.isna(event_dates[idx]) or pd.isna(notif_dates[idx]):
            continue
        
        # Notificación antes del evento
        if notif_dates[idx] < event_dates[idx]:
            issues.append({
                "row": int(idx),
                "columns": [event_col, notif_col],
                "issue": f"Notificación anterior al evento",
                "severity": "alta"
            })
        
        # Notificación muy tardía (>6 meses)
        elif (notif_dates[idx] - event_dates[idx]).days > 180:
            issues.append({
                "row": int(idx),
                "columns": [event_col, notif_col],
                "issue": f"Notificación muy tardía ({(notif_dates[idx] - event_dates[idx]).days} días)",
                "severity": "advertencia"
            })
    
    return issues


def _analyze_methods(df: pd.DataFrame, col: str) -> List[Dict[str, Any]]:
    """
    Analiza estandarización de métodos de suicidio.
    
    Returns:
        Lista de métodos no estandarizados
    """
    issues = []
    
    # Valores únicos
    methods = df[col].dropna().astype(str).str.lower().str.strip()
    unique_methods = methods.value_counts()
    
    # Métodos estándar
    standard_methods = [m.lower() for m in settings.SEMANTIC_METHODS_STANDARD]
    
    # Mapeo fuzzy de variaciones comunes
    fuzzy_map = {
        "ahorcadura": "ahorcamiento",
        "colgamiento": "ahorcamiento",
        "arma fuego": "arma de fuego",
        "disparo": "arma de fuego",
        "envenenamiento": "intoxicacion",
        "sobredosis": "intoxicacion",
        "salto": "precipitacion",
        "caida": "precipitacion",
        "arma blanka": "arma blanca",
        "cuchillo": "arma blanca"
    }
    
    for method, count in unique_methods.items():
        # Verificar si es estándar
        is_standard = method in standard_methods
        
        # Verificar fuzzy match
        suggestion = None
        if not is_standard:
            for fuzzy, standard in fuzzy_map.items():
                if fuzzy in method or method in fuzzy:
                    suggestion = standard
                    break
        
        if not is_standard and suggestion is None:
            # Buscar el más similar
            for standard in standard_methods:
                if standard in method or method in standard:
                    suggestion = standard
                    break
        
        if not is_standard:
            issues.append({
                "value": method,
                "count": int(count),
                "suggestion": suggestion if suggestion else "otro",
                "severity": "media" if count > 5 else "baja"
            })
    
    return issues


def _analyze_distributions(
    df: pd.DataFrame,
    edad_col: str,
    sexo_col: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Analiza distribuciones estadísticas atípicas.
    
    Returns:
        Lista de distribuciones anómalas
    """
    issues = []
    
    age_series = pd.to_numeric(df[edad_col], errors='coerce').dropna()
    
    if len(age_series) < 30:
        return issues
    
    # Distribución de edad
    q1 = age_series.quantile(0.25)
    q3 = age_series.quantile(0.75)
    iqr = q3 - q1
    
    # Detectar outliers extremos
    lower_bound = q1 - 3 * iqr
    upper_bound = q3 + 3 * iqr
    outliers = age_series[(age_series < lower_bound) | (age_series > upper_bound)]
    
    if len(outliers) > len(age_series) * 0.05:  # >5% outliers
        issues.append({
            "variable": edad_col,
            "issue": f"{len(outliers)} outliers extremos en edad ({len(outliers)/len(age_series)*100:.1f}%)",
            "severity": "advertencia"
        })
    
    # Distribución por sexo (si existe)
    if sexo_col:
        sex_dist = df[sexo_col].value_counts(normalize=True)
        if len(sex_dist) >= 2:
            # Verificar balance (esperado: ~75% hombres, 25% mujeres en suicidio)
            if sex_dist.max() > 0.95:
                issues.append({
                    "variable": sexo_col,
                    "issue": f"Distribución muy desequilibrada: {sex_dist.max()*100:.1f}% en una categoría",
                    "severity": "advertencia"
                })
    
    return issues


def _analyze_impossible_values(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detecta valores semánticamente imposibles en columnas numéricas.
    """
    issues = []
    
    for col in df.select_dtypes(include=[np.number]).columns:
        # Detectar valores negativos donde no deberían haberlos
        if any(keyword in col.lower() for keyword in ["cantidad", "numero", "count", "total"]):
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                issues.append({
                    "column": col,
                    "issue": f"{negative_count} valores negativos en columna que debería ser positiva",
                    "severity": "media"
                })
    
    return issues


def _generate_semantic_summary(results: Dict) -> Dict[str, Any]:
    """Genera resumen del análisis semántico."""
    total_issues = sum([
        len(results["edad_invalida"]),
        len(results["fechas_incoherentes"]),
        len(results["metodos_no_estandarizados"]),
        len(results["distribuciones_atipicas"]),
        len(results["valores_imposibles"])
    ])
    
    critical_issues = sum([
        len([x for x in results["edad_invalida"] if x.get("severity") == "critica"]),
        len([x for x in results["fechas_incoherentes"] if x.get("severity") == "critica"])
    ])
    
    score = max(0, 100 - (critical_issues * 10) - (total_issues * 2))
    
    return {
        "total_issues": total_issues,
        "critical_issues": critical_issues,
        "score": float(score),
        "quality_level": "excelente" if score > 90 else "bueno" if score > 70 else "aceptable" if score > 50 else "deficiente"
    }


def _generate_semantic_recommendations(results: Dict) -> List[Dict[str, str]]:
    """Genera recomendaciones basadas en problemas semánticos."""
    recommendations = []
    
    # Edad
    if results["edad_invalida"]:
        critical_age = [x for x in results["edad_invalida"] if x.get("severity") == "critica"]
        if critical_age:
            recommendations.append({
                "priority": "critica",
                "field": "edad",
                "issue": f"{len(critical_age)} registros con edades imposibles",
                "action": "Revisar y corregir edades negativas o superiores a 120 años",
                "impact": "Alto - Invalida análisis demográficos"
            })
    
    # Fechas
    if results["fechas_incoherentes"]:
        recommendations.append({
            "priority": "alta",
            "field": "fechas",
            "issue": f"{len(results['fechas_incoherentes'])} incoherencias temporales",
            "action": "Validar secuencia lógica de fechas (nacimiento < muerte < notificación)",
            "impact": "Alto - Genera errores en análisis temporales"
        })
    
    # Métodos
    if results["metodos_no_estandarizados"]:
        recommendations.append({
            "priority": "media",
            "field": "metodo",
            "issue": f"{len(results['metodos_no_estandarizados'])} métodos sin estandarizar",
            "action": "Mapear a códigos CIE-10 o lista estandarizada",
            "impact": "Medio - Dificulta comparaciones y agregaciones"
        })
    
    return recommendations
