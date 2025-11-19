#!/bin/bash

echo "======================================================"
echo "PDF & Image Extractor - Setup Script"
echo "======================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed!"
    exit 1
fi

echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install Python dependencies!"
    exit 1
fi

echo ""
echo "======================================================"
echo "Checking system dependencies..."
echo "======================================================"

# Check for Tesseract
echo ""
echo "Checking for Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    tesseract --version
    echo "✓ Tesseract is installed"
else
    echo "✗ Tesseract is NOT installed"
    echo ""
    echo "To install Tesseract:"
    echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-ind"
    echo "  macOS: brew install tesseract tesseract-lang"
    echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
fi

# Check for poppler (pdftoimage)
echo ""
echo "Checking for poppler-utils (for PDF to image conversion)..."
if command -v pdftoimage &> /dev/null || command -v pdftoppm &> /dev/null; then
    echo "✓ poppler-utils is installed"
else
    echo "✗ poppler-utils is NOT installed"
    echo ""
    echo "To install poppler-utils:"
    echo "  Ubuntu/Debian: sudo apt-get install poppler-utils"
    echo "  macOS: brew install poppler"
    echo "  Windows: Download from http://blog.alivate.com.au/poppler-windows/"
fi

echo ""
echo "======================================================"
echo "Setup Complete!"
echo "======================================================"
echo ""
echo "Next steps:"
echo "1. Make sure Tesseract and poppler-utils are installed (see above)"
echo "2. Try running the examples:"
echo "   python pdf_extractor.py --help"
echo "   python image_extractor.py --help"
echo "   python examples/example_pdf_extract.py"
echo ""
