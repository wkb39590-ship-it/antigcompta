

# import os
# import cv2
# import numpy as np
# from PIL import Image
# import pytesseract
# from pdf2image import convert_from_path


# class OCRService:
#     def __init__(self, lang: str = "fra"):
#         self.lang = lang

#     # -------------------------
#     # Image preprocessing (OpenCV)
#     # -------------------------
#     def _preprocess_image(self, image_path: str) -> Image.Image:
#         img = cv2.imread(image_path)

#         if img is None:
#             raise ValueError(f"Impossible de lire l'image: {image_path}")

#         # 1) grayscale
#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#         # 2) upscale (améliore la lecture)
#         gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

#         # 3) denoise
#         gray = cv2.bilateralFilter(gray, 9, 75, 75)

#         # 4) threshold (binarisation)
#         th = cv2.adaptiveThreshold(
#             gray, 255,
#             cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
#             31, 10
#         )

#         # 5) léger sharpening
#         kernel = np.array([[0, -1, 0],
#                            [-1, 5, -1],
#                            [0, -1, 0]])
#         th = cv2.filter2D(th, -1, kernel)

#         # Convertir en PIL Image
#         return Image.fromarray(th)

#     def _tesseract_ocr(self, pil_img: Image.Image, psm: int = 6, whitelist: str | None = None) -> str:
#         config = f"--oem 3 --psm {psm}"
#         if whitelist:
#             config += f" -c tessedit_char_whitelist={whitelist}"

#         return pytesseract.image_to_string(pil_img, lang=self.lang, config=config)

#     # -------------------------
#     # Main
#     # -------------------------
#     def extract_text(self, file_path: str) -> str:
#         ext = os.path.splitext(file_path)[1].lower()

#         # Images
#         if ext in [".png", ".jpg", ".jpeg"]:
#             pre = self._preprocess_image(file_path)

#             # OCR global
#             text_full = self._tesseract_ocr(pre, psm=6)

#             # OCR "header" (souvent la date est en haut, on tente une passe dédiée)
#             w, h = pre.size
#             header = pre.crop((0, 0, w, int(h * 0.35)))
#             text_header = self._tesseract_ocr(
#                 header,
#                 psm=6,
#                 whitelist="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/:-. "
#             )

#             return (text_header + "\n" + text_full).strip()

#         # PDF
#         if ext == ".pdf":
#             pages = convert_from_path(file_path, dpi=300)  # dpi élevé = meilleure précision
#             texts = []
#             for page in pages:
#                 # On binarise aussi les pages PDF converties
#                 img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
#                 gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#                 th = cv2.adaptiveThreshold(
#                     gray, 255,
#                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
#                     31, 10
#                 )
#                 pil = Image.fromarray(th)
#                 texts.append(self._tesseract_ocr(pil, psm=6))
#             return "\n".join(texts).strip()

#         raise ValueError(f"Format non supporté: {ext}")






import os
import re
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path


class OCRService:
    def __init__(self, lang: str = "fra"):
        self.lang = lang

    # -------------------------
    # Image preprocessing (OpenCV)
    # -------------------------
    def _preprocess_cv(self, img_bgr: np.ndarray) -> Image.Image:
        # 1) grayscale
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # 2) upscale
        gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

        # 3) denoise
        gray = cv2.bilateralFilter(gray, 9, 75, 75)

        # 4) threshold
        th = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
            31, 10
        )

        # 5) sharpen léger
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        th = cv2.filter2D(th, -1, kernel)

        return Image.fromarray(th)

    def _tesseract_ocr(self, pil_img: Image.Image, psm: int = 6, whitelist: str | None = None) -> str:
        config = f"--oem 3 --psm {psm}"
        if whitelist:
            config += f" -c tessedit_char_whitelist={whitelist}"
        return pytesseract.image_to_string(pil_img, lang=self.lang, config=config)

    # -------------------------
    # OCR spécialisé pour extraire une date
    # -------------------------
    def _extract_date_from_image(self, img_bgr: np.ndarray) -> str | None:
        h, w = img_bgr.shape[:2]

        # ✅ Zone du tableau "Facture / Date / Code client"
        # Dans ton image, c’est vers le haut, après le bloc fournisseur.
        # On prend une bande centrée autour de 25%-45% de la hauteur.
        y1 = int(h * 0.20)
        y2 = int(h * 0.45)
        date_zone = img_bgr[y1:y2, 0:w]

        pre = self._preprocess_cv(date_zone)

        # whitelist orientée chiffres/date
        wl = "0123456789/:-."

        # On teste plusieurs psm (selon documents, un marche mieux)
        candidates = []
        for psm in (6, 7, 11, 12, 13):
            txt = self._tesseract_ocr(pre, psm=psm, whitelist=wl)
            candidates.append(txt)

        merged = "\n".join(candidates)

        # Cherche date dd/mm/yyyy
        m = re.search(r"\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b", merged)
        if m:
            # normaliser -> dd/mm/yyyy
            d = m.group(1).replace("-", "/").replace(".", "/")
            return d

        # fallback: parfois OCR casse l’année (ex: 16/12/202)
        m = re.search(r"\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{3,4})\b", merged)
        if m:
            d = m.group(1).replace("-", "/").replace(".", "/")
            # si année 3 chiffres -> on ignore (trop risqué)
            if len(d.split("/")[-1]) == 4:
                return d

        return None

    # -------------------------
    # Main
    # -------------------------
    def extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        # Images
        if ext in [".png", ".jpg", ".jpeg"]:
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError(f"Impossible de lire l'image: {file_path}")

            # OCR global
            pre_full = self._preprocess_cv(img)
            text_full = self._tesseract_ocr(pre_full, psm=6)

            # OCR date zone
            date_found = self._extract_date_from_image(img)

            # ✅ On injecte une ligne explicite si on a trouvé la date
            # Comme ça ton parse_facture_text la récupère toujours.
            if date_found:
                text_full = f"DATE_FACTURE: {date_found}\n" + text_full

            return text_full.strip()

        # PDF
        if ext == ".pdf":
            pages = convert_from_path(file_path, dpi=300)
            texts = []
            for page in pages:
                img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
                pre = self._preprocess_cv(img)
                texts.append(self._tesseract_ocr(pre, psm=6))
            return "\n".join(texts).strip()

        raise ValueError(f"Format non supporté: {ext}")
