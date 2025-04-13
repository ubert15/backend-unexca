from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from io import BytesIO
import os

class ConstancyPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Ruta al directorio donde se encuentra este archivo
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # Ruta a la imagen del membrete
        self.logo_path = os.path.join(self.base_dir, 'assets', 'membrete.jpg')

    def generate_pdf(self, data):
        """
        Genera un PDF de constancia con los datos proporcionados
        
        Args:
            data (dict): Diccionario con los datos del estudiante
                - nombre: Nombre del estudiante
                - apellido: Apellido del estudiante
                - cedula: Número de cédula
                - nucleo: Núcleo académico
                - periodo: Período académico
                - carrera: Carrera que cursa
                - seccion: Sección
                - turno: Turno (Diurno, Vespertino, Nocturno)
                
        Returns:
            BytesIO: Buffer con el contenido del PDF
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Configurar la fuente
        c.setFont('Times-Roman', 20)
        
        # Agregar subtítulo en negrita
        subtitle = Paragraph("<b>Constancia</b>", self.styles['Heading2'])
        subtitle.wrapOn(c, 600*mm, 160*mm)
        subtitle.drawOn(c, 90*mm, 210*mm)
        
        # Texto principal con los datos personalizados
        texto_constancia = f"""Quien suscribe,<b> Ing Yovany Díaz Jefe(E)Coordinación de Estudios</b> de la UNIVERSIDAD NACIONAL EXPERIMENTAL DE LA GRAN CARACAS, hace constar por medio de la presente que el(la) ciudadano(a) <b>{data['nombre']} {data['apellido']}</b>, titular de la cédula de Identidad N°V- <b>{data['cedula']}</b>, es estudiante activo(a) de esta universidad en el núcleo <b>{data['nucleo']}</b>, actualmente cursa período acádemico <b>{data['periodo']}</b> del Programa Nacional de Formación en <b>{data['carrera']} {data['seccion']}</b>, turno <b>{data['turno']}</b>"""
        
        paragraph = Paragraph(texto_constancia, self.styles["Normal"])
        paragraph.wrapOn(c, 500, 100)
        paragraph.drawOn(c, 20 * mm, 180 * mm)
        
        # Agregar la frase adicional
        paragraph = Paragraph("Constancia que se expide a petición de la parte interesada, en Caracas a los")
        paragraph.wrapOn(c, 500, 20)
        paragraph.drawOn(c, 20 * mm, 170 * mm)
        
        # Agregar texto "Atentamente"
        atentamente = Paragraph("Atentamente", self.styles['Normal'])
        atentamente.wrapOn(c, 500, 30)
        atentamente.drawOn(c, 96*mm, 95*mm)
        
        # Definir tamaño de página y línea
        width, height = A4
        x_start = (width - 180) / 2
        x_end = x_start + 185
        y = 220
        
        # Dibujar la línea
        c.line(x_start, y, x_end, y)
        
        # Agregar información del firmante
        ing_yovany = Paragraph("<b>ING. YOVANY DIAZ</b>", self.styles['Normal'])
        ing_yovany.wrapOn(c, 500, 20)
        ing_yovany.drawOn(c, 90*mm, 65*mm)
        
        jefe = Paragraph("<b>JEFE(E) COORDINACIÓN CONTROL DE ESTUDIOS</b>", self.styles['Normal'])
        jefe.wrapOn(c, 500, 20)
        jefe.drawOn(c, 60*mm, 56*mm)
        
        # Añadir logo si existe
        try:
            logo = ImageReader(self.logo_path)
            c.drawImage(logo, 5*mm, 240*mm, width=200*mm, height=60*mm)
        except Exception as e:
            # Si no encuentra el logo, continuar sin él y registrar el error
            print(f"Error al cargar el logo: {str(e)}")
        
        # Guardar el PDF
        c.save()
        
        # Mover el puntero al inicio del buffer
        buffer.seek(0)
        
        return buffer