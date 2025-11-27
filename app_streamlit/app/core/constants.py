"""
CUIDAR IA - Constants
Centralized constants for the application logic.
"""

# Definición de dimensiones e ítems del CUIDAR Index
DIMENSIONES = {
    "Accesibilidad": {
        "descripcion": "Disponibilidad y facilidad de acceso a los datos sobre suicidio",
        "items": [
            "Existen datos locales sobre suicidio/intentos/autolesiones que pueden ser consultados por actores municipales relevantes.",
            "Los datos relevantes están disponibles en formatos reutilizables (CSV, API) o mediante solicitudes simples.",
            "El tiempo medio entre solicitud formal y entrega de datos es menor a 1 mes.",
            "Se puede acceder a datos provenientes de hospitales, policía y registros civiles desde una única solicitud o plataforma."
        ]
    },
    "Calidad": {
        "descripcion": "Consistencia, actualización y cobertura de los datos",
        "items": [
            "Los registros de eventos tienen >85% de campos clave (edad, método, localidad, fecha) completados.",
            "Existen protocolos escritos para estandarizar definiciones (qué es un intento, muerte por suicidio, autolesiones).",
            "Los datos se actualizan al menos mensualmente.",
            "Se realizan controles periódicos de calidad (comparación entre fuentes, auditorías) documentados."
        ]
    },
    "Interoperabilidad": {
        "descripcion": "Conexión entre sistemas y sectores",
        "items": [
            "Los sistemas usan estándares (códigos uniformes, formatos compartidos) que permiten enlace entre sectores.",
            "Hay capacidad técnica para enlazar casos entre policía, hospitales y registro civil.",
            "Existen acuerdos escritos para compartir datos entre salud, policía, educación y servicios sociales."
        ]
    },
    "Uso de Datos": {
        "descripcion": "Integración en decisiones y estrategias reales",
        "items": [
            "Se elaboran informes de análisis de muertes/intentos de suicidio al menos trimestralmente.",
            "Hay evidencia (actas, planes) de que los datos han informado decisiones o reasignación de recursos.",
            "Existen mecanismos locales para activar respuestas cuando los datos muestran un pico o cluster.",
            "Se evalúa el impacto de intervenciones basadas en datos (campañas, distribución de recursos)."
        ]
    },
    "Capacidad Analítica": {
        "descripcion": "Personal e infraestructura para análisis",
        "items": [
            "Hay personal asignado con formación en análisis de salud pública/epidemiología/estadística.",
            "Existen herramientas (dashboards, software estadístico, GIS) para análisis y visualización.",
            "Se ofrecen capacitaciones periódicas al personal sobre vigilancia de suicidio y análisis de datos.",
            "Hay presupuesto o recursos técnicos dedicados al mantenimiento del sistema y análisis."
        ]
    },
    "Gestión del Conocimiento": {
        "descripcion": "Aprendizaje institucional y retroalimentación de políticas",
        "items": [
            "El gobierno local utiliza investigación o evidencia generada por universidades u observatorios locales.",
            "Las universidades o centros de investigación tienen acceso a los datos locales (bajo convenios éticos).",
            "Existen mesas, comités o espacios formales donde se discutan resultados de investigaciones locales.",
            "Los resultados de investigaciones locales se difunden a la comunidad o autoridades."
        ]
    },
    "Ética y Gobernanza": {
        "descripcion": "Protección de datos, transparencia y participación",
        "items": [
            "Existen políticas y procedimientos para garantizar anonimato, consentimiento y seguridad de los datos.",
            "Se publican políticas de gobernanza de datos y se rinden cuentas públicamente sobre su uso.",
            "Se considera la voz de las personas afectadas (familias, sobrevivientes) en la definición de indicadores."
        ]
    }
}

# Escala Likert unificada
ESCALA = {
    1: "Ausente",
    2: "Muy incipiente",
    3: "Parcial",
    4: "Bueno",
    5: "Completo"
}

# Retroalimentación por nivel
FEEDBACK_TEMPLATES = {
    1: "Esta capacidad está ausente. Recomendamos establecer registros básicos, responsables y protocolos mínimos lo antes posible.",
    2: "Hay avances iniciales pero fragmentados. Priorizar estandarización de formatos y formación básica del equipo.",
    3: "Capacidades moderadas. Implementar controles de calidad y mecanismos regulares de revisión para consolidar procesos.",
    4: "Fuerte desarrollo operativo. Potenciar interoperabilidad y compartir aprendizajes con otros equipos o instituciones.",
    5: "Estructura consolidada. Considerar monitoreo avanzado y documentar como práctica recomendada para replicar."
}
