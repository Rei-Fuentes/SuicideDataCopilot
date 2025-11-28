"""
Configuración centralizada para CUIDAR IA
Fusión de configuración original + Fase 3
"""

from pathlib import Path
from typing import Dict, Tuple, Optional
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    """Configuración global del sistema - Todas las fases"""
    
    # ==================== GENERAL ====================
    APP_NAME: str = "CUIDAR IA - Policy Copilot"
    DEBUG: bool = False
    
    # ==================== RUTAS ====================
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: str = "data"
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    ANONYMIZED_DIR: Path = BASE_DIR / "data" / "anonymized"
    OUTPUTS_DIR: str = "data/outputs"
    VECTORSTORE_DIR: str = "data/vectorstore"
    
    # ==================== OPENAI API (ÚNICO PROVIDER) ====================
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_TEMPERATURE: float = 0.3  # Respuestas más deterministas
    OPENAI_MAX_TOKENS: int = 4000
    
    # ==================== FASE 3: EVALUADOR DE BASES DE DATOS ====================
    
    # Modelo específico para evaluador (puede diferir del RAG)
    EVALUATOR_MODEL: str = "gpt-4o"
    EVALUATOR_TEMPERATURE: float = 0.3
    
    # Umbrales de completitud
    COMPLETENESS_THRESHOLD: float = 0.85  # 85% completitud mínima recomendada
    COMPLETENESS_CRITICAL_THRESHOLD: float = 0.70  # 70% para campos críticos
    
    # Detección PII (Información Personal Identificable)
    PII_RISK_THRESHOLD: float = 5.0  # Score > 5.0 = riesgo crítico
    PII_ENTITIES: list = [
        "PERSON",           # Nombres de personas
        "EMAIL_ADDRESS",    # Emails
        "PHONE_NUMBER",     # Teléfonos
        "LOCATION",         # Direcciones exactas
        "ID_NUMBER",        # DNI, RUT, etc.
        "IBAN_CODE",        # Códigos bancarios
        "CREDIT_CARD",      # Tarjetas de crédito
    ]
    
    # Machine Learning readiness
    ML_MIN_SAMPLES: int = 100  # Mínimo de registros para ML
    ML_MIN_FEATURES: int = 5   # Mínimo de features útiles
    ML_VIABILITY_THRESHOLD: float = 0.65  # Umbral de viabilidad general
    ML_IMBALANCE_THRESHOLD: float = 0.20  # Balance mínimo de clases (20%)
    MIN_FEATURES_FOR_ML: int = 3  # Alias para compatibilidad
    
    # Análisis geoespacial
    GEOSPATIAL_MIN_COVERAGE: float = 0.70  # 70% de casos geocodificables
    GEOSPATIAL_MIN_POINTS: int = 50  # Mínimo para clustering
    
    # Análisis semántico
    SEMANTIC_AGE_MIN: int = 0
    SEMANTIC_AGE_MAX: int = 120
    SEMANTIC_METHODS_STANDARD: list = [
        "ahorcamiento",
        "arma de fuego",
        "intoxicacion",
        "precipitacion",
        "arma blanca",
        "otro"
    ]
    
    # ==================== SEGURIDAD ====================
    FILE_RETENTION_HOURS: int = 1  # Auto-eliminar archivos tras 1 hora
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list = [".csv", ".xlsx", ".xls"]
    
    # ==================== PROCESAMIENTO PARALELO ====================
    MAX_WORKERS: int = 6  # Número de analizadores en paralelo
    TIMEOUT_SECONDS: int = 300  # Timeout por analizador (5 min)
    
    # ==================== VISUALIZACIONES ====================
    PLOT_HEIGHT: int = 400
    PLOT_COLOR_MISSING: str = "#FF5F9E"  # Rosado acento
    PLOT_COLOR_COMPLETE: str = "#0A1A2F"  # Azul oscuro
    PLOT_TEMPLATE: str = "plotly_dark"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # CLAVE: Permite campos adicionales sin error


# Instancia global
settings = Settings()


# ==================== CONSTANTES ADICIONALES ====================

# Mapeo de niveles de riesgo PII
PII_RISK_LEVELS: Dict[str, Tuple[float, str]] = {
    "bajo": (0.0, 3.0),
    "moderado": (3.0, 5.0),
    "alto": (5.0, 7.0),
    "critico": (7.0, 10.0)
}

# Campos críticos para bases de datos de suicidio
CRITICAL_FIELDS_SUICIDE_DATA: list = [
    "fecha",
    "edad",
    "sexo",
    "metodo",
    "municipio",
    "tipo_evento"  # intento vs consumado
]

# Mensajes de advertencia ética
ETHICAL_WARNING_PII = """
⚠️ **RIESGO ÉTICO DETECTADO**

Se ha identificado información de identificación personal (PII) en tu base de datos.

**¿Por qué esto es un problema?**
1. Violación de privacidad de personas fallecidas y sus familias
2. Incumplimiento de leyes de protección de datos (RGPD/LOPD)
3. Riesgo de re-identificación en análisis públicos

**Acción tomada:**
✅ Hemos anonimizado automáticamente estos datos
✅ El análisis se realizará sobre la versión segura
✅ Los datos originales NO serán almacenados

**Recomendación:**
Elimina estas columnas de tu base de datos fuente antes de compartir 
o publicar cualquier resultado.
"""


# Advertencia sobre API Key
if not settings.OPENAI_API_KEY:
    print("⚠️  OPENAI_API_KEY no configurada. Funciones de IA deshabilitadas.")
    print("   Para habilitar: agregar OPENAI_API_KEY=sk-... al archivo .env")
