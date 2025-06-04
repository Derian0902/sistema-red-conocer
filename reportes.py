from database import obtener_actividades
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
import os

def exportar_excel():
    actividades = obtener_actividades()
    df = pd.DataFrame(
        actividades,
        columns=["ID", "Título", "Tipo", "Estado", "Fecha Límite", "Responsable"]
    )
    df.to_excel("reporte_actividades.xlsx", index=False)
    print("📁 Reporte Excel generado correctamente: reporte_actividades.xlsx")

def exportar_pdf():
    actividades = obtener_actividades()
    c = canvas.Canvas("reporte_actividades.pdf", pagesize=letter)
    width, height = letter

    # === Membrete con imagen institucional ===
    logo_path = "9273b1e0-12c9-4fce-9ec2-3b7af8abe179.png"  # Asegúrate que esté en el mismo folder
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, 50, height - 120, width=500, height=70, mask='auto')

    # === Título del reporte ===
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 140, "Reporte de Actividades - Red CONOCER")
    c.line(50, height - 145, width - 50, height - 145)

    # === Tabla de actividades ===
    data = [["ID", "Título", "Tipo", "Estado", "Fecha", "Responsable"]]
    for act in actividades:
        data.append([str(act[0]), act[1], act[2], act[3], act[4], act[5]])

    table = Table(data, colWidths=[50, 150, 80, 80, 80, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.7)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, height - 500)

    # === Pie de página institucional ===
    c.setFont("Helvetica", 8)
    c.drawString(50, 40, "Instituto Tecnológico Superior de Coatzacoalcos | red_conocer@itesco.edu.mx | Tel. (921) 21 1 81 50")
    c.drawRightString(width - 50, 25, "Página 1")

    c.save()
    print("📄 Reporte PDF generado correctamente: reporte_actividades.pdf")
