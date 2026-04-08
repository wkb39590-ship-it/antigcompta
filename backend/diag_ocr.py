import os
import sys
from database import SessionLocal
from models import Facture
from services import gemini_service, ocr_service

db = SessionLocal()
f = db.query(Facture).order_by(Facture.id.desc()).first()

if not f:
    print("No facture found")
    sys.exit(1)

print(f"DIAGNOSTIC FACTURE {f.id} : {f.file_path}")
ocr_result = ocr_service.extract(f.file_path)
ocr_text = ocr_result.text if hasattr(ocr_result, 'text') else str(ocr_result)

print("--- OCR TEXT START ---")
print(ocr_text)
print("--- OCR TEXT END ---")

# Test manually with our fuzzy logic
fuzzy_suppliers = ["EL OUJDI", "ELOUJDI", "EL OUSDI", "OUJDI"]
if any(kw in ocr_text.upper() for kw in fuzzy_suppliers):
    print("FUZZY MATCH SUCCESS: EL OUJDI FOUND")
else:
    print("FUZZY MATCH FAILED: EL OUJDI NOT FOUND")
