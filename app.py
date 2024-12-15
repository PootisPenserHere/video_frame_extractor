import os
from flask import Flask, render_template, request, jsonify, send_file, abort, send_from_directory
import mimetypes
import uuid
import subprocess
import threading
import time
from datetime import datetime
import zipfile
from io import BytesIO
import glob
import shutil

app = Flask(__name__)

# Ensure upload directory exists
UPLOAD_DIR = os.path.join('tmp', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store extraction progress
extraction_progress = {}

def extract_frames(upload_uuid, start_time, end_time, video_path):
    frames_dir = os.path.join(os.path.dirname(video_path), 'frames')
    
    # Clear existing frames directory if it exists
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    
    # Create fresh empty directory
    os.makedirs(frames_dir)
    
    # Calculate total seconds
    start_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(':')))
    end_seconds = sum(x * int(t) for x, t in zip([3600, 60, 1], end_time.split(':')))
    total_frames = end_seconds - start_seconds
    
    extraction_progress[upload_uuid] = {
        'progress': 0,
        'total_frames': total_frames,
        'available_frames': []
    }
    
    for i, second in enumerate(range(start_seconds, end_seconds), 1):
        time_str = f"{second//3600:02d}_{(second%3600)//60:02d}_{second%60:02d}"
        output_path = os.path.join(
            frames_dir, 
            f"frame_{i}_of_{total_frames}_{time_str}.jpg"
        )
        
        timestamp = f"{second//3600:02d}:{(second%3600)//60:02d}:{second%60:02d}"
        
        cmd = [
            'ffmpeg', '-y',
            '-ss', timestamp,
            '-i', video_path,
            '-vframes', '1',
            '-q:v', '2',
            output_path
        ]
        
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        extraction_progress[upload_uuid]['available_frames'].append(i)
        extraction_progress[upload_uuid]['progress'] = int((i / total_frames) * 100)

@app.route('/extract-frames', methods=['POST'])
def start_frame_extraction():
    data = request.json
    upload_uuid = data.get('upload_uuid')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    
    if not all([upload_uuid, start_time, end_time]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    upload_dir = os.path.join(UPLOAD_DIR, upload_uuid)
    video_file = glob.glob(os.path.join(upload_dir, '*.mp4'))[0]
    
    thread = threading.Thread(
        target=extract_frames,
        args=(upload_uuid, start_time, end_time, video_file)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/<upload_uuid>/progress')
def get_progress(upload_uuid):
    progress_data = extraction_progress.get(upload_uuid, {'progress': 0, 'available_frames': []})
    return jsonify(progress_data)

@app.route('/video/<upload_uuid>/frame/<int:frame_order>')
def get_frame(upload_uuid, frame_order):
    frames_dir = os.path.join(UPLOAD_DIR, upload_uuid, 'frames')
    frame_file = glob.glob(os.path.join(frames_dir, f'frame_{frame_order}_of_*'))[0]
    return send_file(frame_file, mimetype='image/jpeg')

@app.route('/<upload_uuid>/frames')
def download_frames(upload_uuid):
    frames_dir = os.path.join(UPLOAD_DIR, upload_uuid, 'frames')
    memory_file = BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for frame_file in sorted(glob.glob(os.path.join(frames_dir, '*.jpg'))):
            zf.write(frame_file, os.path.basename(frame_file))
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'frames_{upload_uuid}.zip'
    )

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
    app.run(host="0.0.0.0", port=5000, debug=True)
