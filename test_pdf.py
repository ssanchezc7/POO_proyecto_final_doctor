#!/usr/bin/env python
"""
Script de prueba para la funcionalidad de PDF con ReportLab
"""

import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proy_clinico.settings')
django.setup()

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import io
from datetime import datetime

def test_pdf_generation():
    """Prueba la generación de PDF básico"""
    print("Iniciando prueba de generación de PDF...")
    
    # Crear un buffer para el PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4F46E5')
    )
    
    # Contenido del PDF
    story = []
    
    # Título
    story.append(Paragraph("RECIBO DE PAGO MÉDICO - PRUEBA", title_style))
    story.append(Spacer(1, 12))
    
    # Información de prueba
    test_data = [
        ['Número de Recibo:', '#123'],
        ['Fecha de Emisión:', datetime.now().strftime('%d/%m/%Y %H:%M')],
        ['Estado del Pago:', 'Pagado'],
        ['Descripción:', 'Pago médico de prueba'],
    ]
    
    test_table = Table(test_data, colWidths=[2*inch, 3*inch])
    test_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(test_table)
    story.append(Spacer(1, 20))
    
    # Generar el PDF
    doc.build(story)
    
    # Guardar en archivo
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Escribir a archivo para prueba
    with open('test_recibo.pdf', 'wb') as f:
        f.write(pdf_content)
    
    print("PDF de prueba generado exitosamente: test_recibo.pdf")
    print(f"Tamaño del archivo: {len(pdf_content)} bytes")
    
    return True

if __name__ == "__main__":
    try:
        test_pdf_generation()
        print("✅ Prueba exitosa - ReportLab está funcionando correctamente")
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
