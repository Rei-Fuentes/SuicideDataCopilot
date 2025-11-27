"""
CUIDAR IA - Diagnóstico CUIDAR Index
Evaluación de madurez institucional con escala Likert unificada y validación
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.utils.styles import load_css
from app.utils.components import render_page_header
from app.core.constants import DIMENSIONES, ESCALA, FEEDBACK_TEMPLATES

# Configuración de la página
st.set_page_config(
    page_title="CUIDAR Index - CUIDAR IA",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos globales
load_css()

# CSS específico para esta página (que no está en global)
st.markdown("""
<style>
    /* Tarjetas de dimensión */
    .dimension-card {
        background: linear-gradient(145deg, #0D2137 0%, #0A1A2F 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 95, 158, 0.1);
        transition: all 0.3s ease;
    }
    
    .dimension-card:hover {
        border-color: rgba(255, 95, 158, 0.3);
    }
    
    .item-incomplete {
        border-left: 3px solid #FF5F9E;
        padding-left: 1rem;
        background: rgba(255, 95, 158, 0.05);
        border-radius: 0 8px 8px 0;
    }
    
    /* Escala leyenda */
    .scale-legend {
        background: #0D2137;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .scale-item {
        display: flex;
        align-items: center;
        margin-bottom: 0.3rem;
        font-size: 0.85rem;
    }
    
    .scale-number {
        background: #FF5F9E;
        color: #0A1A2F;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.75rem;
        margin-right: 0.5rem;
    }
    
    .scale-text {
        color: #B8C5D6;
    }
    
    /* Alerta de validación */
    .validation-alert {
        background: rgba(255, 95, 158, 0.15);
        border: 1px solid rgba(255, 95, 158, 0.4);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        color: #F5F7FA;
    }
    
    .validation-alert strong {
        color: #FF5F9E;
    }
</style>
""", unsafe_allow_html=True)

def calcular_resultados(respuestas):
    """Calcula puntajes por dimensión y total"""
    resultados = {}
    total_puntos = 0
    total_items = 0
    
    for dimension, items in respuestas.items():
        if items:
            puntaje_dim = sum(items.values())
            max_dim = len(items) * 5
            porcentaje = (puntaje_dim / max_dim) * 100
            promedio = puntaje_dim / len(items)
            resultados[dimension] = {
                "puntaje": puntaje_dim,
                "maximo": max_dim,
                "porcentaje": porcentaje,
                "promedio": promedio,
                "items": items
            }
            total_puntos += puntaje_dim
            total_items += len(items)
    
    # Puntaje total normalizado a 100
    if total_items > 0:
        puntaje_total = (total_puntos / (total_items * 5)) * 100
    else:
        puntaje_total = 0
    
    return resultados, puntaje_total

def obtener_nivel_madurez(puntaje):
    """Determina el nivel de madurez según el puntaje"""
    if puntaje <= 25:
        return "Inicial", "Sin capacidad real establecida"
    elif puntaje <= 50:
        return "Básico", "Sistema fragmentado con datos parciales"
    elif puntaje <= 75:
        return "Intermedio", "Funcional pero con brechas claves"
    else:
        return "Avanzado", "Datos usados sistemáticamente para prevención"

def generar_feedback_dimension(dimension, promedio):
    """Genera retroalimentación basada en el promedio de la dimensión"""
    nivel = round(promedio)
    if nivel < 1:
        nivel = 1
    elif nivel > 5:
        nivel = 5
    return FEEDBACK_TEMPLATES[nivel]

def validar_respuestas(respuestas):
    """Valida que todas las preguntas estén respondidas"""
    faltantes = []
    for dimension, data in DIMENSIONES.items():
        for i, item in enumerate(data["items"]):
            if dimension not in respuestas or i not in respuestas[dimension]:
                faltantes.append(f"{dimension} - Pregunta {i+1}")
    return faltantes

# Header de la página
render_page_header(
    title="Diagnóstico CUIDAR Index",
    subtitle="Evalúa la capacidad de tu institución para gestionar, integrar y usar datos en prevención del suicidio"
)

# Inicializar estado de sesión
if "respuestas" not in st.session_state:
    st.session_state.respuestas = {dim: {} for dim in DIMENSIONES.keys()}
if "show_validation_error" not in st.session_state:
    st.session_state.show_validation_error = False
if "faltantes" not in st.session_state:
    st.session_state.faltantes = []

# Sidebar con información
with st.sidebar:
    st.markdown("### Escala de Evaluación")
    
    st.markdown('<div class="scale-legend">', unsafe_allow_html=True)
    for valor, texto in ESCALA.items():
        st.markdown(f"""
        <div class="scale-item">
            <span class="scale-number">{valor}</span>
            <span class="scale-text">{texto}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Progreso
    total_items = sum(len(d["items"]) for d in DIMENSIONES.values())
    items_respondidos = sum(len(r) for r in st.session_state.respuestas.values())
    progreso = items_respondidos / total_items if total_items > 0 else 0
    
    st.markdown("### Progreso")
    st.progress(progreso)
    st.markdown(f"**{items_respondidos}** de **{total_items}** ítems completados")
    
    if items_respondidos < total_items:
        st.markdown(f"*Faltan {total_items - items_respondidos} respuestas*")

# Contenido principal - Cuestionario
st.markdown("### Cuestionario de Evaluación")
st.markdown("Responde cada ítem según la realidad actual de tu institución.")

# Mostrar alerta de validación si hay errores
if st.session_state.show_validation_error and st.session_state.faltantes:
    st.markdown(f"""
    <div class="validation-alert">
        <strong>Faltan {len(st.session_state.faltantes)} respuestas por completar</strong><br>
        Por favor, responde todas las preguntas antes de enviar el diagnóstico.
    </div>
    """, unsafe_allow_html=True)

# Mostrar cuestionario por dimensiones
for dimension, data in DIMENSIONES.items():
    with st.expander(f"{dimension}", expanded=False):
        st.markdown(f"*{data['descripcion']}*")
        st.divider()
        
        for i, item in enumerate(data["items"]):
            # Verificar si este ítem está incompleto
            is_incomplete = (st.session_state.show_validation_error and 
                           (dimension not in st.session_state.respuestas or 
                            i not in st.session_state.respuestas[dimension]))
            
            # Aplicar estilo de incompleto si corresponde
            if is_incomplete:
                st.markdown(f'<div class="item-incomplete">', unsafe_allow_html=True)
            
            st.markdown(f"**{i+1}.** {item}")
            
            # Obtener valor actual si existe
            current_value = st.session_state.respuestas[dimension].get(i, None)
            
            # Radio button para la respuesta
            respuesta = st.radio(
                f"Selecciona tu respuesta",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: f"{x} - {ESCALA[x]}",
                key=f"{dimension}_{i}",
                index=current_value - 1 if current_value else None,
                horizontal=True,
                label_visibility="collapsed"
            )
            
            if respuesta:
                st.session_state.respuestas[dimension][i] = respuesta
            
            if is_incomplete:
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.divider()

# Sección de envío
st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("Enviar diagnóstico", type="primary", use_container_width=True):
        # Validar respuestas
        faltantes = validar_respuestas(st.session_state.respuestas)
        
        if faltantes:
            st.session_state.show_validation_error = True
            st.session_state.faltantes = faltantes
            st.rerun()
        else:
            # Calcular resultados
            resultados, puntaje_total = calcular_resultados(st.session_state.respuestas)
            nivel, descripcion = obtener_nivel_madurez(puntaje_total)
            
            # Generar retroalimentación por dimensión
            feedback = {}
            for dim, data in resultados.items():
                feedback[dim] = generar_feedback_dimension(dim, data["promedio"])
            
            # Ordenar dimensiones
            dims_ordenadas = sorted(resultados.items(), key=lambda x: x[1]["porcentaje"])
            
            # Generar resumen integrado
            fortalezas = [dim for dim, data in dims_ordenadas[-3:] if data["porcentaje"] >= 60]
            brechas = [dim for dim, data in dims_ordenadas[:3] if data["porcentaje"] < 60]
            
            resumen = f"La institución presenta un nivel de madurez **{nivel}** ({puntaje_total:.0f}/100). "
            if fortalezas:
                resumen += f"Las principales fortalezas se encuentran en: {', '.join(fortalezas)}. "
            if brechas:
                resumen += f"Las áreas prioritarias de mejora son: {', '.join(brechas)}."
            
            # Guardar en session_state
            st.session_state.cuidar_results = {
                "answers": st.session_state.respuestas,
                "scores": resultados,
                "total_score": puntaje_total,
                "maturity_level": nivel,
                "maturity_description": descripcion,
                "feedback": feedback,
                "summary": resumen,
                "timestamp": datetime.now().isoformat()
            }
            
            # Limpiar errores de validación
            st.session_state.show_validation_error = False
            st.session_state.faltantes = []
            
            # Redirigir a resultados
            st.switch_page("pages/4_Resultados_CUIDAR_Index.py")
