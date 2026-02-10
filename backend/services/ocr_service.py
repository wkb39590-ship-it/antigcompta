import os
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

class OCRService:
    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        # Images
        if ext in [".png", ".jpg", ".jpeg"]:
            img = Image.open(file_path)
            return pytesseract.image_to_string(img, lang="fra")

        # PDF
        if ext == ".pdf":
            pages = convert_from_path(file_path)
            texts = []
            for page in pages:
                texts.append(pytesseract.image_to_string(page, lang="fra"))
            return "\n".join(texts)

        raise ValueError(f"Format non supporté: {ext}")
