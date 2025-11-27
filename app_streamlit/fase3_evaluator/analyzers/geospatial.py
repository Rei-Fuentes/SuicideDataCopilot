"""
Analizador Geoespacial
Evalúa capacidad de geocodificación y análisis espacial
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from config import settings


def analyze_geospatial(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analiza capacidad geoespacial de los datos.
    
    Args:
        df: DataFrame a analizar
        
    Returns:
        Diccionario con análisis geoespacial
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío")
    
    # Detectar columnas geográficas
    lat_col = _find_column(df, ["latitud", "lat", "latitude"])
    lon_col = _find_column(df, ["longitud", "lon", "lng", "longitude"])
    address_col = _find_column(df, ["direccion", "address", "domicilio"])
    municipality_col = _find_column(df, ["municipio", "comuna", "city", "ciudad", "localidad"])
    region_col = _find_column(df, ["region", "provincia", "state", "departamento"])
    
    # Análisis de coordenadas
    coordinates_analysis = None
    if lat_col and lon_col:
        coordinates_analysis = _analyze_coordinates(df, lat_col, lon_col)
    
    # Análisis de direcciones
    address_analysis = None
    if address_col:
        address_analysis = _analyze_addresses(df, address_col)
    
    # Análisis de municipios/localidades
    municipality_analysis = None
    if municipality_col:
        municipality_analysis = _analyze_municipalities(df, municipality_col, region_col)
    
    # Capacidad de geocodificación
    geocoding_capability = _assess_geocoding_capability(
        coordinates_analysis,
        address_analysis,
        municipality_analysis
    )
    
    # Potencial de clustering espacial
    clustering_potential = _assess_clustering_potential(
        df,
        coordinates_analysis,
        municipality_analysis
    )
    
    # Resumen y recomendaciones
    summary = _generate_geospatial_summary(
        geocoding_capability,
        clustering_potential,
        coordinates_analysis,
        municipality_analysis
    )
    
    recommendations = _generate_geospatial_recommendations(
        geocoding_capability,
        clustering_potential,
        coordinates_analysis,
        address_analysis,
        municipality_analysis
    )
    
    return {
        "summary": summary,
        "coordinates_analysis": coordinates_analysis,
        "address_analysis": address_analysis,
        "municipality_analysis": municipality_analysis,
        "geocoding_capability": geocoding_capability,
        "clustering_potential": clustering_potential,
        "required_fields": _get_required_fields(geocoding_capability),
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


def _analyze_coordinates(df: pd.DataFrame, lat_col: str, lon_col: str) -> Dict[str, Any]:
    """
    Analiza validez de coordenadas geográficas.
    
    Returns:
        Diccionario con análisis de coordenadas
    """
    lat_series = pd.to_numeric(df[lat_col], errors='coerce')
    lon_series = pd.to_numeric(df[lon_col], errors='coerce')
    
    total = len(df)
    valid_pairs = 0
    invalid_coords = []
    
    for idx in df.index:
        lat = lat_series[idx]
        lon = lon_series[idx]
        
        # Ambas deben ser no-nulas
        if pd.isna(lat) or pd.isna(lon):
            continue
        
        # Verificar rangos válidos
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            # Verificar que no sea (0,0) - punto nulo común
            if not (abs(lat) < 0.001 and abs(lon) < 0.001):
                valid_pairs += 1
            else:
                invalid_coords.append({
                    "row": int(idx),
                    "lat": float(lat),
                    "lon": float(lon),
                    "issue": "Coordenadas en (0,0) - probablemente nulas"
                })
        else:
            invalid_coords.append({
                "row": int(idx),
                "lat": float(lat),
                "lon": float(lon),
                "issue": "Coordenadas fuera de rango válido"
            })
    
    coverage = valid_pairs / total if total > 0 else 0.0
    
    # Calcular bounding box si hay coordenadas válidas
    bounding_box = None
    if valid_pairs > 0:
        valid_lats = lat_series[(lat_series >= -90) & (lat_series <= 90)]
        valid_lons = lon_series[(lon_series >= -180) & (lon_series <= 180)]
        
        bounding_box = {
            "min_lat": float(valid_lats.min()),
            "max_lat": float(valid_lats.max()),
            "min_lon": float(valid_lons.min()),
            "max_lon": float(valid_lons.max())
        }
    
    return {
        "columns": {"latitude": lat_col, "longitude": lon_col},
        "total_records": total,
        "valid_pairs": valid_pairs,
        "coverage": float(coverage),
        "invalid_coords": invalid_coords[:10],  # Top 10
        "bounding_box": bounding_box
    }


def _analyze_addresses(df: pd.DataFrame, address_col: str) -> Dict[str, Any]:
    """
    Analiza calidad de direcciones para geocodificación.
    
    Returns:
        Diccionario con análisis de direcciones
    """
    addresses = df[address_col].dropna().astype(str)
    total = len(df)
    non_null = len(addresses)
    
    # Características de calidad
    detailed_addresses = 0
    generic_addresses = 0
    
    for addr in addresses:
        addr_lower = addr.lower().strip()
        
        # Direcciones detalladas (contienen números)
        if any(char.isdigit() for char in addr):
            detailed_addresses += 1
        
        # Direcciones genéricas (solo municipio/ciudad)
        elif len(addr_lower.split()) <= 2:
            generic_addresses += 1
    
    return {
        "column": address_col,
        "total_records": total,
        "non_null_count": non_null,
        "coverage": float(non_null / total) if total > 0 else 0.0,
        "detailed_addresses": detailed_addresses,
        "generic_addresses": generic_addresses,
        "geocodable_estimate": float(detailed_addresses / non_null) if non_null > 0 else 0.0
    }


def _analyze_municipalities(
    df: pd.DataFrame,
    municipality_col: str,
    region_col: Optional[str]
) -> Dict[str, Any]:
    """
    Analiza distribución por municipios/localidades.
    
    Returns:
        Diccionario con análisis municipal
    """
    municipalities = df[municipality_col].dropna()
    total = len(df)
    non_null = len(municipalities)
    
    # Distribución
    municipality_counts = municipalities.value_counts()
    
    # Análisis regional si existe
    regional_dist = None
    if region_col:
        regions = df[region_col].dropna()
        regional_dist = {
            "column": region_col,
            "unique_regions": int(regions.nunique()),
            "distribution": regions.value_counts().head(10).to_dict()
        }
    
    return {
        "column": municipality_col,
        "total_records": total,
        "non_null_count": non_null,
        "coverage": float(non_null / total) if total > 0 else 0.0,
        "unique_municipalities": int(municipality_counts.nunique()),
        "top_municipalities": municipality_counts.head(10).to_dict(),
        "regional_analysis": regional_dist
    }


def _assess_geocoding_capability(
    coordinates_analysis: Optional[Dict],
    address_analysis: Optional[Dict],
    municipality_analysis: Optional[Dict]
) -> Dict[str, Any]:
    """
    Evalúa la capacidad de geocodificar los datos.
    
    Returns:
        Evaluación de capacidad de geocodificación
    """
    capability = {
        "has_coordinates": False,
        "has_addresses": False,
        "has_municipalities": False,
        "coverage": 0.0,
        "method": None,
        "quality": "none"
    }
    
    # Prioridad 1: Coordenadas directas
    if coordinates_analysis and coordinates_analysis["coverage"] > 0:
        capability["has_coordinates"] = True
        capability["coverage"] = coordinates_analysis["coverage"]
        capability["method"] = "coordenadas_directas"
        
        if coordinates_analysis["coverage"] >= settings.GEOSPATIAL_MIN_COVERAGE:
            capability["quality"] = "excelente"
        elif coordinates_analysis["coverage"] >= 0.5:
            capability["quality"] = "buena"
        else:
            capability["quality"] = "parcial"
    
    # Prioridad 2: Direcciones detalladas
    elif address_analysis and address_analysis["geocodable_estimate"] > 0:
        capability["has_addresses"] = True
        capability["coverage"] = address_analysis["geocodable_estimate"]
        capability["method"] = "geocodificacion_direcciones"
        
        if address_analysis["geocodable_estimate"] >= 0.6:
            capability["quality"] = "buena"
        else:
            capability["quality"] = "parcial"
    
    # Prioridad 3: Municipios (geocodificación a nivel agregado)
    elif municipality_analysis and municipality_analysis["coverage"] > 0:
        capability["has_municipalities"] = True
        capability["coverage"] = municipality_analysis["coverage"]
        capability["method"] = "geocodificacion_municipal"
        capability["quality"] = "basica"
    
    return capability


def _assess_clustering_potential(
    df: pd.DataFrame,
    coordinates_analysis: Optional[Dict],
    municipality_analysis: Optional[Dict]
) -> Dict[str, Any]:
    """
    Evalúa potencial para análisis de clustering espacial.
    
    Returns:
        Evaluación de potencial de clustering
    """
    potential = {
        "feasible": False,
        "method": None,
        "min_samples_met": False,
        "spatial_variation": None,
        "recommended_algorithms": []
    }
    
    # Verificar mínimo de muestras
    if len(df) < settings.GEOSPATIAL_MIN_POINTS:
        return potential
    
    potential["min_samples_met"] = True
    
    # Clustering por coordenadas (más preciso)
    if coordinates_analysis and coordinates_analysis["coverage"] >= 0.5:
        potential["feasible"] = True
        potential["method"] = "coordenadas_exactas"
        potential["recommended_algorithms"] = ["DBSCAN", "HDBSCAN", "K-means espacial"]
        
        # Estimar variación espacial
        if coordinates_analysis.get("bounding_box"):
            bbox = coordinates_analysis["bounding_box"]
            lat_range = bbox["max_lat"] - bbox["min_lat"]
            lon_range = bbox["max_lon"] - bbox["min_lon"]
            potential["spatial_variation"] = {
                "lat_range_degrees": float(lat_range),
                "lon_range_degrees": float(lon_range),
                "area_type": "local" if max(lat_range, lon_range) < 0.5 else "regional" if max(lat_range, lon_range) < 2 else "amplio"
            }
    
    # Clustering por municipio (agregado)
    elif municipality_analysis and municipality_analysis["unique_municipalities"] >= 5:
        potential["feasible"] = True
        potential["method"] = "agregacion_municipal"
        potential["recommended_algorithms"] = ["Agregación por municipio", "Análisis de hotspots"]
        potential["spatial_variation"] = {
            "unique_locations": municipality_analysis["unique_municipalities"]
        }
    
    return potential


def _generate_geospatial_summary(
    geocoding_capability: Dict,
    clustering_potential: Dict,
    coordinates_analysis: Optional[Dict],
    municipality_analysis: Optional[Dict]
) -> Dict[str, Any]:
    """Genera resumen del análisis geoespacial."""
    
    # Score basado en capacidades
    score = 0.0
    
    if geocoding_capability["quality"] == "excelente":
        score = 90.0
    elif geocoding_capability["quality"] == "buena":
        score = 70.0
    elif geocoding_capability["quality"] == "parcial":
        score = 50.0
    elif geocoding_capability["quality"] == "basica":
        score = 30.0
    
    # Bonus por clustering
    if clustering_potential["feasible"]:
        score += 10.0
    
    return {
        "geocodable": geocoding_capability["coverage"] > 0,
        "coverage": geocoding_capability["coverage"],
        "quality": geocoding_capability["quality"],
        "clustering_feasible": clustering_potential["feasible"],
        "score": min(100.0, score),
        "primary_method": geocoding_capability["method"]
    }


def _get_required_fields(geocoding_capability: Dict) -> List[str]:
    """Retorna los campos requeridos para análisis geoespacial."""
    if geocoding_capability["has_coordinates"]:
        return ["latitud", "longitud"]
    elif geocoding_capability["has_addresses"]:
        return ["direccion", "municipio", "region"]
    elif geocoding_capability["has_municipalities"]:
        return ["municipio", "region"]
    else:
        return []


def _generate_geospatial_recommendations(
    geocoding_capability: Dict,
    clustering_potential: Dict,
    coordinates_analysis: Optional[Dict],
    address_analysis: Optional[Dict],
    municipality_analysis: Optional[Dict]
) -> List[Dict[str, str]]:
    """Genera recomendaciones geoespaciales."""
    recommendations = []
    
    # Sin capacidad geoespacial
    if geocoding_capability["quality"] == "none":
        recommendations.append({
            "priority": "critica",
            "field": "geolocalización",
            "issue": "No hay información geográfica utilizable",
            "action": "Agregar al menos columna de municipio/localidad en registros futuros",
            "impact": "Alto - Imposibilita análisis de patrones espaciales y clusters"
        })
        return recommendations
    
    # Coordenadas con baja cobertura
    if coordinates_analysis and coordinates_analysis["coverage"] < settings.GEOSPATIAL_MIN_COVERAGE:
        recommendations.append({
            "priority": "alta",
            "field": "coordenadas",
            "issue": f"Solo {coordinates_analysis['coverage']*100:.1f}% de registros tienen coordenadas válidas",
            "action": "Geocodificar direcciones faltantes o usar servicios de geolocalización",
            "impact": "Alto - Limita precisión de análisis espaciales"
        })
    
    # Coordenadas inválidas
    if coordinates_analysis and len(coordinates_analysis.get("invalid_coords", [])) > 0:
        recommendations.append({
            "priority": "media",
            "field": "coordenadas",
            "issue": f"{len(coordinates_analysis['invalid_coords'])} registros con coordenadas inválidas",
            "action": "Revisar y corregir coordenadas fuera de rango o en (0,0)",
            "impact": "Medio - Genera ruido en visualizaciones"
        })
    
    # Potencial de clustering no aprovechado
    if not clustering_potential["feasible"] and municipality_analysis:
        recommendations.append({
            "priority": "baja",
            "field": "clustering",
            "issue": f"Solo {len(municipality_analysis)} registros - insuficiente para clustering robusto",
            "action": "Acumular más registros o realizar análisis agregado por municipio",
            "impact": "Bajo - Análisis espaciales serán limitados"
        })
    
    return recommendations
