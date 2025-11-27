from fpdf import FPDF
from datetime import datetime
import tempfile
import os

class PDFReport(FPDF):
    def __init__(self, title="Reporte CUIDAR IA"):
        super().__init__()
        self.title_doc = title
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        # Logo placeholder or simple text header
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, self.title_doc, 0, 1, 'C')
        self.ln(5)
        
        # Line break
        self.set_draw_color(255, 95, 158) # Pink accent
        self.set_line_width(0.5)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        self.cell(0, 10, f'Generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'R')

    def chapter_title(self, label):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(10, 26, 47) # Dark blue
        self.cell(0, 10, label, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50)
        self.multi_cell(0, 6, text)
        self.ln()

    def add_metric(self, label, value):
        self.set_font('Helvetica', 'B', 10)
        self.cell(50, 8, label, 0, 0)
        self.set_font('Helvetica', '', 10)
        self.cell(0, 8, str(value), 0, 1)

def generate_diagnostic_pdf(results):
    """
    Genera un reporte PDF para el diagnóstico CUIDAR Index.
    results: dict con los resultados del diagnóstico
    """
    pdf = PDFReport("Reporte de Diagnóstico CUIDAR Index")
    
    # Resumen Ejecutivo
    pdf.chapter_title("Resumen Ejecutivo")
    pdf.chapter_body(results.get('summary', 'Sin resumen disponible.'))
    
    # Puntaje General
    pdf.ln(5)
    pdf.set_fill_color(245, 247, 250)
    pdf.rect(10, pdf.get_y(), 190, 20, 'F')
    pdf.set_xy(15, pdf.get_y() + 5)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(90, 10, f"Nivel de Madurez: {results.get('maturity_level', 'N/A')}", 0, 0)
    pdf.cell(90, 10, f"Puntaje: {results.get('total_score', 0):.1f}/100", 0, 1, 'R')
    pdf.ln(10)
    
    # Detalle por Dimensión
    pdf.chapter_title("Detalle por Dimensión")
    
    scores = results.get('scores', {})
    feedback = results.get('feedback', {})
    
    for dim, data in scores.items():
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 8, f"{dim} ({data.get('porcentaje', 0):.1f}%)", 0, 1)
        
        pdf.set_font('Helvetica', 'I', 9)
        pdf.multi_cell(0, 5, f"Feedback: {feedback.get(dim, '')}")
        pdf.ln(3)

    return pdf

def generate_data_quality_pdf(quality_results):
    """
    Genera un reporte PDF para el evaluador de calidad de datos.
    quality_results: dict con los resultados del análisis
    """
    pdf = PDFReport("Reporte de Calidad de Datos")
    
    # Resumen General
    pdf.chapter_title("Resumen de Calidad")
    
    summary = quality_results.get('tipos', {}).get('summary', {})
    completeness = quality_results.get('completitud', {}).get('summary', {})
    
    pdf.add_metric("Puntuación de Calidad:", f"{summary.get('quality_score', 0):.1f}%")
    pdf.add_metric("Completitud Global:", f"{100 - completeness.get('missing_percentage', 0):.1f}%")
    pdf.add_metric("Total Columnas:", summary.get('total_columns', 0))
    pdf.ln(5)
    
    # Privacidad
    pdf.chapter_title("Privacidad y Anonimización")
    privacy = quality_results.get('anonimizacion', {})
    risk = privacy.get('risk_assessment', {}).get('score', 0)
    
    pdf.add_metric("Riesgo de Re-identificación:", f"{risk:.1f}/10")
    
    entities = privacy.get('entities_found', [])
    if entities:
        pdf.chapter_body(f"Se detectaron {len(entities)} entidades de información personal (PII).")
    else:
        pdf.chapter_body("No se detectaron entidades PII obvias.")
        
    pdf.ln(5)
    
    # Viabilidad ML
    pdf.chapter_title("Viabilidad para Machine Learning")
    ml = quality_results.get('ml', {})
    viability = ml.get('overall_viability', 0) * 100
    
    pdf.add_metric("Viabilidad General:", f"{viability:.1f}%")
    
    reasons = ml.get('reasons', [])
    if reasons:
        pdf.chapter_body("Factores evaluados:")
        for reason in reasons:
            pdf.chapter_body(f"- {reason}")

    return pdf
