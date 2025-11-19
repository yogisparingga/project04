"""
Flask Web Application for PDF & Image Extractor
Upload and extract text from PDF and images with OCR
"""

import os
import json
import traceback
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, url_for

from pdf_extractor import PDFExtractor
from image_extractor import ImageExtractor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf': ['pdf'],
    'image': ['png', 'jpg', 'jpeg', 'tiff', 'bmp']
}

# Create necessary directories
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)


def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, [])


def cleanup_old_files():
    """Clean up old uploaded and output files"""
    import time
    current_time = time.time()
    max_age = 3600  # 1 hour

    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
        folder_path = Path(folder)
        if folder_path.exists():
            for file_path in folder_path.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age:
                        try:
                            file_path.unlink()
                        except Exception:
                            pass


@app.route('/')
def index():
    """Main page with upload form"""
    cleanup_old_files()
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get processing type
        process_type = request.form.get('type', 'auto')
        ocr_engine = request.form.get('ocr_engine', 'tesseract')

        # Determine file type
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if file_ext == 'pdf':
            if not allowed_file(file.filename, 'pdf'):
                return jsonify({'error': 'Invalid PDF file'}), 400
            return process_pdf(file, process_type)
        elif file_ext in ALLOWED_EXTENSIONS['image']:
            if not allowed_file(file.filename, 'image'):
                return jsonify({'error': 'Invalid image file'}), 400
            return process_image(file, process_type, ocr_engine)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400

    except Exception as e:
        print(f"Error in upload_file: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def process_pdf(file, process_type):
    """Process PDF file"""
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))

        # Initialize PDF extractor
        extractor = PDFExtractor(str(filepath))

        result = {
            'type': 'pdf',
            'filename': filename,
            'data': {}
        }

        # Extract text
        text = extractor.extract_text()
        result['data']['text'] = text
        result['data']['char_count'] = len(text)

        # Save text to file
        text_filename = f"{filepath.stem}_text.txt"
        text_filepath = Path(app.config['OUTPUT_FOLDER']) / text_filename
        text_filepath.write_text(text, encoding='utf-8')
        result['data']['text_file'] = text_filename

        # Extract tables if requested
        if process_type in ['auto', 'tables']:
            tables = extractor.extract_tables()
            result['data']['tables_count'] = len(tables)
            if tables:
                result['data']['tables'] = tables

        # Convert to images if requested
        if process_type in ['auto', 'images']:
            try:
                images_dir = Path(app.config['OUTPUT_FOLDER']) / f"{filepath.stem}_images"
                images = extractor.pdf_to_images(str(images_dir), dpi=150)
                result['data']['images'] = [Path(img).name for img in images]
                result['data']['images_dir'] = f"{filepath.stem}_images"
            except Exception as e:
                print(f"Error converting PDF to images: {e}")

        return jsonify(result)

    except Exception as e:
        print(f"Error processing PDF: {e}")
        traceback.print_exc()
        return jsonify({'error': f'PDF processing failed: {str(e)}'}), 500


def process_image(file, process_type, ocr_engine='tesseract'):
    """Process image file with OCR"""
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))

        # Initialize image extractor
        extractor = ImageExtractor(str(filepath), ocr_engine=ocr_engine)

        result = {
            'type': 'image',
            'filename': filename,
            'ocr_engine': ocr_engine,
            'data': {}
        }

        # Extract text
        text = extractor.extract_text()
        result['data']['text'] = text

        # Save text to file
        text_filename = f"{filepath.stem}_text.txt"
        text_filepath = Path(app.config['OUTPUT_FOLDER']) / text_filename
        text_filepath.write_text(text, encoding='utf-8')
        result['data']['text_file'] = text_filename

        # Parse KTP if requested
        if process_type == 'ktp':
            ktp_data = extractor.parse_ktp(text)
            result['data']['ktp'] = ktp_data
            result['data']['document_type'] = 'KTP'

            # Save KTP data as JSON
            json_filename = f"{filepath.stem}_ktp.json"
            json_filepath = Path(app.config['OUTPUT_FOLDER']) / json_filename
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(ktp_data, f, indent=2, ensure_ascii=False)
            result['data']['json_file'] = json_filename

        # Parse SIM if requested
        elif process_type == 'sim':
            sim_data = extractor.parse_sim(text)
            result['data']['sim'] = sim_data
            result['data']['document_type'] = 'SIM'

            # Save SIM data as JSON
            json_filename = f"{filepath.stem}_sim.json"
            json_filepath = Path(app.config['OUTPUT_FOLDER']) / json_filename
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(sim_data, f, indent=2, ensure_ascii=False)
            result['data']['json_file'] = json_filename

        # Auto-detect document type
        elif process_type == 'auto':
            text_lower = text.lower()
            if 'nik' in text_lower or 'provinsi' in text_lower:
                ktp_data = extractor.parse_ktp(text)
                result['data']['ktp'] = ktp_data
                result['data']['document_type'] = 'KTP (Auto-detected)'
            elif 'sim' in text_lower or 'surat izin mengemudi' in text_lower:
                sim_data = extractor.parse_sim(text)
                result['data']['sim'] = sim_data
                result['data']['document_type'] = 'SIM (Auto-detected)'
            else:
                result['data']['document_type'] = 'General Image'

        # Save preprocessed image
        processed_filename = f"{filepath.stem}_processed.png"
        processed_filepath = Path(app.config['OUTPUT_FOLDER']) / processed_filename
        extractor.save_processed_image(str(processed_filepath))
        result['data']['processed_image'] = processed_filename

        return jsonify(result)

    except Exception as e:
        print(f"Error processing image: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Image processing failed: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download processed file"""
    try:
        filepath = Path(app.config['OUTPUT_FOLDER']) / secure_filename(filename)
        if filepath.exists():
            return send_file(str(filepath), as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/preview/<filename>')
def preview_file(filename):
    """Preview image file"""
    try:
        # Try upload folder first
        filepath = Path(app.config['UPLOAD_FOLDER']) / secure_filename(filename)
        if not filepath.exists():
            # Try output folder
            filepath = Path(app.config['OUTPUT_FOLDER']) / secure_filename(filename)

        if filepath.exists():
            return send_file(str(filepath))
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("="*60)
    print("PDF & Image Extractor Web Application")
    print("="*60)
    print("\nStarting server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("="*60)

    app.run(debug=True, host='0.0.0.0', port=5000)
