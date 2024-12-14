import os
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
import uuid
import mimetypes

app = Flask(__name__)

# Ensure upload directory exists
UPLOAD_DIR = os.path.join('tmp', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Generate UUID for the upload
    upload_uuid = str(uuid.uuid4())
    upload_path = os.path.join(UPLOAD_DIR, upload_uuid)
    os.makedirs(upload_path, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_path, file.filename)
    file.save(file_path)
    
    return jsonify({
        'uuid': upload_uuid,
        'filename': file.filename
    })

@app.route('/video/<upload_uuid>/<filename>')
def serve_video(upload_uuid, filename):
    video_path = os.path.join(UPLOAD_DIR, upload_uuid)
    
    if not os.path.exists(os.path.join(video_path, filename)):
        abort(404)
    
    # Ensure proper mime type is set for video files
    mimetype = mimetypes.guess_type(filename)[0]
    return send_from_directory(video_path, filename, mimetype=mimetype)

if __name__ == '__main__':
    app.run(debug=True)
