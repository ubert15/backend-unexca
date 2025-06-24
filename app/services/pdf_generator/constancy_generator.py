from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from io import BytesIO
import os
from datetime import datetime
from babel.dates import format_date

class ConstancyPDFGenerator:
    def __init__(self):
        # Inicializa el objeto styles correctamente
        self.styles = getSampleStyleSheet()

        # Estilo justificado
        if 'BodyTextJustified' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyTextJustified',
                parent=self.styles['BodyText'],
                fontSize=12,
                leading=16,
                spaceAfter=12,
                alignment=4  # Justificado
            ))

        # Estilo para firma centrado
        if 'SignatureStyle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SignatureStyle',
                parent=self.styles['Normal'],
                fontSize=11,
                leading=16,
                spaceBefore=6,
                alignment=1  # Centrado
            ))

        # Rutas a assets
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.base_dir, 'assets')
        self.logo_unexca = os.path.join(self.assets_dir, 'unexca_logo.jpg')
        self.logo_gobierno = os.path.join(self.assets_dir, 'gobierno_logo.jpg')

    def generate_pdf(self, data):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)

        left_margin = 25 * mm
        right_margin = 25 * mm
        doc_width = A4[0] - (2 * left_margin)
        center_x = A4[0] / 2

        # Logos
        try:
            logo = ImageReader(self.logo_unexca)
            c.drawImage(logo, left_margin, 255*mm, width=45*mm, height=25*mm, preserveAspectRatio=True)
        except Exception as e:
            print("Error cargando logo UNEXCA:", e)

        try:
            logo = ImageReader(self.logo_gobierno)
            c.drawImage(logo, A4[0] - right_margin - 45*mm, 255*mm, width=45*mm, height=25*mm, preserveAspectRatio=True)
        except Exception as e:
            print("Error cargando logo Gobierno:", e)

        # Encabezados
        c.setFont("Helvetica-Bold", 12)
        header_lines = [
            "REPÚBLICA BOLIVARIANA DE VENEZUELA",
            "MINISTERIO DEL PODER POPULAR PARA LA EDUCACIÓN UNIVERSITARIA",
            "UNIVERSIDAD NACIONAL EXPERIMENTAL DE LA GRAN CARACAS - \"UNEXCA\""
        ]
        y_position = 245 * mm
        for line in header_lines:
            text_width = c.stringWidth(line, "Helvetica-Bold", 12)
            c.drawString(center_x - (text_width / 2), y_position, line)
            y_position -= 6 * mm

        # Título
        subtitle = Paragraph(
            "<b>CONSTANCIA DE ESTUDIOS</b>",
            ParagraphStyle(
                name='TitleStyle',
                parent=self.styles['Heading2'],
                fontSize=16,
                alignment=1,
                spaceAfter=14
            )
        )
        subtitle.wrapOn(c, doc_width, 40*mm)
        subtitle.drawOn(c, left_margin, 210*mm)

        # Fecha en español con Babel
        hoy = format_date(
            datetime.now(),
            "d 'de' MMMM 'de' yyyy",
            locale='es'
        ) + '.'

        # Texto principal
        texto_constancia = (
            f"Quien Suscribe, <b>JEFE(E) Ing. Yovany Diaz Coordinación Control de Estudios</b> "
            f"de la <b>UNIVERSIDAD NACIONAL EXPERIMENTAL DE LA GRAN CARACAS</b>, hace constar por "
            f"medio la presente que el(la) ciudadano(a) <b>{data['nombre']} {data['apellido']}</b>, "
            f"titular de la cédula de identidad N° <b>V-{data['cedula']}</b>, es un estudiante activo(a) "
            f"de esta universidad en el núcleo <b>{data['nucleo']}</b>, cursando el periodo académico "
            f"<b>{data['periodo']}</b> del Programa Nacional de Formación <b>PNF - {data['carrera']}</b>, "
            f"sección <b>{data['seccion']}</b>, turno <b>{data['turno']}</b>."
        )
        paragraph = Paragraph(texto_constancia, self.styles['BodyTextJustified'])
        paragraph.wrapOn(c, doc_width, 100*mm)
        paragraph.drawOn(c, left_margin, 160*mm)

        # Texto de la fecha
        texto_fecha = (
            f"Constancia que se expide a petición de la parte interesada en Caracas a los {hoy}"
        )
        paragraph = Paragraph(texto_fecha, self.styles['BodyTextJustified'])
        paragraph.wrapOn(c, doc_width, 20*mm)
        paragraph.drawOn(c, left_margin, 140*mm)

        # Firma
        c.setFont("Helvetica-Bold", 11)
        text_width = c.stringWidth("Atentamente", "Helvetica-Bold", 11)
        c.drawString(center_x - (text_width / 2), 115*mm, "Atentamente")
        line_length = 60 * mm
        c.line(center_x - (line_length / 2), 90*mm, center_x + (line_length / 2), 90*mm)

        texts = [
            "ING. YOVANY DIAZ",
            "JEFE(E) COORDINACIÓN CONTROL DE ESTUDIOS",
            "NUCLEO - ALTAGRACIA"
        ]
        y_position = 85 * mm
        for text in texts:
            text_width = c.stringWidth(text, "Helvetica-Bold", 11)
            c.drawString(center_x - (text_width / 2), y_position, text)
            y_position -= 5 * mm

        # Pie de página
        c.setFont("Helvetica", 9)
        contact_lines = [
            "Esq. De Mijares. Av.Oeste 3. Caracas-Venezuela 1010A. Correo: cesolicitudes.unexca@gmail.com",
            "Telefono:0212-860.51.81 Extensión 128. COORDINACION CONTROL DE ESTUDIOS - UNEXCA",
            "RIF G-200128259"
        ]
        y_position = 30 * mm
        for line in contact_lines:
            text_width = c.stringWidth(line, "Helvetica", 9)
            c.drawString(center_x - (text_width / 2), y_position, line)
            y_position -= 5 * mm

        c.save()
        buffer.seek(0)
        return buffer
