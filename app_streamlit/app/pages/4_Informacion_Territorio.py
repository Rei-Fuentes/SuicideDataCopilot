"""
CUIDAR IA - Información de tu Territorio
Subida de documentos locales para análisis contextualizado
"""

import streamlit as st
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from utils.rag_engine import get_rag_engine

# Configuración de la página
st.set_page_config(
    page_title="Información Territorio - CUIDAR IA",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS con la paleta de colores premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --azul-oscuro: #0A1A2F;
        --azul-profundo: #061018;
        --rosado-acento: #FF5F9E;
        --blanco-suave: #F5F7FA;
        --gris-texto: #B8C5D6;
    }
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0A1A2F;
    }
    
    /* Header de página */
    .page-header {
        background: linear-gradient(135deg, #0D2137 0%, #0A1A2F 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 95, 158, 0.1);
    }
    
    .page-title {
        font-size: 2rem;
        font-weight: 600;
        color: #F5F7FA;
        margin-bottom: 0.5rem;
    }
    
    .page-subtitle {
        font-size: 1rem;
        color: #B8C5D6;
        font-weight: 300;
    }
    
    /* Tarjetas de tipo de documento */
    .doc-type-card {
        background: linear-gradient(145deg, #0D2137 0%, #0A1A2F 100%);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(255, 95, 158, 0.1);
        transition: all 0.3s ease;
    }
    
    .doc-type-card:hover {
        border-color: rgba(255, 95, 158, 0.3);
    }
    
    .doc-type-title {
        font-weight: 600;
        color: #F5F7FA;
        margin-bottom: 0.3rem;
        font-size: 0.95rem;
    }
    
    .doc-type-desc {
        font-size: 0.8rem;
        color: #B8C5D6;
        line-height: 1.4;
    }
    
    /* Panel de estado */
    .status-panel {
        background: linear-gradient(145deg, #0D2137 0%, #0A1A2F 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 95, 158, 0.2);
        text-align: center;
    }
    
    .status-metric {
        font-size: 3rem;
        font-weight: 700;
        color: #FF5F9E;
    }
    
    .status-label {
        font-size: 0.9rem;
        color: #B8C5D6;
        margin-top: 0.5rem;
    }
    
    /* Info box */
    .info-box {
        background: rgba(74, 111, 165, 0.15);
        border: 1px solid rgba(74, 111, 165, 0.3);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #F5F7FA;
        font-size: 0.9rem;
    }
    
    .info-box p {
        margin: 0;
        color: #F5F7FA;
    }
    
    /* Warning box */
    .warning-box {
        background: rgba(255, 95, 158, 0.1);
        border: 1px solid rgba(255, 95, 158, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box strong {
        color: #FF5F9E;
    }
    
    .warning-box p {
        color: #F5F7FA;
        margin-top: 0.5rem;
        margin-bottom: 0;
        font-size: 0.9rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #061018;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #F5F7FA;
    }
    
    /* Botones */
    .stButton > button {
        background: linear-gradient(135deg, #FF5F9E 0%, #FF8FAE 100%);
        color: #0A1A2F;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 95, 158, 0.3);
    }
    
    /* Botones secundarios */
    .secondary-btn > button {
        background: transparent !important;
        border: 1px solid rgba(255, 95, 158, 0.5) !important;
        color: #F5F7FA !important;
    }
    
    .secondary-btn > button:hover {
        background: rgba(255, 95, 158, 0.1) !important;
        border-color: #FF5F9E !important;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #0D2137;
        border-radius: 12px;
        padding: 1rem;
        border: 2px dashed rgba(255, 95, 158, 0.3);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #FF5F9E;
    }
    
    /* Textos generales */
    p, li {
        color: #B8C5D6;
    }
    
    h1, h2, h3, h4 {
        color: #F5F7FA;
    }
    
    /* Notas */
    .notes-section {
        background: #061018;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .notes-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #F5F7FA;
        margin-bottom: 1rem;
    }
    
    .notes-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
    }
    
    .note-item h4 {
        font-size: 0.95rem;
        color: #FF5F9E;
        margin-bottom: 0.5rem;
    }
    
    .note-item p {
        font-size: 0.85rem;
        color: #B8C5D6;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="page-header">
    <h1 class="page-title">Información de tu Territorio</h1>
    <p class="page-subtitle">
        Sube documentos locales para obtener análisis contextualizados adaptados a tu realidad institucional y comunitaria
    </p>
</div>
""", unsafe_allow_html=True)

# Inicializar motor RAG
if "rag_engine" not in st.session_state:
    with st.spinner("Cargando sistema..."):
        try:
            st.session_state.rag_engine = get_rag_engine()
        except Exception as e:
            st.error(f"Error al cargar el sistema: {str(e)}")
            st.stop()

# Columnas principales
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Subir Documento")
    
    # Uploader de archivos
    uploaded_file = st.file_uploader(
        "Selecciona un archivo PDF",
        type=["pdf"],
        help="Sube informes epidemiológicos, planes de prevención, investigaciones locales u otros documentos relevantes."
    )
    
    if uploaded_file is not None:
        st.markdown(f"**Archivo seleccionado:** {uploaded_file.name}")
        st.markdown(f"**Tamaño:** {uploaded_file.size / 1024:.1f} KB")
        
        if st.button("Procesar documento", type="primary"):
            with st.spinner("Procesando documento..."):
                result = st.session_state.rag_engine.add_local_document(
                    uploaded_file,
                    uploaded_file.name
                )
            
            if result["success"]:
                st.success(result["message"])
                if "pages" in result:
                    st.info(f"Páginas procesadas: {result['pages']}")
            else:
                st.error(result["message"])
    
    st.divider()
    
    # Información sobre tipos de documentos
    st.markdown("### Tipos de Documentos Recomendados")
    
    doc_types = [
        ("Informes Epidemiológicos", "Datos de incidencia, prevalencia y tendencias locales de suicidio e intentos."),
        ("Planes de Prevención", "Estrategias y programas de prevención del suicidio a nivel municipal o regional."),
        ("Investigaciones Locales", "Estudios realizados por universidades u observatorios de tu zona."),
        ("Informes de Presupuesto", "Asignación de recursos para salud mental y prevención."),
        ("Actas y Protocolos", "Acuerdos interinstitucionales, protocolos de atención y rutas de derivación.")
    ]
    
    for title, desc in doc_types:
        st.markdown(f"""
        <div class="doc-type-card">
            <div class="doc-type-title">{title}</div>
            <div class="doc-type-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### Documentos Cargados")
    
    local_count = st.session_state.rag_engine.get_local_docs_count()
    
    if local_count > 0:
        st.markdown(f"""
        <div class="status-panel">
            <div class="status-metric">{local_count}</div>
            <div class="status-label">fragmentos indexados</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <p>Los documentos locales se incluirán automáticamente en las búsquedas del chat.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("Eliminar todos los documentos locales", use_container_width=True):
            result = st.session_state.rag_engine.clear_local_documents()
            if result["success"]:
                st.success(result["message"])
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("### Siguiente paso")
        st.markdown("Ahora puedes hacer consultas que consideren tus documentos locales.")
        
        if st.button("Ir a Consultar CUIDAR IA", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Consultar_CUIDAR_IA.py")
    
    else:
        st.markdown(f"""
        <div class="status-panel">
            <div class="status-metric">0</div>
            <div class="status-label">documentos cargados</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <strong>¿Por qué subir documentos locales?</strong>
            <p>
                Al agregar información de tu contexto, el asistente puede darte 
                recomendaciones más específicas y relevantes para tu situación institucional.
            </p>
        </div>
        """, unsafe_allow_html=True)

# Notas importantes
st.markdown("""
<div class="notes-section">
    <div class="notes-title">Notas Importantes</div>
    <div class="notes-grid">
        <div class="note-item">
            <h4>Privacidad y Seguridad</h4>
            <p>
                Los documentos se procesan localmente en tu sesión. 
                No se almacenan permanentemente en el servidor. 
                Se eliminan al cerrar la aplicación.
            </p>
        </div>
        <div class="note-item">
            <h4>Limitaciones</h4>
            <p>
                Solo se aceptan archivos PDF. 
                El texto debe ser seleccionable (no imágenes escaneadas). 
                Tamaño máximo recomendado: 50 MB.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
