
import os
import sys
from dotenv import load_dotenv

# Path fix
sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv()

from services.gemini_service import extract_invoice_full
from services.pdf_utils import pdf_to_png_images_bytes

def test():
    # Use an existing file from uploads if possible
    upload_dir = "backend/uploads"
    files = [f for f in os.listdir(upload_dir) if f.endswith((".pdf", ".jpg", ".png"))]
    if not files:
        print("No files found in uploads.")
        return

    test_file = os.path.join(upload_dir, files[0])
    print(f"Testing Gemini with file: {test_file}")

    try:
        if test_file.endswith(".pdf"):
            image_data = pdf_to_png_images_bytes(test_file)
            mime_type = "image/png"
        else:
            with open(test_file, "rb") as f:
                image_data = f.read()
            mime_type = "image/jpeg" if test_file.endswith(".jpg") else "image/png"

        result = extract_invoice_full(image_data, mime_type=mime_type)
        print("\n--- Result ---")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n--- ERROR ---")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
