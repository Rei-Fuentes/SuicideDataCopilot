"""
CUIDAR IA - Policy Copilot para Prevención del Suicidio
Página principal con hero fullscreen mejorado y navegación por tarjetas
"""

import streamlit as st
import sys
import os

# Add project root to sys.path to allow importing 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.styles import load_css
from app.utils.components import render_hero, render_card

# Configuración de la página
st.set_page_config(
    page_title="CUIDAR IA",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cargar estilos globales
load_css()

# Renderizar Hero Section
render_hero()

# Sección de tarjetas
st.markdown('<div class="cards-section">', unsafe_allow_html=True)

# CTA condicional para ver resultados si existen
if "cuidar_results" in st.session_state and st.session_state.cuidar_results:
    st.info("✅ Ya completaste tu diagnóstico. Ve a la página de Resultados para ver el análisis completo.")
    if st.button("Ver Resultados del CUIDAR Index", type="primary", use_container_width=True):
        st.switch_page("pages/2_Resultados_CUIDAR_Index.py")

st.markdown('<h2 style="text-align: center; margin-bottom: 2rem;">¿Cómo quieres trabajar hoy?</h2>', unsafe_allow_html=True)

# Crear las CUATRO tarjetas
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_card(
        icon="◈",
        title="Diagnóstico CUIDAR Index",
        description="Evalúa la madurez de tu institución para gestionar, integrar y usar datos en prevención del suicidio.",
        button_text="Iniciar Diagnóstico",
        key="btn_index",
        on_click_page="pages/1_Diagnostico_CUIDAR_Index.py"
    )

with col2:
    render_card(
        icon="◉",
        title="Consultar a CUIDAR IA",
        description="Asistente basado en evidencia científica y guías validadas para apoyar decisiones y diseñar protocolos.",
        button_text="Consultar Asistente",
        key="btn_chat",
        on_click_page="pages/3_Consultar_CUIDAR_IA.py"
    )

with col3:
    render_card(
        icon="◎",
        title="Información de tu Territorio",
        description="Sube documentos locales para obtener análisis contextualizados adaptados a tu realidad institucional.",
        button_text="Analizar Documentos",
        key="btn_docs",
        on_click_page="pages/4_Informacion_Territorio.py"
    )

with col4:
    render_card(
        icon="📊",
        title="Evaluador de Bases de Datos",
        description="Análisis automatizado de calidad, completitud, privacidad y viabilidad de tus datos para prevención.",
        button_text="Evaluar Datos",
        key="btn_evaluador",
        on_click_page="pages/5_Evaluador_Bases_Datos.py"
    )

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 3rem; opacity: 0.6; font-size: 0.85rem;">
    <p>CUIDAR IA — Plataforma GovTech para la Prevención del Suicidio</p>
</div>
""", unsafe_allow_html=True)
