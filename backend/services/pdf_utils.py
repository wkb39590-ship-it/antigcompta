"""
pdf_utils.py — Conversion PDF → images PNG en mémoire (utilisant PyMuPDF)
"""
import io
from typing import List

try:
    import fitz  # PyMuPDF
    _HAS_FITZ = True
except ImportError:
    _HAS_FITZ = False


def pdf_to_png_images_bytes(
    pdf_path: str,
    dpi: int = 300,
    max_pages: int = 10,
) -> List[bytes]:
    """
    Convertit un PDF en liste de bytes PNG (une entrée par page).
    Utilise PyMuPDF (fitz) pour éviter la dépendance externe Poppler.
    """
    if not _HAS_FITZ:
        return []

    result = []
    try:
        doc = fitz.open(pdf_path)
        for i in range(min(len(doc), max_pages)):
            page = doc.load_page(i)
            # Calculer le facteur de zoom pour le DPI souhaité (72 par défaut dans PDF)
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convertir en bytes PNG
            img_data = pix.tobytes("png")
            result.append(img_data)
        doc.close()
    except Exception as e:
        print(f"[PDF_UTILS] Erreur conversion PDF: {str(e)}")
        
    return result
