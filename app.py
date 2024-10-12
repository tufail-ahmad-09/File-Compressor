from flask import Flask,render_template,request,redirect,send_file
import os
from werkzeug.utils import secure_filename
from PIL import Image
import ffmpeg

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Allowed_Extensions = ['png','jpg','jpeg','gif','mp4','mp3','wav','avi','webp']

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_types(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Allowed_Extensions


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST','GET'])
def uploads_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_types(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        compressed_filepath = compress_file(file_path)
        return render_template('success.html', compressed_filename=os.path.basename(compressed_filepath))
    
    return "Invalid filetype"

def compress_file(file_path):
    extension = file_path.rsplit('.', 1)[1].lower() 

    if extension in {'png','jpeg','jpg','mpeg','gif','webp'}:
        return compress_image(file_path)
    elif extension in {'mp3','wav'}:
        return compress_audio(file_path)
    elif extension in {'mp4','avi'}:
        return compress_vedio(file_path) 
    else:
        return file_path

def compress_image(file_path):
    image = Image.open(file_path)
    compressed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'compressed'+ os.path.basename(file_path))
    image.save(compressed_filepath, optimize = True, quality = 70)
    return compressed_filepath

def compress_audio(file_path):
    compressed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'compressed'+ os.path.basename(file_path))
    ffmpeg.input(file_path).output(compressed_filepath, audio_bitrate = '64k').run()
    return compressed_filepath

def compress_vedio(file_path):
    compressed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'compressed'+ os.path.basename(file_path))
    ffmpeg.input(file_path).output(compressed_filepath, vedio_bitrate = '500k').run()
    return compressed_filepath

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)





if __name__ == "__main__":
    app.run(debug=True)