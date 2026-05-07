import os
import sys
import json
from pprint import pprint

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.gemini_service import extract_invoice_full

def test_extract():
    image_path = "/app/uploads/7a083041-c7cc-48ee-b19e-83310652f78b.png"
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    context = "Nom de notre société : STE COMPTOIRE ARRAHMA SARL\nICE : 002012861000010\nIF : 25005226"
    
    print("Envoi a Gemini...")
    result = extract_invoice_full(
        image_data=image_bytes,
        mime_type="image/png",
        context_text=context
    )
    
    print("--- RESULTAT ---")
    pprint(result)

if __name__ == "__main__":
    test_extract()
