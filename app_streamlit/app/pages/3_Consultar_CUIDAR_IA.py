"""
CUIDAR IA - Consultar a CUIDAR IA
Asistente RAG basado en evidencia científica
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
    page_title="Consultar CUIDAR IA",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS con la paleta de colores premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --azul-oscuro: #0A1A2F;
        --azul-profundo: #050D18;
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
    
    /* Mensajes del chat */
    .chat-message {
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    .user-message {
        background: linear-gradient(135deg, #1a3a5c 0%, #0D2137 100%);
        border-left: 3px solid #FF5F9E;
        color: #F5F7FA;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #0D2137 0%, #0A1A2F 100%);
        border-left: 3px solid #4A6FA5;
        color: #F5F7FA;
    }
    
    .message-label {
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .user-label {
        color: #FF5F9E;
    }
    
    .assistant-label {
        color: #4A6FA5;
    }
    
    .message-content {
        color: #F5F7FA;
    }
    
    /* Etiquetas de fuentes */
    .source-tag {
        display: inline-block;
        background-color: rgba(74, 111, 165, 0.3);
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        margin: 0.2rem;
        color: #B8C5D6;
        border: 1px solid rgba(74, 111, 165, 0.3);
    }
    
    .local-tag {
        background-color: rgba(255, 95, 158, 0.2);
        border-color: rgba(255, 95, 158, 0.3);
        color: #FF5F9E;
    }
    
    .sources-container {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(184, 197, 214, 0.1);
    }
    
    .sources-label {
        font-size: 0.8rem;
        color: #B8C5D6;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #050D18;
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
    
    /* Botones secundarios en sidebar */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: 1px solid rgba(255, 95, 158, 0.5);
        color: #F5F7FA;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 95, 158, 0.1);
        border-color: #FF5F9E;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(255, 95, 158, 0.1);
        border: 1px solid rgba(255, 95, 158, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #F5F7FA;
    }
    
    /* Welcome box */
    .welcome-box {
        background: linear-gradient(135deg, #0D2137 0%, #0A1A2F 100%);
        border: 1px solid rgba(255, 95, 158, 0.2);
        border-radius: 12px;
        padding: 2rem;
        color: #F5F7FA;
    }
    
    .welcome-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #FF5F9E;
        margin-bottom: 1rem;
    }
    
    .welcome-text {
        color: #B8C5D6;
        line-height: 1.6;
    }
    
    .welcome-list {
        margin-top: 1rem;
        padding-left: 1.5rem;
    }
    
    .welcome-list li {
        color: #F5F7FA;
        margin-bottom: 0.5rem;
    }
    
    /* Chat input */
    .stChatInput > div {
        background-color: #0D2137 !important;
        border-color: rgba(255, 95, 158, 0.3) !important;
    }
    
    .stChatInput input {
        color: #F5F7FA !important;
    }
    
    /* Textos generales */
    p, li {
        color: #B8C5D6;
    }
    
    h1, h2, h3, h4 {
        color: #F5F7FA;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #F5F7FA !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="page-header">
    <h1 class="page-title">Consultar a CUIDAR IA</h1>
    <p class="page-subtitle">
        Asistente basado en evidencia científica y guías validadas para apoyar decisiones en prevención del suicidio
    </p>
</div>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_engine" not in st.session_state:
    with st.spinner("Preparando asistente..."):
        try:
            st.session_state.rag_engine = get_rag_engine()
        except Exception as e:
            st.error(f"Error al cargar el sistema: {str(e)}")
            st.stop()

# Sidebar con información y opciones
with st.sidebar:
    st.markdown("### Configuración")
    
    # Mostrar documentos locales cargados
    local_count = st.session_state.rag_engine.get_local_docs_count()
    if local_count > 0:
        st.markdown(f"""
        <div class="info-box">
            <strong>{local_count}</strong> fragmentos de documentos locales cargados
        </div>
        """, unsafe_allow_html=True)
        include_local = st.checkbox("Incluir documentos locales en búsqueda", value=True)
        if st.button("Limpiar documentos locales"):
            st.session_state.rag_engine.clear_local_documents()
            st.rerun()
    else:
        include_local = False
        st.markdown("*No hay documentos locales cargados*")
        if st.button("Subir documentos"):
            st.switch_page("pages/3_Informacion_Territorio.py")
    
    st.divider()
    
    st.markdown("### Consultas sugeridas")
    
    suggested_queries = [
        "¿Qué consideraciones éticas debo tener para manejar datos de predicción del suicidio?",
        "¿Cómo mejorar la calidad de los datos para prevención del suicidio?",
        "¿Qué protocolos de screening se recomiendan en atención primaria?",
        "¿Cuáles son las intervenciones más efectivas según la evidencia?"
    ]
    
    for query in suggested_queries:
        if st.button(query, key=f"suggest_{hash(query)}", use_container_width=True):
            st.session_state.pending_query = query
    
    st.divider()
    
    if st.button("Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Mostrar historial de mensajes
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-label user-label">Tú</div>
            <div class="message-content">{message["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Mensaje del asistente
        sources_html = ""
        if "sources" in message and message["sources"]:
            sources_html = '<div class="sources-container"><div class="sources-label">Fuentes consultadas:</div>'
            for source in message["sources"]:
                tag_class = "source-tag local-tag" if "local" in source.lower() else "source-tag"
                sources_html += f'<span class="{tag_class}">{source}</span>'
            sources_html += '</div>'
        
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <div class="message-label assistant-label">CUIDAR IA</div>
            <div class="message-content">{message["content"]}</div>
            {sources_html}
        </div>
        """, unsafe_allow_html=True)

# Procesar consulta sugerida si existe
if "pending_query" in st.session_state:
    query = st.session_state.pending_query
    del st.session_state.pending_query
    
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Generar respuesta
    with st.spinner("Buscando información relevante..."):
        result = st.session_state.rag_engine.generate_response(
            query, 
            include_local=include_local if local_count > 0 else False
        )
    
    # Agregar respuesta al historial
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["respuesta"],
        "sources": result.get("fuentes", [])
    })
    
    st.rerun()

# Input del usuario
user_input = st.chat_input("Escribe tu consulta sobre prevención del suicidio...")

if user_input:
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generar respuesta
    with st.spinner("Buscando información relevante..."):
        result = st.session_state.rag_engine.generate_response(
            user_input,
            include_local=include_local if local_count > 0 else False
        )
    
    # Agregar respuesta al historial
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["respuesta"],
        "sources": result.get("fuentes", [])
    })
    
    st.rerun()

# Información adicional al final si no hay mensajes
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        <div class="welcome-title">Bienvenido al asistente CUIDAR IA</div>
        <p class="welcome-text">
            Puedes hacer preguntas sobre prevención del suicidio, gobernanza de datos y políticas públicas 
            de salud mental. El asistente está entrenado con evidencia científica y guías validadas.
        </p>
        <ul class="welcome-list">
            <li>Consideraciones éticas para el manejo de datos</li>
            <li>Calidad e interoperabilidad de sistemas de información</li>
            <li>Protocolos de screening y detección</li>
            <li>Intervenciones efectivas en prevención del suicidio</li>
            <li>Gobernanza de datos en salud mental</li>
        </ul>
        <p class="welcome-text" style="margin-top: 1rem;">
            Escribe tu consulta en el campo de texto inferior o selecciona una de las sugerencias en el menú lateral.
        </p>
    </div>
    """, unsafe_allow_html=True)
