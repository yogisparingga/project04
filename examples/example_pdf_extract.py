"""
Example: Extract text and images from PDF
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdf_extractor import PDFExtractor


def main():
    # Example PDF file path
    pdf_file = "sample.pdf"

    # Check if file exists
    if not Path(pdf_file).exists():
        print(f"Error: {pdf_file} not found!")
        print("Please provide a PDF file named 'sample.pdf' in the current directory")
        return

    print("="*60)
    print("PDF EXTRACTION EXAMPLE")
    print("="*60)

    # Initialize extractor
    extractor = PDFExtractor(pdf_file)

    # 1. Extract text
    print("\n1. Extracting text...")
    text = extractor.extract_text()
    print(f"Extracted {len(text)} characters")
    print(f"First 500 characters:\n{text[:500]}...")

    # Save to file
    output_text_file = "output_text.txt"
    Path(output_text_file).write_text(text, encoding='utf-8')
    print(f"Full text saved to: {output_text_file}")

    # 2. Extract tables
    print("\n2. Extracting tables...")
    tables = extractor.extract_tables("output_tables")
    print(f"Found {len(tables)} table(s)")
    if tables:
        print("Tables saved to: output_tables/")

    # 3. Convert to images
    print("\n3. Converting PDF pages to images...")
    images = extractor.pdf_to_images("output_images", dpi=200)
    print(f"Converted {len(images)} page(s)")
    print("Images saved to: output_images/")

    print("\n" + "="*60)
    print("EXTRACTION COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    main()
