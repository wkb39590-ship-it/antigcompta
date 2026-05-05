
import os
import sys
import json
import asyncio

# Setup path
os.chdir("/app")
sys.path.append("/app")

# Import the functions directly
from services.gemini_service import extract_invoice_header, extract_invoice_lines

async def test_extraction():
    file_path = "/app/uploads/a431c6e9-b632-4dee-b2cd-4c665210fdfb.jpg"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"--- Extracting Header for {file_path} ---")
    try:
        # We need to read the file as bytes
        with open(file_path, "rb") as f:
            image_data = f.read()
        
        # Test Header Extraction
        header = await extract_invoice_header(image_data)
        print("\nExtracted Header:")
        print(json.dumps(header, indent=2))
        
        # Test Lines Extraction
        lines = await extract_invoice_lines(image_data)
        print("\nExtracted Lines Count:", len(lines))
        if lines:
            print(json.dumps(lines[0], indent=2), "... (first line)")

    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_extraction())
