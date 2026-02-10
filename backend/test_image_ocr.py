from services.ocr_service import OCRService

ocr = OCRService()

text = ocr.extract_text("uploads/test_image.jpeg")


print("====== TEXTE OCR IMAGE ======")
print(text)
