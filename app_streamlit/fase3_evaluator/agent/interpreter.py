"""
Agente Intérprete con LLM
Genera diagnósticos en lenguaje natural a partir del JSON consolidado
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from openai import OpenAI
import logging

from config import settings
from .prompts import (
    SYSTEM_PROMPT,
    DIAGNOSIS_PROMPT_TEMPLATE,
    FOLLOWUP_PROMPT_TEMPLATE,
    VISUALIZATION_SUGGESTION_PROMPT
)

logger = logging.getLogger(__name__)


def _convert_numpy_types(obj):
    """
    Convierte tipos de NumPy/Pandas a tipos nativos de Python para JSON serialization.
    
    Args:
        obj: Objeto a convertir
        
    Returns:
        Objeto convertido a tipos nativos Python
    """
    if isinstance(obj, dict):
        return {key: _convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj


def generate_diagnosis(
    consolidated_json: Dict[str, Any],
    anonymized_df: Optional[pd.DataFrame] = None,
    include_sample: bool = True
) -> Dict[str, str]:
    """
    Genera diagnóstico completo en lenguaje natural.
    
    Args:
        consolidated_json: JSON consolidado de análisis
        anonymized_df: DataFrame anonimizado (opcional, para estadísticas descriptivas)
        include_sample: Si True, incluye muestra de datos en el prompt
        
    Returns:
        Diccionario con diagnóstico y metadatos
        
    Raises:
        ValueError: Si falta la API key de OpenAI
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY no está configurada en el archivo .env")
    
    # Convertir tipos NumPy/Pandas a tipos nativos Python
    consolidated_json_clean = _convert_numpy_types(consolidated_json)
    
    # Preparar datos para el prompt
    json_str = json.dumps(consolidated_json_clean, indent=2, ensure_ascii=False)
    
    # Generar sample de datos si está disponible
    sample_str = ""
    if include_sample and anonymized_df is not None:
        sample_str = _generate_data_sample(anonymized_df, consolidated_json)
    
    # Construir prompt
    user_prompt = DIAGNOSIS_PROMPT_TEMPLATE.format(
        json_data=json_str,
        anonymized_sample=sample_str
    )
    
    # Llamar a OpenAI
    logger.info("Generando diagnóstico con OpenAI...")
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS
        )
        
        diagnosis_text = response.choices[0].message.content
        
        logger.info("Diagnóstico generado exitosamente")
        
        return {
            "diagnosis": diagnosis_text,
            "model_used": settings.OPENAI_MODEL,
            "tokens_used": response.usage.total_tokens,
            "timestamp": consolidated_json["metadata"]["analysis_date"]
        }
        
    except Exception as e:
        logger.error(f"Error al generar diagnóstico: {str(e)}")
        raise


def ask_followup_question(
    question: str,
    consolidated_json: Dict[str, Any]
) -> str:
    """
    Permite hacer preguntas específicas sobre el análisis.
    
    Args:
        question: Pregunta del usuario
        consolidated_json: JSON consolidado de análisis
        
    Returns:
        Respuesta del agente
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY no está configurada")
    
    # Crear resumen compacto del JSON (solo métricas clave)
    json_summary = _create_json_summary(consolidated_json)
    
    user_prompt = FOLLOWUP_PROMPT_TEMPLATE.format(
        user_question=question,
        json_summary=json_summary
    )
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error en pregunta de seguimiento: {str(e)}")
        raise


def suggest_visualizations(consolidated_json: Dict[str, Any]) -> str:
    """
    Sugiere visualizaciones apropiadas para los datos.
    
    Args:
        consolidated_json: JSON consolidado de análisis
        
    Returns:
        Sugerencias de visualizaciones en formato texto
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY no está configurada")
    
    json_summary = _create_json_summary(consolidated_json)
    
    user_prompt = VISUALIZATION_SUGGESTION_PROMPT.format(
        json_summary=json_summary
    )
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,  # Más creativo para sugerencias
            max_tokens=1500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error al sugerir visualizaciones: {str(e)}")
        raise


def _generate_data_sample(df: pd.DataFrame, consolidated_json: Dict) -> str:
    """
    Genera un sample informativo de los datos anonimizados.
    
    Returns:
        String con estadísticas descriptivas
    """
    sample_parts = []
    
    # Información básica
    sample_parts.append(f"Dataset: {len(df)} registros, {len(df.columns)} columnas")
    
    # Columnas numéricas: estadísticas
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        sample_parts.append("\n### Estadísticas de variables numéricas:")
        for col in numeric_cols[:5]:  # Top 5
            stats = df[col].describe()
            sample_parts.append(
                f"- {col}: media={stats['mean']:.2f}, mediana={stats['50%']:.2f}, "
                f"rango=[{stats['min']:.2f}, {stats['max']:.2f}]"
            )
    
    # Columnas categóricas: distribución
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(categorical_cols) > 0:
        sample_parts.append("\n### Distribución de variables categóricas:")
        for col in categorical_cols[:5]:  # Top 5
            value_counts = df[col].value_counts().head(3)
            sample_parts.append(f"- {col}:")
            for val, count in value_counts.items():
                percentage = (count / len(df)) * 100
                sample_parts.append(f"  * {val}: {count} ({percentage:.1f}%)")
    
    return "\n".join(sample_parts)


def _create_json_summary(consolidated_json: Dict[str, Any]) -> str:
    """
    Crea un resumen compacto del JSON para preguntas de seguimiento.
    
    Returns:
        String con métricas clave en formato legible
    """
    summary_parts = [
        f"Dataset: {consolidated_json['metadata']['rows']} registros, "
        f"{consolidated_json['metadata']['columns']} columnas"
    ]
    
    # Scores
    summary_parts.append("\nScores de calidad:")
    summary_parts.append(f"- Completitud: {consolidated_json['completitud']['evaluation']['score']:.1f}/100")
    summary_parts.append(f"- Tipología: {consolidated_json['tipos']['summary']['quality_score']:.1f}/100")
    summary_parts.append(f"- Semántica: {consolidated_json['semantica']['summary']['score']:.1f}/100")
    summary_parts.append(f"- Geoespacial: {consolidated_json['geoespacial']['summary']['score']:.1f}/100")
    
    # Riesgo PII
    pii_summary = consolidated_json['anonimizacion']['summary']
    if pii_summary['pii_detected']:
        summary_parts.append(
            f"\n⚠️ PII detectada: Riesgo {consolidated_json['anonimizacion']['risk_assessment']['level']} "
            f"(score: {consolidated_json['anonimizacion']['risk_assessment']['score']:.1f}/10)"
        )
    
    # Viabilidad ML
    ml_summary = consolidated_json['ml']['ml_viability']
    summary_parts.append(
        f"\nML viable: {'Sí' if ml_summary['viable'] else 'No'} "
        f"(score: {ml_summary['score']:.1f}/100)"
    )
    
    return "\n".join(summary_parts)
