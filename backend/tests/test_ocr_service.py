from services.ocr_service import OCRService

ocr = OCRService()
text = ocr.extract_text("uploads/test_facture.jpg")  # mets ton fichier ici
print(text)
