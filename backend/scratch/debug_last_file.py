
import os
import sys
from dotenv import load_dotenv

# Path fix
sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv()

from services.gemini_service import extract_invoice_full
from services.pdf_utils import pdf_to_png_images_bytes

def test():
    test_file = "backend/uploads/31ea839b-529a-48b1-a96c-247384b2ca73.pdf"
    print(f"Testing Gemini with file: {test_file}")

    try:
        image_data = pdf_to_png_images_bytes(test_file)
        mime_type = "image/png"
        
        # Contexte société
        context_text = "Nom de notre société: STE Comptoire Arrahma S.A.R.L\nNotre ICE: 02012861000010"

        result = extract_invoice_full(image_data, mime_type=mime_type, context_text=context_text)
        print("\n--- Result ---")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n--- ERROR ---")
        print(e)

if __name__ == "__main__":
    test()
