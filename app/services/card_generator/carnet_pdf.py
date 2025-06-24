# services/card_generator/carnet_pdf.py
import os
from io import BytesIO
from reportlab.pdfgen import canvas
import qrcode
from qrcode.constants import ERROR_CORRECT_L
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader


# Tamaño de carnet real en puntos (≈ 3.37 x 2.13 pulgadas)
CARNET_WIDTH = 148  # ≈ 8.6 cm
CARNET_HEIGHT = 251 # ≈ 5.4 cm

def generar_pdf_en_memoria(ruta_anverso, ruta_reverso, cedula=None, modo='horizontal'):
    buffer = BytesIO()
    page_width, page_height = letter  # Tamaño carta
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    # Coordenadas según modo
    if modo == 'horizontal':
        pos_anverso = (50, page_height - CARNET_HEIGHT - 50)  # izquierda
        pos_reverso = (pos_anverso[0] + CARNET_WIDTH + 20, pos_anverso[1])  # derecha
    else:  # vertical
        pos_anverso = ((page_width - CARNET_WIDTH) / 2, page_height - CARNET_HEIGHT - 50)
        pos_reverso = (pos_anverso[0], pos_anverso[1] - CARNET_HEIGHT - 30)

    # Cargar anverso
    if ruta_anverso and os.path.exists(ruta_anverso):
        c.drawImage(
            ImageReader(ruta_anverso),
            pos_anverso[0],
            pos_anverso[1],
            width=CARNET_WIDTH,
            height=CARNET_HEIGHT
        )

    # Cargar reverso
    if ruta_reverso and os.path.exists(ruta_reverso):
        c.drawImage(
            ImageReader(ruta_reverso),
            pos_reverso[0],
            pos_reverso[1],
            width=CARNET_WIDTH,
            height=CARNET_HEIGHT
        )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generar_qr(cedula):
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(cedula)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white').get_image().convert("RGB")
    qr_buffer = BytesIO()
    img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    return qr_buffer