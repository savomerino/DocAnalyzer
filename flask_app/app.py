from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configurar Tesseract (ajusta la ruta si es necesario)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Umbralización con Otsu para obtener una imagen binarizada invertida
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thresh

def extract_text_from_image(image):
    return pytesseract.image_to_string(image, lang='eng')

def extract_signatures_and_stamps(image):
    processed = preprocess_image(image)
    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detected_objects = []
    
    umbral_minimo = 300  # Ajusta según el tamaño esperado de la firma/sello
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > umbral_minimo:
            x, y, w, h = cv2.boundingRect(contour)
            roi = image[y:y+h, x:x+w]
            detected_objects.append(roi)
    
    return detected_objects

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para servir archivos subidos
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/extract-pdf', methods=['POST'])
def extract_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400
    
    # Guardar el archivo
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    # Convertir PDF a imágenes (una por página)
    try:
        images = convert_from_path(file_path)
    except Exception as e:
        return jsonify({'error': f'Error al convertir PDF: {str(e)}'}), 500
    
    extracted_text = ""
    detected_images = []
    
    for i, img in enumerate(images):
        open_cv_image = np.array(img)
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        
        # Extraer texto de la imagen
        extracted_text += extract_text_from_image(open_cv_image) + "\n"
        # Extraer firmas o sellos
        detected_objects = extract_signatures_and_stamps(open_cv_image)
        
        for j, obj in enumerate(detected_objects):
            img_name = f'stamp_{i}_{j}.png'
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
            cv2.imwrite(save_path, obj)
            # Retornar la URL para acceder al archivo desde el navegador
            detected_images.append(f'/uploads/{img_name}')
    
    return jsonify({'extracted_text': extracted_text, 'images': detected_images})

# Resto de las rutas (process-excel, generate-report, consulta-db, etc.) se mantienen igual...

if __name__ == '__main__':
    app.run(debug=True)
