import os
import sys
import json

os.chdir("/app")
sys.path.append("/app")

from services.gemini_service import extract_invoice_header
from services.pdf_utils import pdf_to_png_images_bytes

def test_extraction():
    file_path = "/app/facture_16.pdf"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"--- Extracting Header for {file_path} ---")
    try:
        images = pdf_to_png_images_bytes(file_path, dpi=300, max_pages=1)
        if not images:
            print("Failed to convert PDF")
            return
            
        header = extract_invoice_header(images[0], mime_type="image/png")
        print("\nExtracted Header:")
        print(json.dumps(header, indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_extraction()
