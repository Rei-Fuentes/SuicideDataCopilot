"""
CUIDAR IA - Resultados del CUIDAR Index
Visualización y análisis de resultados del diagnóstico institucional
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.utils.styles import load_css
from app.utils.components import render_page_header
from app.utils.pdf_generator import generate_diagnostic_pdf

# Cargar variables de entorno
load_dotenv()

# Configuración de página
st.set_page_config(
    page_title="Resultados CUIDAR Index",
    page_icon="📊",
    layout="wide"
)

# Cargar estilos globales
load_css()

# CSS específico para esta página
st.markdown("""
    <style>
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .score-inicial {
        background-color: rgba(231, 76, 60, 0.2);
        color: #e74c3c;
        border: 1px solid #e74c3c;
    }
    .score-basico {
        background-color: rgba(241, 196, 15, 0.2);
        color: #f1c40f;
        border: 1px solid #f1c40f;
    }
    .score-intermedio {
        background-color: rgba(52, 152, 219, 0.2);
        color: #3498db;
        border: 1px solid #3498db;
    }
    .score-avanzado {
        background-color: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
        border: 1px solid #2ecc71;
    }
    .ia-analysis {
        background: rgba(100, 255, 218, 0.05);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #64FFDA;
        margin: 1rem 0;
        color: #E6F1FF;
    }
    </style>
""", unsafe_allow_html=True)

# Header
render_page_header(
    title="Resultados del CUIDAR Index",
    subtitle="Diagnóstico de Capacidad Institucional en Gestión de Datos"
)

# Verificar si hay resultados
if 'cuidar_results' not in st.session_state or not st.session_state.cuidar_results:
    st.warning("⚠️ No hay resultados disponibles. Por favor, completa primero el diagnóstico.")
    if st.button("Ir al Diagnóstico"):
        st.switch_page("pages/1_Diagnostico_CUIDAR_Index.py")
    st.stop()

# Obtener resultados
results = st.session_state.cuidar_results
puntaje_total = results.get('total_score', 0)
nivel_madurez = results.get('maturity_level', 'inicial')
scores_raw = results.get('scores', {})
fecha = results.get('timestamp', datetime.now().isoformat())

# Procesar puntajes por dimensión
puntajes_dimension = {}
for dimension, datos in scores_raw.items():
    if isinstance(datos, dict):
        puntajes_dimension[dimension] = datos.get('porcentaje', 0)
    else:
        puntajes_dimension[dimension] = datos

# Definir niveles de madurez
NIVELES_MADUREZ = {
    "inicial": {
        "rango": (0, 25),
        "color": "#e74c3c",
        "descripcion": "Sin capacidad real de gestión de datos",
        "clase": "score-inicial"
    },
    "basico": {
        "rango": (26, 50),
        "color": "#f1c40f",
        "descripcion": "Datos fragmentados y parciales",
        "clase": "score-basico"
    },
    "intermedio": {
        "rango": (51, 75),
        "color": "#3498db",
        "descripcion": "Funcional pero con brechas clave",
        "clase": "score-intermedio"
    },
    "avanzado": {
        "rango": (76, 100),
        "color": "#2ecc71",
        "descripcion": "Datos usados sistemáticamente para prevención",
        "clase": "score-avanzado"
    }
}

nivel_info = NIVELES_MADUREZ.get(nivel_madurez.lower(), NIVELES_MADUREZ['inicial'])

# ==================== SECCIÓN 1: NIVEL DE MADUREZ ====================
col_gauge, col_info = st.columns([1, 1])

with col_gauge:
    # Gauge Premium
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=puntaje_total,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>{nivel_madurez.upper()}</b>", 'font': {'size': 24, 'color': nivel_info['color']}},
        number={'suffix': "/100", 'font': {'size': 40, 'color': "#E6F1FF"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#8892B0"},
            'bar': {'color': nivel_info['color'], 'thickness': 0.8},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "#112240",
            'steps': [
                {'range': [0, 25], 'color': "rgba(231, 76, 60, 0.1)"},
                {'range': [25, 50], 'color': "rgba(241, 196, 15, 0.1)"},
                {'range': [50, 75], 'color': "rgba(52, 152, 219, 0.1)"},
                {'range': [75, 100], 'color': "rgba(46, 204, 113, 0.1)"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': puntaje_total
            }
        }
    ))

    fig_gauge.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': "Inter, sans-serif"}
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_info:
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: {nivel_info['color']} !important;">{nivel_madurez.upper()}</h3>
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">{nivel_info['descripcion']}</p>
        <p style="color: #8892B0;">Este nivel indica la madurez actual de la institución en cuanto a la gestión de datos para la prevención del suicidio.</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== SECCIÓN 2: ANÁLISIS CON IA ====================
st.markdown("### 🤖 Evaluación Personalizada con IA")

if st.button("🔮 Generar Análisis con IA", type="primary"):
    with st.spinner("Analizando resultados con inteligencia artificial..."):
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error("⚠️ API Key de OpenAI no configurada. Agrega OPENAI_API_KEY al archivo .env")
            else:
                client = OpenAI(api_key=api_key)
                contexto = f"""
                Eres un experto en prevención del suicidio y gestión de datos en salud pública.
                Analiza los siguientes resultados del CUIDAR Index para una institución:
                PUNTAJE TOTAL: {puntaje_total:.1f}/100
                NIVEL DE MADUREZ: {nivel_madurez.upper()}
                PUNTAJES POR DIMENSIÓN:
                """
                for dim, punt in puntajes_dimension.items():
                    contexto += f"- {dim}: {punt:.1f}/100\n"
                
                contexto += """
                Por favor proporciona:
                1. Un análisis general de la situación institucional (2-3 párrafos)
                2. Las 3 fortalezas principales identificadas
                3. Las 3 brechas más críticas que requieren atención urgente
                4. Recomendaciones específicas y accionables para mejorar
                Sé empático, constructivo y enfocado en soluciones prácticas.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Eres un experto en prevención del suicidio."},
                        {"role": "user", "content": contexto}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                analisis_ia = response.choices[0].message.content
                
                st.markdown(f"""
                    <div class="ia-analysis">
                        <h4>💡 Análisis Generado por IA</h4>
                        {analisis_ia.replace('\n', '<br>')}
                    </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Error al generar análisis: {str(e)}")

# ==================== SECCIÓN 3: PERFIL POR DIMENSIÓN ====================
st.markdown("### 🕸️ Perfil de Capacidades")

col_radar, col_bar = st.columns([1, 1])

with col_radar:
    # Radar Chart Premium
    dimensiones_nombres = list(puntajes_dimension.keys())
    puntajes_valores = list(puntajes_dimension.values())

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=puntajes_valores,
        theta=dimensiones_nombres,
        fill='toself',
        name='Puntaje',
        line=dict(color='#64FFDA', width=2),
        fillcolor='rgba(100, 255, 218, 0.2)'
    ))

    fig_radar.update_layout(
        polar=dict(
            bgcolor='rgba(17, 34, 64, 0.5)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10, color='#8892B0'),
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#E6F1FF'),
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.1)'
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=40, r=40, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_bar:
    # Bar Chart Premium
    df_scores = pd.DataFrame({
        'Dimensión': dimensiones_nombres,
        'Puntaje': puntajes_valores
    }).sort_values('Puntaje', ascending=True)

    fig_bar = px.bar(
        df_scores,
        x='Puntaje',
        y='Dimensión',
        orientation='h',
        text='Puntaje',
        color='Puntaje',
        color_continuous_scale=['#e74c3c', '#f1c40f', '#2ecc71']
    )

    fig_bar.update_traces(
        texttemplate='%{text:.1f}',
        textposition='outside',
        marker_line_width=0,
        opacity=0.8
    )

    fig_bar.update_layout(
        xaxis=dict(showgrid=False, showticklabels=False, range=[0, 110]),
        yaxis=dict(showgrid=False, tickfont=dict(color='#E6F1FF')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        coloraxis_showscale=False,
        height=400,
        margin=dict(l=0, r=0, t=20, b=20),
        font=dict(family="Inter, sans-serif")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ==================== SECCIÓN 4: DESCARGAS ====================
st.markdown("### 📥 Exportar Resultados")

col_pdf, col_json = st.columns(2)

with col_pdf:
    st.markdown("""
    <div class="glass-card">
        <h4>📄 Informe PDF</h4>
        <p>Descarga un informe completo con gráficos y recomendaciones.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generar PDF en memoria
    if st.button("Generar PDF"):
        try:
            pdf = generate_diagnostic_pdf(results)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            
            st.download_button(
                label="⬇️ Descargar PDF",
                data=pdf_bytes,
                file_name=f"reporte_cuidar_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error al generar PDF: {str(e)}")

with col_json:
    st.markdown("""
    <div class="glass-card">
        <h4>💾 Datos JSON</h4>
        <p>Descarga los datos crudos para integración con otros sistemas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    json_str = json.dumps(results, indent=2, ensure_ascii=False)
    st.download_button(
        label="⬇️ Descargar JSON",
        data=json_str,
        file_name=f"cuidar_index_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True
    )

# ==================== FOOTER ====================
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 Nuevo Diagnóstico", use_container_width=True):
        if 'cuidar_results' in st.session_state:
            del st.session_state.cuidar_results
        st.switch_page("pages/1_Diagnostico_CUIDAR_Index.py")
with col2:
    if st.button("🏠 Volver al Inicio", use_container_width=True):
        st.switch_page("app/main.py")
