"""
Example: Extract data from SIM (Indonesian driver's license)
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_extractor import ImageExtractor


def main():
    # Example SIM image file path
    sim_file = "sim_sample.jpg"

    # Check if file exists
    if not Path(sim_file).exists():
        print(f"Error: {sim_file} not found!")
        print("Please provide a SIM image file named 'sim_sample.jpg' in the current directory")
        print("\nYou can use any image file. Just rename it or change the 'sim_file' variable.")
        return

    print("="*60)
    print("SIM EXTRACTION EXAMPLE")
    print("="*60)

    # Initialize extractor with EasyOCR (better for Indonesian text)
    print("\nInitializing OCR engine (EasyOCR)...")
    print("Note: First run will download language models (may take a few minutes)")

    extractor = ImageExtractor(sim_file, ocr_engine='easyocr')

    # Extract raw text
    print("\n1. Extracting raw text from SIM...")
    text = extractor.extract_text()

    print("\n" + "-"*60)
    print("RAW EXTRACTED TEXT:")
    print("-"*60)
    print(text)

    # Parse SIM data
    print("\n2. Parsing SIM fields...")
    sim_data = extractor.parse_sim()

    print("\n" + "="*60)
    print("PARSED SIM DATA:")
    print("="*60)

    # Display in formatted way
    for key, value in sim_data.items():
        if value:
            field_name = key.replace('_', ' ').title()
            print(f"{field_name:20s}: {value}")

    # Save as JSON
    json_output = "sim_data.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(sim_data, f, indent=2, ensure_ascii=False)
    print(f"\nData saved to: {json_output}")

    # Save preprocessed image
    processed_image = "sim_processed.png"
    extractor.save_processed_image(processed_image)
    print(f"Preprocessed image saved to: {processed_image}")

    print("\n" + "="*60)
    print("EXTRACTION COMPLETE!")
    print("="*60)


if __name__ == '__main__':
    main()
