"""
Configuración de CUIDAR IA
Constantes y rutas del sistema
"""

from pathlib import Path

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = DATA_DIR / "chroma_db" / "production"
TEMP_UPLOAD_DIR = DATA_DIR / "temp_uploads"

# Configuración del RAG
RAG_CONFIG = {
    "collection_name": "cuidar_rag_production",
    "embedding_model": "text-embedding-3-small",
    "llm_model": "gpt-4o-mini",
    "temperature": 0.3,
    "max_tokens": 1200,
    "k_results": 5
}

# Configuración de chunking para documentos locales
CHUNK_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200
}

# Prompt del sistema
SYSTEM_PROMPT = """
Eres un asistente experto en prevención del suicidio, gobernanza de datos y políticas públicas de salud mental.

Tu rol es apoyar a equipos de gobiernos locales y servicios de salud en la toma de decisiones basadas en evidencia para la prevención del suicidio.

Instrucciones:
1. Responde siempre en español, de forma clara y profesional.
2. Basa tus respuestas en el contexto proporcionado (documentos científicos y guías).
3. Cita las fuentes cuando sea relevante (nombre del documento).
4. Si la información del contexto es insuficiente, indícalo claramente.
5. Cuando sea pertinente, sugiere que el usuario considere investigación o datos locales para complementar las recomendaciones.
6. Mantén un tono técnico pero accesible para tomadores de decisiones.
7. Prioriza recomendaciones prácticas y accionables.

Recuerda: Tu objetivo es facilitar el uso efectivo de datos para la prevención del suicidio, alineado con las dimensiones del índice CUIDAR (Accesibilidad, Calidad, Interoperabilidad, Uso, Capacidad Analítica, Gestión del Conocimiento, Ética y Gobernanza).
"""

# Categorías de documentos
DOCUMENT_CATEGORIES = {
    "clinical": "Enfoques Clínicos y Sistemas de Salud",
    "ethics": "Fundamentos Éticos y Gobernanza de Datos",
    "public_health": "Perspectivas Salud Pública y Comunitaria",
    "local": "Documentos Locales del Usuario"
}
