"""
Example: Batch process multiple images with OCR
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_extractor import ImageExtractor


def process_image(image_path, output_dir, ocr_engine='tesseract'):
    """
    Process a single image and save results

    Args:
        image_path: Path to image file
        output_dir: Directory to save results
        ocr_engine: OCR engine to use
    """
    print(f"\nProcessing: {image_path.name}")
    print("-" * 50)

    try:
        # Initialize extractor
        extractor = ImageExtractor(str(image_path), ocr_engine=ocr_engine)

        # Extract text
        text = extractor.extract_text()

        # Save text to file
        text_file = output_dir / f"{image_path.stem}.txt"
        text_file.write_text(text, encoding='utf-8')
        print(f"Text saved to: {text_file}")

        # Try to detect document type and parse accordingly
        text_lower = text.lower()

        if 'nik' in text_lower or 'provinsi' in text_lower:
            # Likely a KTP
            print("Detected: KTP document")
            ktp_data = extractor.parse_ktp(text)

            # Save KTP data as JSON
            json_file = output_dir / f"{image_path.stem}_ktp.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(ktp_data, f, indent=2, ensure_ascii=False)
            print(f"KTP data saved to: {json_file}")

        elif 'sim' in text_lower or 'surat izin mengemudi' in text_lower:
            # Likely a SIM
            print("Detected: SIM document")
            sim_data = extractor.parse_sim(text)

            # Save SIM data as JSON
            json_file = output_dir / f"{image_path.stem}_sim.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(sim_data, f, indent=2, ensure_ascii=False)
            print(f"SIM data saved to: {json_file}")

        else:
            print("Document type: General image")

        # Save preprocessed image
        processed_file = output_dir / f"{image_path.stem}_processed.png"
        extractor.save_processed_image(str(processed_file))
        print(f"Processed image saved to: {processed_file}")

        return True

    except Exception as e:
        print(f"Error processing {image_path.name}: {e}")
        return False


def main():
    print("="*60)
    print("BATCH IMAGE PROCESSING EXAMPLE")
    print("="*60)

    # Configuration
    input_dir = Path("input_images")  # Directory containing images
    output_dir = Path("output_results")  # Directory for results
    ocr_engine = 'tesseract'  # or 'easyocr'

    # Supported image formats
    image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']

    # Create directories if they don't exist
    if not input_dir.exists():
        input_dir.mkdir(parents=True)
        print(f"\nCreated directory: {input_dir}")
        print(f"Please add image files to '{input_dir}' and run again.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all images
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_dir.glob(f"*{ext}"))
        image_files.extend(input_dir.glob(f"*{ext.upper()}"))

    if not image_files:
        print(f"\nNo image files found in: {input_dir}")
        print(f"Supported formats: {', '.join(image_extensions)}")
        return

    print(f"\nFound {len(image_files)} image(s)")
    print(f"OCR Engine: {ocr_engine}")
    print(f"Output directory: {output_dir}")

    # Process each image
    success_count = 0
    for i, image_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}]")
        if process_image(image_file, output_dir, ocr_engine):
            success_count += 1

    # Summary
    print("\n" + "="*60)
    print("BATCH PROCESSING COMPLETE!")
    print("="*60)
    print(f"Total images: {len(image_files)}")
    print(f"Successfully processed: {success_count}")
    print(f"Failed: {len(image_files) - success_count}")
    print(f"\nResults saved to: {output_dir}")


if __name__ == '__main__':
    main()
