




# import os
# import re
# from dataclasses import dataclass
# from pathlib import Path
# from typing import List, Optional

# import cv2
# import numpy as np
# import pytesseract
# from PIL import Image
# from pdf2image import convert_from_path
# import pdfplumber


# @dataclass
# class OCRResult:
#     text: str
#     method: str          # "pdfplumber" | "tesseract"
#     pages: int
#     chars: int
#     preview: str


# def _normalize_text(text: str) -> str:
#     if not text:
#         return ""
#     t = text.replace("\u00A0", " ")
#     t = t.replace("\r", "\n")
#     t = re.sub(r"[ \t]+", " ", t)
#     t = re.sub(r"\n{3,}", "\n\n", t)
#     return t.strip()


# def _make_preview(text: str, n: int = 1200) -> str:
#     return (text or "").strip()[:n]


# def _count_pdf_pages(pdf_path: str) -> int:
#     try:
#         with pdfplumber.open(pdf_path) as pdf:
#             return len(pdf.pages)
#     except Exception:
#         return 1


# class OCRService:
#     def __init__(self, lang: str = "fra"):
#         self.lang = lang

#     # --------- preprocessing ----------
#     def _preprocess_cv(self, img_bgr: np.ndarray) -> Image.Image:
#         gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
#         gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
#         gray = cv2.bilateralFilter(gray, 9, 75, 75)

#         th = cv2.adaptiveThreshold(
#             gray, 255,
#             cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#             cv2.THRESH_BINARY,
#             31, 10
#         )

#         kernel = np.array([[0, -1, 0],
#                            [-1, 5, -1],
#                            [0, -1, 0]])
#         th = cv2.filter2D(th, -1, kernel)
#         return Image.fromarray(th)

#     def _tesseract_ocr(self, pil_img: Image.Image, psm: int = 6, whitelist: Optional[str] = None) -> str:
#         config = f"--oem 1 --psm {psm}"
#         if whitelist:
#             config += f" -c tessedit_char_whitelist={whitelist}"
#         return pytesseract.image_to_string(pil_img, lang=self.lang, config=config)

#     # --------- date helper (optional) ----------
#     def _extract_date_from_image(self, img_bgr: np.ndarray) -> Optional[str]:
#         h, w = img_bgr.shape[:2]
#         y1 = int(h * 0.20)
#         y2 = int(h * 0.45)
#         zone = img_bgr[y1:y2, 0:w]

#         pre = self._preprocess_cv(zone)
#         wl = "0123456789/:-."

#         candidates = []
#         for psm in (6, 7, 11, 12, 13):
#             candidates.append(self._tesseract_ocr(pre, psm=psm, whitelist=wl))

#         merged = "\n".join(candidates)
#         m = re.search(r"\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b", merged)
#         if m:
#             return m.group(1).replace("-", "/").replace(".", "/")
#         return None

#     # --------- PDF digital ----------
#     def _pdfplumber_text(self, pdf_path: str) -> str:
#         parts: List[str] = []
#         with pdfplumber.open(pdf_path) as pdf:
#             for p in pdf.pages:
#                 parts.append(p.extract_text() or "")
#         return _normalize_text("\n".join(parts))

#     # --------- main ----------
#     def extract(self, file_path: str) -> OCRResult:
#         path = Path(file_path)
#         if not path.exists():
#             raise FileNotFoundError(file_path)

#         ext = path.suffix.lower()

#         # ---- PDF ----
#         if ext == ".pdf":
#             # 1) essayer PDF digital
#             txt = ""
#             try:
#                 txt = self._pdfplumber_text(str(path))
#             except Exception:
#                 txt = ""

#             # si suffisamment de texte -> on garde pdfplumber
#             if len(txt) >= 400:
#                 pages = _count_pdf_pages(str(path))
#                 return OCRResult(
#                     text=txt,
#                     method="pdfplumber",
#                     pages=pages,
#                     chars=len(txt),
#                     preview=_make_preview(txt),
#                 )

#             # 2) sinon OCR via images
#             pages_img = convert_from_path(str(path), dpi=300)
#             texts = []
#             for page in pages_img[:2]:  # facture: souvent 1-2 pages
#                 img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
#                 pre = self._preprocess_cv(img)
#                 texts.append(self._tesseract_ocr(pre, psm=6))
#             ocr_txt = _normalize_text("\n".join(texts))
#             pages = _count_pdf_pages(str(path))
#             return OCRResult(
#                 text=ocr_txt,
#                 method="tesseract",
#                 pages=pages,
#                 chars=len(ocr_txt),
#                 preview=_make_preview(ocr_txt),
#             )

#         # ---- Images ----
#         img = cv2.imread(str(path))
#         if img is None:
#             raise ValueError(f"Impossible de lire l'image: {file_path}")

#         pre_full = self._preprocess_cv(img)
#         text_full = self._tesseract_ocr(pre_full, psm=6)

#         date_found = self._extract_date_from_image(img)
#         if date_found:
#             text_full = f"DATE_FACTURE: {date_found}\n" + text_full

#         text_full = _normalize_text(text_full)
#         return OCRResult(
#             text=text_full,
#             method="tesseract",
#             pages=1,
#             chars=len(text_full),
#             preview=_make_preview(text_full),
#         )


# # ✅ Instance globale + fonction module-level
# _service = OCRService(lang=os.getenv("TESSERACT_LANG", "fra"))

# def extract(file_path: str) -> OCRResult:
#     return _service.extract(file_path)








# # services/ocr_service.py
# import os
# import re
# from dataclasses import dataclass
# from pathlib import Path
# from typing import List, Optional

# import cv2
# import numpy as np
# from PIL import Image
# import pytesseract

# try:
#     import pdfplumber
# except Exception:
#     pdfplumber = None

# from pdf2image import convert_from_path

# @dataclass
# class OCRResult:
#     text: str
#     method: str                # "pdf_text" | "tesseract"
#     pages: int
#     chars: int
#     preview: str

# class OCRService:
#     def __init__(self, lang: str = "fra"):
#         self.lang = lang

#     def _preprocess_cv(self, img_bgr: np.ndarray) -> Image.Image:
#         gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
#         gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
#         gray = cv2.bilateralFilter(gray, 9, 75, 75)
#         th = cv2.adaptiveThreshold(
#             gray, 255,
#             cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
#             31, 10
#         )
#         kernel = np.array([[0, -1, 0],
#                            [-1, 5, -1],
#                            [0, -1, 0]])
#         th = cv2.filter2D(th, -1, kernel)
#         return Image.fromarray(th)

#     def _tesseract(self, pil_img: Image.Image, psm: int = 6, whitelist: Optional[str] = None) -> str:
#         config = f"--oem 3 --psm {psm}"
#         if whitelist:
#             config += f" -c tessedit_char_whitelist={whitelist}"
#         return pytesseract.image_to_string(pil_img, lang=self.lang, config=config)

#     def _pdf_text_extract(self, pdf_path: str) -> Optional[str]:
#         if pdfplumber is None:
#             return None
#         try:
#             txt_parts = []
#             with pdfplumber.open(pdf_path) as pdf:
#                 for page in pdf.pages:
#                     t = page.extract_text() or ""
#                     txt_parts.append(t)
#             joined = "\n".join(txt_parts).strip()
#             # si PDF digital -> beaucoup de texte
#             if len(joined) >= 800:
#                 return joined
#             return None
#         except Exception:
#             return None

#     def _images_ocr(self, images_bgr: List[np.ndarray]) -> str:
#         out = []
#         for img in images_bgr:
#             pre = self._preprocess_cv(img)
#             out.append(self._tesseract(pre, psm=6))
#         return "\n".join(out).strip()

#     def extract(self, file_path: str) -> OCRResult:
#         ext = Path(file_path).suffix.lower()

#         # PDF digital d'abord
#         if ext == ".pdf":
#             direct = self._pdf_text_extract(file_path)
#             if direct:
#                 prev = direct[:1200]
#                 return OCRResult(
#                     text=direct,
#                     method="pdf_text",
#                     pages=max(1, direct.count("\f") + 1),
#                     chars=len(direct),
#                     preview=prev
#                 )

#             # sinon OCR via images
#             pages = convert_from_path(file_path, dpi=300)
#             imgs = [cv2.cvtColor(np.array(p), cv2.COLOR_RGB2BGR) for p in pages]
#             txt = self._images_ocr(imgs)
#             return OCRResult(
#                 text=txt,
#                 method="tesseract",
#                 pages=len(imgs),
#                 chars=len(txt),
#                 preview=txt[:1200]
#             )

#         # Images
#         img = cv2.imread(file_path)
#         if img is None:
#             raise ValueError(f"Impossible de lire l'image: {file_path}")

#         pre = self._preprocess_cv(img)
#         txt = self._tesseract(pre, psm=6)

#         return OCRResult(
#             text=txt.strip(),
#             method="tesseract",
#             pages=1,
#             chars=len(txt),
#             preview=txt[:1200]
#         )

# # instance singleton
# ocr_service = OCRService(lang=os.getenv("OCR_LANG", "fra"))
















import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pdfplumber


@dataclass
class OCRResult:
    text: str
    method: str          # "pdfplumber" | "tesseract"
    pages: int
    chars: int
    preview: str


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    t = text.replace("\u00A0", " ")
    t = t.replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _make_preview(text: str, n: int = 1200) -> str:
    return (text or "").strip()[:n]


def _count_pdf_pages(pdf_path: str) -> int:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)
    except Exception:
        return 1


class OCRService:
    def __init__(self, lang: str = "fra"):
        self.lang = lang

    # --------- preprocessing ----------
    def _preprocess_cv(self, img_bgr: np.ndarray) -> Image.Image:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)

        th = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 10
        )

        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        th = cv2.filter2D(th, -1, kernel)
        return Image.fromarray(th)

    def _tesseract_ocr(self, pil_img: Image.Image, psm: int = 6, whitelist: Optional[str] = None) -> str:
        config = f"--oem 1 --psm {psm}"
        if whitelist:
            config += f" -c tessedit_char_whitelist={whitelist}"
        return pytesseract.image_to_string(pil_img, lang=self.lang, config=config)

    # --------- date helper (optional) ----------
    def _extract_date_from_image(self, img_bgr: np.ndarray) -> Optional[str]:
        h, w = img_bgr.shape[:2]
        y1 = int(h * 0.20)
        y2 = int(h * 0.45)
        zone = img_bgr[y1:y2, 0:w]

        pre = self._preprocess_cv(zone)
        wl = "0123456789/:-."

        candidates = []
        for psm in (6, 7, 11, 12, 13):
            candidates.append(self._tesseract_ocr(pre, psm=psm, whitelist=wl))

        merged = "\n".join(candidates)
        m = re.search(r"\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b", merged)
        if m:
            return m.group(1).replace("-", "/").replace(".", "/")
        return None

    # --------- PDF digital ----------
    def _pdfplumber_text(self, pdf_path: str) -> str:
        parts: List[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for p in pdf.pages:
                parts.append(p.extract_text() or "")
        return _normalize_text("\n".join(parts))

    # --------- main ----------
    def extract(self, file_path: str) -> OCRResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(file_path)

        ext = path.suffix.lower()

        # ---- PDF ----
        if ext == ".pdf":
            # 1) essayer PDF digital
            txt = ""
            try:
                txt = self._pdfplumber_text(str(path))
            except Exception:
                txt = ""

            # si suffisamment de texte -> on garde pdfplumber
            if len(txt) >= 400:
                pages = _count_pdf_pages(str(path))
                return OCRResult(
                    text=txt,
                    method="pdfplumber",
                    pages=pages,
                    chars=len(txt),
                    preview=_make_preview(txt),
                )

            # 2) sinon OCR via images
            pages_img = convert_from_path(str(path), dpi=300)
            texts = []
            for page in pages_img[:2]:  # facture: souvent 1-2 pages
                img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
                pre = self._preprocess_cv(img)
                texts.append(self._tesseract_ocr(pre, psm=6))
            ocr_txt = _normalize_text("\n".join(texts))
            pages = _count_pdf_pages(str(path))
            return OCRResult(
                text=ocr_txt,
                method="tesseract",
                pages=pages,
                chars=len(ocr_txt),
                preview=_make_preview(ocr_txt),
            )

        # ---- Images ----
        img = cv2.imread(str(path))
        if img is None:
            raise ValueError(f"Impossible de lire l'image: {file_path}")

        pre_full = self._preprocess_cv(img)
        text_full = self._tesseract_ocr(pre_full, psm=6)

        date_found = self._extract_date_from_image(img)
        if date_found:
            text_full = f"DATE_FACTURE: {date_found}\n" + text_full

        text_full = _normalize_text(text_full)
        return OCRResult(
            text=text_full,
            method="tesseract",
            pages=1,
            chars=len(text_full),
            preview=_make_preview(text_full),
        )


# ✅ Instance globale + fonction module-level
_service = OCRService(lang=os.getenv("TESSERACT_LANG", "fra"))

def extract(file_path: str) -> OCRResult:
    return _service.extract(file_path)
