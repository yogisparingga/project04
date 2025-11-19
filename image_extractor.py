"""
Image Extractor with OCR - Extract text from images using OCR
Supports KTP, SIM, and other Indonesian documents
"""

import os
import sys
import re
from pathlib import Path
try:
    from PIL import Image
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Error: Missing required library. Please install: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


class ImageExtractor:
    """Extract text from images using OCR"""

    def __init__(self, image_path, ocr_engine='tesseract'):
        """
        Initialize Image extractor

        Args:
            image_path: Path to image file
            ocr_engine: OCR engine to use ('tesseract' or 'easyocr')
        """
        self.image_path = Path(image_path)
        if not self.image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        self.ocr_engine = ocr_engine.lower()
        self.image = None
        self.text = None

        # Initialize OCR engine
        if self.ocr_engine == 'tesseract':
            try:
                import pytesseract
                self.ocr = pytesseract
            except ImportError:
                print("Error: pytesseract not installed. Run: pip install pytesseract")
                print("Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
                sys.exit(1)
        elif self.ocr_engine == 'easyocr':
            try:
                import easyocr
                print("Initializing EasyOCR (this may take a moment)...")
                self.ocr = easyocr.Reader(['id', 'en'])  # Indonesian and English
            except ImportError:
                print("Error: easyocr not installed. Run: pip install easyocr")
                sys.exit(1)
        else:
            raise ValueError(f"Unknown OCR engine: {ocr_engine}. Use 'tesseract' or 'easyocr'")

    def preprocess_image(self, image_path=None):
        """
        Preprocess image for better OCR results

        Args:
            image_path: Path to image (uses self.image_path if not provided)

        Returns:
            Preprocessed image as numpy array
        """
        if image_path is None:
            image_path = self.image_path

        # Read image
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to get binary image
        # Using adaptive threshold for better results with varying lighting
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary)

        # Optional: Resize for better OCR (if image is too small)
        height, width = denoised.shape
        if height < 500:
            scale = 500 / height
            new_width = int(width * scale)
            denoised = cv2.resize(denoised, (new_width, 500))

        self.image = denoised
        return denoised

    def extract_text(self, preprocess=True, lang='ind+eng'):
        """
        Extract text from image using OCR

        Args:
            preprocess: Whether to preprocess image (default: True)
            lang: Language for Tesseract (default: 'ind+eng' for Indonesian and English)

        Returns:
            Extracted text as string
        """
        if preprocess:
            img = self.preprocess_image()
        else:
            img = cv2.imread(str(self.image_path))

        print(f"Extracting text using {self.ocr_engine}...")

        if self.ocr_engine == 'tesseract':
            # Use Tesseract OCR
            self.text = self.ocr.image_to_string(img, lang=lang)
        elif self.ocr_engine == 'easyocr':
            # Use EasyOCR
            result = self.ocr.readtext(img, detail=0)
            self.text = '\n'.join(result)

        return self.text

    def extract_with_boxes(self, preprocess=True):
        """
        Extract text with bounding box information

        Args:
            preprocess: Whether to preprocess image

        Returns:
            List of dictionaries with text and bounding box info
        """
        if preprocess:
            img = self.preprocess_image()
        else:
            img = cv2.imread(str(self.image_path))

        results = []

        if self.ocr_engine == 'tesseract':
            # Get detailed OCR data
            data = self.ocr.image_to_data(img, output_type=self.ocr.Output.DICT)
            n_boxes = len(data['text'])

            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:  # confidence > 0
                    results.append({
                        'text': data['text'][i],
                        'confidence': data['conf'][i],
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })

        elif self.ocr_engine == 'easyocr':
            # Get detailed OCR data
            result = self.ocr.readtext(img, detail=1)

            for bbox, text, conf in result:
                results.append({
                    'text': text,
                    'confidence': conf,
                    'bbox': bbox
                })

        return results

    def parse_ktp(self, text=None):
        """
        Parse KTP (Indonesian ID card) data from OCR text

        Args:
            text: OCR text (uses self.text if not provided)

        Returns:
            Dictionary with parsed KTP fields
        """
        if text is None:
            if self.text is None:
                self.extract_text()
            text = self.text

        ktp_data = {
            'nik': None,
            'nama': None,
            'tempat_lahir': None,
            'tanggal_lahir': None,
            'jenis_kelamin': None,
            'alamat': None,
            'rt_rw': None,
            'kelurahan': None,
            'kecamatan': None,
            'agama': None,
            'status_perkawinan': None,
            'pekerjaan': None,
            'kewarganegaraan': None,
            'berlaku_hingga': None
        }

        # NIK: 16 digits
        nik_match = re.search(r'\b(\d{16})\b', text)
        if nik_match:
            ktp_data['nik'] = nik_match.group(1)

        # Nama
        nama_match = re.search(r'Nama\s*:?\s*([A-Z\s]+)', text, re.IGNORECASE)
        if nama_match:
            ktp_data['nama'] = nama_match.group(1).strip()

        # Tempat/Tanggal Lahir
        ttl_match = re.search(
            r'(?:Tempat.*?Lahir|TTL)\s*:?\s*([A-Za-z\s]+),?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            text,
            re.IGNORECASE
        )
        if ttl_match:
            ktp_data['tempat_lahir'] = ttl_match.group(1).strip()
            ktp_data['tanggal_lahir'] = ttl_match.group(2).strip()

        # Jenis Kelamin
        jk_match = re.search(r'(?:Jenis.*?Kelamin|Kelamin)\s*:?\s*(LAKI-LAKI|PEREMPUAN)', text, re.IGNORECASE)
        if jk_match:
            ktp_data['jenis_kelamin'] = jk_match.group(1).upper()

        # Alamat
        alamat_match = re.search(r'Alamat\s*:?\s*([^\n]+)', text, re.IGNORECASE)
        if alamat_match:
            ktp_data['alamat'] = alamat_match.group(1).strip()

        # RT/RW
        rtrw_match = re.search(r'RT[/\s]*RW\s*:?\s*(\d+)[/\s]+(\d+)', text, re.IGNORECASE)
        if rtrw_match:
            ktp_data['rt_rw'] = f"{rtrw_match.group(1)}/{rtrw_match.group(2)}"

        # Agama
        agama_match = re.search(r'Agama\s*:?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
        if agama_match:
            ktp_data['agama'] = agama_match.group(1).strip()

        # Status Perkawinan
        status_match = re.search(
            r'(?:Status.*?Perkawinan|Perkawinan)\s*:?\s*(BELUM KAWIN|KAWIN|CERAI)',
            text,
            re.IGNORECASE
        )
        if status_match:
            ktp_data['status_perkawinan'] = status_match.group(1).upper()

        # Pekerjaan
        pekerjaan_match = re.search(r'Pekerjaan\s*:?\s*([^\n]+)', text, re.IGNORECASE)
        if pekerjaan_match:
            ktp_data['pekerjaan'] = pekerjaan_match.group(1).strip()

        # Kewarganegaraan
        warga_match = re.search(r'Kewarganegaraan\s*:?\s*([A-Z\s]+)', text, re.IGNORECASE)
        if warga_match:
            ktp_data['kewarganegaraan'] = warga_match.group(1).strip()

        # Berlaku Hingga
        berlaku_match = re.search(
            r'Berlaku\s+Hingga\s*:?\s*(SEUMUR HIDUP|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            text,
            re.IGNORECASE
        )
        if berlaku_match:
            ktp_data['berlaku_hingga'] = berlaku_match.group(1).upper()

        return ktp_data

    def parse_sim(self, text=None):
        """
        Parse SIM (Indonesian driver's license) data from OCR text

        Args:
            text: OCR text (uses self.text if not provided)

        Returns:
            Dictionary with parsed SIM fields
        """
        if text is None:
            if self.text is None:
                self.extract_text()
            text = self.text

        sim_data = {
            'nomor_sim': None,
            'nama': None,
            'tempat_lahir': None,
            'tanggal_lahir': None,
            'jenis_kelamin': None,
            'alamat': None,
            'pekerjaan': None,
            'golongan_darah': None,
            'tinggi_badan': None,
            'berlaku_hingga': None,
            'jenis_sim': None
        }

        # Nomor SIM
        sim_match = re.search(r'\b(\d{12,14})\b', text)
        if sim_match:
            sim_data['nomor_sim'] = sim_match.group(1)

        # Jenis SIM (A, B1, B2, C, D, dll)
        jenis_match = re.search(r'SIM\s*([A-D][I1-2]?)', text, re.IGNORECASE)
        if jenis_match:
            sim_data['jenis_sim'] = jenis_match.group(1).upper()

        # Nama
        nama_match = re.search(r'Nama\s*:?\s*([A-Z\s]+)', text, re.IGNORECASE)
        if nama_match:
            sim_data['nama'] = nama_match.group(1).strip()

        # Tempat/Tanggal Lahir
        ttl_match = re.search(
            r'(?:Tempat.*?Lahir|TTL)\s*:?\s*([A-Za-z\s]+),?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            text,
            re.IGNORECASE
        )
        if ttl_match:
            sim_data['tempat_lahir'] = ttl_match.group(1).strip()
            sim_data['tanggal_lahir'] = ttl_match.group(2).strip()

        # Jenis Kelamin
        jk_match = re.search(r'(?:Jenis.*?Kelamin|Kelamin)\s*:?\s*(LAKI-LAKI|PEREMPUAN|L|P)', text, re.IGNORECASE)
        if jk_match:
            jk = jk_match.group(1).upper()
            sim_data['jenis_kelamin'] = 'LAKI-LAKI' if jk in ['LAKI-LAKI', 'L'] else 'PEREMPUAN'

        # Alamat
        alamat_match = re.search(r'Alamat\s*:?\s*([^\n]+)', text, re.IGNORECASE)
        if alamat_match:
            sim_data['alamat'] = alamat_match.group(1).strip()

        # Golongan Darah
        gol_darah_match = re.search(r'Gol.*?Darah\s*:?\s*([ABO][-+]?)', text, re.IGNORECASE)
        if gol_darah_match:
            sim_data['golongan_darah'] = gol_darah_match.group(1).upper()

        # Tinggi Badan
        tinggi_match = re.search(r'Tinggi\s*:?\s*(\d{2,3})', text, re.IGNORECASE)
        if tinggi_match:
            sim_data['tinggi_badan'] = tinggi_match.group(1)

        # Berlaku Hingga
        berlaku_match = re.search(
            r'Berlaku\s+(?:Hingga|s[/.]?d)\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            text,
            re.IGNORECASE
        )
        if berlaku_match:
            sim_data['berlaku_hingga'] = berlaku_match.group(1)

        return sim_data

    def save_processed_image(self, output_path):
        """
        Save preprocessed image

        Args:
            output_path: Path to save image
        """
        if self.image is None:
            self.preprocess_image()

        cv2.imwrite(str(output_path), self.image)
        print(f"Processed image saved to: {output_path}")


def main():
    """Command line interface for Image extractor"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Extract text from images using OCR')
    parser.add_argument('image_file', help='Path to image file')
    parser.add_argument('-e', '--engine', choices=['tesseract', 'easyocr'],
                        default='tesseract', help='OCR engine to use')
    parser.add_argument('-o', '--output', help='Save extracted text to file')
    parser.add_argument('-k', '--ktp', action='store_true', help='Parse as KTP document')
    parser.add_argument('-s', '--sim', action='store_true', help='Parse as SIM document')
    parser.add_argument('--no-preprocess', action='store_true', help='Skip image preprocessing')
    parser.add_argument('--save-processed', help='Save preprocessed image to file')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')

    args = parser.parse_args()

    try:
        extractor = ImageExtractor(args.image_file, ocr_engine=args.engine)

        # Extract text
        text = extractor.extract_text(preprocess=not args.no_preprocess)

        # Save preprocessed image if requested
        if args.save_processed:
            extractor.save_processed_image(args.save_processed)

        # Parse specific document types
        if args.ktp:
            ktp_data = extractor.parse_ktp(text)
            if args.json:
                print(json.dumps(ktp_data, indent=2, ensure_ascii=False))
            else:
                print("\n" + "="*50)
                print("KTP DATA:")
                print("="*50)
                for key, value in ktp_data.items():
                    if value:
                        print(f"{key.upper()}: {value}")
        elif args.sim:
            sim_data = extractor.parse_sim(text)
            if args.json:
                print(json.dumps(sim_data, indent=2, ensure_ascii=False))
            else:
                print("\n" + "="*50)
                print("SIM DATA:")
                print("="*50)
                for key, value in sim_data.items():
                    if value:
                        print(f"{key.upper()}: {value}")
        else:
            # Default: print extracted text
            if not args.json:
                print("\n" + "="*50)
                print("EXTRACTED TEXT:")
                print("="*50)
            print(text)

        # Save to file if requested
        if args.output:
            Path(args.output).write_text(text, encoding='utf-8')
            print(f"\nText saved to: {args.output}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
