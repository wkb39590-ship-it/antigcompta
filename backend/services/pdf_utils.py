import io
from typing import List

from pdf2image import convert_from_path


def pdf_to_png_images_bytes(pdf_path: str, dpi: int = 300, max_pages: int = 1) -> List[bytes]:
    """
    Convertit un PDF en images PNG (bytes).
    - dpi 300 = bon compromis
    - max_pages=1 suffit souvent pour une facture
    """
    pages = convert_from_path(pdf_path, dpi=dpi)
    out: List[bytes] = []
    for page in pages[:max_pages]:
        buf = io.BytesIO()
        page.save(buf, format="PNG")
        out.append(buf.getvalue())
    return out
