from flask import Flask, render_template, request, send_file
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from generar_pdf import crear_justificante_pdf  # la lógica que ya tienes separada
from io import BytesIO

app = Flask(__name__)

# Ruta para almacenar las imágenes subidas
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración para limitar los tipos de archivos permitidos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Función para verificar las extensiones de archivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":
        # Obtener los datos del formulario
        data = {key: request.form.get(key, '') for key in [
            'nombre', 'fecha', 'direccion_religiosa', 'direccion_civil', 
            'direccion_celebracion', 'hora', 'telefono', 'motivo', 
            'total', 'desplazamiento', 'reserva', 'a_pagar', 'servicios'
        ]}
        
        # Subir logo y firma
        logo_file = request.files.get('logo')
        firma_file = request.files.get('firma')

        logo_path = None
        firma_path = None

        if logo_file and allowed_file(logo_file.filename):
            logo_filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
            logo_file.save(logo_path)

        if firma_file and allowed_file(firma_file.filename):
            firma_filename = secure_filename(firma_file.filename)
            firma_path = os.path.join(app.config['UPLOAD_FOLDER'], firma_filename)
            firma_file.save(firma_path)

        # Crear el PDF en memoria
        output_pdf = BytesIO()
        crear_justificante_pdf(data, output_pdf, logo_path=logo_path, firma_path=firma_path)
        output_pdf.seek(0)

        # Generar el nombre del archivo PDF
        filename = f"Justificante_{data['nombre'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(output_pdf, as_attachment=True, download_name=filename, mimetype='application/pdf')

    return render_template("formulario.html")

if __name__ == "__main__":
    # Configuración para despliegue en Render
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
