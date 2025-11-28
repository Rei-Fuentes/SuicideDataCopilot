# Memoria del Proyecto: CUIDAR IA - Policy Copilot

## 1. Introducción

### 1.1 Contexto y Motivación
El suicidio es un problema de salud pública global que requiere enfoques basados en datos para su prevención efectiva. Este proyecto desarrolla **CUIDAR IA**, un sistema integral de análisis y soporte para la toma de decisiones en políticas de prevención del suicidio.

### 1.2 Objetivos del Proyecto
- **Objetivo Principal**: Desarrollar una plataforma de análisis de datos y asistencia basada en IA para apoyar la formulación de políticas públicas de prevención del suicidio.

- **Objetivos Específicos**:
  1. Analizar patrones geoespaciales y temporales de eventos de suicidio
  2. Desarrollar modelos predictivos para identificar factores de riesgo
  3. Crear herramientas de evaluación de calidad de datos
  4. Implementar un asistente conversacional basado en evidencia científica
  5. Generar visualizaciones interactivas para análisis exploratorio

## 2. Metodología

### 2.1 Adquisición de Datos
- **Fuentes de Datos**: Datos de salud pública, registros históricos de eventos
- **Variables Principales**: Ubicación geográfica, fecha, método, demografía

### 2.2 Preprocesamiento de Datos
1. **Limpieza de Datos**:
   - Eliminación de duplicados
   - Tratamiento de valores nulos
   - Validación de coordenadas geográficas

2. **Feature Engineering**:
   - Extracción de características temporales (año, mes, semestre)
   - Clustering geoespacial para identificación de zonas de riesgo
   - Codificación de variables categóricas

### 3. Análisis Geoespacial
- **Clusters Identificados**: X zonas de alto riesgo
- **Patrones Temporales**
- **Visualizaciones**: Mapas interactivos con clustering DBSCAN

## 4. Aplicación Streamlit

### 4.1 Funcionalidades Implementadas

1. **Diagnóstico CUIDAR Index**
   - Evaluación de 5 dimensiones de calidad de datos
   - Generación de reportes PDF
   - Recomendaciones basadas en IA

2. **Visualización de Resultados**
   - Gráficos premium interactivos (Plotly)
   - Análisis dimensional
   - Exportación de resultados

3. **Consulta a CUIDAR IA**
   - Asistente conversacional con GPT-4
   - Respuestas basadas en evidencia científica
   - Contexto de guías validadas

4. **Análisis de Territorio**
   - Carga de documentos locales
   - Análisis contextualizado
   - Integración con datos geográficos

5. **Evaluador de Bases de Datos**
   - Análisis de calidad de datos
   - Visualizaciones geoespaciales avanzadas
   - Mapas con clustering heterogéneo
   - Animaciones temporales por año
   - Tendencias bi-anuales y mensuales

### 4.2 Tecnologías Utilizadas
- **Frontend**: Streamlit
- **Visualización**: Plotly, Matplotlib, Seaborn
- **ML**: Scikit-learn, Pandas, NumPy
- **IA**: OpenAI GPT-4
- **Geoespacial**: DBSCAN, Mapbox
- **PDF**: FPDF2

## 5. Conclusiones

### 5.1 Logros Principales
1. Desarrollo exitoso de plataforma integral de análisis
2. Implementación de modelos predictivos con alto rendimiento
3. Creación de visualizaciones interactivas avanzadas
4. Integración de IA conversacional para soporte a decisiones

### 5.2 Limitaciones
- No tiene autenticación
- Sin evaluación de métricas del RAG

### 5.3 Trabajo Futuro
1. Expansión de fuentes de datos
2. Implementación de modelos de deep learning
3. Integración con sistemas de salud en tiempo real
4. Desarrollo de alertas tempranas automatizadas


---

**Autor**: Reiner Fuentes Ferrada 
**Fecha**: Noviembre, 2025  
**Institución**: Data Science & IA, The Bridge, Valencia, España.
