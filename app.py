from flask import Flask, request, send_file, render_template
from PIL import Image
import os
import io
from pdf2image import convert_from_bytes

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('web_file_converter.html')

@app.route('/convert', methods=['POST'])
def convert():
    file_type = request.form.get('file_type')
    files = request.files.getlist('images')
    if file_type == 'JPG':
        images = [Image.open(f.stream).convert('RGB') for f in files if f.filename.lower().endswith(('.jpg', '.jpeg'))]
        if not images:
            return "No valid JPG images found", 400

        pdf_io = io.BytesIO()
        images[0].save(pdf_io, format='PDF', save_all=True, append_images=images[1:])
        pdf_io.seek(0)

        return send_file(pdf_io, download_name='output.pdf', as_attachment=True)

    elif file_type == 'PDF':
        pdf_file = next((f for f in files if f.filename.lower().endswith('.pdf')), None)
        if not pdf_file:
            convert()
            return "No valid PDF file found", 400

        images = convert_from_bytes(pdf_file.read())
        zip_io = io.BytesIO()
        from zipfile import ZipFile
        with ZipFile(zip_io, 'w') as zipf:
            for i, img in enumerate(images):
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)
                zipf.writestr(f'page_{i+1}.jpg', img_io.read())
        zip_io.seek(0)

        return send_file(zip_io, download_name='output_images.zip', as_attachment=True)

    return "Invalid file type selected", 400

if __name__ == '__main__':
    app.run(debug=True)
