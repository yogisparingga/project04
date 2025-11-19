# Web Interface untuk PDF & Image Extractor

Web application dengan Flask untuk upload dan extract text dari PDF dan gambar dengan OCR.

## Fitur Web Interface

- 📤 **Upload Form dengan Drag & Drop**: Upload file dengan mudah
- 👁️ **Preview File**: Lihat preview file sebelum processing
- 🎯 **Auto-detect Document Type**: Otomatis deteksi KTP, SIM, atau dokumen umum
- 🔍 **Pilihan OCR Engine**: Tesseract (cepat) atau EasyOCR (akurat untuk Indonesia)
- 📊 **Display Hasil**: Tampilkan hasil extraction dalam format yang rapi
- 💾 **Download Results**: Download text, JSON data, dan processed image
- 📱 **Responsive Design**: Berfungsi baik di desktop dan mobile

## Instalasi

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-ind poppler-utils
```

**macOS:**
```bash
brew install tesseract tesseract-lang poppler
```

## Menjalankan Web Application

### Development Mode

```bash
python app.py
```

Aplikasi akan berjalan di: **http://localhost:5000**

### Production Mode (dengan Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Jalankan dengan gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Cara Menggunakan Web Interface

### 1. Upload File

- **Drag & Drop**: Seret file ke area upload
- **Click to Select**: Klik tombol "Choose File" untuk pilih file
- Supported formats: PDF, JPG, PNG, TIFF, BMP
- Maximum file size: 16MB

### 2. Pilih Options

**Document Type:**
- **Auto Detect**: Otomatis deteksi jenis dokumen
- **KTP**: Parse sebagai Kartu Tanda Penduduk
- **SIM**: Parse sebagai Surat Izin Mengemudi
- **General**: Extract text biasa

**OCR Engine (untuk gambar):**
- **Tesseract**: Cepat, cocok untuk dokumen sederhana
- **EasyOCR**: Lebih akurat untuk teks Indonesia (recommended)

### 3. Process File

Klik tombol "Process File" dan tunggu hingga selesai.

### 4. Lihat Hasil

Setelah processing selesai, akan ditampilkan:
- **Document Information**: Info file dan hasil extraction
- **Extracted Data**: Data terstruktur untuk KTP/SIM
- **Extracted Text**: Text yang berhasil di-extract
- **Download Options**: Download hasil dalam berbagai format

## Screenshot Workflow

```
1. Upload Page
   ↓
2. File Preview + Options
   ↓
3. Processing (Loading...)
   ↓
4. Results Display
   - Document Info
   - KTP/SIM Data (jika applicable)
   - Extracted Text
   - Download Buttons
```

## API Endpoints

### POST /upload

Upload dan process file.

**Parameters:**
- `file`: File to upload (multipart/form-data)
- `type`: Document type ('auto', 'ktp', 'sim', 'general')
- `ocr_engine`: OCR engine ('tesseract' or 'easyocr')

**Response:**
```json
{
  "type": "image",
  "filename": "ktp.jpg",
  "ocr_engine": "easyocr",
  "data": {
    "text": "extracted text...",
    "document_type": "KTP",
    "ktp": {
      "nik": "1234567890123456",
      "nama": "JOHN DOE",
      ...
    },
    "text_file": "ktp_text.txt",
    "json_file": "ktp_ktp.json",
    "processed_image": "ktp_processed.png"
  }
}
```

### GET /download/<filename>

Download processed file.

### GET /preview/<filename>

Preview uploaded or processed image.

### GET /health

Health check endpoint.

## File Structure

```
project04/
├── app.py                 # Flask application
├── pdf_extractor.py       # PDF extraction logic
├── image_extractor.py     # Image OCR logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main page template
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── main.js       # JavaScript logic
├── uploads/              # Uploaded files (auto-created)
└── outputs/              # Processed files (auto-created)
```

## Konfigurasi

Edit `app.py` untuk mengubah konfigurasi:

```python
app.config['SECRET_KEY'] = 'your-secret-key'  # Ganti dengan secret key Anda
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size (16MB)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
```

## Cleanup Otomatis

Aplikasi secara otomatis menghapus file yang lebih dari 1 jam di folder `uploads/` dan `outputs/` untuk menghemat space.

Edit di `cleanup_old_files()` untuk mengubah durasi:

```python
max_age = 3600  # 1 hour (dalam detik)
```

## Tips Penggunaan

1. **Untuk dokumen Indonesia (KTP/SIM)**: Gunakan EasyOCR untuk hasil lebih akurat
2. **Untuk dokumen bahasa Inggris**: Tesseract sudah cukup dan lebih cepat
3. **Kualitas gambar**: Upload gambar dengan resolusi tinggi (300 DPI+) untuk hasil terbaik
4. **File besar**: Kompress PDF terlebih dahulu jika ukuran > 16MB

## Troubleshooting

### Port 5000 sudah digunakan

Ubah port di `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Ganti 5000 ke 8080
```

### Error "No module named 'flask'"

Install Flask:
```bash
pip install flask
```

### OCR tidak akurat

- Gunakan EasyOCR untuk teks Indonesia
- Upload gambar dengan kualitas lebih baik
- Pastikan pencahayaan gambar baik

### File upload gagal

- Cek ukuran file (max 16MB)
- Cek format file (PDF, JPG, PNG, TIFF, BMP)
- Cek permission folder `uploads/`

## Security Notes

Untuk production:
1. Ganti `SECRET_KEY` dengan random string yang aman
2. Gunakan HTTPS
3. Add rate limiting
4. Add user authentication jika diperlukan
5. Scan uploaded files untuk virus/malware

## Development

Untuk development dengan auto-reload:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## Production Deployment

Contoh deployment dengan Nginx + Gunicorn:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

## License

MIT License

## Author

Created for easy PDF and Image text extraction with web interface.
