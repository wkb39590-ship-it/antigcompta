import os
import sys
import re
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

def diag_file(filepath):
    print(f"--- Diagnostic pour : {filepath} ---")
    
    text = ""
    if filepath.lower().endswith('.pdf'):
        doc = fitz.open(filepath)
        page = doc[0]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img, lang='fra+eng')
    else:
        text = pytesseract.image_to_string(Image.open(filepath), lang='fra+eng')
    
    print("TEXTE BRUT EXTRAIT :")
    print("-" * 20)
    print(text)
    print("-" * 20)
    
    # Test des regex
    patterns_num = [
        r"Facture\s*[\n\r\t]*([A-Z0-9/\-\.]{3,20})", 
        r"N[°º.o]?\s*[:\-]?\s*([A-Z0-9/\-\.]{3,20})",
    ]
    for p in patterns_num:
        m = re.search(p, text, re.I)
        if m:
            print(f"MATCH NUMERO: {m.group(1)} (Pattern: {p})")
            
    match_date = re.search(r"Date\s*[\n\r\t]*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})", text, re.I)
    if match_date:
        print(f"MATCH DATE: {match_date.group(1)}")

if __name__ == "__main__":
    # On prend le fichier le plus récent dans uploads
    uploads_dir = "uploads"
    files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
    files.sort(key=os.path.getmtime, reverse=True)
    
    if files:
        diag_file(files[0])
    else:
        print("Aucun fichier trouvé dans uploads/")
