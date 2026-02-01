#!/usr/bin/env python3
"""
Flask web application for laser engraving file converter.
Provides a web interface accessible from any device for file conversion.
"""

import os
import uuid
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import converter_core

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'outputs')
app.config['SECRET_KEY'] = os.urandom(24)

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {
    'svg', 'dxf', 'ai', 'eps',  # Vector formats
    'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'tif'  # Raster formats
}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files():
    """Remove files older than 1 hour."""
    current_time = time.time()
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                if current_time - os.path.getmtime(filepath) > 3600:  # 1 hour
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass


@app.route('/')
def index():
    """Main page with upload interface."""
    return render_template('index.html')


@app.route('/api/use-cases')
def get_use_cases():
    """Get available use cases."""
    use_cases = list(converter_core.MATERIAL_SUGGESTIONS['svg'].keys())
    return jsonify({'use_cases': use_cases})


@app.route('/api/best-practices')
def get_best_practices():
    """Get best practices for laser engraving."""
    practices = converter_core.get_best_practices()
    return jsonify({'practices': practices})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    cleanup_old_files()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{unique_id}_{original_filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save file
    file.save(filepath)
    
    # Detect file type
    try:
        file_type = converter_core.detect_file_type(filepath)
    except ValueError as e:
        os.remove(filepath)
        return jsonify({'error': str(e)}), 400
    
    return jsonify({
        'success': True,
        'filename': filename,
        'original_filename': original_filename,
        'file_type': file_type,
        'unique_id': unique_id
    })


@app.route('/api/convert', methods=['POST'])
def convert_file():
    """Handle file conversion."""
    data = request.json
    
    if not data or 'filename' not in data:
        return jsonify({'error': 'No filename provided'}), 400
    
    filename = data['filename']
    output_type = data.get('output_type', 'svg')
    dpi = int(data.get('dpi', 300))
    threshold = int(data.get('threshold', 128))
    use_case = data.get('use_case', 'general')
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(input_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Generate output filename
    unique_id = filename.split('_')[0]
    base_name = '_'.join(filename.split('_')[1:])
    base_name = os.path.splitext(base_name)[0]
    output_filename = f"{unique_id}_{base_name}_converted.{output_type}"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    # Convert file
    result = converter_core.convert_file(
        input_path,
        output_type=output_type,
        dpi=dpi,
        threshold=threshold,
        use_case=use_case,
        verbose=False
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 500
    
    # Move converted file to output folder
    if result['output_path'] != output_path:
        import shutil
        shutil.move(result['output_path'], output_path)
    
    # Get file size
    file_size = os.path.getsize(output_path)
    file_size_mb = round(file_size / (1024 * 1024), 2)
    
    return jsonify({
        'success': True,
        'output_filename': output_filename,
        'file_type': result['file_type'],
        'material_suggestion': result['material_suggestion'],
        'file_size': file_size,
        'file_size_mb': file_size_mb
    })


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download converted file."""
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(filepath, as_attachment=True)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    print("="*70)
    print("Laser Engraving File Converter - Web Interface")
    print("="*70)
    print("\nStarting web server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("="*70)
    app.run(host='0.0.0.0', port=5000, debug=True)
