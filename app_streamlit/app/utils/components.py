"""
CUIDAR IA - UI Components
Reusable UI components for the application.
"""

import streamlit as st
from app.utils.styles import COLORS

def render_hero():
    """Renders the main Hero section."""
    st.markdown("""
    <style>
        .hero-container {
            padding: 4rem 2rem;
            text-align: center;
            background: radial-gradient(circle at top right, rgba(255, 95, 158, 0.1) 0%, transparent 60%);
            margin-bottom: 3rem;
            border-bottom: 1px solid rgba(255, 95, 158, 0.1);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, #F5F7FA 0%, #B8C5D6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
            text-align: center;
            width: 100%;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            color: #FF5F9E;
            font-weight: 500;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-align: center;
            width: 100%;
        }
        .hero-desc {
            font-size: 1.1rem;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.6;
            color: #B8C5D6;
            text-align: center;
        }
    </style>
    <div class="hero-container">
        <div class="hero-subtitle">Policy Copilot</div>
        <h1 class="hero-title">CUIDAR IA</h1>
        <p class="hero-desc">
            Plataforma de inteligencia artificial para la prevención del suicidio basada en datos y evidencia científica.
            Evalúa, analiza y actúa.
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_page_header(title, subtitle):
    """Renders a standard page header."""
    st.markdown(f"""
    <div class="page-header">
        <h1 style="margin:0; font-size: 2.2rem;">{title}</h1>
        <p style="margin-top:0.5rem; font-size: 1.1rem; opacity: 0.8;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def render_card(icon, title, description, button_text, key, on_click_page):
    """
    Renders a navigation card.
    
    Args:
        icon (str): Emoji or icon character.
        title (str): Card title.
        description (str): Card description.
        button_text (str): Text for the button.
        key (str): Unique key for the button.
        on_click_page (str): Page path to navigate to.
    """
    st.markdown(f"""
    <div class="card">
        <div style="font-size: 2.5rem; margin-bottom: 1rem; color: {COLORS['secondary']};">{icon}</div>
        <h3 style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">{title}</h3>
        <p style="font-size: 0.9rem; line-height: 1.5; margin-bottom: 1.5rem; min-height: 60px;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Button is placed outside the HTML div because Streamlit buttons can't be embedded in HTML
    # We use a container to visually group them, but the layout relies on the column structure
    if st.button(button_text, key=key, use_container_width=True):
        st.switch_page(on_click_page)

def render_metric(label, value, delta=None, color="primary"):
    """Renders a styled metric."""
    delta_html = ""
    if delta:
        color_hex = COLORS['success'] if delta > 0 else COLORS['error']
        sign = "+" if delta > 0 else ""
        delta_html = f'<div style="color: {color_hex}; font-size: 0.8rem; margin-top: 0.2rem;">{sign}{delta}%</div>'
        
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)
