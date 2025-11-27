# CUIDAR IA - Policy Copilot

Sistema Integral de Análisis y Soporte para Políticas de Prevención del Suicidio

Autor: Reiner Fuentes Ferrada  
Fecha: Noviembre 2025

## Descripción

CUIDAR IA es una plataforma avanzada que he desarrollado para el análisis de datos y asistencia basada en IA con el objetivo de apoyar la formulación de políticas públicas de prevención del suicidio. El sistema ofrece:

- Diagnóstico de Calidad de Datos mediante el CUIDAR Index
- Análisis Geoespacial Avanzado con clustering y animaciones temporales
- Asistente IA Conversacional basado en evidencia científica
- Visualizaciones Interactivas premium con Plotly
- Generación de Reportes PDF automáticos
- Evaluación de Bases de Datos con métricas de calidad

## Estructura del Proyecto

```
SuicideDataCopilot/
├── data/
│   ├── raw/                    # Datos originales sin procesar
│   └── processed/              # Datos procesados y limpios
├── notebooks/
│   ├── 01_Fuentes.ipynb       # Adquisición y unión de datos
│   └── 02_LimpiezaEDA.ipynb   # Limpieza y análisis exploratorio
├── app_streamlit/
│   ├── app/                    # Código de la aplicación
│   │   ├── main.py            # Página principal
│   │   ├── pages/             # Páginas de la aplicación
│   │   ├── utils/             # Utilidades (styles, components, pdf)
│   │   └── core/              # Constantes y configuración
│   ├── config/                 # Archivos de configuración
│   ├── fase3_evaluator/        # Evaluador de bases de datos
│   ├── app.py                  # Punto de entrada principal
│   └── requirements.txt        # Dependencias
├── docs/
│   ├── memoria.md              # Memoria del proyecto
│   └── presentaciones/         # Presentaciones del proyecto
├── .env.example                # Ejemplo de variables de entorno
├── .gitignore                  # Archivos ignorados por git
└── README.md                   # Este archivo
```

## Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Cuenta de OpenAI con API key (para funcionalidades de IA)

### Pasos de Instalación

1. Clonar el repositorio
```bash
git clone https://github.com/reinerfuentes/SuicideDataCopilot.git
cd SuicideDataCopilot
```

2. Crear entorno virtual
```bash
python -m venv venv_cuidar
source venv_cuidar/bin/activate  # En Windows: venv_cuidar\Scripts\activate
```

3. Instalar dependencias
```bash
cd app_streamlit
pip install -r requirements.txt
```

4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env y agregar tu OPENAI_API_KEY
```

## Uso

### Ejecutar la Aplicación Streamlit

```bash
cd app_streamlit
streamlit run app.py
```

La aplicación se abrirá en http://localhost:8501

## Funcionalidades Principales

### 1. Diagnóstico CUIDAR Index
He implementado un sistema de evaluación de calidad de datos en 5 dimensiones:
- Completitud
- Precisión
- Actualidad
- Consistencia
- Formato

El sistema genera reportes PDF con diagnóstico y recomendaciones basadas en IA.

### 2. Análisis Geoespacial
He desarrollado visualizaciones avanzadas que incluyen:

**Mapa de Puntos por Año**
- Filtro interactivo para visualizar eventos por año específico
- Control de tamaño de puntos
- Estadísticas dinámicas por año seleccionado

**Animación Temporal**
- Evolución anual con clusters diferenciados por intensidad mediante colores
  - Azul: Baja intensidad
  - Naranja: Media intensidad
  - Rojo: Alta intensidad
  - Rojo intenso: Concentración crítica
- Control de velocidad de animación
- Slider temporal para navegación por años

**Análisis de Tendencias**
- Visualización configurable bi-anual (2 registros por año)
- Visualización mensual (12 registros por año)
- Gráficos interactivos con relleno y marcadores destacados

### 3. Asistente IA (CUIDAR IA)
He integrado un asistente conversacional que proporciona consultas basadas en:
- Evidencia científica
- Guías de la OMS
- Protocolos validados
- Contexto local

### 4. Evaluador de Bases de Datos
Sistema de análisis que incluye:
- Análisis de calidad de datos
- Detección automática de problemas
- Recomendaciones de mejora
- Exportación de resultados en PDF

### 5. Análisis de Territorio
- Carga de documentos locales
- Análisis contextualizado
- Integración con datos geográficos

## Tecnologías Utilizadas

He construido este proyecto utilizando:

**Backend y Análisis**
- Python 3.8+
- Pandas para manipulación de datos
- NumPy para cálculos numéricos
- Scikit-learn para clustering (DBSCAN)

**Frontend**
- Streamlit para la interfaz web

**Visualización**
- Plotly para gráficos interactivos
- Matplotlib y Seaborn para visualizaciones estáticas

**Inteligencia Artificial**
- OpenAI GPT-4 para asistente conversacional

**Geoespacial**
- DBSCAN para clustering geoespacial
- Mapbox para mapas interactivos

**Generación de Documentos**
- FPDF2 para generación de reportes PDF

**Otros**
- python-dotenv para gestión de variables de entorno
- PyYAML para archivos de configuración

## Datos

### Estructura de Datos Esperada
Los datos deben incluir al mínimo:
- Coordenadas geográficas (latitud, longitud)
- Fecha del evento
- Variables demográficas
- Método (si aplica)
- Ubicación descriptiva

### Formato
- CSV, Excel o formatos compatibles con Pandas
- Codificación UTF-8 recomendada
- Coordenadas en formato decimal

## Configuración de API Keys

1. Obtener API key de OpenAI en https://platform.openai.com/api-keys
2. Copiar .env.example a .env
3. Agregar tu API key:
```
OPENAI_API_KEY=sk-...
```

## Documentación Adicional

- Memoria del Proyecto: docs/memoria.md
- Notebooks: Carpeta notebooks/ con análisis detallados
- Presentaciones: Carpeta docs/ con presentaciones del proyecto

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (git checkout -b feature/AmazingFeature)
3. Commit tus cambios (git commit -m 'Add some AmazingFeature')
4. Push a la rama (git push origin feature/AmazingFeature)
5. Abre un Pull Request

## Consideraciones Éticas

Este proyecto maneja datos sensibles de salud pública. He implementado consideraciones para:
- Respetar la privacidad de los datos
- Cumplir con regulaciones locales de protección de datos
- Usar los insights para prevención y políticas públicas responsables
- Evitar discriminación o estigmatización

## Licencia

Este proyecto está bajo la Licencia MIT. Ver LICENSE para más detalles.

## Autor

Reiner Fuentes Ferrada  
Noviembre 2025

Desarrollador Principal del Proyecto CUIDAR IA

## Agradecimientos

Agradezco a las organizaciones de salud pública por los datos, a la comunidad de código abierto, y a los investigadores en prevención del suicidio cuyo trabajo ha informado este proyecto.

## Contacto

Para consultas sobre este proyecto, por favor contactar a través de los canales oficiales del repositorio.

---

Nota: Este proyecto es para fines de investigación y apoyo a políticas públicas. No sustituye el juicio profesional de expertos en salud mental.
