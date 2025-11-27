"""
Motor de Anonimización Automática
Anonimiza datos sensibles antes del análisis LLM
"""

import pandas as pd
import numpy as np
import hashlib
from typing import Dict, List, Tuple, Any
import re


def anonymize_dataframe(
    df: pd.DataFrame,
    pii_columns: List[str],
    anonymization_strategy: str = "hash"
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Anonimiza un DataFrame eliminando o enmascarando PII.
    
    Args:
        df: DataFrame original
        pii_columns: Lista de columnas con PII detectada
        anonymization_strategy: Estrategia de anonimización
            - "hash": Reemplaza con hash SHA-256
            - "mask": Reemplaza con máscaras genéricas
            - "remove": Elimina la columna
            
    Returns:
        Tupla (DataFrame anonimizado, Mapeo de transformaciones)
    """
    df_anon = df.copy()
    transformations = {}
    
    for col in pii_columns:
        if col not in df_anon.columns:
            continue
        
        # Determinar tipo de PII y aplicar estrategia apropiada
        col_lower = col.lower()
        
        if any(kw in col_lower for kw in ["nombre", "apellido", "person"]):
            df_anon[col], transform = _anonymize_names(df_anon[col], anonymization_strategy)
            transformations[col] = transform
            
        elif any(kw in col_lower for kw in ["email", "correo"]):
            df_anon[col], transform = _anonymize_emails(df_anon[col])
            transformations[col] = transform
            
        elif any(kw in col_lower for kw in ["telefono", "phone"]):
            df_anon[col], transform = _anonymize_phones(df_anon[col])
            transformations[col] = transform
            
        elif any(kw in col_lower for kw in ["direccion", "address", "domicilio"]):
            df_anon[col], transform = _anonymize_addresses(df_anon[col])
            transformations[col] = transform
            
        elif any(kw in col_lower for kw in ["dni", "rut", "cedula", "id"]):
            df_anon[col], transform = _anonymize_ids(df_anon[col], anonymization_strategy)
            transformations[col] = transform
            
        else:
            # Por defecto: hash o eliminación
            if anonymization_strategy == "remove":
                df_anon = df_anon.drop(columns=[col])
                transformations[col] = "column_removed"
            else:
                df_anon[col], transform = _anonymize_generic(df_anon[col], anonymization_strategy)
                transformations[col] = transform
    
    return df_anon, transformations


def _anonymize_names(series: pd.Series, strategy: str) -> Tuple[pd.Series, str]:
    """Anonimiza nombres de personas."""
    if strategy == "hash":
        return series.apply(lambda x: _hash_value(str(x)) if pd.notna(x) else x), "hashed"
    elif strategy == "mask":
        # Reemplazar con PERSONA_N
        unique_names = series.dropna().unique()
        name_mapping = {name: f"PERSONA_{i+1}" for i, name in enumerate(unique_names)}
        return series.map(lambda x: name_mapping.get(x, x)), "masked"
    else:  # remove
        return pd.Series([np.nan] * len(series)), "removed"


def _anonymize_emails(series: pd.Series) -> Tuple[pd.Series, str]:
    """Anonimiza emails - solo se conserva dominio."""
    def mask_email(email):
        if pd.isna(email):
            return email
        try:
            local, domain = str(email).split("@")
            return f"usuario_anonimo@{domain}"
        except:
            return "email_invalido"
    
    return series.apply(mask_email), "masked_preserving_domain"


def _anonymize_phones(series: pd.Series) -> Tuple[pd.Series, str]:
    """Anonimiza teléfonos - solo se conserva código de área."""
    def mask_phone(phone):
        if pd.isna(phone):
            return phone
        phone_str = re.sub(r'\D', '', str(phone))  # Solo dígitos
        if len(phone_str) >= 6:
            return phone_str[:3] + "X" * (len(phone_str) - 3)
        return "XXX"
    
    return series.apply(mask_phone), "masked_partial"


def _anonymize_addresses(series: pd.Series) -> Tuple[pd.Series, str]:
    """Anonimiza direcciones - solo se conserva municipio/región."""
    def mask_address(addr):
        if pd.isna(addr):
            return addr
        # Extraer última palabra (suele ser municipio/ciudad)
        words = str(addr).split()
        if len(words) > 1:
            return words[-1]  # Solo última palabra (municipio)
        return "LOCALIDAD_ANONIMA"
    
    return series.apply(mask_address), "aggregated_to_municipality"


def _anonymize_ids(series: pd.Series, strategy: str) -> Tuple[pd.Series, str]:
    """Anonimiza IDs (DNI, RUT, etc.)."""
    if strategy == "hash":
        return series.apply(lambda x: _hash_value(str(x)) if pd.notna(x) else x), "hashed"
    else:
        return pd.Series([np.nan] * len(series)), "removed"


def _anonymize_generic(series: pd.Series, strategy: str) -> Tuple[pd.Series, str]:
    """Anonimización genérica para columnas sin tipo específico."""
    if strategy == "hash":
        return series.apply(lambda x: _hash_value(str(x)) if pd.notna(x) else x), "hashed"
    else:
        return series.apply(lambda x: "[REDACTADO]" if pd.notna(x) else x), "masked"


def _hash_value(value: str) -> str:
    """
    Genera hash SHA-256 de un valor.
    
    Returns:
        Hash hexadecimal truncado a 16 caracteres
    """
    hash_obj = hashlib.sha256(value.encode('utf-8'))
    return hash_obj.hexdigest()[:16]


def generate_anonymization_report(
    original_df: pd.DataFrame,
    anonymized_df: pd.DataFrame,
    transformations: Dict[str, str]
) -> Dict[str, Any]:
    """
    Genera reporte de anonimización realizada.
    
    Returns:
        Diccionario con estadísticas de anonimización
    """
    return {
        "original_columns": len(original_df.columns),
        "anonymized_columns": len(anonymized_df.columns),
        "columns_removed": len(original_df.columns) - len(anonymized_df.columns),
        "transformations_applied": len(transformations),
        "transformation_details": transformations,
        "data_preserved": {
            "rows": len(anonymized_df),
            "usable_columns": len([col for col in anonymized_df.columns 
                                   if anonymized_df[col].notna().sum() > 0])
        }
    }


def validate_anonymization(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Valida que el DataFrame esté correctamente anonimizado.
    
    Returns:
        Diccionario con resultado de validación
    """
    validation = {
        "is_safe": True,
        "warnings": [],
        "residual_pii_risk": 0.0
    }
    
    # Buscar patrones de PII residuales
    for col in df.columns:
        col_sample = df[col].dropna().astype(str).head(100)
        
        # Emails
        if col_sample.str.contains(r'@.*\.', regex=True, na=False).any():
            validation["is_safe"] = False
            validation["warnings"].append(f"Posibles emails en columna '{col}'")
            validation["residual_pii_risk"] += 1.0
        
        # Teléfonos (patrones sin anonimizar)
        if col_sample.str.contains(r'\d{9,}', regex=True, na=False).any():
            validation["warnings"].append(f"Posibles teléfonos en columna '{col}'")
            validation["residual_pii_risk"] += 0.5
        
        # Nombres propios (2-3 palabras capitalizadas)
        name_pattern = r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,2}$'
        if col_sample.str.match(name_pattern, na=False).sum() > 10:
            validation["is_safe"] = False
            validation["warnings"].append(f"Posibles nombres en columna '{col}'")
            validation["residual_pii_risk"] += 2.0
    
    return validation
