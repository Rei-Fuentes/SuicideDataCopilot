"""
Analizador de Anonimización y Detección PII
Detecta información personal identificable y calcula riesgo ético
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re

from config import settings, PII_RISK_LEVELS


def analyze_anonymization(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analiza presencia de PII (Personally Identifiable Information).
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con análisis de PII y riesgo
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío")
    
    pii_detected = False
    entities_found = []
    columns_with_pii = []
    risk_score = 0.0
    
    # Analizar cada columna
    for col in df.columns:
        col_analysis = _analyze_column_pii(df, col)
        
        if col_analysis["has_pii"]:
            pii_detected = True
            columns_with_pii.append(col)
            
            # Agregar entidades encontradas
            for entity in col_analysis["entities"]:
                entities_found.append({
                    "type": entity["type"],
                    "column": col,
                    "count": entity["count"],
                    "examples": entity["examples"][:2],  # Solo 2 ejemplos por privacidad
                    "risk_contribution": entity["risk_score"]
                })
            
            risk_score += col_analysis["column_risk_score"]
    
    # Normalizar risk score (0-10)
    if len(df.columns) > 0:
        risk_score = min(10.0, risk_score / len(df.columns) * 10)
    
    # Determinar nivel de riesgo
    risk_level = _determine_risk_level(risk_score)
    
    # Generar recomendaciones
    recommendations = _generate_anonymization_recommendations(
        pii_detected,
        risk_level,
        entities_found,
        columns_with_pii
    )
    
    # Resumen
    summary = {
        "pii_detected": pii_detected,
        "risk_score": float(risk_score),
        "risk_level": risk_level,
        "columns_with_pii_count": len(columns_with_pii),
        "entity_types_found": len(set([e["type"] for e in entities_found])),
        "total_pii_instances": sum([e["count"] for e in entities_found]),
        "requires_action": risk_score >= settings.PII_RISK_THRESHOLD
    }
    
    return {
        "summary": summary,
        "entities_found": entities_found,
        "columns_with_pii": columns_with_pii,
        "risk_assessment": {
            "score": float(risk_score),
            "level": risk_level,
            "threshold": settings.PII_RISK_THRESHOLD,
            "critical": risk_score >= settings.PII_RISK_THRESHOLD
        },
        "recommendations": recommendations,
        "analysis_timestamp": datetime.now().isoformat()
    }


def _analyze_column_pii(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Analiza una columna específica en busca de PII.
    
    Returns:
        Diccionario con análisis de PII de la columna
    """
    col_data = df[column].dropna().astype(str)
    
    if len(col_data) == 0:
        return {
            "has_pii": False,
            "entities": [],
            "column_risk_score": 0.0
        }
    
    entities = []
    column_risk = 0.0
    
    # Detectar por tipo de entidad
    for entity_type in settings.PII_ENTITIES:
        detector_func = _get_detector_function(entity_type)
        if detector_func:
            detected = detector_func(col_data, column)
            if detected["count"] > 0:
                entities.append(detected)
                column_risk += detected["risk_score"]
    
    has_pii = len(entities) > 0
    
    return {
        "has_pii": has_pii,
        "entities": entities,
        "column_risk_score": column_risk
    }


def _get_detector_function(entity_type: str):
    """Retorna la función detectora apropiada para cada tipo de entidad."""
    detectors = {
        "PERSON": _detect_person_names,
        "EMAIL_ADDRESS": _detect_emails,
        "PHONE_NUMBER": _detect_phones,
        "LOCATION": _detect_addresses,
        "ID_NUMBER": _detect_id_numbers,
        "IBAN_CODE": _detect_iban,
        "CREDIT_CARD": _detect_credit_cards
    }
    return detectors.get(entity_type)


def _detect_person_names(series: pd.Series, column_name: str) -> Dict[str, Any]:
    """
    Detecta nombres de personas.
    
    Heurística:
    - Columnas con keywords: nombre, apellido, paciente, fallecido
    - Formato: 2-4 palabras capitalizadas
    """
    keywords = ["nombre", "apellido", "paciente", "fallecido", "persona"]
    col_lower = column_name.lower()
    
    # Si la columna sugiere nombres, asumir que son nombres
    if any(kw in col_lower for kw in keywords):
        count = len(series)
        examples = series.head(3).tolist()
        
        return {
            "type": "PERSON",
            "count": count,
            "examples": examples,
            "risk_score": 3.0,  # Riesgo alto
            "confidence": "alta"
        }
    
    # Detectar patrón de nombres (2-4 palabras capitalizadas)
    name_pattern = re.compile(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3}$')
    matches = series[series.str.match(name_pattern, na=False)]
    
    if len(matches) > len(series) * 0.3:  # >30% parecen nombres
        return {
            "type": "PERSON",
            "count": len(matches),
            "examples": matches.head(3).tolist(),
            "risk_score": 2.5,
            "confidence": "media"
        }
    
    return {"type": "PERSON", "count": 0, "examples": [], "risk_score": 0.0, "confidence": "baja"}


def _detect_emails(series: pd.Series, column_name: str) -> Dict[str, Any]:
    """Detecta direcciones de email."""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    matches = series[series.str.match(email_pattern, na=False)]
    
    if len(matches) > 0:
        return {
            "type": "EMAIL_ADDRESS",
            "count": len(matches),
            "examples": matches.head(2).tolist(),
            "risk_score": 2.0,
            "confidence": "alta"
        }
    
    return {"type": "EMAIL_ADDRESS", "count": 0, "examples": [], "risk_score": 0.0, "confidence": "baja"}


def _detect_phones(series: pd.Series, column_name: str) -> Dict[str, Any]:
    """Detecta números de teléfono."""
    # Patrones comunes: +34 XXX XXX XXX, (XX) XXXX-XXXX, etc.
    phone_patterns = [
        r'\+?\d{1,3}[\s-]?\(?\d{2,3}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}',
        r'\d{9,15}'
    ]
    
    matches = []
    for pattern in phone_patterns:
        phone_regex = re.compile(pattern)
        matches.extend(series[series.str.contains(phone_regex, na=False)])
    
    if len(matches) > 0:
        return {
            "type": "PHONE_NUMBER",
            "count": len(matches),
            "examples": matches[:2],
            "risk_score": 1.5,
            "confidence": "media"
        }
    
    return {"type": "PHONE_NUMBER", "count": 0, "examples": [], "risk_score": 0.0, "confidence": "baja"}


def _detect_addresses(series: pd.Series, column_name: str) -> Dict[str, Any]:
    """
    Detecta direcciones físicas detalladas.
    
    Heurística: direcciones con número de calle, piso, etc.
    """
    keywords = ["direccion", "address", "domicilio", "calle"]
    col_lower = column_name.lower()
    
    if any(kw in col_lower for kw in keywords):
        # Detectar direcciones detalladas (contienen números y palabras como "calle", "nº", "piso")
        detailed_pattern = re.compile(r'(calle|c/|av\.|avenida|nº|piso|planta|puerta)', re.IGNORECASE)
        detailed_addresses = series[series.str.contains(detailed_pattern, na=False)]
        
        if len(detailed_addresses) > 0:
            return {
                "type": "LOCATION",
                "count": len(detailed_addresses),
                "examples": detailed_addresses.head(2).tolist(),
                "risk_score": 2.5,  # Riesgo alto - re-identificación posible
                "confidence": "alta"
            }
    
    return {"type": "LOCATION", "count": 0, "examples": [], "risk_score": 0.0, "confidence": "baja"}


def _detect_id_numbers(series: pd.Series, column_name: str) -> Dict[str, Any]:
    """Detecta números de identificación (DNI, RUT, etc.)."""
    keywords = ["dni", "rut", "cedula", "identificacion", "id"]
    col_lower = column_name.lower()
    
    if any(kw in col_lower for kw in keywords):
        # Asumir que la columna contiene IDs
        count = len(series)
        examples = series.head(2).tolist()
        
        return {
            "type": "ID_NUMBER",
            "count": count,
            "examples": examples,
            "risk_score": 3.0,  # Riesgo crítico
            "confidence": "alta"
        }
    
    # Patrón DNI español: 8 dígitos + letra
    dni_pattern = re.compile(r'^\d{8}[A-Z]$')
    matches = series[series.str.match(dni_pattern, na=False)]
    
    if len(matches) > 0:
        return {
            "type": "ID_NUMBER",
            "count": len(matches),
            "examples": matches.head(2).tolist(),
            "risk_score": 3.0,
            "confidence": "alta"
        }
    
    return {"type": "ID_NUMBER", "count": 0, "examples": [], "risk_score": 0.0, "confidence": "baja"}


def _detect_iban(series: pd.Series, column_name: str) -> Dict[str, Any]:
    """Detecta códigos IBAN."""
    iban_pattern = re.compile(r'^[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}$')
    matches = series[series.str.match(iban_pattern, na=False)]
    
    if len(matches) > 0:
        return {
            "type": "IBAN_CODE",
            "count": len(matches),
            "examples": ["REDACTED"] * min(2, len(matches)),  # No mostrar ejemplos
            "risk_score": 2.5,
            "confidence": "alta"
        }
    
    return {"type": "IBAN_CODE", "count": 0, "examples": [], "risk_score": 0.0, "confidence": "baja"}


def _detect_credit_cards(series: pd.Series, column_name: str) -> Dict[str, Any]:
    """Detecta números de tarjeta de crédito."""
    # Patrón básico: 13-19 dígitos, opcionalmente con espacios o guiones
    cc_pattern = re.compile(r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4,7}$')
    matches = series[series.str.match(cc_pattern, na=False)]
    
    if len(matches) > 0:
        return {
            "type": "CREDIT_CARD",
            "count": len(matches),
            "examples": ["REDACTED"] * min(2, len(matches)),
            "risk_score": 3.0,
            "confidence": "media"
        }
    
    return {"type": "CREDIT_CARD", "count": 0, "examples": [], "risk_score": 0.0, "confidence": "baja"}


def _determine_risk_level(risk_score: float) -> str:
    """Determina el nivel de riesgo basado en el score."""
    for level, (min_score, max_score) in PII_RISK_LEVELS.items():
        if min_score <= risk_score < max_score:
            return level
    return "critico"


def _generate_anonymization_recommendations(
    pii_detected: bool,
    risk_level: str,
    entities_found: List[Dict],
    columns_with_pii: List[str]
) -> List[Dict[str, str]]:
    """Genera recomendaciones de anonimización."""
    recommendations = []
    
    if not pii_detected:
        recommendations.append({
            "priority": "informacion",
            "field": "general",
            "issue": "No se detectó PII en la base de datos",
            "action": "Mantener buenas prácticas de privacidad en registros futuros",
            "impact": "Ninguno - La base cumple con estándares de privacidad"
        })
        return recommendations
    
    # Riesgo crítico
    if risk_level in ["critico", "alto"]:
        recommendations.append({
            "priority": "critica",
            "field": ", ".join(columns_with_pii[:3]),
            "issue": f"Riesgo {risk_level} - PII detectada en {len(columns_with_pii)} columnas",
            "action": "ELIMINAR estas columnas inmediatamente o aplicar hash SHA-256 irreversible",
            "impact": "Crítico - Violación de RGPD/LOPD, riesgo legal y ético"
        })
    
    # Recomendaciones por tipo de entidad
    high_risk_entities = [e for e in entities_found if e["risk_contribution"] >= 2.0]
    
    for entity in high_risk_entities[:3]:  # Top 3
        if entity["type"] == "PERSON":
            action = f"Reemplazar nombres con IDs anonimizados: hash(nombre) o 'PERSONA_{id}'"
        elif entity["type"] == "LOCATION":
            action = "Agregar a nivel de municipio/región, eliminar direcciones exactas"
        elif entity["type"] == "ID_NUMBER":
            action = "Aplicar hash SHA-256 o eliminar columna si no es esencial"
        elif entity["type"] in ["EMAIL_ADDRESS", "PHONE_NUMBER"]:
            action = "Eliminar columna - no es necesaria para análisis epidemiológico"
        else:
            action = "Eliminar o enmascarar datos sensibles"
        
        recommendations.append({
            "priority": "alta",
            "field": entity["column"],
            "issue": f"{entity['count']} instancias de {entity['type']}",
            "action": action,
            "impact": "Alto - Riesgo de re-identificación"
        })
    
    return recommendations
