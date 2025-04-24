import os
import io
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from PIL import Image
from datetime import datetime

def crear_justificante_pdf(data, output_path, logo_path=None, firma_path=None):
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    width, height = landscape(A4)

    c.setLineWidth(1)
    c.rect(1*cm, 1*cm, width - 2*cm, height - 2*cm)

    if logo_path and os.path.exists(logo_path):
        try:
            logo_img = Image.open(logo_path).convert("RGBA")
            alpha = logo_img.split()[3].point(lambda p: p * 0.15)
            logo_img.putalpha(alpha)
            img_buffer = io.BytesIO()
            logo_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            watermark = ImageReader(img_buffer)
            c.drawImage(watermark,
                        (width - 27*cm) / 2,
                        (height - 27*cm) / 2,
                        width=27*cm,
                        height=27*cm,
                        preserveAspectRatio=True,
                        mask='auto')
        except:
            pass

    if logo_path and os.path.exists(logo_path):
        c.drawImage(logo_path, (width - 7.8*cm) / 2, height - 4.1*cm,
                    width=7.8*cm, height=3.6*cm, preserveAspectRatio=True, mask='auto')

    c.setFont("Times-Roman", 24)
    c.drawCentredString(width / 2, height - 4.2*cm, "CONFIRMACION DE RESERVA")

    y = height - 5.2*cm
    def write_line(label, value):
        nonlocal y
        if value.strip():
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2.5*cm, y, label)
            c.setFont("Helvetica", 12)
            c.drawString(10.2*cm, y, value.strip())
            y -= 0.7*cm

    campos = [
        ("Nombre:", data.get('nombre', '')),
        ("Fecha:", data.get('fecha', '')),
        ("Dirección ceremonia religiosa:", data.get('direccion_religiosa', '')),
        ("Dirección ceremonia civil:", data.get('direccion_civil', '')),
        ("Dirección de celebración:", data.get('direccion_celebracion', '')),
        ("Hora:", data.get('hora', '')),
        ("Teléfono de contacto:", data.get('telefono', '')),
        ("Motivo:", data.get('motivo', ''))
    ]

    for label, value in campos:
        write_line(label, value)

    if data.get('servicios', '').strip():
        y -= 0.3*cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2.5*cm, y, "Servicios contratados:")
        y -= 0.6*cm
        c.setFont("Helvetica", 11)
        for line in data['servicios'].split('\n'):
            if line.strip():
                c.drawString(3.2*cm, y, line.strip())
                y -= 0.5*cm

    y = 3.5*cm
    c.setFont("Helvetica-Bold", 12)
    monetarios = [
        ("TOTAL:", data.get('total', '')),
        ("DESPLAZAMIENTO:", data.get('desplazamiento', '')),
        ("RESERVA:", data.get('reserva', '')),
        ("A PAGAR:", data.get('a_pagar', ''))
    ]
    texto = "    ".join([f"{k} {v.upper()}" for k, v in monetarios if v.strip()])
    c.drawString(2.5*cm, y, texto)

    notas = [
        "*Reserva con comprobante de 20€.",
        "*La reserva se descuenta del total.",
        "*Pagos: 50% día evento, 50% entrega final."
    ]
    c.setFont("Helvetica", 8.5)
    for i, nota in enumerate(notas):
        c.drawString(2.3*cm, 2.6*cm - (i * 0.4*cm), nota)

    if firma_path and os.path.exists(firma_path):
        c.drawImage(firma_path, width - 7*cm, 2.5*cm,
                    width=5.2*cm, height=2.3*cm,
                    preserveAspectRatio=True, mask='auto')

    c.save()
