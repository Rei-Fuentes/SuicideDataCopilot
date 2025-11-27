"""
CUIDAR IA - Centralized Styles
Defines the color palette and global CSS for the application.
"""

import streamlit as st

# Color Palette
COLORS = {
    "background": "#0A1A2F",
    "background_secondary": "#112240",
    "primary": "#64FFDA",  # Teal/Cyan neon for a more tech feel
    "secondary": "#FF5F9E", # Pink accent kept as requested
    "text": "#E6F1FF",
    "text_muted": "#8892B0",
    "success": "#2ecc71",
    "warning": "#f1c40f",
    "error": "#e74c3c",
    "card_bg": "rgba(17, 34, 64, 0.7)", # Glassmorphism base
    "border_soft": "rgba(100, 255, 218, 0.2)" # Added missing key
}

def load_css():
    """Injects global CSS into the Streamlit app."""
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {{
            --bg-color: {COLORS['background']};
            --bg-secondary: {COLORS['background_secondary']};
            --primary-color: {COLORS['primary']};
            --secondary-color: {COLORS['secondary']};
            --text-color: {COLORS['text']};
            --text-muted: {COLORS['text_muted']};
        }}
        
        .stApp {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
        }}
        
        /* Hide Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        
        /* Glassmorphism Card */
        .glass-card {{
            background: rgba(17, 34, 64, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .glass-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            border-color: rgba(100, 255, 218, 0.3);
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: var(--text-color) !important;
            font-weight: 600;
        }}
        
        h1 {{
            background: linear-gradient(90deg, #E6F1FF 0%, #64FFDA 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        p, li, label, .stMarkdown {{
            color: var(--text-muted) !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(90deg, var(--secondary-color) 0%, #FF8FAE 100%);
            color: #0A1A2F;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            box-shadow: 0 0 15px rgba(255, 95, 158, 0.5);
            transform: scale(1.02);
        }}
        
        .stButton > button:active {{
            color: #0A1A2F;
        }}
        
        /* Secondary Button (Outline) */
        .stButton button[kind="secondary"] {{
            background: transparent;
            border: 1px solid var(--primary-color);
            color: var(--primary-color);
        }}
        
        /* Inputs */
        .stTextInput > div > div > input {{
            background-color: var(--bg-secondary);
            color: var(--text-color);
            border: 1px solid rgba(100, 255, 218, 0.2);
            border-radius: 8px;
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: #0D2137;
            color: var(--text-color) !important;
            border-radius: 8px;
        }}
        
        /* Progress Bar */
        .stProgress > div > div > div > div {{
            background-color: var(--secondary-color);
        }}
        
        /* Custom Classes */
        .card {{
            background: {COLORS['card_bg']};
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid {COLORS.get('border_soft', 'rgba(255, 255, 255, 0.1)')};
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            border-color: rgba(255, 95, 158, 0.3);
        }}
        
        .page-header {{
            background: linear-gradient(135deg, #0D2137 0%, #0A1A2F 100%);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            border: 1px solid {COLORS.get('border_soft', 'rgba(255, 255, 255, 0.1)')};
        }}
        
        .metric-container {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-color);
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            color: var(--text-muted);
        }}
    </style>
    """, unsafe_allow_html=True)
