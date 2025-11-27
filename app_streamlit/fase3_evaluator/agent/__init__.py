"""
Agente Intérprete con LLM
Genera diagnósticos en lenguaje natural
"""

from .interpreter import (
    generate_diagnosis,
    ask_followup_question,
    suggest_visualizations
)
from .prompts import (
    SYSTEM_PROMPT,
    DIAGNOSIS_PROMPT_TEMPLATE,
    FOLLOWUP_PROMPT_TEMPLATE,
    VISUALIZATION_SUGGESTION_PROMPT
)

__all__ = [
    "generate_diagnosis",
    "ask_followup_question",
    "suggest_visualizations",
    "SYSTEM_PROMPT",
    "DIAGNOSIS_PROMPT_TEMPLATE",
    "FOLLOWUP_PROMPT_TEMPLATE",
    "VISUALIZATION_SUGGESTION_PROMPT"
]
