from services.ocr_service import OCRService

ocr = OCRService()

text = ocr.extract_text("uploads/test_facture.pdf")

print("====== TEXTE OCR PDF ======")
print(text)
