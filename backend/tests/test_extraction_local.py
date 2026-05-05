
import os
import sys
from dotenv import load_dotenv

# Ajoute le dossier actuel au path pour importer les services
sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv()

from services.gemini_service import extract_invoice_header
from services.pdf_utils import pdf_to_png_images_bytes

def test_extraction():
    pdf_path = "facture_16.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found")
        return

    print(f"Testing extraction on {pdf_path}...")
    try:
        images = pdf_to_png_images_bytes(pdf_path)
        result = extract_invoice_header(images, mime_type="image/png")
        print("\n--- Extraction Results ---")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    test_extraction()
