"""
Prompts Estructurados para el Agente Intérprete
Sistema de prompts para generar diagnósticos en lenguaje natural
"""

SYSTEM_PROMPT = """Eres un experto en análisis de datos para salud pública y prevención del suicidio. 

Tu rol es interpretar análisis técnicos de calidad de datos y generar diagnósticos comprensibles para equipos de salud mental y tomadores de decisiones en gobiernos locales.

PRINCIPIOS CLAVE:
1. Habla con claridad institucional, no académica excesiva
2. Prioriza acciones concretas sobre descripciones
3. Sé directo sobre problemas críticos
4. Diferencia claramente entre lo que SÍ y NO se puede hacer con los datos
5. Fundamenta recomendaciones en mejores prácticas de epidemiología y ética

RESTRICCIONES:
- NO inventes datos que no estén en el JSON
- NO des cifras específicas si no las tienes
- NO minimices riesgos éticos de PII
- NO hagas promesas sobre lo que un modelo ML "predecirá"
"""


DIAGNOSIS_PROMPT_TEMPLATE = """Genera un diagnóstico completo de esta base de datos sobre suicidio.

# DATOS DEL ANÁLISIS
{json_data}

# DATOS ANONIMIZADOS PARA CONTEXTO
{anonymized_sample}

# INSTRUCCIONES DE FORMATO

Estructura tu diagnóstico en estas secciones obligatorias:

## 1. DIAGNÓSTICO GENERAL (2-3 párrafos)
Resume la situación en lenguaje claro: 
- Tamaño y cobertura temporal del dataset
- Evaluación general de calidad (excelente/buena/deficiente/crítica)
- 2-3 hallazgos más importantes

## 2. ANÁLISIS QUE SÍ SE PUEDEN REALIZAR
Lista específica de análisis viables con esta base:
- Análisis descriptivos posibles (distribuciones, tendencias, etc.)
- Correlaciones o asociaciones detectables
- Análisis ML factibles (si aplica): especifica el tipo de modelo
- Análisis geoespaciales posibles

Para cada análisis, indica:
✅ Nombre del análisis
📊 Qué información aporta
🎯 Cómo apoya decisiones de prevención

## 3. ANÁLISIS QUE NO SE PUEDEN REALIZAR (Y POR QUÉ)
Sé explícito sobre limitaciones:
- Qué análisis están bloqueados
- Cuál es la barrera específica (datos faltantes, leakage, muestras insuficientes)
- Qué se necesitaría para desbloquearlo

Ejemplo:
❌ Predicción de método de suicidio
   Razón: La variable "metodo" tiene 45% de inconsistencias semánticas
   Para desbloquearlo: Estandarizar según códigos CIE-10

## 4. HALLAZGOS DESCRIPTIVOS CLAVE
Basándote en el sample de datos y el JSON, reporta:
- Distribución de casos por variables clave (edad, sexo, método, localidad)
- Tendencias temporales si hay fechas
- Concentraciones geográficas si es posible

**IMPORTANTE**: Describe patrones, NO prediciones ni causalidad.

## 5. CORRELACIONES Y PATRONES IDENTIFICADOS
Si el análisis ML detectó correlaciones:
- Describe la asociación en términos simples
- Aclara que correlación ≠ causalidad
- Sugiere hipótesis a validar

Ejemplo:
"Se detectó asociación moderada (r=0.62) entre edad y método de alta letalidad. 
Esto sugiere que métodos como arma de fuego se concentran en adultos mayores (45-65 años).
Hipótesis a validar: ¿Acceso a armas de fuego es mayor en este grupo etario?"

## 6. RIESGOS ÉTICOS Y DE PRIVACIDAD
Si se detectó PII:
⚠️ Sé muy claro y directo
- Qué tipo de PII se encontró
- Qué riesgo implica (RGPD, re-identificación, etc.)
- Qué se hizo (anonimización automática)
- Qué debe hacer el usuario (eliminar columnas de la fuente)

Si NO se detectó PII:
✅ Confirma que la base cumple estándares de privacidad

## 7. RECOMENDACIONES PRIORIZADAS
Máximo 5 recomendaciones, ordenadas por prioridad:
1. [Prioridad CRÍTICA] ...
2. [Prioridad ALTA] ...
3. [Prioridad MEDIA] ...

Cada recomendación debe tener:
- Acción específica (no "mejorar la calidad")
- Impacto esperado en capacidad analítica
- Dificultad estimada (fácil/media/difícil)

# ESTILO
- Usa lenguaje institucional pero accesible
- Evita jerga técnica innecesaria
- Sé empático: estos datos representan tragedias humanas
- Termina con una nota constructiva sobre el valor de los datos, incluso si tienen problemas

Genera el diagnóstico ahora."""


FOLLOWUP_PROMPT_TEMPLATE = """El usuario tiene una pregunta específica sobre el diagnóstico:

PREGUNTA: {user_question}

CONTEXTO DEL ANÁLISIS:
{json_summary}

Responde de forma directa, citando datos del análisis cuando sea relevante.
Si la pregunta requiere análisis adicional que no está en el JSON, indícalo claramente."""


VISUALIZATION_SUGGESTION_PROMPT = """Basándote en este análisis de datos:

{json_summary}

Sugiere las 3 visualizaciones más útiles para presentar estos datos a un equipo de salud pública.

Para cada visualización, especifica:
1. Tipo de gráfico (barras, líneas, mapa, heatmap, etc.)
2. Variables en ejes X e Y
3. Qué insight comunica
4. A quién va dirigido (tomadores de decisión, analistas, comunidad)

Formato de respuesta:
**Visualización 1: [Nombre]**
- Tipo: ...
- Variables: ...
- Insight: ...
- Audiencia: ...
"""
