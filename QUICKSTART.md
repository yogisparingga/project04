# Quick Start Guide

Panduan cepat untuk memulai menggunakan PDF & Image Extractor.

## Instalasi Cepat

### 1. Install Dependencies

```bash
# Jalankan setup script (Linux/Mac)
./setup.sh

# Atau install manual
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-ind poppler-utils
```

**macOS:**
```bash
brew install tesseract tesseract-lang poppler
```

**Windows:**
- Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download Poppler: http://blog.alivate.com.au/poppler-windows/

## Contoh Penggunaan

### Extract Text dari PDF

```bash
python pdf_extractor.py dokumen.pdf -t hasil.txt
```

### Extract KTP

```bash
python image_extractor.py foto_ktp.jpg -k
```

Output:
```
NIK: 1234567890123456
NAMA: JOHN DOE
TEMPAT LAHIR: Jakarta
TANGGAL LAHIR: 01-01-1990
...
```

### Extract KTP dengan JSON

```bash
python image_extractor.py foto_ktp.jpg -k --json
```

Output:
```json
{
  "nik": "1234567890123456",
  "nama": "JOHN DOE",
  "tempat_lahir": "Jakarta",
  "tanggal_lahir": "01-01-1990",
  ...
}
```

### Extract SIM

```bash
python image_extractor.py foto_sim.jpg -s
```

### Menggunakan EasyOCR (Lebih Akurat untuk Teks Indonesia)

```bash
python image_extractor.py foto_ktp.jpg -e easyocr -k
```

**Note:** EasyOCR akan download model pada penggunaan pertama (sekitar 100MB)

## Contoh Kode Python

### Extract KTP

```python
from image_extractor import ImageExtractor

# Gunakan EasyOCR untuk akurasi lebih baik
extractor = ImageExtractor('ktp.jpg', ocr_engine='easyocr')

# Parse data KTP
ktp_data = extractor.parse_ktp()

print(f"NIK: {ktp_data['nik']}")
print(f"Nama: {ktp_data['nama']}")
print(f"Alamat: {ktp_data['alamat']}")
```

### Extract PDF

```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor('dokumen.pdf')

# Extract text
text = extractor.extract_text('output.txt')

# Convert ke images
images = extractor.pdf_to_images('output_images/')
```

## Jalankan Contoh

```bash
# PDF extraction
cd examples
python example_pdf_extract.py

# KTP extraction
python example_ktp_extract.py

# SIM extraction
python example_sim_extract.py

# Batch processing
python example_batch_process.py
```

## Tips

1. **Kualitas Gambar**: Gunakan resolusi tinggi (300 DPI atau lebih)
2. **OCR Engine**:
   - Tesseract: Lebih cepat, untuk dokumen sederhana
   - EasyOCR: Lebih akurat untuk teks Indonesia
3. **Preprocessing**: Aktif secara default untuk hasil lebih baik
4. **Format**: Mendukung JPG, PNG, TIFF, BMP

## Troubleshooting

### Error: "pytesseract: command not found"
Install Tesseract OCR sistem package (lihat bagian instalasi)

### Error: "Failed to load image"
Pastikan file gambar ada dan format didukung

### OCR kurang akurat
- Coba gunakan EasyOCR: `-e easyocr`
- Pastikan kualitas gambar bagus
- Gunakan pencahayaan yang baik saat memfoto dokumen

## Bantuan

```bash
# Lihat semua opsi PDF extractor
python pdf_extractor.py --help

# Lihat semua opsi Image extractor
python image_extractor.py --help
```

## Lisensi

MIT License - Bebas digunakan dan dimodifikasi.
