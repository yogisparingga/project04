# PDF & Image Extractor

Simple yet powerful PDF and Image extractor with OCR capabilities, specifically designed for Indonesian documents like KTP and SIM.

## 🌐 Web Interface Available!

This tool now includes a **web interface** for easy file upload and processing!

```bash
python app.py
```

Then open: **http://localhost:5000**

Features:
- 📤 Drag & drop file upload
- 👁️ File preview
- 🎯 Auto-detect document type (KTP/SIM)
- 📊 Beautiful results display
- 💾 Download extracted data

See [WEB_APP_README.md](WEB_APP_README.md) for web interface documentation.

## Features

### PDF Extractor
- Extract text from PDF files
- Extract tables from PDF and save as CSV
- Convert PDF pages to images
- Extract embedded images from PDF
- Support for multi-page documents

### Image Extractor
- OCR text extraction from images
- Support for multiple OCR engines (Tesseract, EasyOCR)
- Image preprocessing for better accuracy
- Specialized parsers for Indonesian documents:
  - KTP (Kartu Tanda Penduduk)
  - SIM (Surat Izin Mengemudi)
- Bounding box detection
- JSON output support

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (Optional but Recommended)

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-ind
```

#### macOS:
```bash
brew install tesseract tesseract-lang
```

#### Windows:
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### 3. Install poppler-utils (for PDF to Image conversion)

#### Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils
```

#### macOS:
```bash
brew install poppler
```

#### Windows:
Download from: http://blog.alivate.com.au/poppler-windows/

## Usage

### PDF Extractor

#### Command Line

```bash
# Extract text from PDF (display in terminal)
python pdf_extractor.py document.pdf

# Extract text to file
python pdf_extractor.py document.pdf -t output.txt

# Convert PDF pages to images
python pdf_extractor.py document.pdf -i output_images/

# Extract tables to CSV files
python pdf_extractor.py document.pdf -T output_tables/

# Convert with custom DPI
python pdf_extractor.py document.pdf -i output_images/ --dpi 300
```

#### Python API

```python
from pdf_extractor import PDFExtractor

# Initialize extractor
extractor = PDFExtractor('document.pdf')

# Extract text
text = extractor.extract_text('output.txt')
print(text)

# Extract tables
tables = extractor.extract_tables('tables_output/')

# Convert PDF to images
images = extractor.pdf_to_images('images_output/', dpi=200)

# Get embedded images
embedded = extractor.extract_images('embedded_output/')
```

### Image Extractor

#### Command Line

```bash
# Extract text from image (using Tesseract)
python image_extractor.py photo.jpg

# Use EasyOCR instead
python image_extractor.py photo.jpg -e easyocr

# Save extracted text to file
python image_extractor.py photo.jpg -o output.txt

# Extract and parse KTP data
python image_extractor.py ktp.jpg -k

# Extract and parse KTP data as JSON
python image_extractor.py ktp.jpg -k --json

# Extract and parse SIM data
python image_extractor.py sim.jpg -s

# Save preprocessed image
python image_extractor.py photo.jpg --save-processed processed.png

# Skip preprocessing
python image_extractor.py photo.jpg --no-preprocess
```

#### Python API

```python
from image_extractor import ImageExtractor

# Initialize extractor with Tesseract
extractor = ImageExtractor('ktp.jpg', ocr_engine='tesseract')

# Or use EasyOCR (better for Indonesian text)
extractor = ImageExtractor('ktp.jpg', ocr_engine='easyocr')

# Extract text
text = extractor.extract_text()
print(text)

# Parse KTP data
ktp_data = extractor.parse_ktp()
print(f"NIK: {ktp_data['nik']}")
print(f"Nama: {ktp_data['nama']}")
print(f"Alamat: {ktp_data['alamat']}")

# Parse SIM data
sim_data = extractor.parse_sim()
print(f"Nomor SIM: {sim_data['nomor_sim']}")
print(f"Nama: {sim_data['nama']}")
print(f"Jenis SIM: {sim_data['jenis_sim']}")

# Get text with bounding boxes
boxes = extractor.extract_with_boxes()
for box in boxes:
    print(f"Text: {box['text']}, Confidence: {box['confidence']}")

# Save preprocessed image
extractor.save_processed_image('processed.png')
```

## Examples

### Example 1: Extract text from PDF and save to file

```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor('invoice.pdf')
text = extractor.extract_text('invoice_text.txt')
print(f"Extracted {len(text)} characters")
```

### Example 2: Convert PDF to images for OCR

```python
from pdf_extractor import PDFExtractor
from image_extractor import ImageExtractor

# Convert PDF to images
pdf_extractor = PDFExtractor('document.pdf')
images = pdf_extractor.pdf_to_images('output_images/', dpi=300)

# OCR each image
for image_path in images:
    img_extractor = ImageExtractor(image_path, ocr_engine='easyocr')
    text = img_extractor.extract_text()
    print(f"\n--- {image_path} ---")
    print(text)
```

### Example 3: Extract KTP data

```python
from image_extractor import ImageExtractor
import json

extractor = ImageExtractor('ktp_scan.jpg', ocr_engine='easyocr')
ktp_data = extractor.parse_ktp()

# Print as JSON
print(json.dumps(ktp_data, indent=2, ensure_ascii=False))

# Access specific fields
if ktp_data['nik']:
    print(f"NIK: {ktp_data['nik']}")
if ktp_data['nama']:
    print(f"Nama: {ktp_data['nama']}")
if ktp_data['alamat']:
    print(f"Alamat: {ktp_data['alamat']}")
```

### Example 4: Extract SIM data

```python
from image_extractor import ImageExtractor

extractor = ImageExtractor('sim_photo.jpg', ocr_engine='tesseract')
sim_data = extractor.parse_sim()

print(f"Nomor SIM: {sim_data['nomor_sim']}")
print(f"Jenis SIM: {sim_data['jenis_sim']}")
print(f"Nama: {sim_data['nama']}")
print(f"Berlaku Hingga: {sim_data['berlaku_hingga']}")
```

### Example 5: Batch process multiple images

```python
from pathlib import Path
from image_extractor import ImageExtractor

image_dir = Path('scanned_documents/')
output_dir = Path('extracted_text/')
output_dir.mkdir(exist_ok=True)

for image_file in image_dir.glob('*.jpg'):
    print(f"Processing {image_file.name}...")

    extractor = ImageExtractor(image_file, ocr_engine='easyocr')
    text = extractor.extract_text()

    # Save to text file
    output_file = output_dir / f"{image_file.stem}.txt"
    output_file.write_text(text, encoding='utf-8')

    print(f"Saved to {output_file}")
```

## OCR Engine Comparison

### Tesseract
- **Pros**: Fast, lightweight, widely used
- **Cons**: Less accurate for Indonesian text
- **Best for**: English documents, simple layouts

### EasyOCR
- **Pros**: Better accuracy for Indonesian text, no additional installation
- **Cons**: Slower, requires more memory, downloads models on first use
- **Best for**: Indonesian documents (KTP, SIM), complex layouts

## KTP Fields Extracted

- NIK (16 digits)
- Nama (Full name)
- Tempat Lahir (Place of birth)
- Tanggal Lahir (Date of birth)
- Jenis Kelamin (Gender)
- Alamat (Address)
- RT/RW
- Kelurahan/Desa
- Kecamatan
- Agama (Religion)
- Status Perkawinan (Marital status)
- Pekerjaan (Occupation)
- Kewarganegaraan (Citizenship)
- Berlaku Hingga (Valid until)

## SIM Fields Extracted

- Nomor SIM (License number)
- Jenis SIM (License type: A, B1, B2, C, D)
- Nama (Full name)
- Tempat Lahir (Place of birth)
- Tanggal Lahir (Date of birth)
- Jenis Kelamin (Gender)
- Alamat (Address)
- Pekerjaan (Occupation)
- Golongan Darah (Blood type)
- Tinggi Badan (Height)
- Berlaku Hingga (Valid until)

## Tips for Better OCR Results

1. **Image Quality**: Use high-resolution scans (300 DPI or higher)
2. **Lighting**: Ensure good, even lighting when photographing documents
3. **Alignment**: Keep the document flat and parallel to the camera
4. **Preprocessing**: The tool automatically preprocesses images, but you can skip it with `--no-preprocess`
5. **OCR Engine**: Try both Tesseract and EasyOCR to see which works better for your documents
6. **Language**: For Indonesian documents, EasyOCR generally provides better results

## Troubleshooting

### "pytesseract: command not found"
Install Tesseract OCR system package (see Installation section)

### "Failed to load image"
Make sure the image file exists and is in a supported format (JPG, PNG, TIFF, etc.)

### "Poor OCR accuracy"
- Try using EasyOCR instead of Tesseract
- Ensure good image quality
- Check if preprocessing helps (enabled by default)
- Increase image DPI when scanning

### "Memory error with EasyOCR"
EasyOCR requires significant memory. Try:
- Using Tesseract instead
- Processing images one at a time
- Reducing image size

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Author

Created for extracting Indonesian documents (KTP, SIM) and general PDF/image text extraction.
