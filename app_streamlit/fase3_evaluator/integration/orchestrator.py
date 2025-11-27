"""
Orquestador Paralelo de Analizadores
Ejecuta los 6 analizadores en paralelo y consolida resultados
"""

import pandas as pd
from typing import Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from datetime import datetime
import logging

from config import settings
from ..analyzers import (
    analyze_completeness,
    analyze_typology,
    analyze_semantic,
    analyze_geospatial,
    analyze_anonymization,
    analyze_ml_readiness
)
from .anonymizer import anonymize_dataframe, generate_anonymization_report, validate_anonymization
from .schema import ConsolidatedAnalysis

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_parallel_analysis(
    df: pd.DataFrame,
    filename: str = "dataset.csv",
    auto_anonymize: bool = True
) -> Tuple[Dict[str, Any], pd.DataFrame, Dict[str, Any]]:
    """
    Ejecuta todos los analizadores en paralelo.
    
    Args:
        df: DataFrame a analizar
        filename: Nombre del archivo original
        auto_anonymize: Si True, anonimiza automáticamente columnas con PII
        
    Returns:
        Tupla (JSON consolidado, DataFrame anonimizado, Reporte de anonimización)
        
    Raises:
        ValueError: Si el DataFrame está vacío
        TimeoutError: Si algún analizador excede el timeout
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío")
    
    logger.info(f"Iniciando análisis paralelo de '{filename}' con {len(df)} registros y {len(df.columns)} columnas")
    
    # Metadatos
    metadata = {
        "filename": filename,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "analysis_date": datetime.now().isoformat(),
        "auto_anonymized": auto_anonymize
    }
    
    # Paso 1: Ejecutar analizadores en paralelo sobre datos ORIGINALES
    logger.info("Ejecutando analizadores en paralelo...")
    analysis_results = _run_analyzers_parallel(df)
    
    # Paso 2: Detectar PII y anonimizar si es necesario
    df_anonymized = df.copy()
    anonymization_report = None
    
    if auto_anonymize and analysis_results.get("anonymization"):
        anon_result = analysis_results["anonymization"]
        
        if anon_result["summary"]["pii_detected"]:
            logger.warning(f"PII detectada en {len(anon_result['columns_with_pii'])} columnas - anonimizando...")
            
            df_anonymized, transformations = anonymize_dataframe(
                df,
                anon_result["columns_with_pii"],
                anonymization_strategy="mask"  # Estrategia por defecto
            )
            
            anonymization_report = generate_anonymization_report(df, df_anonymized, transformations)
            
            # Validar anonimización
            validation = validate_anonymization(df_anonymized)
            anonymization_report["validation"] = validation
            
            if not validation["is_safe"]:
                logger.error("ADVERTENCIA: Anonimización incompleta - revisar manualmente")
            else:
                logger.info("Anonimización completada y validada")
    
    # Paso 3: Consolidar resultados en JSON estructurado
    logger.info("Consolidando resultados...")
    consolidated_json = {
        "metadata": metadata,
        "completitud": analysis_results["completeness"],
        "tipos": analysis_results["typology"],
        "semantica": analysis_results["semantic"],
        "geoespacial": analysis_results["geospatial"],
        "anonimizacion": analysis_results["anonymization"],
        "ml": analysis_results["ml_readiness"]
    }
    
    # Validar con Pydantic
    try:
        validated = ConsolidatedAnalysis(**consolidated_json)
        consolidated_json = validated.model_dump()
        logger.info("JSON consolidado validado correctamente")
    except Exception as e:
        logger.warning(f"Advertencia en validación Pydantic: {e}")
    
    logger.info("Análisis completado exitosamente")
    
    return consolidated_json, df_anonymized, anonymization_report


def _run_analyzers_parallel(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Ejecuta los 6 analizadores en paralelo usando ThreadPoolExecutor.
    
    Returns:
        Diccionario con resultados de cada analizador
    """
    analyzers = {
        "completeness": analyze_completeness,
        "typology": analyze_typology,
        "semantic": analyze_semantic,
        "geospatial": analyze_geospatial,
        "anonymization": analyze_anonymization,
        "ml_readiness": analyze_ml_readiness
    }
    
    results = {}
    errors = {}
    
    with ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
        # Enviar todos los analizadores
        future_to_analyzer = {
            executor.submit(analyzer_func, df): name
            for name, analyzer_func in analyzers.items()
        }
        
        # Recoger resultados conforme van terminando
        for future in as_completed(future_to_analyzer):
            analyzer_name = future_to_analyzer[future]
            
            try:
                result = future.result(timeout=settings.TIMEOUT_SECONDS)
                results[analyzer_name] = result
                logger.info(f"✓ {analyzer_name} completado")
                
            except TimeoutError:
                logger.error(f"✗ {analyzer_name} excedió timeout de {settings.TIMEOUT_SECONDS}s")
                errors[analyzer_name] = "timeout"
                results[analyzer_name] = _get_error_result(analyzer_name, "timeout")
                
            except Exception as e:
                logger.error(f"✗ {analyzer_name} falló: {str(e)}")
                errors[analyzer_name] = str(e)
                results[analyzer_name] = _get_error_result(analyzer_name, str(e))
    
    # Verificar que todos los analizadores terminaron
    if errors:
        logger.warning(f"Advertencia: {len(errors)} analizadores fallaron: {list(errors.keys())}")
    
    return results


def _get_error_result(analyzer_name: str, error_msg: str) -> Dict[str, Any]:
    """
    Genera un resultado de error para un analizador que falló.
    
    Returns:
        Diccionario con estructura mínima para no romper el JSON consolidado
    """
    return {
        "summary": {
            "error": True,
            "error_message": error_msg,
            "analyzer": analyzer_name
        },
        "recommendations": [{
            "priority": "critica",
            "field": "general",
            "issue": f"Analizador {analyzer_name} falló",
            "action": "Revisar logs para más detalles",
            "impact": "No se pudo completar este análisis"
        }],
        "analysis_timestamp": datetime.now().isoformat()
    }


def run_single_analyzer(
    df: pd.DataFrame,
    analyzer_name: str
) -> Dict[str, Any]:
    """
    Ejecuta un solo analizador (útil para debugging o re-runs).
    
    Args:
        df: DataFrame a analizar
        analyzer_name: Nombre del analizador a ejecutar
        
    Returns:
        Resultado del analizador
        
    Raises:
        ValueError: Si el nombre del analizador no existe
    """
    analyzers_map = {
        "completeness": analyze_completeness,
        "typology": analyze_typology,
        "semantic": analyze_semantic,
        "geospatial": analyze_geospatial,
        "anonymization": analyze_anonymization,
        "ml_readiness": analyze_ml_readiness
    }
    
    if analyzer_name not in analyzers_map:
        raise ValueError(
            f"Analizador '{analyzer_name}' no existe. "
            f"Opciones: {list(analyzers_map.keys())}"
        )
    
    logger.info(f"Ejecutando {analyzer_name}...")
    result = analyzers_map[analyzer_name](df)
    logger.info(f"✓ {analyzer_name} completado")
    
    return result


def get_analysis_summary(consolidated_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera un resumen ejecutivo del análisis consolidado.
    
    Returns:
        Diccionario con métricas clave
    """
    summary = {
        "dataset": {
            "rows": consolidated_json["metadata"]["rows"],
            "columns": consolidated_json["metadata"]["columns"],
            "filename": consolidated_json["metadata"]["filename"]
        },
        "scores": {
            "completitud": consolidated_json["completitud"]["evaluation"]["score"],
            "tipologia": consolidated_json["tipos"]["summary"]["quality_score"],
            "semantica": consolidated_json["semantica"]["summary"]["score"],
            "geoespacial": consolidated_json["geoespacial"]["summary"]["score"],
            "ml_viabilidad": consolidated_json["ml"]["ml_viability"]["score"]
        },
        "critical_issues": {
            "pii_detected": consolidated_json["anonimizacion"]["summary"]["pii_detected"],
            "pii_risk_level": consolidated_json["anonimizacion"]["risk_assessment"]["level"],
            "completitud_critica": len(consolidated_json["completitud"]["critical_fields_missing"]) > 0,
            "leakage_risks": len(consolidated_json["ml"]["leakage_risks"])
        },
        "capabilities": {
            "geocodable": consolidated_json["geoespacial"]["summary"]["geocodable"],
            "ml_viable": consolidated_json["ml"]["ml_viability"]["viable"],
            "clustering_feasible": consolidated_json["geoespacial"]["clustering_potential"]["feasible"]
        }
    }
    
    # Score general promedio
    scores_list = list(summary["scores"].values())
    summary["overall_score"] = sum(scores_list) / len(scores_list)
    
    return summary
