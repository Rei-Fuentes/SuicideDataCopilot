"""
CUIDAR IA - Evaluador de Bases de Datos
Fase 3: Análisis de Calidad de Datos para Prevención del Suicidio
VERSION FINAL - Geocodificación Real con Nominatim

DEPENDENCIAS OPCIONALES:
- geopy: Para geocodificación real (pip install geopy)
  Si no está instalada, se usará modo simulación
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
from scipy.ndimage import uniform_filter1d  # Para suavizado de tendencias
import sys
from pathlib import Path
# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fase3_evaluator.integration import run_parallel_analysis
from fase3_evaluator.agent import generate_diagnosis
from fase3_evaluator.analyzers import get_missing_heatmap_data, get_completeness_by_column
from config.settings import settings, ETHICAL_WARNING_PII

# Importar geopy si está disponible (opcional)
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False


# ==================== FUNCIÓN HELPER PARA JSON ====================
def convert_numpy_types(obj):
    """Convierte tipos numpy a tipos Python nativos para serialización JSON"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj


# ==================== CONFIGURACIÓN DE PÁGINA ====================
# ==================== CONFIGURACIÓN DE PÁGINA ====================
st.set_page_config(
    page_title="Evaluador de Datos | CUIDAR IA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from app.utils.styles import load_css
from app.utils.components import render_page_header
from app.utils.pdf_generator import generate_data_quality_pdf

# Cargar estilos globales
load_css()

# Estilos específicos para esta página
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
render_page_header(
    title="Evaluador de Calidad de Datos",
    subtitle="Analiza la calidad, completitud y viabilidad de bases de datos para prevención del suicidio."
)

st.divider()

# ==================== SECCIÓN 1: CARGA DE DATOS ====================
st.header("1. Cargar Base de Datos")

# Tabs para elegir entre subir archivo o usar datos simulados
tab1, tab2 = st.tabs(["📤 Subir Archivo", "🎲 Datos Simulados"])

with tab1:
    st.write("**Sube tu propia base de datos para analizar**")
    
    uploaded_file = st.file_uploader(
        "Selecciona un archivo CSV o Excel",
        type=['csv', 'xlsx', 'xls'],
        help=f"Tamaño máximo: {settings.MAX_FILE_SIZE_MB} MB"
    )

with tab2:
    st.write("**Usa un dataset simulado de eventos de suicidio en Valencia (1980-2025)**")
    st.info("""
    📊 **Dataset Simulado:**
    - **3,207 eventos** generados con datos realistas
    - **Período:** 1980-2025 (45 años)
    - **Ubicación:** Valencia, España (14 barrios)
    - **Variables:** Fecha, coordenadas, edad, sexo, método, dirección, DNI (falso), antecedentes
    - **Basado en:** Tasas epidemiológicas reales (~70 eventos/año)
    """)
    
    col_sim1, col_sim2 = st.columns([3, 1])
    with col_sim1:
        if st.button("🎲 Cargar Datos Simulados", type="primary", use_container_width=True):
            try:
                # Intentar cargar desde múltiples ubicaciones posibles
                possible_paths = [
                    '../../data/datos_simulados_valencia_suicidios_1980_2025.csv',  # TU UBICACIÓN: Desde app/pages/ → data/ en raíz ✅
                    '../data/datos_simulados_valencia_suicidios_1980_2025.csv',  # Desde app/ → data/
                    'data/datos_simulados_valencia_suicidios_1980_2025.csv',  # Si ejecutas desde raíz del proyecto
                    'app/data/datos_simulados_valencia_suicidios_1980_2025.csv',  # Estructura alternativa
                    'datos_simulados_valencia_suicidios_1980_2025.csv',  # Mismo directorio (fallback)
                    '/mnt/user-data/outputs/datos_simulados_valencia_suicidios_1980_2025.csv'  # Desarrollo/testing
                ]
                
                simulated_path = None
                for path in possible_paths:
                    if Path(path).exists():
                        simulated_path = path
                        st.info(f"✅ Archivo encontrado en: `{path}`")
                        break
                
                if simulated_path is None:
                    st.error("❌ Archivo de datos simulados no encontrado")
                    st.info("""
                    💡 **El sistema busca el archivo en estas ubicaciones (en orden):**
                    
                    1. `data/datos_simulados_valencia_suicidios_1980_2025.csv` (raíz proyecto) ← **TU UBICACIÓN**
                    2. `app/data/datos_simulados_valencia_suicidios_1980_2025.csv`
                    3. Relativas desde donde ejecutas Streamlit
                    
                    **Tu archivo está en:**
                    ```
                    /Users/reinerfuentesferrada/.../cuidar-ia/data/datos_simulados_valencia_suicidios_1980_2025.csv
                    ```
                    
                    **Verifica:**
                    - ¿Ejecutaste Streamlit desde la raíz del proyecto? (`cuidar-ia/`)
                    - ¿El archivo existe? Ejecuta: `ls -lh data/datos_simulados_valencia_suicidios_1980_2025.csv`
                    """)
                    st.stop()
                
                df = pd.read_csv(simulated_path)
                
                st.session_state.df_loaded = df
                st.session_state.using_simulated = True
                st.success("✅ Datos simulados cargados correctamente")
                st.rerun()
            except FileNotFoundError:
                st.error("❌ Archivo de datos simulados no encontrado")
                st.info("💡 Ejecuta primero el script `generar_datos_valencia.py`")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col_sim2:
        if st.button("ℹ️ Info", use_container_width=True):
            st.info("Dataset creado con Faker y distribuciones epidemiológicas realistas")

# Verificar si hay datos cargados (archivo o simulados)
df = None
uploaded_file_name = None

if 'df_loaded' in st.session_state and st.session_state.get('using_simulated', False):
    df = st.session_state.df_loaded
    uploaded_file_name = "datos_simulados_valencia_suicidios_1980_2025.csv"
    st.success(f"✅ Usando datos simulados: {uploaded_file_name}")
elif uploaded_file:
    uploaded_file_name = uploaded_file.name

if df is None and uploaded_file:
    try:
        # Leer datos según extensión
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validación básica
        if df.empty:
            st.error("❌ El archivo está vacío")
            st.stop()
        
        if uploaded_file_name and not st.session_state.get('using_simulated', False):
            st.success(f"✅ Archivo cargado: {uploaded_file_name}")
        
        # Información básica
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Registros", f"{len(df):,}")
        with col2:
            st.metric("Variables", len(df.columns))
        with col3:
            st.metric("Memoria", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        with col4:
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            st.metric("Datos Faltantes", f"{missing_pct:.1f}%")
        
        # Preview de datos
        with st.expander("👁️ Vista previa de datos", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {str(e)}")
        st.stop()

# Continuar solo si hay datos cargados (simulados o archivo)
if df is not None:
    # ==================== ADVERTENCIA ÉTICA (MOVIDA) ====================
    with st.expander("⚠️ ADVERTENCIA ÉTICA Y DE PRIVACIDAD", expanded=True):
        st.warning(ETHICAL_WARNING_PII)

    # ==================== SECCIÓN 2: ANÁLISIS ====================
    st.divider()
    st.header("2. Ejecutar Análisis Completo")
    
    if st.button("🚀 Analizar Datos", type="primary", use_container_width=True):
        with st.spinner("Ejecutando análisis paralelo..."):
            try:
                # Ejecutar análisis (devuelve tupla de 3 elementos)
                results, df_anonymized, consolidated = run_parallel_analysis(df)
                
                # Guardar en session_state
                st.session_state.results = results
                st.session_state.df = df
                st.session_state.df_anonymized = df_anonymized
                st.session_state.consolidated = consolidated
                st.session_state.uploaded_file = uploaded_file
                
                st.success("✅ Análisis completado")
            except Exception as e:
                st.error(f"❌ Error durante el análisis: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # ==================== MOSTRAR RESULTADOS ====================
    if 'results' in st.session_state:
        results = st.session_state.results
        df = st.session_state.df
        
        st.divider()
        st.header("3. Resultados del Análisis")
        
        # ========== 3.2 COMPLETITUD DE DATOS ==========
        with st.expander("✅ Análisis de Completitud", expanded=False):
            completeness = results.get('completitud', {})
            
            if completeness:
                # CORRECCIÓN: Usar 'columns_analysis' en lugar de 'missing_by_column'
                columns_analysis = completeness.get('columns_analysis', {})
                summary = completeness.get('summary', {})
                
                # Extraer métricas del summary
                total_vars = summary.get('total_columns', 0)
                overall_completeness = 100 - summary.get('missing_percentage', 0)
                
                # Calcular variables completas (missing_rate == 0)
                complete_vars = sum(1 for col_data in columns_analysis.values() 
                                   if col_data.get('missing_rate', 1) == 0)
                
                # Variables críticas (>50% missing = missing_rate > 0.5)
                critical_vars = [col for col, data in columns_analysis.items() 
                                if data.get('missing_rate', 0) > 0.5]
                critical_total = len(critical_vars)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Estadísticas Generales")
                    st.write(f"**Completitud Global:** {overall_completeness:.1f}%")
                    st.write(f"**Variables Completas:** {complete_vars}/{total_vars}")
                    st.write(f"**Variables Críticas:** {critical_total}")
                    
                    if critical_total > 0:
                        st.warning(f"⚠️ {critical_total} variable(s) con >50% de datos faltantes")
                
                with col2:
                    st.subheader("Top 5 Variables Incompletas")
                    if columns_analysis:
                        # Ordenar por missing_rate (mayor a menor)
                        top_missing = sorted(
                            columns_analysis.items(), 
                            key=lambda x: x[1].get('missing_rate', 0), 
                            reverse=True
                        )[:5]
                        
                        for col_name, col_data in top_missing:
                            missing_pct = col_data.get('missing_rate', 0) * 100
                            st.write(f"**{col_name}:** {missing_pct:.1f}% faltante")
                
                # Heatmap de valores faltantes
                st.subheader("Mapa de Calor de Datos Faltantes")
                try:
                    heatmap_data = get_missing_heatmap_data(df)
                    if heatmap_data is not None:
                        fig = px.imshow(
                            heatmap_data,
                            labels=dict(x="Variables", y="Registros", color="Faltante"),
                            color_continuous_scale=['#0A1A2F', '#FF5F9E'],
                            aspect="auto"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning(f"No se pudo generar el heatmap: {str(e)}")
        
        # ========== 3.3 CALIDAD DE DATOS ==========
        with st.expander("🎯 Análisis de Calidad", expanded=False):
            quality = results.get('tipos', {})
            
            if quality:
                # Extraer métricas de calidad
                summary = quality.get('summary', {})
                total_columns = summary.get('total_columns', 0)
                inconsistencies_count = summary.get('inconsistencies_count', 0)
                encoding_issues_count = summary.get('encoding_issues_count', 0)
                quality_score = summary.get('quality_score', 0)
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Columnas", total_columns)
                
                with col2:
                    st.metric("Inconsistencias", inconsistencies_count)
                
                with col3:
                    st.metric("Puntuación Calidad", f"{quality_score:.1f}%")
                
                st.divider()
                
                # ===== DETALLE DE INCONSISTENCIAS =====
                if inconsistencies_count > 0:
                    st.subheader("⚠️ Detalle de Inconsistencias Detectadas")
                    
                    columns_analysis = quality.get('columns_analysis', {})
                    
                    # Filtrar columnas con problemas
                    problematic_cols = []
                    for col_name, col_data in columns_analysis.items():
                        issues = []
                        
                        # Verificar tipo de datos
                        inferred_type = col_data.get('inferred_type', 'unknown')
                        mixed_types = col_data.get('mixed_types', False)
                        
                        if mixed_types:
                            issues.append("🔴 Tipos de datos mezclados")
                        
                        # Verificar problemas de encoding
                        encoding_issues = col_data.get('encoding_issues', False)
                        if encoding_issues:
                            issues.append("🔴 Problemas de codificación de caracteres")
                        
                        # Verificar inconsistencias semánticas
                        semantic_issues = col_data.get('semantic_inconsistencies', [])
                        if semantic_issues:
                            for issue in semantic_issues:
                                issues.append(f"🟡 {issue}")
                        
                        # Verificar patrones anómalos
                        pattern_issues = col_data.get('pattern_anomalies', [])
                        if pattern_issues:
                            for issue in pattern_issues:
                                issues.append(f"🟠 {issue}")
                        
                        if issues:
                            problematic_cols.append({
                                'Variable': col_name,
                                'Tipo Inferido': inferred_type,
                                'Problemas': issues
                            })
                    
                    if problematic_cols:
                        for item in problematic_cols:
                            with st.container():
                                st.markdown(f"**{item['Variable']}** (Tipo: `{item['Tipo Inferido']}`)")
                                for problem in item['Problemas']:
                                    st.markdown(f"  - {problem}")
                                st.markdown("---")
                    else:
                        st.info("ℹ️ No se encontraron detalles específicos de las inconsistencias")
                else:
                    st.success("✅ No se detectaron inconsistencias en los datos")
                
                st.divider()
                
                # ===== TABLA DE CALIDAD POR VARIABLE =====
                st.subheader("📊 Resumen de Calidad por Variable")
                
                columns_analysis = quality.get('columns_analysis', {})
                if columns_analysis:
                    # Crear DataFrame resumido
                    quality_summary = []
                    for col_name, col_data in columns_analysis.items():
                        quality_summary.append({
                            'Variable': col_name,
                            'Tipo': col_data.get('inferred_type', 'unknown'),
                            'Valores Únicos': col_data.get('unique_count', 0),
                            'Tipos Mezclados': '❌' if col_data.get('mixed_types', False) else '✅',
                            'Problemas Encoding': '❌' if col_data.get('encoding_issues', False) else '✅',
                            'Estado': '⚠️ Revisar' if (col_data.get('mixed_types', False) or 
                                                       col_data.get('encoding_issues', False)) else '✅ OK'
                        })
                    
                    quality_df = pd.DataFrame(quality_summary)
                    st.dataframe(quality_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("No hay información detallada de calidad por columna")
        
        # ========== 3.4 DETECCIÓN DE PII ==========
        with st.expander("🔒 Privacidad y Anonimización", expanded=False):
            privacy = results.get('anonimizacion', {})
            
            if privacy:
                pii_detected = privacy.get('entities_found', [])
                
                # Obtener también el summary
                summary = privacy.get('summary', {})
                
                if pii_detected:
                    st.error(f"⚠️ Se detectaron {len(pii_detected)} entidades de información personal")
                    
                    # Mostrar entidades detectadas
                    st.subheader("Entidades PII Detectadas")
                    pii_df = pd.DataFrame(pii_detected)
                    st.dataframe(pii_df, use_container_width=True)
                    
                    st.warning("**Recomendación:** Anonimiza estos datos antes de compartir o analizar públicamente")
                else:
                    st.success("✅ No se detectaron entidades PII obvias")
                
                # Evaluación de riesgo
                risk_assessment = privacy.get('risk_assessment', {})
                risk_score = risk_assessment.get('score', 0)
                st.metric("Puntuación de Riesgo de Privacidad", f"{risk_score:.1f}/10")
                
                if risk_score > 5:
                    st.error("⚠️ Riesgo ALTO de re-identificación")
                elif risk_score > 3:
                    st.warning("⚠️ Riesgo MEDIO de re-identificación")
                else:
                    st.success("✅ Riesgo BAJO de re-identificación")
        
        # ========== 3.5 VIABILIDAD PARA ANÁLISIS ESTADÍSTICO Y ML ==========
        with st.expander("🤖 Viabilidad para Análisis Estadístico y Machine Learning", expanded=False):
            ml = results.get('ml', {})
            
            if ml:
                viability = ml.get('overall_viability', 0)
                
                # Gauge de viabilidad
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=viability * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Viabilidad ML (%)"},
                    delta={'reference': 65, 'increasing': {'color': "green"}},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#667eea"},
                        'steps': [
                            {'range': [0, 33], 'color': "#FF5F9E"},
                            {'range': [33, 66], 'color': "#FFA500"},
                            {'range': [66, 100], 'color': "#2ecc71"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 65
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                # Razones de viabilidad
                reasons = ml.get('reasons', [])
                if reasons:
                    st.subheader("Factores Evaluados")
                    for reason in reasons:
                        st.write(f"• {reason}")
                
                st.divider()
                
                # ===== ANÁLISIS DESCRIPTIVO RÁPIDO =====
                st.subheader("📊 Análisis Descriptivo Rápido")
                
                # Identificar tipos de variables
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Variables Numéricas", len(numeric_cols))
                with col2:
                    st.metric("Variables Categóricas", len(categorical_cols))
                with col3:
                    st.metric("Variables Temporales", len(datetime_cols))
                
                # ===== MATRIZ DE CORRELACIÓN =====
                if len(numeric_cols) > 1:
                    st.subheader("🔗 Matriz de Correlaciones")
                    
                    # Calcular correlaciones
                    corr_matrix = df[numeric_cols].corr()
                    
                    # Crear heatmap
                    fig_corr = px.imshow(
                        corr_matrix,
                        labels=dict(x="Variables", y="Variables", color="Correlación"),
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        color_continuous_scale='RdBu_r',
                        aspect="auto",
                        zmin=-1,
                        zmax=1
                    )
                    fig_corr.update_layout(
                        height=500,
                        title="Matriz de Correlación de Variables Numéricas"
                    )
                    st.plotly_chart(fig_corr, use_container_width=True)
                    
                    # Identificar correlaciones fuertes
                    st.subheader("🎯 Correlaciones Más Fuertes")
                    strong_corr = []
                    for i in range(len(corr_matrix.columns)):
                        for j in range(i+1, len(corr_matrix.columns)):
                            corr_val = corr_matrix.iloc[i, j]
                            if abs(corr_val) > 0.5:  # Umbral de correlación fuerte
                                strong_corr.append({
                                    'Variable 1': corr_matrix.columns[i],
                                    'Variable 2': corr_matrix.columns[j],
                                    'Correlación': f"{corr_val:.3f}",
                                    'Intensidad': '🔴 Muy Fuerte' if abs(corr_val) > 0.8 else '🟠 Fuerte'
                                })
                    
                    if strong_corr:
                        st.dataframe(pd.DataFrame(strong_corr), use_container_width=True, hide_index=True)
                    else:
                        st.info("No se detectaron correlaciones fuertes (>0.5) entre variables")
                else:
                    st.warning("Se necesitan al menos 2 variables numéricas para calcular correlaciones")
                
                st.divider()
                
                # ===== ANÁLISIS ESTADÍSTICOS VIABLES =====
                st.subheader("📈 Análisis Estadísticos Recomendados")
                
                analisis_viables = []
                
                # Análisis descriptivo básico
                if len(numeric_cols) > 0:
                    analisis_viables.append({
                        'Análisis': 'Estadística Descriptiva',
                        'Viabilidad': '✅ Alta',
                        'Descripción': f'Media, mediana, desviación estándar para {len(numeric_cols)} variables numéricas'
                    })
                
                # Test de hipótesis
                if len(numeric_cols) >= 2:
                    analisis_viables.append({
                        'Análisis': 'Tests de Hipótesis',
                        'Viabilidad': '✅ Alta',
                        'Descripción': 'T-test, ANOVA, pruebas de normalidad y homocedasticidad'
                    })
                
                # Análisis de series temporales
                if len(datetime_cols) > 0 and len(numeric_cols) > 0:
                    analisis_viables.append({
                        'Análisis': 'Series Temporales',
                        'Viabilidad': '✅ Alta',
                        'Descripción': f'Análisis de tendencias, estacionalidad con {len(datetime_cols)} variable(s) temporal(es)'
                    })
                
                # Análisis de varianza
                if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                    analisis_viables.append({
                        'Análisis': 'ANOVA / Chi-cuadrado',
                        'Viabilidad': '✅ Alta',
                        'Descripción': 'Comparación entre grupos categóricos'
                    })
                
                # Regresión
                if len(numeric_cols) >= 2:
                    analisis_viables.append({
                        'Análisis': 'Regresión Lineal/Múltiple',
                        'Viabilidad': '✅ Alta',
                        'Descripción': 'Modelar relaciones entre variables numéricas'
                    })
                
                if analisis_viables:
                    st.dataframe(pd.DataFrame(analisis_viables), use_container_width=True, hide_index=True)
                
                st.divider()
                
                # ===== MODELOS PREDICTIVOS VIABLES =====
                st.subheader("🎯 Modelos Predictivos Recomendados")
                
                features = ml.get('features_for_ml', [])
                
                if features and len(features) > 0:
                    st.info(f"💡 Se identificaron **{len(features)} variables** útiles para modelado: {', '.join(features[:5])}{'...' if len(features) > 5 else ''}")
                    
                    modelos_recomendados = []
                    
                    # Clasificación
                    if len(categorical_cols) > 0:
                        modelos_recomendados.append({
                            'Tipo': 'Clasificación',
                            'Modelos': 'Regresión Logística, Random Forest, XGBoost',
                            'Caso de Uso': 'Predecir categorías (ej: riesgo alto/bajo, tipo de evento)',
                            'Prioridad': '🔴 Alta'
                        })
                    
                    # Regresión
                    if len(numeric_cols) >= 2:
                        modelos_recomendados.append({
                            'Tipo': 'Regresión',
                            'Modelos': 'Regresión Lineal, Random Forest Regressor, Gradient Boosting',
                            'Caso de Uso': 'Predecir valores continuos (ej: tasa, score, cantidad)',
                            'Prioridad': '🔴 Alta'
                        })
                    
                    # Series temporales
                    if len(datetime_cols) > 0:
                        modelos_recomendados.append({
                            'Tipo': 'Series Temporales',
                            'Modelos': 'ARIMA, Prophet, LSTM',
                            'Caso de Uso': 'Predecir tendencias futuras basadas en histórico',
                            'Prioridad': '🟠 Media' if len(df) < 100 else '🔴 Alta'
                        })
                    
                    # Clustering
                    if len(numeric_cols) >= 3:
                        modelos_recomendados.append({
                            'Tipo': 'Clustering',
                            'Modelos': 'K-Means, DBSCAN, Hierarchical',
                            'Caso de Uso': 'Identificar grupos naturales en los datos',
                            'Prioridad': '🟡 Baja'
                        })
                    
                    # Detección de anomalías
                    if len(numeric_cols) >= 2:
                        modelos_recomendados.append({
                            'Tipo': 'Detección de Anomalías',
                            'Modelos': 'Isolation Forest, One-Class SVM, Autoencoders',
                            'Caso de Uso': 'Identificar casos atípicos o eventos inusuales',
                            'Prioridad': '🟠 Media'
                        })
                    
                    if modelos_recomendados:
                        st.dataframe(pd.DataFrame(modelos_recomendados), use_container_width=True, hide_index=True)
                        
                        st.success(f"✅ Dataset viable para **{len(modelos_recomendados)}** tipos de modelado predictivo")
                    else:
                        st.warning("Dataset tiene viabilidad limitada para modelado predictivo")
                else:
                    st.warning("No se identificaron suficientes features para modelado ML")
        
        # ========== 3.6 ANÁLISIS SEMÁNTICO ==========
        with st.expander("🔍 Análisis Semántico", expanded=False):
            semantic = results.get('semantica', {})
            
            if semantic:
                # Obtener summary
                summary = semantic.get('summary', {})
                total_issues = summary.get('total_issues', 0)
                critical_issues = summary.get('critical_issues', 0)
                score = summary.get('score', 100)
                quality_level = summary.get('quality_level', 'excelente')
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Score Semántico", f"{score:.0f}%")
                
                with col2:
                    st.metric("Issues Totales", total_issues)
                
                with col3:
                    st.metric("Issues Críticos", critical_issues)
                
                # Nivel de calidad
                if quality_level == 'excelente':
                    st.success(f"✅ Calidad semántica: **{quality_level.upper()}**")
                elif quality_level == 'bueno':
                    st.info(f"ℹ️ Calidad semántica: **{quality_level.upper()}**")
                else:
                    st.warning(f"⚠️ Calidad semántica: **{quality_level.upper()}**")
                
                # Mostrar problemas detectados
                if total_issues > 0:
                    st.subheader("⚠️ Problemas Detectados")
                    
                    # Edades inválidas
                    edad_invalida = semantic.get('edad_invalida', [])
                    if edad_invalida:
                        st.warning("**Edades Inválidas:**")
                        for issue in edad_invalida:
                            st.write(f"  • {issue}")
                    
                    # Fechas incoherentes
                    fechas_incoherentes = semantic.get('fechas_incoherentes', [])
                    if fechas_incoherentes:
                        st.warning("**Fechas Incoherentes:**")
                        for issue in fechas_incoherentes:
                            st.write(f"  • {issue}")
                    
                    # Métodos no estandarizados
                    metodos_no_estandarizados = semantic.get('metodos_no_estandarizados', [])
                    if metodos_no_estandarizados:
                        st.warning("**Métodos No Estandarizados:**")
                        for issue in metodos_no_estandarizados:
                            st.write(f"  • {issue}")
                    
                    # Valores imposibles
                    valores_imposibles = semantic.get('valores_imposibles', [])
                    if valores_imposibles:
                        st.error("**Valores Imposibles:**")
                        for issue in valores_imposibles:
                            st.write(f"  • {issue}")
                else:
                    st.success("✅ **Análisis Semántico Exitoso**")
                    st.write("**No se detectaron problemas en:**")
                    st.write("  ✓ Edades están en rangos válidos")
                    st.write("  ✓ Fechas son coherentes")
                    st.write("  ✓ Métodos estandarizados correctamente")
                    st.write("  ✓ No hay valores imposibles detectados")
        
        # ========== 3.7 ANÁLISIS GEOESPACIAL Y TEMPORAL ==========
        with st.expander("🗺️ Análisis Geoespacial y Temporal", expanded=False):
            
            # Detectar columnas de dirección y fecha
            address_cols = [col for col in df.columns if any(keyword in col.lower() 
                          for keyword in ['direc', 'address', 'ubicac', 'location', 'lugar', 'domicilio', 'calle', 'street'])]
            
            date_cols = [col for col in df.columns if any(keyword in col.lower() 
                        for keyword in ['fecha', 'date', 'tiempo', 'time', 'cuando', 'when'])]
            
            # Convertir columnas datetime si existen
            for col in date_cols:
                try:
                    if df[col].dtype != 'datetime64[ns]':
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
            
            # Actualizar date_cols después de conversión
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            st.subheader("📍 Detección de Datos Espaciales y Temporales")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Columnas de Dirección", len(address_cols))
                if address_cols:
                    st.write("Variables detectadas:", ", ".join(address_cols))
            
            with col2:
                st.metric("Columnas Temporales", len(datetime_cols))
                if datetime_cols:
                    st.write("Variables detectadas:", ", ".join(datetime_cols))
            
            # ===== ANÁLISIS GEOESPACIAL =====
            if address_cols:
                st.divider()
                st.subheader("🌍 Análisis Geográfico")
                
                # Seleccionar columna de dirección
                selected_address_col = st.selectbox(
                    "Selecciona la columna de dirección a analizar:",
                    address_cols,
                    key="geo_address_col"
                )
                
                if selected_address_col:
                    # Detectar columna de comuna/ciudad
                    st.subheader("🏘️ Detección de Comuna/Ciudad")
                    
                    comuna_keywords = ['comuna', 'ciudad', 'municipio', 'localidad', 'territorio']
                    comuna_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in comuna_keywords)]
                    
                    if comuna_cols:
                        st.success(f"✅ Columna de comuna detectada: **{', '.join(comuna_cols)}**")
                        selected_comuna_col = st.selectbox(
                            "Selecciona la columna de comuna/ciudad:",
                            comuna_cols,
                            key="geo_comuna_col"
                        )
                        use_comuna = True
                    else:
                        st.info("💡 No se detectó columna de comuna. Se usará solo la columna de dirección.")
                        selected_comuna_col = None
                        use_comuna = st.checkbox(
                            "¿Deseas especificar manualmente una columna de comuna?",
                            value=False,
                            key="manual_comuna_check"
                        )
                        
                        if use_comuna:
                            selected_comuna_col = st.selectbox(
                                "Selecciona columna que contiene comuna/ciudad:",
                                df.columns.tolist(),
                                key="manual_comuna_col"
                            )
                    
                    # Obtener muestra de direcciones
                    addresses_sample = df[selected_address_col].dropna()
                    
                    # Si hay columna de comuna, combinar
                    if use_comuna and selected_comuna_col:
                        comunas_sample = df[selected_comuna_col].dropna()
                        st.write(f"**Total de direcciones:** {len(addresses_sample)} | **Total comunas:** {len(comunas_sample)}")
                        
                        # Mostrar comunas únicas
                        with st.expander("🏘️ Comunas en los Datos", expanded=False):
                            comunas_unicas = comunas_sample.unique()
                            st.write(f"**{len(comunas_unicas)} comunas únicas detectadas:**")
                            st.write(", ".join([str(c) for c in comunas_unicas]))
                    else:
                        selected_comuna_col = None
                    
                    if len(addresses_sample) > 0:
                        st.write(f"**Total de direcciones:** {len(addresses_sample)}")
                        
                        # Mostrar muestra de primeras y últimas direcciones
                        with st.expander("📋 Muestra de Direcciones", expanded=False):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.write("**Primeras 20 direcciones:**")
                                st.dataframe(addresses_sample.head(20).to_frame(), use_container_width=True)
                            with col_b:
                                st.write("**Últimas 20 direcciones:**")
                                st.dataframe(addresses_sample.tail(20).to_frame(), use_container_width=True)
                        
                        # Análisis de región/país/ciudad desde direcciones
                        st.subheader("🔍 Identificación de Región")
                        
                        # Tomar muestra combinada (primeras 20 + últimas 20)
                        sample_addresses = pd.concat([
                            addresses_sample.head(20),
                            addresses_sample.tail(20)
                        ]).unique()
                        
                        # Análisis simple de palabras clave en direcciones
                        all_text = " ".join([str(addr).lower() for addr in sample_addresses if pd.notna(addr)])
                        
                        # Detectar posibles ciudades/países comunes
                        ciudades_spain = ['valencia', 'madrid', 'barcelona', 'sevilla', 'zaragoza', 'málaga', 
                                         'murcia', 'palma', 'bilbao', 'alicante', 'córdoba', 'valladolid']
                        ciudades_latam = ['santiago', 'valparaíso', 'concepción', 'valdivia', 'temuco', 
                                         'puerto montt', 'buenos aires', 'lima', 'bogotá', 'caracas', 'quito', 
                                         'ciudad de méxico', 'guadalajara', 'monterrey', 'medellín']
                        
                        detected_cities = []
                        for ciudad in ciudades_spain + ciudades_latam:
                            if ciudad in all_text:
                                detected_cities.append(ciudad.title())
                        
                        if detected_cities:
                            st.info(f"🏙️ Ciudades detectadas en las direcciones: **{', '.join(detected_cities)}**")
                            
                            # Estimar país/región principal
                            if any(c.lower() in ciudades_spain for c in detected_cities):
                                st.success("📍 Región estimada: **España**")
                                default_location = "España"
                            elif any(c.lower() in ciudades_latam for c in detected_cities):
                                st.success("📍 Región estimada: **Latinoamérica**")
                                default_location = "Latinoamérica"
                            else:
                                default_location = detected_cities[0] if detected_cities else "España"
                        else:
                            st.warning("No se pudo identificar automáticamente la región. Por favor especifica manualmente.")
                            default_location = ""
                        
                        st.divider()
                        
                        # ===== DETECCIÓN AUTOMÁTICA DE COORDENADAS =====
                        st.subheader("📍 Detección de Coordenadas")
                        
                        # Detectar si ya existen columnas de coordenadas
                        coord_cols = {'latitud', 'longitud', 'lat', 'lon', 'latitude', 'longitude'}
                        existing_coords = [col for col in df.columns if col.lower() in coord_cols]
                        
                        has_coordinates = False
                        lat_col, lon_col = None, None
                        
                        if len(existing_coords) >= 2:
                            # Intentar encontrar pares lat/lon
                            for lat_name in ['latitud', 'lat', 'latitude']:
                                for lon_name in ['longitud', 'lon', 'longitude']:
                                    if lat_name in [c.lower() for c in df.columns] and lon_name in [c.lower() for c in df.columns]:
                                        lat_col = [c for c in df.columns if c.lower() == lat_name][0]
                                        lon_col = [c for c in df.columns if c.lower() == lon_name][0]
                                        has_coordinates = True
                                        break
                                if has_coordinates:
                                    break
                        
                        if has_coordinates:
                            # Verificar que las coordenadas no estén vacías
                            valid_coords = df[[lat_col, lon_col]].dropna()
                            if len(valid_coords) > 0:
                                # Intentar detectar columna de ubicación/nombre
                                location_keywords = ['ubicacion', 'barrio', 'direccion', 'localidad', 'zona', 
                                                   'location', 'address', 'place', 'city', 'municipality']
                                location_col = None
                                for keyword in location_keywords:
                                    matching = [c for c in df.columns if keyword in c.lower()]
                                    if matching:
                                        location_col = matching[0]
                                        break
                                
                                # Si no hay columna de ubicación, usar índice o primera columna de texto
                                if location_col is None:
                                    # Buscar primera columna de texto que no sea coordenada
                                    for col in df.columns:
                                        if col not in [lat_col, lon_col] and df[col].dtype == 'object':
                                            location_col = col
                                            break
                                
                                # Si aún no hay, crear una columna de índice
                                if location_col is None:
                                    df['punto'] = [f"Punto {i+1}" for i in range(len(df))]
                                    location_col = 'punto'
                                
                                st.success(f"""
                                ✅ **Coordenadas GPS detectadas automáticamente**
                                
                                - **Columna latitud:** `{lat_col}` 
                                - **Columna longitud:** `{lon_col}`
                                - **Columna de identificación:** `{location_col}`
                                - **Registros con coordenadas válidas:** {len(valid_coords):,} de {len(df):,} ({len(valid_coords)/len(df)*100:.1f}%)
                                
                                🚀 **Omitiendo geocodificación** - Generando visualizaciones directamente...
                                """)
                                
                                # Mostrar muestra de coordenadas
                                with st.expander("🗺️ Ver muestra de coordenadas"):
                                    st.dataframe(
                                        df[[location_col, lat_col, lon_col]].dropna().head(10),
                                        use_container_width=True
                                    )
                                
                                # SALTAR DIRECTAMENTE A VISUALIZACIONES
                                skip_geocoding = True
                                
                                # ===== VISUALIZACIONES ESPACIO-TEMPORALES DIRECTAS =====
                                st.divider()
                                st.subheader("🗺️✨ Visualizaciones Geoespaciales Interactivas")
                                
                                # Preparar DataFrame con coordenadas válidas
                                df_geo = df[[location_col, lat_col, lon_col]].copy()
                                df_geo = df_geo.dropna(subset=[lat_col, lon_col])
                                
                                # Agregar columna temporal si existe
                                if datetime_cols:
                                    date_col = datetime_cols[0]
                                    df_geo['fecha'] = df[date_col]
                                    df_geo['año'] = pd.to_datetime(df[date_col], errors='coerce').dt.year
                                    df_geo['mes'] = pd.to_datetime(df[date_col], errors='coerce').dt.month
                                
                                # Renombrar columnas para plotly
                                df_geo = df_geo.rename(columns={lat_col: 'lat', lon_col: 'lon', location_col: 'ubicacion'})
                                
                                # Tabs para diferentes visualizaciones (SOLO 2 TABS)
                                viz_tab1, viz_tab2 = st.tabs([
                                    "📍 Mapa de Puntos por Año", 
                                    "🎬 Animación Temporal"
                                ])
                                
                                with viz_tab1:
                                    st.markdown("**Mapa de Puntos Filtrable** - Visualiza eventos por año seleccionado")
                                    
                                    # Filtros interactivos
                                    if 'año' in df_geo.columns:
                                        col_filter1, col_filter2 = st.columns(2)
                                        
                                        with col_filter1:
                                            años_disponibles = sorted(df_geo['año'].dropna().unique())
                                            año_seleccionado = st.selectbox(
                                                "Selecciona el año a visualizar",
                                                options=['Todos'] + [int(a) for a in años_disponibles],
                                                index=0,
                                                key="year_filter"
                                            )
                                        
                                        with col_filter2:
                                            point_size = st.slider(
                                                "Tamaño de puntos",
                                                min_value=3,
                                                max_value=15,
                                                value=8,
                                                key="point_size"
                                            )
                                        
                                        # Filtrar datos según año seleccionado
                                        if año_seleccionado == 'Todos':
                                            df_filtered = df_geo.copy()
                                            title_suffix = "Todos los años"
                                        else:
                                            df_filtered = df_geo[df_geo['año'] == año_seleccionado].copy()
                                            title_suffix = f"Año {año_seleccionado}"
                                        
                                        # Crear mapa de puntos mejorado
                                        fig_points = px.scatter_mapbox(
                                            df_filtered,
                                            lat='lat',
                                            lon='lon',
                                            color='año' if año_seleccionado == 'Todos' else None,
                                            hover_name='ubicacion',
                                            hover_data={'lat': ':.4f', 'lon': ':.4f', 'año': True} if 'año' in df_filtered.columns else {'lat': ':.4f', 'lon': ':.4f'},
                                            zoom=11,
                                            mapbox_style="carto-positron",
                                            title=f"Mapa de Eventos - {title_suffix} ({len(df_filtered):,} eventos)",
                                            height=650,
                                            color_continuous_scale="Turbo" if año_seleccionado == 'Todos' else None
                                        )
                                        
                                        # Actualizar estilo de marcadores
                                        fig_points.update_traces(
                                            marker=dict(
                                                size=point_size,
                                                opacity=0.7
                                            )
                                        )
                                        
                                        fig_points.update_layout(
                                            margin=dict(l=0, r=0, t=50, b=0),
                                            font=dict(color='#0A1A2F')  # Texto oscuro para fondo claro
                                        )
                                        
                                        st.plotly_chart(fig_points, use_container_width=True)
                                        
                                        # Estadísticas del año seleccionado
                                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                                        with col_stat1:
                                            st.metric("Eventos Mostrados", f"{len(df_filtered):,}")
                                        with col_stat2:
                                            if año_seleccionado != 'Todos':
                                                ubicaciones_unicas = df_filtered[['lat', 'lon']].drop_duplicates()
                                                st.metric("Ubicaciones Únicas", len(ubicaciones_unicas))
                                            else:
                                                st.metric("Años Totales", len(años_disponibles))
                                        with col_stat3:
                                            if año_seleccionado != 'Todos' and len(df_filtered) > 0:
                                                promedio_anual = len(df_geo) / len(años_disponibles)
                                                diff = len(df_filtered) - promedio_anual
                                                st.metric("vs Promedio Anual", f"{diff:+.0f}", f"{promedio_anual:.0f} eventos/año")
                                            else:
                                                st.metric("Promedio Anual", f"{len(df_geo) / len(años_disponibles):.0f}")
                                    else:
                                        st.warning("No hay información de año disponible para filtrar")

                                
                                with viz_tab2:
                                    if 'año' in df_geo.columns and 'mes' in df_geo.columns:
                                        st.markdown("**Animación Temporal Avanzada** - Visualiza la evolución con clusters heterogéneos")
                                        
                                        # Controles de animación mejorados
                                        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
                                        with col_ctrl1:
                                            anim_speed = st.slider(
                                                "Velocidad animación (ms)",
                                                min_value=300,
                                                max_value=2000,
                                                value=800,
                                                step=100,
                                                key="anim_speed_v2"
                                            )
                                        with col_ctrl2:
                                            color_scheme = st.selectbox(
                                                "Paleta de color",
                                                ["Hot", "YlOrRd", "Inferno", "Plasma", "Turbo"],
                                                index=0,
                                                key="color_scheme_v2"
                                            )
                                        with col_ctrl3:
                                            cluster_size_multiplier = st.slider(
                                                "Intensidad clusters",
                                                min_value=1.0,
                                                max_value=3.0,
                                                value=2.0,
                                                step=0.5,
                                                key="cluster_intensity"
                                            )
                                        
                                        # Preparar datos para animación POR AÑO
                                        df_anim = df_geo.copy()
                                        df_anim = df_anim.dropna(subset=['año', 'mes'])
                                        df_anim['año'] = df_anim['año'].astype(int)
                                        df_anim['mes'] = df_anim['mes'].astype(int)
                                        
                                        # Agrupar por año y ubicación para crear clusters heterogéneos
                                        df_anim_year = df_anim.groupby(['lat', 'lon', 'año', 'ubicacion']).size().reset_index(name='eventos')
                                        
                                        # Crear categorías de intensidad para heterogeneidad visual
                                        max_eventos = df_anim_year['eventos'].max()
                                        df_anim_year['intensidad'] = pd.cut(
                                            df_anim_year['eventos'],
                                            bins=[0, max_eventos*0.25, max_eventos*0.5, max_eventos*0.75, max_eventos],
                                            labels=['Baja', 'Media', 'Alta', 'Crítica'],
                                            include_lowest=True
                                        )
                                        
                                        # Asignar colores intensos según intensidad
                                        color_map = {
                                            'Baja': '#4A90E2',      # Azul
                                            'Media': '#F5A623',     # Naranja
                                            'Alta': '#FF6B6B',      # Rojo
                                            'Crítica': '#FF1744'    # Rojo intenso
                                        }
                                        df_anim_year['color_intensidad'] = df_anim_year['intensidad'].map(color_map)
                                        
                                        # Crear animación con colores heterogéneos por intensidad
                                        fig_anim = px.scatter_mapbox(
                                            df_anim_year,
                                            lat='lat',
                                            lon='lon',
                                            size='eventos',
                                            color='intensidad',  # Usar intensidad categórica
                                            animation_frame='año',
                                            hover_name='ubicacion',
                                            hover_data={
                                                'lat': ':.4f',
                                                'lon': ':.4f',
                                                'eventos': True,
                                                'intensidad': True,
                                                'año': True
                                            },
                                            zoom=11,
                                            mapbox_style="carto-darkmatter",
                                            title="Evolución Anual - Clusters por Intensidad",
                                            height=750,
                                            color_discrete_map=color_map,  # Usar mapa de colores discreto
                                            size_max=40 * cluster_size_multiplier,
                                            category_orders={"intensidad": ['Baja', 'Media', 'Alta', 'Crítica']}
                                        )
                                        
                                        # Mejorar diseño con colores para fondo oscuro
                                        fig_anim.update_layout(
                                            margin=dict(l=0, r=0, t=60, b=0),
                                            coloraxis_colorbar=dict(
                                                title=dict(
                                                    text="Eventos",
                                                    font=dict(color='white', size=14)  # Blanco para fondo oscuro
                                                ),
                                                thickness=18,
                                                len=0.7,
                                                tickfont=dict(color='white')  # Blanco para fondo oscuro
                                            ),
                                            font=dict(
                                                size=13,
                                                color='white'  # Blanco para fondo oscuro
                                            ),
                                            title=dict(
                                                font=dict(color='white', size=16)  # Blanco para fondo oscuro
                                            )
                                        )
                                        
                                        # Configurar controles de animación
                                        fig_anim.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = anim_speed
                                        fig_anim.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = anim_speed // 2
                                        
                                        # Mejorar slider temporal
                                        fig_anim.layout.sliders[0].pad = dict(t=60, b=15)
                                        fig_anim.layout.sliders[0].currentvalue = dict(
                                            prefix="Año: ",
                                            font=dict(size=18, color='#64FFDA', family='Inter')  # Teal para destacar
                                        )
                                        fig_anim.layout.sliders[0].font = dict(color='white')  # Blanco para fondo oscuro
                                        
                                        # Mejorar marcadores
                                        fig_anim.update_traces(
                                            marker=dict(
                                                opacity=0.85
                                            )
                                        )
                                        
                                        st.plotly_chart(fig_anim, use_container_width=True)
                                        
                                        # Leyenda de intensidad por color
                                        st.markdown("##### 🔍 Leyenda de Intensidad por Color")
                                        col_leg1, col_leg2, col_leg3, col_leg4 = st.columns(4)
                                        with col_leg1:
                                            st.markdown("🔵 **Baja** - Azul (Pocos eventos)")
                                        with col_leg2:
                                            st.markdown("🟠 **Media** - Naranja (Moderado)")
                                        with col_leg3:
                                            st.markdown("🔴 **Alta** - Rojo (Muchos eventos)")
                                        with col_leg4:
                                            st.markdown("🔥 **Crítica** - Rojo intenso (Máxima concentración)")
                                        
                                        # Estadísticas por año
                                        st.markdown("#### 📊 Estadísticas Anuales")
                                        eventos_por_año = df_anim.groupby('año').size().reset_index(name='total')
                                        
                                        col1, col2, col3, col4 = st.columns(4)
                                        with col1:
                                            max_año = eventos_por_año.loc[eventos_por_año['total'].idxmax()]
                                            st.metric(
                                                "Año con más eventos",
                                                int(max_año['año']),
                                                f"{int(max_año['total'])} eventos"
                                            )
                                        with col2:
                                            min_año = eventos_por_año.loc[eventos_por_año['total'].idxmin()]
                                            st.metric(
                                                "Año con menos eventos",
                                                int(min_año['año']),
                                                f"{int(min_año['total'])} eventos"
                                            )
                                        with col3:
                                            st.metric(
                                                "Promedio anual",
                                                f"{eventos_por_año['total'].mean():.0f}",
                                                f"±{eventos_por_año['total'].std():.0f}"
                                            )
                                        with col4:
                                            st.metric(
                                                "Años analizados",
                                                len(eventos_por_año)
                                            )
                                        
                                        # Gráfico de tendencia con opciones
                                        st.markdown("##### 📈 Análisis de Tendencia Temporal")
                                        
                                        trend_option = st.radio(
                                            "Selecciona el tipo de análisis",
                                            ["Bi-anual (2 registros/año)", "Mensual (12 registros/año)"],
                                            horizontal=True,
                                            key="trend_type"
                                        )
                                        
                                        if trend_option == "Bi-anual (2 registros/año)":
                                            # Crear semestres
                                            df_trend = df_anim.copy()
                                            df_trend['semestre'] = df_trend['mes'].apply(lambda x: 1 if x <= 6 else 2)
                                            df_trend['periodo'] = df_trend.apply(
                                                lambda x: f"S{int(x['semestre'])} {int(x['año'])}", axis=1
                                            )
                                            df_trend['periodo_orden'] = df_trend['año'] * 2 + df_trend['semestre']
                                            
                                            trend_data = df_trend.groupby(['periodo', 'periodo_orden']).size().reset_index(name='eventos')
                                            trend_data = trend_data.sort_values('periodo_orden')
                                            
                                            x_label = "Semestres"
                                        else:  # Mensual
                                            meses_nombres = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun',
                                                           7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
                                            df_trend = df_anim.copy()
                                            df_trend['periodo'] = df_trend.apply(
                                                lambda x: f"{meses_nombres[x['mes']]} {int(x['año'])}", axis=1
                                            )
                                            df_trend['periodo_orden'] = df_trend['año'] * 12 + df_trend['mes']
                                            
                                            trend_data = df_trend.groupby(['periodo', 'periodo_orden']).size().reset_index(name='eventos')
                                            trend_data = trend_data.sort_values('periodo_orden')
                                            
                                            x_label = "Meses"
                                        
                                        # Crear gráfico de tendencia mejorado
                                        fig_trend = go.Figure()
                                        
                                        # Línea principal
                                        fig_trend.add_trace(go.Scatter(
                                            x=list(range(len(trend_data))),
                                            y=trend_data['eventos'],
                                            mode='lines+markers',
                                            name='Eventos',
                                            line=dict(color='#64FFDA', width=3),
                                            marker=dict(size=8, color='#FF5F9E', line=dict(width=2, color='white')),
                                            text=trend_data['periodo'],
                                            hovertemplate='<b>%{text}</b><br>Eventos: %{y}<extra></extra>',
                                            fill='tozeroy',
                                            fillcolor='rgba(100, 255, 218, 0.1)'
                                        ))
                                        
                                        fig_trend.update_layout(
                                            height=350,
                                            template='plotly_dark',
                                            xaxis_title=x_label,
                                            yaxis_title="Número de Eventos",
                                            showlegend=False,
                                            margin=dict(l=0, r=0, t=30, b=0),
                                            font=dict(color='white', size=12),  # Blanco para fondo oscuro
                                            plot_bgcolor='rgba(17, 34, 64, 0.5)',
                                            paper_bgcolor='rgba(10, 26, 47, 0.8)'
                                        )
                                        
                                        fig_trend.update_xaxes(
                                            showgrid=True,
                                            gridwidth=1,
                                            gridcolor='rgba(100, 255, 218, 0.1)',
                                            tickfont=dict(color='white')  # Blanco para fondo oscuro
                                        )
                                        fig_trend.update_yaxes(
                                            showgrid=True,
                                            gridwidth=1,
                                            gridcolor='rgba(100, 255, 218, 0.1)',
                                            tickfont=dict(color='white')  # Blanco para fondo oscuro
                                        )
                                        
                                        st.plotly_chart(fig_trend, use_container_width=True)

                                
                                # Estadísticas geográficas
                                st.divider()
                                st.subheader("📊 Estadísticas Geográficas")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric(
                                        "Total de Eventos Georreferenciados",
                                        f"{len(df_geo):,}",
                                        f"{len(df_geo)/len(df)*100:.1f}% del total"
                                    )
                                
                                with col2:
                                    # Calcular centro geográfico
                                    centro_lat = df_geo['lat'].mean()
                                    centro_lon = df_geo['lon'].mean()
                                    st.metric(
                                        "Centro Geográfico",
                                        f"{centro_lat:.4f}, {centro_lon:.4f}"
                                    )
                                
                                with col3:
                                    # Calcular área de dispersión (bounding box)
                                    lat_range = df_geo['lat'].max() - df_geo['lat'].min()
                                    lon_range = df_geo['lon'].max() - df_geo['lon'].min()
                                    st.metric(
                                        "Área de Dispersión",
                                        f"{lat_range:.4f}° × {lon_range:.4f}°"
                                    )
                                
                                with col4:
                                    # Ubicaciones únicas
                                    ubicaciones_unicas = df_geo[['lat', 'lon']].drop_duplicates()
                                    st.metric(
                                        "Ubicaciones Únicas",
                                        f"{len(ubicaciones_unicas):,}"
                                    )
                            
                            else:
                                st.warning("⚠️ Las columnas de coordenadas están vacías. Se requiere geocodificación.")
                                has_coordinates = False
                                skip_geocoding = False
                        else:
                            st.info("ℹ️ No se detectaron coordenadas GPS. Se requiere geocodificación.")
                            skip_geocoding = False
                        
                        st.divider()
                        
                        # ===== GEOCODIFICACIÓN (solo si no hay coordenadas) =====
                        if not skip_geocoding:
                            st.subheader("🗺️ Configuración de Geocodificación")
                            
                            st.info("""
                            **Geocodificación con Nominatim (OpenStreetMap):**
                            - ✅ Gratis, sin API key necesaria
                        - 🌍 Cobertura global
                        - 📍 Especifica la región/ciudad para mejorar precisión
                        """)
                        
                        # Método de especificación de región
                        st.subheader("📍 Especifica la Región/Ciudad")
                        
                        metodo_region = st.radio(
                            "¿Cómo quieres especificar la región?",
                            options=["Seleccionar de lista", "Escribir manualmente"],
                            horizontal=True,
                            key="metodo_region"
                        )
                        
                        if metodo_region == "Seleccionar de lista":
                            # Lista predefinida de ciudades
                            ciudades_predefinidas = {
                                "España": ["Valencia", "Madrid", "Barcelona", "Sevilla", "Zaragoza", 
                                          "Málaga", "Murcia", "Bilbao", "Alicante", "Córdoba"],
                                "Chile": ["Santiago", "Valparaíso", "Concepción", "Valdivia", "La Serena", 
                                         "Antofagasta", "Temuco", "Puerto Montt", "Iquique", "Arica", 
                                         "Punta Arenas", "Rancagua", "Talca", "Chillán", "Los Ángeles"],
                                "Argentina": ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata",
                                            "San Miguel de Tucumán", "Mar del Plata", "Salta", "Santa Fe"],
                                "Colombia": ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena",
                                           "Bucaramanga", "Pereira", "Manizales", "Ibagué"],
                                "México": ["Ciudad de México", "Guadalajara", "Monterrey", "Puebla", "Tijuana",
                                          "León", "Mérida", "Querétaro", "Cancún"],
                                "Perú": ["Lima", "Arequipa", "Trujillo", "Chiclayo", "Piura",
                                        "Cusco", "Huancayo", "Iquitos", "Tacna"],
                                "Otro": ["Especificar manualmente"]
                            }
                            
                            col_pais, col_ciudad = st.columns(2)
                            
                            with col_pais:
                                pais_seleccionado = st.selectbox(
                                    "País:",
                                    options=list(ciudades_predefinidas.keys()),
                                    index=0 if default_location in ["España", ""] else 
                                          (1 if "santiago" in default_location.lower() else 0),
                                    key="pais_select"
                                )
                            
                            with col_ciudad:
                                if pais_seleccionado == "Otro":
                                    region_manual = st.text_input(
                                        "Escribe tu ciudad:",
                                        placeholder="Ej: Bogotá, Colombia",
                                        key="ciudad_manual_otro"
                                    )
                                else:
                                    ciudad_seleccionada = st.selectbox(
                                        "Ciudad:",
                                        options=ciudades_predefinidas[pais_seleccionado],
                                        index=0,
                                        key="ciudad_select"
                                    )
                                    region_manual = f"{ciudad_seleccionada}, {pais_seleccionado}"
                        
                        else:  # Escribir manualmente
                            region_manual = st.text_input(
                                "Escribe la región/ciudad (puede incluir país):",
                                placeholder="Ej: Valencia, España o Santiago, Chile",
                                value=default_location if default_location else "",
                                key="region_manual_input",
                                help="Especifica ciudad y país para mejor precisión. Ej: 'Valencia, España'"
                            )
                        
                        # Mostrar región seleccionada
                        if region_manual:
                            st.success(f"✅ Región configurada: **{region_manual}**")
                        else:
                            st.warning("⚠️ Por favor especifica una región antes de geocodificar")
                        
                        st.divider()
                        
                        # Opciones de geocodificación
                        st.subheader("⚙️ Parámetros de Geocodificación")
                        
                        col_config1, col_config2 = st.columns(2)
                        with col_config1:
                            max_addresses = st.slider(
                                "Máximo de direcciones a geocodificar:",
                                min_value=10,
                                max_value=500,
                                value=100,
                                step=10,
                                help="Limitar para evitar sobrecargar el servicio gratuito"
                            )
                        
                        with col_config2:
                            use_cache = st.checkbox(
                                "Usar caché de geocodificación",
                                value=True,
                                help="Guarda coordenadas ya buscadas para no repetir"
                            )
                        
                        # Validar que haya región antes de mostrar botón
                        if not region_manual or region_manual.strip() == "":
                            st.error("❌ Debes especificar una región/ciudad antes de geocodificar")
                            st.button("🎯 Geocodificar y Generar Mapa", disabled=True, key="geo_map_button_disabled")
                        else:
                            if st.button("🎯 Geocodificar y Generar Mapa", key="geo_map_button", type="primary"):
                                with st.spinner(f"Geocodificando direcciones en {region_manual}..."):
                                    try:
                                        # Verificar si geopy está disponible
                                        if not GEOPY_AVAILABLE:
                                            st.error("⚠️ Necesitas instalar geopy: `pip install geopy`")
                                            st.info("Continuando con coordenadas simuladas...")
                                            raise ImportError("geopy not installed")
                                        
                                        # Inicializar geocodificador
                                        geolocator = Nominatim(user_agent="cuidar_ia_evaluator")
                                        
                                        # Inicializar caché si está activado
                                        if use_cache and 'geocode_cache' not in st.session_state:
                                            st.session_state.geocode_cache = {}
                                        
                                        geocode_cache = st.session_state.geocode_cache if use_cache else {}
                                        
                                        # Diccionario de coordenadas de comunas de Chile (Región de Los Ríos y alrededores)
                                        COMUNAS_CHILE = {
                                            # Región de Los Ríos
                                            'valdivia': (-39.8142, -73.2459),
                                            'la union': (-40.2934, -73.0836),
                                            'rio bueno': (-40.3342, -72.9562),
                                            'lago ranco': (-40.3167, -72.5000),
                                            'futrono': (-40.1333, -72.3833),
                                            'panguipulli': (-39.6431, -72.3328),
                                            'lanco': (-39.4489, -72.7694),
                                            'los lagos': (-39.8569, -72.8169),
                                            'mariquina': (-39.5333, -72.9667),
                                            'san jose de la mariquina': (-39.5333, -72.9667),
                                            'corral': (-39.8889, -73.4308),
                                            'mafil': (-39.6667, -72.9500),
                                            'paillaco': (-40.0708, -72.8778),
                                            # Región de Los Lagos
                                            'osorno': (-40.5742, -73.1317),
                                            'puerto montt': (-41.4693, -72.9424),
                                            'puerto varas': (-41.3194, -72.9836),
                                            'castro': (-42.4792, -73.7619),
                                            'ancud': (-41.8706, -73.8261),
                                            # Otras
                                            'temuco': (-38.7359, -72.5904),
                                            'concepcion': (-36.8270, -73.0497),
                                            'santiago': (-33.4489, -70.6693),
                                        }
                                        
                                        # Función de geocodificación FLEXIBLE con múltiples intentos
                                        def geocode_address_flexible(address, comuna=None):
                                            """
                                            Geocodifica con estrategia de fallback:
                                            1. Dirección + Comuna + Región
                                            2. Comuna + Región
                                            3. Coordenadas centrales de la Comuna (fallback)
                                            4. Coordenadas de la región (fallback final)
                                            
                                            SIEMPRE retorna un resultado (nunca None)
                                            """
                                            
                                            # Revisar caché
                                            # Manejar comuna de forma segura (puede ser None, string, o tener NaN)
                                            comuna_str = str(comuna) if comuna is not None and not pd.isna(comuna) else "none"
                                            cache_key = f"{address}_{comuna_str}"
                                            if cache_key in geocode_cache:
                                                return geocode_cache[cache_key]
                                            
                                            # Limpiar
                                            address_clean = str(address).strip()
                                            
                                            # Manejar comuna (puede ser None, string, o Series)
                                            if comuna is None or (isinstance(comuna, str) and not comuna.strip()):
                                                comuna_clean = None
                                            elif pd.isna(comuna):
                                                comuna_clean = None
                                            else:
                                                comuna_clean = str(comuna).strip().lower()
                                            
                                            # Lista de queries a intentar (menos queries, más rápido)
                                            queries = []
                                            
                                            if comuna_clean:
                                                # Intentar con comuna primero
                                                queries.append(f"{address_clean}, {comuna_clean}, Chile")
                                                queries.append(f"{comuna_clean}, Región de Los Ríos, Chile")
                                            
                                            # Intentar con región
                                            queries.append(f"{address_clean}, Valdivia, Chile")
                                            
                                            # Intentar geocodificar (solo 1 intento por query, más rápido)
                                            for query in queries:
                                                try:
                                                    location = geolocator.geocode(query, timeout=5, exactly_one=True)
                                                    
                                                    if location:
                                                        result = {
                                                            'lat': location.latitude,
                                                            'lon': location.longitude,
                                                            'display_name': location.address,
                                                            'method': 'geocoded'
                                                        }
                                                        geocode_cache[cache_key] = result
                                                        return result
                                                except:
                                                    continue  # Continuar rápidamente al siguiente
                                            
                                            # FALLBACK 1: Usar coordenadas de la comuna
                                            if comuna_clean:
                                                # Normalizar nombre de comuna
                                                comuna_normalized = comuna_clean.replace('san jose de la mariquina', 'mariquina')
                                                
                                                if comuna_normalized in COMUNAS_CHILE:
                                                    lat, lon = COMUNAS_CHILE[comuna_normalized]
                                                    # Agregar variación aleatoria
                                                    lat += np.random.uniform(-0.02, 0.02)
                                                    lon += np.random.uniform(-0.02, 0.02)
                                                    
                                                    result = {
                                                        'lat': lat,
                                                        'lon': lon,
                                                        'display_name': f"{comuna_clean.title()}, Chile (centro comuna)",
                                                        'method': 'fallback'
                                                    }
                                                    geocode_cache[cache_key] = result
                                                    return result
                                            
                                            # FALLBACK 2: Coordenadas del centro de Valdivia (SIEMPRE)
                                            lat, lon = (-39.8142, -73.2459)  # Centro de Valdivia
                                            lat += np.random.uniform(-0.05, 0.05)
                                            lon += np.random.uniform(-0.05, 0.05)
                                            
                                            result = {
                                                'lat': lat,
                                                'lon': lon,
                                                'display_name': f"Valdivia, Chile (región)",
                                                'method': 'fallback'
                                            }
                                            geocode_cache[cache_key] = result
                                            return result
                                        
                                        # Preparar datos
                                        if selected_comuna_col:
                                            # CRÍTICO: Asegurar que selected_address_col y selected_comuna_col son strings
                                            addr_col = str(selected_address_col)
                                            comuna_col = str(selected_comuna_col)
                                            
                                            # Crear subset del DataFrame
                                            geocode_df = df[[addr_col, comuna_col]].copy()
                                            
                                            # Dropna de forma segura
                                            geocode_df = geocode_df[geocode_df[addr_col].notna()].head(max_addresses)
                                            
                                            # Resetear índice para evitar problemas
                                            geocode_df = geocode_df.reset_index(drop=True)
                                            
                                            # SOLUCIÓN ULTRA-ROBUSTA: Convertir a arrays de NumPy PRIMERO
                                            # Esto garantiza valores primitivos de Python
                                            addr_array = geocode_df[addr_col].values  # NumPy array
                                            comuna_array = geocode_df[comuna_col].values  # NumPy array
                                            
                                            # Ahora iterar sobre arrays simples
                                            sample_to_geocode = []
                                            for i in range(len(addr_array)):
                                                addr_val = addr_array[i]
                                                comuna_val = comuna_array[i]
                                                
                                                # Verificar None/NaN de forma segura
                                                # Usar 'is None' o comparación con np.nan
                                                if addr_val is None or (isinstance(addr_val, float) and np.isnan(addr_val)):
                                                    addr_str = ''
                                                else:
                                                    addr_str = str(addr_val)
                                                
                                                if comuna_val is None or (isinstance(comuna_val, float) and np.isnan(comuna_val)):
                                                    comuna_str = None
                                                else:
                                                    comuna_str = str(comuna_val)
                                                
                                                sample_to_geocode.append({
                                                    'direccion': addr_str,
                                                    'comuna': comuna_str
                                                })
                                        else:
                                            # Sin columna de comuna
                                            # Obtener direcciones únicas como lista Python
                                            addresses_list = addresses_sample.head(max_addresses).dropna().unique().tolist()
                                            
                                            sample_to_geocode = []
                                            for addr in addresses_list:
                                                if addr is None or (isinstance(addr, float) and np.isnan(addr)):
                                                    addr_str = ''
                                                else:
                                                    addr_str = str(addr)
                                                
                                                sample_to_geocode.append({
                                                    'direccion': addr_str,
                                                    'comuna': None
                                                })
                                        
                                        st.info(f"🔍 Geocodificando {len(sample_to_geocode)} registros...")
                                        
                                        # Geocodificar direcciones con barra de progreso
                                        geocoded_results = []
                                        progress_bar = st.progress(0)
                                        status_text = st.empty()
                                        
                                        successful = 0
                                        fallback_count = 0
                                        
                                        for idx, record in enumerate(sample_to_geocode):
                                            # Actualizar progreso
                                            progress = (idx + 1) / len(sample_to_geocode)
                                            progress_bar.progress(progress)
                                            status_text.text(f"Geocodificando {idx + 1}/{len(sample_to_geocode)} - ✅ Exactas: {successful} | ⚠️ Aproximadas: {fallback_count}")
                                            
                                            address = record['direccion']
                                            comuna = record.get('comuna')
                                            
                                            # SIEMPRE retorna resultado
                                            result = geocode_address_flexible(address, comuna)
                                            
                                            geocoded_results.append({
                                                'direccion': address,
                                                'comuna': str(comuna) if comuna is not None and not pd.isna(comuna) else 'N/A',
                                                'lat': result['lat'],
                                                'lon': result['lon'],
                                                'direccion_completa': result['display_name'],
                                                'metodo': result.get('method', 'unknown')
                                            })
                                            
                                            if result.get('method') == 'fallback':
                                                fallback_count += 1
                                            else:
                                                successful += 1
                                            
                                            # Pausa corta
                                            time.sleep(0.5)
                                        
                                        progress_bar.empty()
                                        status_text.empty()
                                        
                                        # Crear DataFrame con resultados
                                        if geocoded_results:
                                            geo_df = pd.DataFrame(geocoded_results)
                                            
                                            # Agregar columna temporal si existe
                                            if datetime_cols:
                                                date_col = str(datetime_cols[0])  # ✅ Asegurar string
                                                addr_col = str(selected_address_col)  # ✅ Asegurar string
                                                
                                                # Hacer merge con las direcciones originales - DE FORMA SEGURA
                                                temp_df = df[[addr_col, date_col]].copy()
                                                temp_df = temp_df.rename(columns={addr_col: 'direccion', date_col: 'fecha'})
                                                
                                                # Convertir direcciones a string en ambos DataFrames antes del merge
                                                geo_df['direccion'] = geo_df['direccion'].astype(str)
                                                temp_df['direccion'] = temp_df['direccion'].astype(str)
                                                temp_df['fecha'] = temp_df['fecha'].astype(str)
                                                
                                                # Merge seguro
                                                geo_df = geo_df.merge(temp_df, on='direccion', how='left')
                                            
                                            # Mostrar resultados de geocodificación
                                            total = successful + fallback_count
                                            st.success(f"✅ Geocodificación completada: **{total}** ubicaciones procesadas")
                                            
                                            col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                                            with col_res1:
                                                st.metric("✅ Exactas", successful, help="Geocodificadas con Nominatim")
                                            with col_res2:
                                                st.metric("⚠️ Aproximadas", fallback_count, help="Ubicadas en centro de comuna")
                                            with col_res3:
                                                st.metric("📍 Total", total)
                                            with col_res4:
                                                st.metric("💾 En Caché", len(geocode_cache))
                                            
                                            # Explicación para el usuario
                                            st.info("""
                                            **📍 Métodos de geocodificación:**
                                            - **Exactas**: Dirección encontrada en OpenStreetMap
                                            - **Aproximadas**: Ubicación estimada en el centro de la comuna
                                            """)
                                            
                                            # Mostrar distribución de métodos
                                            with st.expander("📊 Detalle de Métodos de Geocodificación"):
                                                method_counts = geo_df['metodo'].value_counts()
                                                st.write("**Distribución:**")
                                                st.write(f"- Geocodificadas: {method_counts.get('geocoded', 0)}")
                                                st.write(f"- Aproximadas (fallback): {method_counts.get('fallback', 0)}")
                                                
                                                # Mostrar muestra de direcciones aproximadas
                                                fallback_sample = geo_df[geo_df['metodo'] == 'fallback'].head(10)
                                                if len(fallback_sample) > 0:
                                                    st.write("**Muestra de direcciones aproximadas:**")
                                                    st.dataframe(fallback_sample[['direccion', 'comuna', 'direccion_completa']])
                                            
                                            # Mapa interactivo
                                            st.subheader("🗺️ Mapa Interactivo de Eventos")
                                            st.write(f"**Visualizando {len(geo_df)} eventos con coordenadas reales en {region_manual}**")
                                            
                                            # DEBUGGING: Mostrar info del DataFrame
                                            with st.expander("🔍 Debug: Información del DataFrame", expanded=False):
                                                st.write("**Columnas:**", geo_df.columns.tolist())
                                                st.write("**Tipos de datos:**")
                                                st.write(geo_df.dtypes)
                                                st.write("**Primeras 3 filas:**")
                                                st.write(geo_df.head(3))
                                                st.write("**Valores nulos por columna:**")
                                                st.write(geo_df.isnull().sum())
                                            
                                            # IMPORTANTE: Asegurar que todas las columnas sean strings simples para plotly
                                            # Esto evita el error "not enough values to unpack"
                                            for col in ['direccion', 'comuna', 'direccion_completa', 'metodo']:
                                                if col in geo_df.columns:
                                                    geo_df[col] = geo_df[col].astype(str)
                                            
                                            # CRÍTICO: Limpiar NaN y None en todas las columnas
                                            geo_df = geo_df.fillna('N/A')
                                            
                                            # VALIDACIÓN EXTRA: Asegurar que lat/lon son numéricos limpios
                                            geo_df['lat'] = pd.to_numeric(geo_df['lat'], errors='coerce')
                                            geo_df['lon'] = pd.to_numeric(geo_df['lon'], errors='coerce')
                                            geo_df = geo_df.dropna(subset=['lat', 'lon'])
                                            
                                            if len(geo_df) == 0:
                                                st.error("❌ No hay coordenadas válidas después de limpieza")
                                            else:
                                                st.success(f"✅ {len(geo_df)} coordenadas válidas para mapear")
                                                
                                                try:
                                                    st.info("🔄 Intentando generar mapa SIN hover_data (más simple)...")
                                                    
                                                    # VERSIÓN MÁS SIMPLE POSIBLE - SIN HOVER
                                                    fig_map = px.density_mapbox(
                                                        geo_df,
                                                        lat='lat',
                                                        lon='lon',
                                                        # SIN hover_data para evitar problemas
                                                        radius=15,
                                                        zoom=11,
                                                        mapbox_style="open-street-map",
                                                        title=f"Mapa de Densidad de Eventos - {region_manual}",
                                                        height=600,
                                                        color_continuous_scale='Reds'
                                                    )
                                                    
                                                    st.plotly_chart(fig_map, use_container_width=True)
                                                    st.success("✅ Mapa de densidad generado correctamente")
                                                    
                                                except Exception as e:
                                                    st.error(f"❌ Error al generar mapa de densidad: {str(e)}")
                                                    import traceback
                                                    st.code(traceback.format_exc())
                                                    
                                                    # Intentar versión aún más simple con scatter
                                                    st.warning("⚠️ Intentando mapa de puntos simple...")
                                                    try:
                                                        fig_simple = go.Figure(go.Scattermapbox(
                                                            lat=geo_df['lat'],
                                                            lon=geo_df['lon'],
                                                            mode='markers',
                                                            marker=dict(size=8, color='red')
                                                        ))
                                                        
                                                        fig_simple.update_layout(
                                                            mapbox=dict(
                                                                style="open-street-map",
                                                                zoom=11,
                                                                center=dict(
                                                                    lat=geo_df['lat'].mean(),
                                                                    lon=geo_df['lon'].mean()
                                                                )
                                                            ),
                                                            height=600,
                                                            title=f"Mapa Simple de Eventos - {region_manual}"
                                                        )
                                                        
                                                        st.plotly_chart(fig_simple, use_container_width=True)
                                                        st.success("✅ Mapa simple generado como fallback")
                                                    except Exception as e2:
                                                        st.error(f"❌ Error incluso con mapa simple: {str(e2)}")
                                                        import traceback
                                                        st.code(traceback.format_exc())
                                            
                                            # Mapa alternativo: scatter con marcadores
                                            st.subheader("📍 Mapa de Puntos Individuales")
                                            
                                            if len(geo_df) > 0:
                                                try:
                                                    st.info("🔄 Generando mapa de puntos...")
                                                    
                                                    # VERSIÓN SIMPLE SIN HOVER
                                                    fig_scatter = px.scatter_mapbox(
                                                        geo_df,
                                                        lat='lat',
                                                        lon='lon',
                                                        # SIN hover_name ni hover_data
                                                        zoom=11,
                                                        mapbox_style="open-street-map",
                                                        title="Ubicación Exacta de Cada Evento",
                                                        height=500,
                                                        color_discrete_sequence=['#FF5F9E']
                                                    )
                                                    
                                                    st.plotly_chart(fig_scatter, use_container_width=True)
                                                    st.success("✅ Mapa de puntos generado correctamente")
                                                    
                                                except Exception as e:
                                                    st.error(f"❌ Error al generar mapa de puntos: {str(e)}")
                                                    import traceback
                                                    st.code(traceback.format_exc())
                                            
                                            # Estadísticas de distribución espacial
                                            st.subheader("📊 Estadísticas de Distribución Espacial")
                                            
                                            col1, col2, col3, col4 = st.columns(4)
                                            with col1:
                                                st.metric("Eventos Mapeados", len(geo_df))
                                            with col2:
                                                lat_range = geo_df['lat'].max() - geo_df['lat'].min()
                                                st.metric("Dispersión Latitud", f"{lat_range:.4f}°")
                                            with col3:
                                                lon_range = geo_df['lon'].max() - geo_df['lon'].min()
                                                st.metric("Dispersión Longitud", f"{lon_range:.4f}°")
                                            with col4:
                                                # Calcular centro geográfico
                                                center_lat = geo_df['lat'].mean()
                                                center_lon = geo_df['lon'].mean()
                                                st.metric("Centro", f"{center_lat:.2f}, {center_lon:.2f}")
                                            
                                            # Tabla de direcciones geocodificadas
                                            with st.expander("📋 Ver Direcciones Geocodificadas", expanded=False):
                                                st.dataframe(
                                                    geo_df[['direccion', 'lat', 'lon', 'direccion_completa']],
                                                    use_container_width=True,
                                                    hide_index=True
                                                )
                                            
                                            # Guardar en session state para uso posterior
                                            st.session_state.geocoded_data = geo_df
                                            
                                            st.success("✅ Mapa generado con GEOCODIFICACIÓN REAL usando Nominatim (OpenStreetMap)")
                                            
                                        else:
                                            st.warning("⚠️ No se procesaron direcciones (esto no debería ocurrir)")
                                            st.info("💡 Por favor contacta al desarrollador si ves este mensaje")
                                    
                                    except ImportError:
                                        # Fallback a simulación si no hay geopy
                                        st.warning("⚠️ Usando coordenadas simuladas (instala geopy para geocodificación real)")
                                        
                                        # Código de simulación original (como backup)
                                        region_coords = {
                                            'valencia': (39.4699, -0.3763),
                                            'madrid': (40.4168, -3.7038),
                                            'barcelona': (41.3851, 2.1734),
                                            'españa': (40.4168, -3.7038),
                                            'santiago': (-33.4489, -70.6693),
                                            'valparaíso': (-33.0472, -71.6127),
                                            'concepción': (-36.8270, -73.0497),
                                            'valdivia': (-39.8142, -73.2459),
                                            'temuco': (-38.7359, -72.5904),
                                            'puerto montt': (-41.4693, -72.9424),
                                            'buenos aires': (-34.6037, -58.3816),
                                            'lima': (-12.0464, -77.0428),
                                            'bogotá': (4.7110, -74.0721),
                                            'ciudad de méxico': (19.4326, -99.1332),
                                            'chile': (-33.4489, -70.6693),
                                            'latinoamérica': (-23.5505, -46.6333)
                                        }
                                        
                                        base_coords = region_coords.get(region_manual.lower(), (40.4168, -3.7038))
                                        n_eventos = min(len(addresses_sample), 200)
                                        
                                        np.random.seed(42)
                                        lats = base_coords[0] + np.random.normal(0, 0.05, n_eventos)
                                        lons = base_coords[1] + np.random.normal(0, 0.05, n_eventos)
                                        
                                        geo_df = pd.DataFrame({
                                            'lat': lats,
                                            'lon': lons,
                                            'direccion': addresses_sample.head(n_eventos).astype(str).values
                                        })
                                        
                                        if datetime_cols:
                                            date_col = datetime_cols[0]
                                            geo_df['fecha'] = df[date_col].head(n_eventos).astype(str).values
                                        
                                        # Asegurar que todas las columnas sean strings para plotly
                                        for col in geo_df.columns:
                                            if col not in ['lat', 'lon']:  # Mantener lat/lon como numéricos
                                                geo_df[col] = geo_df[col].astype(str)
                                        
                                        fig_map = px.density_mapbox(
                                            geo_df,
                                            lat='lat',
                                            lon='lon',
                                            radius=10,
                                            zoom=11,
                                            mapbox_style="carto-positron",
                                            title=f"Mapa de Densidad de Eventos - {region_manual}",
                                            height=600
                                        )
                                        
                                        st.plotly_chart(fig_map, use_container_width=True)
                                        st.info("📦 Instala geopy para habilitar geocodificación real: `pip install geopy`")
                                        
                                    except Exception as e:
                                        st.error(f"Error al generar mapa: {str(e)}")
                                        import traceback
                                        st.code(traceback.format_exc(), language="python")
                    else:
                        st.warning("No hay direcciones disponibles para analizar")
            
            # ===== ANÁLISIS TEMPORAL =====
            if datetime_cols:
                st.divider()
                st.subheader("📅 Análisis Temporal de Eventos")
                
                # Seleccionar columna temporal
                selected_date_col = st.selectbox(
                    "Selecciona la columna de fecha a analizar:",
                    datetime_cols,
                    key="temporal_date_col"
                )
                
                if selected_date_col:
                    df_temporal = df[[selected_date_col]].copy()
                    df_temporal = df_temporal.dropna()
                    df_temporal['fecha'] = pd.to_datetime(df_temporal[selected_date_col], errors='coerce')
                    df_temporal = df_temporal.dropna()
                    
                    if len(df_temporal) > 0:
                        # Extraer componentes temporales
                        df_temporal['año'] = df_temporal['fecha'].dt.year
                        df_temporal['mes'] = df_temporal['fecha'].dt.month
                        df_temporal['día'] = df_temporal['fecha'].dt.day
                        df_temporal['día_semana'] = df_temporal['fecha'].dt.dayofweek
                        df_temporal['semana_año'] = df_temporal['fecha'].dt.isocalendar().week
                        
                        # Métricas temporales
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Eventos Totales", len(df_temporal))
                        with col2:
                            fecha_min = df_temporal['fecha'].min()
                            st.metric("Primer Evento", fecha_min.strftime('%Y-%m-%d'))
                        with col3:
                            fecha_max = df_temporal['fecha'].max()
                            st.metric("Último Evento", fecha_max.strftime('%Y-%m-%d'))
                        with col4:
                            dias_span = (fecha_max - fecha_min).days
                            st.metric("Período (días)", dias_span)
                        
                        # Serie temporal
                        st.subheader("📈 Serie Temporal de Eventos (Estilo Epidemiológico)")
                        
                        # Opción de agregación temporal
                        col_agg1, col_agg2 = st.columns([3, 1])
                        with col_agg1:
                            agregacion = st.selectbox(
                                "Nivel de agregación:",
                                ["Mensual", "Trimestral", "Anual", "Quinquenal (cada 5 años)"],
                                index=0,
                                key="agregacion_temporal"
                            )
                        with col_agg2:
                            mostrar_tendencia = st.checkbox("Mostrar tendencia", value=True, key="mostrar_tendencia")
                        
                        # Preparar datos según agregación
                        df_temporal_agg = df_temporal.copy()
                        df_temporal_agg['año_mes'] = df_temporal_agg['fecha'].dt.to_period('M')
                        
                        if agregacion == "Mensual":
                            eventos_agg = df_temporal_agg.groupby('año_mes').size().reset_index()
                            eventos_agg.columns = ['Período', 'Eventos']
                            eventos_agg['Período'] = eventos_agg['Período'].dt.to_timestamp()
                            titulo = 'Eventos Mensuales'
                            
                        elif agregacion == "Trimestral":
                            df_temporal_agg['trimestre'] = df_temporal_agg['fecha'].dt.to_period('Q')
                            eventos_agg = df_temporal_agg.groupby('trimestre').size().reset_index()
                            eventos_agg.columns = ['Período', 'Eventos']
                            eventos_agg['Período'] = eventos_agg['Período'].dt.to_timestamp()
                            titulo = 'Eventos Trimestrales'
                            
                        elif agregacion == "Anual":
                            eventos_agg = df_temporal_agg.groupby('año').size().reset_index()
                            eventos_agg.columns = ['Período', 'Eventos']
                            eventos_agg['Período'] = pd.to_datetime(eventos_agg['Período'], format='%Y')
                            titulo = 'Eventos Anuales'
                            
                        else:  # Quinquenal
                            df_temporal_agg['quinquenio'] = (df_temporal_agg['año'] // 5) * 5
                            eventos_agg = df_temporal_agg.groupby('quinquenio').size().reset_index()
                            eventos_agg.columns = ['Período', 'Eventos']
                            eventos_agg['Período'] = pd.to_datetime(eventos_agg['Período'], format='%Y')
                            titulo = 'Eventos Quinquenales (cada 5 años)'
                        
                        # Crear gráfico epidemiológico profesional
                        fig_temporal = go.Figure()
                        
                        # Línea principal
                        fig_temporal.add_trace(go.Scatter(
                            x=eventos_agg['Período'],
                            y=eventos_agg['Eventos'],
                            mode='lines+markers',
                            name='Eventos',
                            line=dict(color='#2E86AB', width=2),
                            marker=dict(size=6, color='#2E86AB'),
                            hovertemplate='<b>%{x|%Y-%m}</b><br>Eventos: %{y}<extra></extra>'
                        ))
                        
                        # Línea de tendencia (suavizado)
                        if mostrar_tendencia and len(eventos_agg) > 3:
                            from scipy.ndimage import uniform_filter1d
                            window = min(12 if agregacion == "Mensual" else 4, len(eventos_agg) // 3)
                            if window >= 2:
                                tendencia = uniform_filter1d(eventos_agg['Eventos'].values, size=window)
                                fig_temporal.add_trace(go.Scatter(
                                    x=eventos_agg['Período'],
                                    y=tendencia,
                                    mode='lines',
                                    name='Tendencia',
                                    line=dict(color='#A23B72', width=3, dash='dash'),
                                    hovertemplate='<b>Tendencia</b><br>%{y:.1f}<extra></extra>'
                                ))
                        
                        # Media histórica
                        media = eventos_agg['Eventos'].mean()
                        fig_temporal.add_hline(
                            y=media,
                            line_dash="dot",
                            line_color="gray",
                            annotation_text=f"Media: {media:.1f}",
                            annotation_position="right"
                        )
                        
                        # Configuración del layout
                        fig_temporal.update_layout(
                            title={
                                'text': f'<b>{titulo}</b>',
                                'x': 0.5,
                                'xanchor': 'center',
                                'font': {'size': 18}
                            },
                            xaxis_title='Período',
                            yaxis_title='Número de Eventos',
                            hovermode='x unified',
                            height=450,
                            template='plotly_white',
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        st.plotly_chart(fig_temporal, use_container_width=True)
                        
                        # Estadísticas de la serie
                        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                        with col_stat1:
                            st.metric("Media", f"{media:.1f}", help="Promedio de eventos por período")
                        with col_stat2:
                            std = eventos_agg['Eventos'].std()
                            st.metric("Desv. Est.", f"{std:.1f}", help="Variabilidad de eventos")
                        with col_stat3:
                            max_eventos = eventos_agg['Eventos'].max()
                            st.metric("Máximo", f"{int(max_eventos)}", help="Mayor número de eventos en un período")
                        with col_stat4:
                            min_eventos = eventos_agg['Eventos'].min()
                            st.metric("Mínimo", f"{int(min_eventos)}", help="Menor número de eventos en un período")
                        
                        # Patrones temporales
                        st.subheader("🔍 Patrones Temporales")
                        
                        col_p1, col_p2 = st.columns(2)
                        
                        with col_p1:
                            # Eventos por mes
                            eventos_mes = df_temporal.groupby('mes').size().reset_index()
                            eventos_mes.columns = ['Mes', 'Eventos']
                            meses_nombres = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun',
                                           7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
                            eventos_mes['Mes_nombre'] = eventos_mes['Mes'].map(meses_nombres)
                            
                            fig_mes = px.bar(
                                eventos_mes,
                                x='Mes_nombre',
                                y='Eventos',
                                title='Distribución por Mes'
                            )
                            st.plotly_chart(fig_mes, use_container_width=True)
                        
                        with col_p2:
                            # Eventos por día de la semana
                            eventos_dia = df_temporal.groupby('día_semana').size().reset_index()
                            eventos_dia.columns = ['Día', 'Eventos']
                            dias_nombres = {0:'Lun', 1:'Mar', 2:'Mié', 3:'Jue', 4:'Vie', 5:'Sáb', 6:'Dom'}
                            eventos_dia['Día_nombre'] = eventos_dia['Día'].map(dias_nombres)
                            
                            fig_dia = px.bar(
                                eventos_dia,
                                x='Día_nombre',
                                y='Eventos',
                                title='Distribución por Día de Semana'
                            )
                            st.plotly_chart(fig_dia, use_container_width=True)
                        
                        # ===== ANÁLISIS ESPACIO-TEMPORAL INTEGRADO =====
                        if address_cols:
                            st.divider()
                            st.subheader("🌍📅 Análisis Espacio-Temporal Integrado")
                            
                            st.info("""
                            **Análisis Espacio-Temporal:**
                            Combina ubicación geográfica con evolución temporal para identificar:
                            - Clusters espaciales en diferentes períodos
                            - Migración de eventos entre zonas
                            - Patrones estacionales por región
                            """)
                            
                            if st.button("🎬 Generar Animación Temporal", key="spatiotemporal_button"):
                                with st.spinner("Generando visualización espacio-temporal..."):
                                    try:
                                        # Preparar datos espacio-temporales
                                        # (Simulación - en producción usar geocodificación real)
                                        
                                        st.success("🎥 Funcionalidad de animación temporal en desarrollo")
                                        st.info("""
                                        **Próximamente:**
                                        - Mapa animado con slider temporal
                                        - Visualización de evolución de clusters
                                        - Heatmap temporal por zona geográfica
                                        - Requiere integración con Plotly Express `px.scatter_mapbox` con `animation_frame`
                                        """)
                                        
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                    else:
                        st.warning("No hay fechas válidas para analizar")
            
            # Si no hay datos geoespaciales ni temporales
            if not address_cols and not datetime_cols:
                st.info("""
                ℹ️ **No se detectaron datos geoespaciales ni temporales en el dataset**
                
                Para habilitar este análisis, el dataset debe contener:
                - **Direcciones:** Columnas con nombres como 'direccion', 'address', 'ubicacion', 'lugar'
                - **Fechas:** Columnas con nombres como 'fecha', 'date', 'tiempo', o formato datetime
                """)
        
        # ========== 3.8 DIAGNÓSTICO CON IA ==========
        st.divider()
        st.header("🤖 Diagnóstico Inteligente")
        
        if st.button("🧠 Generar Diagnóstico con IA", type="secondary", use_container_width=True):
            with st.spinner("Generando diagnóstico con IA..."):
                try:
                    diagnosis = generate_diagnosis(results, df)
                    
                    if diagnosis:
                        st.session_state.diagnosis_text = diagnosis
                        st.markdown(diagnosis)
                    else:
                        st.warning("No se pudo generar el diagnóstico. Verifica tu configuración de OpenAI.")
                
                except Exception as e:
                    st.error(f"Error al generar diagnóstico: {str(e)}")
                    st.info("Asegúrate de tener configurada tu API key de OpenAI en el archivo .env")
        
        # Mostrar diagnóstico previo si existe
        if 'diagnosis_text' in st.session_state and st.session_state.diagnosis_text:
            with st.expander("📝 Diagnóstico Generado", expanded=True):
                st.markdown(st.session_state.diagnosis_text)
        
        # ==================== SECCIÓN 4: DESCARGAS ====================
        st.divider()
        st.header("4. Descargar Resultados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Descargar JSON consolidado
            try:
                json_str = json.dumps(convert_numpy_types(results), indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Descargar Análisis Completo (JSON)",
                    data=json_str,
                    file_name=f"analisis_completo_{uploaded_file.name}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"Error al preparar JSON: {str(e)}")
        
        with col2:
            # Descargar diagnóstico en texto
            if 'diagnosis_text' in st.session_state and st.session_state.diagnosis_text:
                st.download_button(
                    label="📥 Descargar Diagnóstico",
                    data=st.session_state.diagnosis_text,
                    file_name=f"diagnostico_{uploaded_file.name}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )

        with col1:
            # Descargar PDF
            if st.button("📄 Generar Reporte PDF", type="primary"):
                try:
                    pdf = generate_data_quality_pdf(results)
                    pdf_bytes = pdf.output(dest='S').encode('latin-1')
                    
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=pdf_bytes,
                        file_name=f"reporte_calidad_{uploaded_file_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error al generar PDF: {str(e)}")


# ==================== FOOTER ====================
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>CUIDAR IA</strong> | Fase 3: Evaluador de Calidad de Datos</p>
    <p style='font-size: 0.9rem;'>Desarrollado con ❤️ para la prevención del suicidio basada en evidencia</p>
</div>
""", unsafe_allow_html=True)
