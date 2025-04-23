import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
from datetime import datetime

JUSTIFICANTES_FOLDER = "justificantes"
LOGO_PATH = "logo.png"
FIRMA_PATH = "firma.png"

os.makedirs(JUSTIFICANTES_FOLDER, exist_ok=True)

def crear_justificante_pdf(data, output_path, logo_path=LOGO_PATH, firma_path=FIRMA_PATH):
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    width, height = landscape(A4)

    c.setLineWidth(1)
    c.rect(1*cm, 1*cm, width - 2*cm, height - 2*cm)

    # Marca de agua
    if os.path.exists(logo_path):
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
        except Exception as e:
            print(f"Error al aplicar marca de agua: {e}")

    # Logo superior
    if os.path.exists(logo_path):
        try:
            logo_w = 7.8*cm
            logo_h = 3.6*cm
            bottom = height - 4.1*cm
            c.drawImage(logo_path, (width - logo_w) / 2, bottom,
                        width=logo_w, height=logo_h,
                        preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error al cargar logo: {e}")

    # Título
    c.setFont("Times-Roman", 24)
    c.drawCentredString(width / 2, height - 4.2*cm, "CONFIRMACION DE RESERVA")

    y = height - 5.2*cm
    label_font_size = 14
    value_font_size = 12

    def write_line(label, value):
        nonlocal y
        if value.strip():
            c.setFont("Helvetica-Bold", label_font_size)
            c.drawString(2.5*cm, y, label)
            c.setFont("Helvetica", value_font_size)
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

    # Servicios contratados
    if data.get('servicios', '').strip():
        y -= 0.3*cm
        c.setFont("Helvetica-Bold", label_font_size)
        c.drawString(2.5*cm, y, "Servicios contratados:")
        y -= 0.6*cm
        c.setFont("Helvetica", value_font_size - 1)
        for line in data['servicios'].split('\n'):
            if line.strip():
                c.drawString(3.2*cm, y, f"{line.strip()}")
                y -= 0.5*cm

    # ---- BLOQUE INFERIOR ----
    # Base inferior del cuadro (1cm margen) + espacio
    base_inferior = 1*cm

    # Posición donde empiezan las notas
    notas_start_y = base_inferior + 1*cm

    # Posición de los campos monetarios
    monetarios_y = notas_start_y + 0.5*cm  # 0.5 cm encima de las notas

    # Campos monetarios en horizontal
    monetarios = [
        ("TOTAL:", data.get('total', '')),
        ("DESPLAZAMIENTO:", data.get('desplazamiento', '')),
        ("RESERVA:", data.get('reserva', '')),
        ("A PAGAR:", data.get('a_pagar', ''))
    ]
    campos_presentes = [(label, valor) for label, valor in monetarios if valor.strip()]
    if campos_presentes:
        c.setFont("Helvetica-Bold", 12)
        texto = "    ".join([f"{label} {valor.strip().upper()}" for label, valor in campos_presentes])
        c.drawString(2.3*cm, monetarios_y, texto)

    # Escribir notas
    notas = [
        "*Toda reserva de fecha se realiza con el comprobante o captura de la transferencia de 20 euros.",
        "*El importe de reserva se descontará del importe total del servicio.",
        "*Los pagos se realizarán en 2 partes de 50%, una el día del evento y otra cuando se entregue el trabajo final descontando el monto de reserva."
    ]
    c.setFont("Helvetica", 8.5)
    for i, nota in enumerate(notas):
        c.drawString(2.3*cm, notas_start_y - (i * 0.4*cm), nota)

    # Firma
    if os.path.exists(firma_path):
        try:
            firma_w = 5.2*cm
            firma_h = 2.3*cm
            c.drawImage(firma_path,
                        width - firma_w - 2*cm,
                        3.2*cm,
                        width=firma_w,
                        height=firma_h,
                        preserveAspectRatio=True,
                        mask='auto')
        except Exception as e:
            print(f"Error al cargar firma: {e}")

    c.save()

def app():
    root = tk.Tk()
    root.title("Generador de Justificantes de Boda")

    campos = [
        ("Nombre", 'nombre'),
        ("Fecha", 'fecha'),
        ("Dirección ceremonia religiosa", 'direccion_religiosa'),
        ("Dirección ceremonia civil", 'direccion_civil'),
        ("Dirección de celebración", 'direccion_celebracion'),
        ("Hora", 'hora'),
        ("Teléfono de contacto", 'telefono'),
        ("Motivo", 'motivo'),
        ("Total", 'total'),
        ("Desplazamiento", 'desplazamiento'),
        ("Reserva", 'reserva'),
        ("A pagar", 'a_pagar')
    ]

    entries = {}

    for i, (label_text, var_name) in enumerate(campos):
        tk.Label(root, text=label_text).grid(row=i, column=0, sticky='e', padx=5, pady=2)
        entry = tk.Entry(root, width=60)
        entry.grid(row=i, column=1, padx=5, pady=2, sticky='w')
        entries[var_name] = entry

    tk.Label(root, text="Servicios contratados").grid(row=len(campos), column=0, sticky='ne', padx=5)
    servicios_text = tk.Text(root, width=60, height=6)
    servicios_text.grid(row=len(campos), column=1, padx=5, pady=5)

    def seleccionar_logo():
        global LOGO_PATH
        path = filedialog.askopenfilename(title="Seleccionar Logo", filetypes=[("Imagen", "*.png;*.jpg;*.jpeg")])
        if path:
            LOGO_PATH = path
            messagebox.showinfo("Logo seleccionado", f"Logo actualizado:\n{path}")

    def seleccionar_firma():
        global FIRMA_PATH
        path = filedialog.askopenfilename(title="Seleccionar Firma", filetypes=[("Imagen", "*.png;*.jpg;*.jpeg")])
        if path:
            FIRMA_PATH = path
            messagebox.showinfo("Firma seleccionada", f"Firma actualizada:\n{path}")

    def generar():
        data = {k: v.get() if isinstance(v, tk.Entry) else v.get("1.0", tk.END).strip() for k, v in entries.items()}
        data['servicios'] = servicios_text.get("1.0", tk.END).strip()
        filename = f"Justificante_{data.get('nombre', 'reserva').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(JUSTIFICANTES_FOLDER, filename)
        crear_justificante_pdf(data, output_path, logo_path=LOGO_PATH, firma_path=FIRMA_PATH)
        messagebox.showinfo("Éxito", f"Justificante guardado como {filename}")

    ttk.Button(root, text="Seleccionar Logo", command=seleccionar_logo).grid(row=len(campos)+1, column=0, pady=5)
    ttk.Button(root, text="Seleccionar Firma", command=seleccionar_firma).grid(row=len(campos)+1, column=1, sticky='w', pady=5)
    ttk.Button(root, text="Generar Justificante", command=generar).grid(row=len(campos)+2, column=1, pady=10, sticky='w')

    root.mainloop()

if __name__ == "__main__":
    app()
