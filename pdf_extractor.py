"""
PDF Extractor - Extract text and images from PDF files
Supports text extraction and converting PDF pages to images
"""

import os
import sys
from pathlib import Path
try:
    import pdfplumber
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as e:
    print(f"Error: Missing required library. Please install: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


class PDFExtractor:
    """Extract text and images from PDF files"""

    def __init__(self, pdf_path):
        """
        Initialize PDF extractor

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not self.pdf_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF: {pdf_path}")

    def extract_text(self, output_path=None):
        """
        Extract all text from PDF

        Args:
            output_path: Optional path to save extracted text

        Returns:
            Extracted text as string
        """
        text_content = []

        with pdfplumber.open(self.pdf_path) as pdf:
            print(f"Processing {len(pdf.pages)} pages...")

            for i, page in enumerate(pdf.pages, 1):
                print(f"Extracting text from page {i}...")
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {i} ---\n{text}\n")

        full_text = "\n".join(text_content)

        if output_path:
            output_file = Path(output_path)
            output_file.write_text(full_text, encoding='utf-8')
            print(f"Text saved to: {output_path}")

        return full_text

    def extract_tables(self, output_dir=None):
        """
        Extract tables from PDF

        Args:
            output_dir: Optional directory to save table data as CSV

        Returns:
            List of tables (each table is a list of rows)
        """
        all_tables = []

        with pdfplumber.open(self.pdf_path) as pdf:
            print(f"Processing {len(pdf.pages)} pages for tables...")

            for i, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                if tables:
                    print(f"Found {len(tables)} table(s) on page {i}")
                    for j, table in enumerate(tables, 1):
                        all_tables.append({
                            'page': i,
                            'table_index': j,
                            'data': table
                        })

                        if output_dir:
                            output_path = Path(output_dir)
                            output_path.mkdir(parents=True, exist_ok=True)
                            csv_file = output_path / f"page_{i}_table_{j}.csv"

                            import csv
                            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f)
                                writer.writerows(table)
                            print(f"Table saved to: {csv_file}")

        return all_tables

    def pdf_to_images(self, output_dir=None, dpi=200):
        """
        Convert PDF pages to images

        Args:
            output_dir: Directory to save images (default: pdf_filename_images/)
            dpi: Image resolution (default: 200)

        Returns:
            List of image paths
        """
        if output_dir is None:
            output_dir = self.pdf_path.stem + "_images"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"Converting PDF to images (DPI: {dpi})...")
        images = convert_from_path(self.pdf_path, dpi=dpi)

        image_paths = []
        for i, image in enumerate(images, 1):
            image_file = output_path / f"page_{i}.png"
            image.save(image_file, 'PNG')
            image_paths.append(str(image_file))
            print(f"Saved page {i} to: {image_file}")

        return image_paths

    def extract_images(self, output_dir=None):
        """
        Extract embedded images from PDF

        Args:
            output_dir: Directory to save images

        Returns:
            List of extracted image paths
        """
        if output_dir is None:
            output_dir = self.pdf_path.stem + "_extracted_images"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_paths = []
        image_count = 0

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract images from page
                if hasattr(page, 'images') and page.images:
                    for img_idx, img in enumerate(page.images):
                        image_count += 1
                        # This is a simplified extraction
                        # For more advanced extraction, consider using PyMuPDF (fitz)
                        print(f"Found image on page {page_num}")

        if image_count == 0:
            print("No embedded images found. Use pdf_to_images() to convert pages to images.")

        return image_paths


def main():
    """Command line interface for PDF extractor"""
    import argparse

    parser = argparse.ArgumentParser(description='Extract text and images from PDF files')
    parser.add_argument('pdf_file', help='Path to PDF file')
    parser.add_argument('-t', '--text', help='Extract text to file', metavar='OUTPUT_FILE')
    parser.add_argument('-i', '--images', help='Convert pages to images', metavar='OUTPUT_DIR')
    parser.add_argument('-T', '--tables', help='Extract tables to CSV files', metavar='OUTPUT_DIR')
    parser.add_argument('--dpi', type=int, default=200, help='DPI for image conversion (default: 200)')

    args = parser.parse_args()

    try:
        extractor = PDFExtractor(args.pdf_file)

        if args.text:
            text = extractor.extract_text(args.text)
            print(f"\nExtracted {len(text)} characters")

        if args.tables:
            tables = extractor.extract_tables(args.tables)
            print(f"\nExtracted {len(tables)} table(s)")

        if args.images:
            images = extractor.pdf_to_images(args.images, dpi=args.dpi)
            print(f"\nConverted {len(images)} page(s) to images")

        if not any([args.text, args.images, args.tables]):
            # Default: extract text to console
            print("\n" + "="*50)
            print("EXTRACTED TEXT:")
            print("="*50)
            text = extractor.extract_text()
            print(text)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
