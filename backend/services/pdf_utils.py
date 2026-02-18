"""
pdf_utils.py — Conversion PDF → images PNG en mémoire
"""
import io
from typing import List

try:
    from pdf2image import convert_from_path
    _HAS_PDF2IMAGE = True
except ImportError:
    _HAS_PDF2IMAGE = False


def pdf_to_png_images_bytes(
    pdf_path: str,
    dpi: int = 300,
    max_pages: int = 10,
) -> List[bytes]:
    """
    Convertit un PDF en liste de bytes PNG (une entrée par page).
    Retourne une liste vide si pdf2image n'est pas disponible.
    """
    if not _HAS_PDF2IMAGE:
        return []

    images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=max_pages)
    result = []
    for img in images:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        result.append(buf.getvalue())
    return result
