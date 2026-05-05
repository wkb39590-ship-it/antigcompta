
import os
import sys
from pathlib import Path

# Add app to path
sys.path.append(os.getcwd())

from services.gemini_service import extract_bank_statement
from services.pdf_utils import pdf_to_png_images_bytes

def test_extraction(file_path):
    print(f"Testing extraction for: {file_path}")
    ext = Path(file_path).suffix.lower()
    
    with open(file_path, "rb") as f:
        image_data = f.read()
    
    if ext == ".pdf":
        mime_type = "application/pdf"
    else:
        mime_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"

    print("Calling Gemini extraction...")
    try:
        result = extract_bank_statement(image_data, mime_type=mime_type)
        print("Extraction Result:")
        import json
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    # Try one of the uploaded files
    upload_dir = Path("uploads")
    pdfs = list(upload_dir.glob("*.pdf"))
    if pdfs:
        # Sort by mtime to get the latest
        pdfs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        test_extraction(str(pdfs[0]))
    else:
        print("No PDF files found in uploads/")
