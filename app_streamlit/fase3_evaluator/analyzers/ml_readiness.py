"""
Analizador de Preparación para Machine Learning
Evalúa viabilidad de modelos predictivos, balance de clases, features, leakage
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
from scipy.stats import chi2_contingency

from config import settings


def analyze_ml_readiness(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analiza la preparación de los datos para Machine Learning.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con análisis de preparación ML
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío")
    
    # Identificar columnas target potenciales
    target_col = _identify_target_column(df)
    
    # Análisis de features
    features_analysis = _analyze_features(df, target_col)
    
    # Análisis de balance de clases
    balance_analysis = None
    if target_col:
        balance_analysis = _analyze_class_balance(df, target_col)
    
    # Detección de data leakage
    leakage_risks = _detect_leakage(df, target_col)
    
    # Análisis de correlaciones
    correlation_analysis = _analyze_correlations(df, target_col)
    
    # Evaluación de viabilidad ML
    ml_viability = _assess_ml_viability(
        len(df),
        features_analysis,
        balance_analysis,
        leakage_risks
    )
    
    # Sugerencias de modelos
    model_suggestions = _suggest_models(
        target_col,
        balance_analysis,
        features_analysis,
        len(df)
    )
    
    # Resumen y recomendaciones
    summary = _generate_ml_summary(ml_viability, features_analysis, balance_analysis)
    recommendations = _generate_ml_recommendations(
        ml_viability,
        features_analysis,
        balance_analysis,
        leakage_risks
    )
    
    return {
        "summary": summary,
        "target_column": target_col,
        "features_analysis": features_analysis,
        "balance_analysis": balance_analysis,
        "leakage_risks": leakage_risks,
        "correlation_analysis": correlation_analysis,
        "ml_viability": ml_viability,
        "model_suggestions": model_suggestions,
        "recommendations": recommendations,
        "analysis_timestamp": datetime.now().isoformat()
    }


def _identify_target_column(df: pd.DataFrame) -> Optional[str]:
    """
    Identifica la columna target más probable.
    
    Heurística para datos de suicidio:
    - Columnas tipo: "tipo_evento", "resultado", "consumado", "intento"
    - Variables binarias que indican desenlace
    """
    target_keywords = [
        "tipo_evento", "tipo", "resultado", "consumado", 
        "intento", "desenlace", "outcome", "target", "label"
    ]
    
    # Buscar por keywords
    for col in df.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in target_keywords):
            # Verificar que sea categórica con pocas clases
            if df[col].nunique() <= 10:
                return col
    
    # Buscar variables binarias que podrían ser target
    binary_cols = [col for col in df.columns if df[col].nunique() == 2]
    if binary_cols:
        # Priorizar las que tienen valores como sí/no, true/false, etc.
        for col in binary_cols:
            unique_vals = df[col].dropna().unique()
            unique_str = [str(v).lower() for v in unique_vals]
            if any(val in unique_str for val in ['si', 'no', 'true', 'false', '1', '0']):
                return col
    
    return None


def _analyze_features(df: pd.DataFrame, target_col: Optional[str]) -> Dict[str, Any]:
    """
    Analiza las features disponibles para ML.
    
    Returns:
        Diccionario con análisis de features
    """
    # Excluir target y columnas no útiles
    exclude_cols = [target_col] if target_col else []
    exclude_cols.extend(_get_non_feature_columns(df))
    
    potential_features = [col for col in df.columns if col not in exclude_cols]
    
    # Clasificar features por tipo
    numeric_features = []
    categorical_features = []
    datetime_features = []
    text_features = []
    
    for col in potential_features:
        dtype = df[col].dtype
        
        if pd.api.types.is_numeric_dtype(dtype):
            numeric_features.append(col)
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            datetime_features.append(col)
        elif pd.api.types.is_string_dtype(dtype):
            # Distinguir categóricas de texto libre
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.5:  # <50% únicos = categórica
                categorical_features.append(col)
            else:
                text_features.append(col)
        else:
            categorical_features.append(col)
    
    # Calcular completitud de features
    features_completeness = {}
    for col in potential_features:
        completeness = 1 - (df[col].isna().sum() / len(df))
        features_completeness[col] = float(completeness)
    
    # Features útiles (>70% completas)
    usable_features = [
        col for col, comp in features_completeness.items()
        if comp >= 0.7
    ]
    
    return {
        "total_columns": len(df.columns),
        "potential_features": len(potential_features),
        "usable_features": len(usable_features),
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "datetime_features": datetime_features,
        "text_features": text_features,
        "features_completeness": features_completeness,
        "meets_minimum": len(usable_features) >= settings.ML_MIN_FEATURES
    }


def _get_non_feature_columns(df: pd.DataFrame) -> List[str]:
    """
    Identifica columnas que no deberían usarse como features.
    
    Returns:
        Lista de nombres de columnas no útiles
    """
    non_features = []
    
    for col in df.columns:
        col_lower = col.lower()
        
        # IDs únicos
        if df[col].nunique() == len(df):
            non_features.append(col)
        
        # Columnas de identificación
        elif any(kw in col_lower for kw in ['id', 'identificador', 'codigo']):
            non_features.append(col)
        
        # Nombres y PII
        elif any(kw in col_lower for kw in ['nombre', 'apellido', 'direccion', 'email']):
            non_features.append(col)
    
    return non_features


def _analyze_class_balance(df: pd.DataFrame, target_col: str) -> Dict[str, Any]:
    """
    Analiza el balance de clases del target.
    
    Returns:
        Diccionario con análisis de balance
    """
    target_series = df[target_col].dropna()
    
    if len(target_series) == 0:
        return None
    
    # Distribución de clases
    class_counts = target_series.value_counts()
    class_proportions = target_series.value_counts(normalize=True)
    
    # Calcular balance
    min_proportion = class_proportions.min()
    max_proportion = class_proportions.max()
    
    # Determinar nivel de desbalance
    if min_proportion >= 0.4:
        balance_level = "balanceado"
    elif min_proportion >= 0.2:
        balance_level = "ligeramente_desbalanceado"
    elif min_proportion >= 0.1:
        balance_level = "moderadamente_desbalanceado"
    else:
        balance_level = "severamente_desbalanceado"
    
    return {
        "column": target_col,
        "n_classes": len(class_counts),
        "class_distribution": class_counts.to_dict(),
        "class_proportions": {k: float(v) for k, v in class_proportions.items()},
        "min_class_proportion": float(min_proportion),
        "max_class_proportion": float(max_proportion),
        "balance_level": balance_level,
        "requires_balancing": min_proportion < settings.ML_IMBALANCE_THRESHOLD
    }


def _detect_leakage(df: pd.DataFrame, target_col: Optional[str]) -> List[Dict[str, Any]]:
    """
    Detecta posibles fuentes de data leakage.
    
    Returns:
        Lista de riesgos de leakage identificados
    """
    leakage_risks = []
    
    if not target_col:
        return leakage_risks
    
    target_series = df[target_col].dropna()
    
    # Detectar columnas con correlación perfecta o casi perfecta
    for col in df.columns:
        if col == target_col:
            continue
        
        # Solo analizar numéricas y categóricas
        if not pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_string_dtype(df[col]):
            continue
        
        # Para categóricas, verificar si una clase del target corresponde perfectamente a una categoría
        if pd.api.types.is_string_dtype(df[col]) or df[col].nunique() < 20:
            try:
                contingency = pd.crosstab(df[col], target_series)
                chi2, p_value, dof, expected = chi2_contingency(contingency)
                
                # P-value muy bajo indica dependencia fuerte
                if p_value < 0.001 and df[col].nunique() == target_series.nunique():
                    leakage_risks.append({
                        "column": col,
                        "reason": "Correlación perfecta con target (posible proxy o consecuencia)",
                        "severity": "alta",
                        "p_value": float(p_value)
                    })
            except:
                pass
        
        # Para numéricas, calcular correlación
        elif pd.api.types.is_numeric_dtype(df[col]):
            # Encodear target si es necesario
            if not pd.api.types.is_numeric_dtype(target_series):
                le = LabelEncoder()
                target_encoded = le.fit_transform(target_series)
            else:
                target_encoded = target_series
            
            # Calcular correlación
            col_numeric = pd.to_numeric(df[col], errors='coerce')
            valid_mask = ~(col_numeric.isna() | pd.Series(target_encoded).isna())
            
            if valid_mask.sum() > 10:
                corr = np.corrcoef(col_numeric[valid_mask], target_encoded[valid_mask])[0, 1]
                
                if abs(corr) > 0.95:
                    leakage_risks.append({
                        "column": col,
                        "reason": f"Correlación muy alta con target (r={corr:.3f})",
                        "severity": "alta",
                        "correlation": float(corr)
                    })
    
    # Detectar columnas temporales posteriores al evento
    temporal_cols = [col for col in df.columns if any(kw in col.lower() for kw in ['fecha', 'date', 'timestamp'])]
    
    for col in temporal_cols:
        col_lower = col.lower()
        # Columnas de notificación, reporte, etc. son posteriores al evento
        if any(kw in col_lower for kw in ['notificacion', 'reporte', 'registro', 'ingreso']):
            leakage_risks.append({
                "column": col,
                "reason": "Fecha posterior al evento (no disponible al momento de predicción)",
                "severity": "critica"
            })
    
    return leakage_risks


def _analyze_correlations(df: pd.DataFrame, target_col: Optional[str]) -> Dict[str, Any]:
    """
    Analiza correlaciones entre features numéricas.
    
    Returns:
        Análisis de correlaciones relevantes
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        return {"has_correlations": False}
    
    # Matriz de correlación
    corr_matrix = df[numeric_cols].corr()
    
    # Encontrar correlaciones altas entre features (>0.8)
    high_correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]
            if abs(corr_val) > 0.8:
                high_correlations.append({
                    "feature1": corr_matrix.columns[i],
                    "feature2": corr_matrix.columns[j],
                    "correlation": float(corr_val)
                })
    
    return {
        "has_correlations": True,
        "numeric_features_count": len(numeric_cols),
        "high_correlations": high_correlations[:10],  # Top 10
        "multicollinearity_risk": len(high_correlations) > 5
    }


def _assess_ml_viability(
    n_samples: int,
    features_analysis: Dict,
    balance_analysis: Optional[Dict],
    leakage_risks: List[Dict]
) -> Dict[str, Any]:
    """
    Evalúa la viabilidad general de ML.
    
    Returns:
        Diccionario con evaluación de viabilidad
    """
    viability = {
        "viable": True,
        "confidence": "alta",
        "blockers": [],
        "warnings": [],
        "score": 100.0
    }
    
    # Verificar mínimo de muestras
    if n_samples < settings.ML_MIN_SAMPLES:
        viability["viable"] = False
        viability["confidence"] = "nula"
        viability["blockers"].append(
            f"Insuficientes muestras: {n_samples} < {settings.ML_MIN_SAMPLES} requeridas"
        )
        viability["score"] -= 50
    
    # Verificar features
    if not features_analysis["meets_minimum"]:
        viability["viable"] = False
        viability["blockers"].append(
            f"Insuficientes features útiles: {features_analysis['usable_features']} < {settings.ML_MIN_FEATURES}"
        )
        viability["score"] -= 30
    
    # Desbalance severo
    if balance_analysis and balance_analysis["balance_level"] == "severamente_desbalanceado":
        viability["warnings"].append(
            f"Desbalance severo de clases ({balance_analysis['min_class_proportion']*100:.1f}% clase minoritaria)"
        )
        viability["confidence"] = "media"
        viability["score"] -= 15
    
    # Leakage crítico
    critical_leakage = [r for r in leakage_risks if r["severity"] == "critica"]
    if critical_leakage:
        viability["warnings"].append(
            f"{len(critical_leakage)} columnas con riesgo crítico de leakage"
        )
        viability["score"] -= 20
    
    viability["score"] = max(0, viability["score"])
    
    return viability


def _suggest_models(
    target_col: Optional[str],
    balance_analysis: Optional[Dict],
    features_analysis: Dict,
    n_samples: int
) -> List[Dict[str, str]]:
    """
    Sugiere modelos de ML apropiados.
    
    Returns:
        Lista de modelos sugeridos con justificación
    """
    suggestions = []
    
    if not target_col:
        suggestions.append({
            "task": "clustering",
            "models": ["K-means", "DBSCAN", "Hierarchical Clustering"],
            "reason": "No hay variable target - análisis no supervisado"
        })
        return suggestions
    
    # Clasificación vs Regresión
    if balance_analysis:
        n_classes = balance_analysis["n_classes"]
        
        if n_classes == 2:
            # Clasificación binaria
            if n_samples < 1000:
                suggestions.append({
                    "task": "clasificacion_binaria",
                    "models": ["Logistic Regression", "Random Forest", "XGBoost"],
                    "reason": "Dataset pequeño - modelos interpretables recomendados"
                })
            else:
                suggestions.append({
                    "task": "clasificacion_binaria",
                    "models": ["Random Forest", "XGBoost", "LightGBM", "Redes Neuronales"],
                    "reason": "Dataset grande - modelos complejos viables"
                })
            
            # Si hay desbalance
            if balance_analysis["requires_balancing"]:
                suggestions.append({
                    "task": "manejo_desbalance",
                    "models": ["SMOTE", "Class weights", "Undersampling"],
                    "reason": f"Clases desbalanceadas ({balance_analysis['min_class_proportion']*100:.1f}% minoritaria)"
                })
        
        elif n_classes <= 10:
            # Clasificación multiclase
            suggestions.append({
                "task": "clasificacion_multiclase",
                "models": ["Random Forest", "XGBoost", "Multi-class Logistic Regression"],
                "reason": f"{n_classes} clases - clasificación multiclase"
            })
    
    # Análisis de series temporales si hay fechas
    if features_analysis["datetime_features"]:
        suggestions.append({
            "task": "series_temporales",
            "models": ["ARIMA", "Prophet", "LSTM"],
            "reason": "Datos con componente temporal - análisis de tendencias posible"
        })
    
    return suggestions


def _generate_ml_summary(
    viability: Dict,
    features_analysis: Dict,
    balance_analysis: Optional[Dict]
) -> Dict[str, Any]:
    """Genera resumen del análisis ML."""
    return {
        "viable": viability["viable"],
        "confidence": viability["confidence"],
        "score": viability["score"],
        "usable_features": features_analysis["usable_features"],
        "has_target": balance_analysis is not None,
        "balance_level": balance_analysis["balance_level"] if balance_analysis else None,
        "critical_issues": len(viability["blockers"])
    }


def _generate_ml_recommendations(
    viability: Dict,
    features_analysis: Dict,
    balance_analysis: Optional[Dict],
    leakage_risks: List[Dict]
) -> List[Dict[str, str]]:
    """Genera recomendaciones para ML."""
    recommendations = []
    
    # Blockers
    for blocker in viability["blockers"]:
        recommendations.append({
            "priority": "critica",
            "field": "general",
            "issue": blocker,
            "action": "Resolver antes de intentar ML",
            "impact": "Crítico - ML no viable sin esto"
        })
    
    # Leakage
    for risk in leakage_risks[:3]:
        recommendations.append({
            "priority": "alta" if risk["severity"] == "critica" else "media",
            "field": risk["column"],
            "issue": f"Riesgo de leakage: {risk['reason']}",
            "action": "Eliminar columna o verificar que esté disponible al momento de predicción",
            "impact": "Alto - Resultados optimistas pero inútiles en producción"
        })
    
    # Desbalance
    if balance_analysis and balance_analysis["requires_balancing"]:
        recommendations.append({
            "priority": "media",
            "field": balance_analysis["column"],
            "issue": f"Desbalance de clases: {balance_analysis['min_class_proportion']*100:.1f}% minoritaria",
            "action": "Aplicar SMOTE, ajustar pesos de clase o usar métricas apropiadas (F1, AUC-ROC)",
            "impact": "Medio - Modelos pueden ignorar clase minoritaria"
        })
    
    return recommendations
