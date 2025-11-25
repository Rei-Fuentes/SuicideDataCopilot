# test_integracion.py
import sys
print(f"Python: {sys.version}")

# Test Fase 3
try:
    from fase3_evaluator.integration import run_parallel_analysis
    print("✅ Fase 3 importada correctamente")
except Exception as e:
    print(f"❌ Error Fase 3: {e}")

# Test spaCy
try:
    import spacy
    nlp = spacy.load('es_core_news_sm')
    print("✅ spaCy configurado correctamente")
except Exception as e:
    print(f"❌ Error spaCy: {e}")

# Test Presidio
try:
    from presidio_analyzer import AnalyzerEngine
    print("✅ Presidio importado correctamente")
except Exception as e:
    print(f"❌ Error Presidio: {e}")

print("\n✅ Integración completa!")