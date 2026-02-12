






# import os
# import uuid
# from pathlib import Path
# from typing import Any, Dict, Optional, List

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture

# from services import ocr_service
# from services import extract_fields

# from services.gemini_service import extract_invoice_fields_from_image_bytes
# from services.pdf_utils import pdf_to_png_images_bytes
# from services.validators import validate_or_fix, merge_fields

# from utils.parsers import parse_date_fr, parse_amount


# router = APIRouter(prefix="/factures", tags=["factures"])

# UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# # -------------------------
# # Helpers
# # -------------------------

# def save_upload_file(upload: UploadFile) -> str:
#     ext = Path(upload.filename or "").suffix.lower()

#     if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
#         raise HTTPException(status_code=400, detail=f"Extension non supportée: {ext}")

#     unique_name = f"{uuid.uuid4()}{ext}"
#     dest = UPLOAD_DIR / unique_name

#     data = upload.file.read()
#     if not data:
#         raise HTTPException(status_code=400, detail="Fichier vide")

#     with open(dest, "wb") as f:
#         f.write(data)

#     return str(dest)


# def guess_mime_type(file_path: str) -> str:
#     ext = Path(file_path).suffix.lower()
#     if ext == ".png":
#         return "image/png"
#     if ext in [".jpg", ".jpeg"]:
#         return "image/jpeg"
#     if ext == ".webp":
#         return "image/webp"
#     if ext in [".tif", ".tiff"]:
#         return "image/tiff"
#     return "application/octet-stream"


# def to_dict(obj: Any) -> Dict[str, Any]:
#     if obj is None:
#         return {}
#     if isinstance(obj, dict):
#         return obj
#     if hasattr(obj, "dict"):
#         return obj.dict()
#     if hasattr(obj, "__dict__"):
#         return dict(obj.__dict__)
#     return dict(obj)


# def should_use_gemini(ocr: Any, fields: Dict[str, Any]) -> bool:
#     important_keys = ["numero_facture", "montant_ttc", "montant_tva", "ice_frs"]

#     null_count = sum(1 for k in important_keys if fields.get(k) in [None, "", 0])

#     chars = getattr(ocr, "chars", None)
#     low_chars = (chars is not None and chars < 700)

#     return null_count >= 2 or low_chars


# def extract_with_gemini(file_path: str) -> Dict[str, Any]:
#     ext = Path(file_path).suffix.lower()

#     if ext == ".pdf":
#         images = pdf_to_png_images_bytes(file_path, dpi=300, max_pages=1)
#         if not images:
#             raise HTTPException(status_code=500, detail="Impossible de convertir le PDF en image")
#         image_bytes = images[0]
#         mime_type = "image/png"
#     else:
#         with open(file_path, "rb") as f:
#             image_bytes = f.read()
#         mime_type = guess_mime_type(file_path)

#     gemini_raw = extract_invoice_fields_from_image_bytes(image_bytes, mime_type=mime_type)

#     gemini_clean, issues = validate_or_fix(gemini_raw)
#     gemini_clean["_gemini_issues"] = issues
#     return gemini_clean


# # -------------------------
# # Endpoints
# # -------------------------

# @router.post("/upload-facture/")
# def upload_facture(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     """
#     Upload facture -> OCR -> extraction -> fallback Gemini -> DB
#     """
#     file_path = save_upload_file(file)

#     # 1) OCR
#     ocr = ocr_service.extract(file_path)

#     # 2) Extraction classique
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_issues: List[str] = []

#     # 3) Fallback Gemini si nécessaire
#     if should_use_gemini(ocr, fields):
#         used_gemini = True
#         gemini_fields = extract_with_gemini(file_path)
#         gemini_issues = gemini_fields.pop("_gemini_issues", [])
#         fields = merge_fields(fields, gemini_fields)

#     # 4) Règle métier
#     fields["date_paie"] = fields.get("date_facture")

#     # 5) Conversion types pour DB
#     date_facture_db = parse_date_fr(fields.get("date_facture"))
#     date_paie_db = parse_date_fr(fields.get("date_paie"))

#     facture = Facture(
#         fournisseur=fields.get("fournisseur"),
#         date_facture=date_facture_db,
#         date_paie=date_paie_db,
#         numero_facture=fields.get("numero_facture"),
#         designation=fields.get("designation"),

#         montant_ht=parse_amount(fields.get("montant_ht")),
#         montant_tva=parse_amount(fields.get("montant_tva")),
#         montant_ttc=parse_amount(fields.get("montant_ttc")),

#         statut="brouillon",

#         if_frs=fields.get("if_frs") or fields.get("if_fiscal"),
#         ice_frs=fields.get("ice_frs") or fields.get("ice"),

#         taux_tva=parse_amount(fields.get("taux_tva")),
#         id_paie=fields.get("id_paie"),

#         ded_file_path=file_path,
#     )

#     db.add(facture)
#     db.commit()
#     db.refresh(facture)

#     return {
#         "message": "Facture uploadée et enregistrée",
#         "id": facture.id,
#         "file_path": file_path,
#         "used_gemini": used_gemini,
#         "gemini_issues": gemini_issues,
#         "ocr": {
#             "method": getattr(ocr, "method", None),
#             "pages": getattr(ocr, "pages", None),
#             "chars": getattr(ocr, "chars", None),
#             "preview": getattr(ocr, "preview", None),
#         },
#         "fields": fields,
#     }


# @router.post("/debug-extract/")
# def debug_extract(
#     file: UploadFile = File(...),
# ):
#     """
#     Debug extraction: renvoie OCR preview + champs classiques + Gemini + merged.
#     """
#     file_path = save_upload_file(file)

#     ocr = ocr_service.extract(file_path)
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_fields: Optional[Dict[str, Any]] = None
#     gemini_issues: List[str] = []

#     if should_use_gemini(ocr, fields):
#         used_gemini = True
#         gemini_fields = extract_with_gemini(file_path)
#         gemini_issues = gemini_fields.pop("_gemini_issues", [])
#         merged = merge_fields(fields, gemini_fields)
#     else:
#         merged = fields

#     merged["date_paie"] = merged.get("date_facture")

#     return {
#         "file_path": file_path,
#         "used_gemini": used_gemini,
#         "gemini_issues": gemini_issues,
#         "ocr": {
#             "method": getattr(ocr, "method", None),
#             "pages": getattr(ocr, "pages", None),
#             "chars": getattr(ocr, "chars", None),
#             "preview": getattr(ocr, "preview", None),
#         },
#         "classic_fields": fields,
#         "gemini_fields": gemini_fields,
#         "merged_fields": merged,
#     }


# @router.get("/")
# def list_factures(db: Session = Depends(get_db)):
#     factures = db.query(Facture).order_by(Facture.id.desc()).all()

#     return [
#         {
#             "id": f.id,
#             "fournisseur": f.fournisseur,
#             "date_facture": str(f.date_facture) if f.date_facture else None,
#             "numero_facture": f.numero_facture,
#             "montant_ht": f.montant_ht,
#             "montant_tva": f.montant_tva,
#             "montant_ttc": f.montant_ttc,
#             "statut": f.statut,
#             "ice_frs": f.ice_frs,
#             "if_frs": f.if_frs,
#         }
#         for f in factures
#     ]


# @router.get("/{facture_id}")
# def get_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     return {
#         "id": facture.id,
#         "fournisseur": facture.fournisseur,
#         "date_facture": str(facture.date_facture) if facture.date_facture else None,
#         "date_paie": str(facture.date_paie) if facture.date_paie else None,
#         "numero_facture": facture.numero_facture,
#         "designation": facture.designation,
#         "montant_ht": facture.montant_ht,
#         "montant_tva": facture.montant_tva,
#         "montant_ttc": facture.montant_ttc,
#         "statut": facture.statut,
#         "if_frs": facture.if_frs,
#         "ice_frs": facture.ice_frs,
#         "taux_tva": facture.taux_tva,
#         "id_paie": facture.id_paie,
#         "ded_file_path": facture.ded_file_path,
#         "ded_pdf_path": facture.ded_pdf_path,
#         "ded_xlsx_path": facture.ded_xlsx_path,
#     }


# @router.delete("/{facture_id}")
# def delete_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     db.delete(facture)
#     db.commit()

#     return {"message": "Facture supprimée"}














# import os
# import uuid
# from pathlib import Path
# from typing import Any, Dict, Optional, List

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture

# from services import ocr_service
# from services import extract_fields

# from services.gemini_service import extract_invoice_fields_from_image_bytes
# from services.pdf_utils import pdf_to_png_images_bytes
# from services.validators import validate_or_fix, merge_fields
# from services.postprocess import fix_fields  # ✅ AJOUT

# from utils.parsers import parse_date_fr, parse_amount


# router = APIRouter(prefix="/factures", tags=["factures"])

# UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# # -------------------------
# # Helpers
# # -------------------------

# def save_upload_file(upload: UploadFile) -> str:
#     ext = Path(upload.filename or "").suffix.lower()

#     if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
#         raise HTTPException(status_code=400, detail=f"Extension non supportée: {ext}")

#     unique_name = f"{uuid.uuid4()}{ext}"
#     dest = UPLOAD_DIR / unique_name

#     data = upload.file.read()
#     if not data:
#         raise HTTPException(status_code=400, detail="Fichier vide")

#     with open(dest, "wb") as f:
#         f.write(data)

#     return str(dest)


# def guess_mime_type(file_path: str) -> str:
#     ext = Path(file_path).suffix.lower()
#     if ext == ".png":
#         return "image/png"
#     if ext in [".jpg", ".jpeg"]:
#         return "image/jpeg"
#     if ext == ".webp":
#         return "image/webp"
#     if ext in [".tif", ".tiff"]:
#         return "image/tiff"
#     return "application/octet-stream"


# def to_dict(obj: Any) -> Dict[str, Any]:
#     if obj is None:
#         return {}
#     if isinstance(obj, dict):
#         return obj
#     if hasattr(obj, "dict"):
#         return obj.dict()
#     if hasattr(obj, "__dict__"):
#         return dict(obj.__dict__)
#     return dict(obj)


# def should_use_gemini(ocr: Any, fields: Dict[str, Any]) -> bool:
#     important_keys = ["numero_facture", "montant_ttc", "montant_tva", "ice_frs"]

#     null_count = sum(1 for k in important_keys if fields.get(k) in [None, "", 0])

#     chars = getattr(ocr, "chars", None)
#     low_chars = (chars is not None and chars < 700)

#     return null_count >= 2 or low_chars


# def extract_with_gemini(file_path: str) -> Dict[str, Any]:
#     ext = Path(file_path).suffix.lower()

#     if ext == ".pdf":
#         images = pdf_to_png_images_bytes(file_path, dpi=300, max_pages=1)
#         if not images:
#             raise RuntimeError("Impossible de convertir le PDF en image")
#         image_bytes = images[0]
#         mime_type = "image/png"
#     else:
#         with open(file_path, "rb") as f:
#             image_bytes = f.read()
#         mime_type = guess_mime_type(file_path)

#     gemini_raw = extract_invoice_fields_from_image_bytes(image_bytes, mime_type=mime_type)

#     gemini_clean, issues = validate_or_fix(gemini_raw)
#     gemini_clean["_gemini_issues"] = issues
#     return gemini_clean


# def safe_preview(ocr: Any) -> str:
#     """
#     Ton ocr.preview contient déjà du texte OCR.
#     Si tu as un autre champ ocr.text, tu peux l'ajouter ici.
#     """
#     return (getattr(ocr, "preview", "") or "").strip()


# # -------------------------
# # Endpoints
# # -------------------------

# @router.post("/upload-facture/")
# def upload_facture(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     """
#     Upload facture -> OCR -> extraction -> fallback Gemini -> postprocess -> DB
#     """
#     file_path = save_upload_file(file)

#     # 1) OCR
#     ocr = ocr_service.extract(file_path)

#     # 2) Extraction classique
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_issues: List[str] = []

#     # 3) Fallback Gemini (SAFE: ne plante plus)
#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             fields = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             # ✅ IMPORTANT: ne pas faire 500 si Gemini échoue
#             used_gemini = False
#             gemini_issues = [f"Gemini failed: {type(e).__name__}: {e}"]

#     # 4) Règle métier
#     fields["date_paie"] = fields.get("date_facture")

#     # ✅ 5) Postprocess intelligent (fix TVA / fix numero facture)
#     fields = fix_fields(fields, safe_preview(ocr))

#     # 6) Conversion types pour DB
#     date_facture_db = parse_date_fr(fields.get("date_facture"))
#     date_paie_db = parse_date_fr(fields.get("date_paie"))

#     facture = Facture(
#         fournisseur=fields.get("fournisseur"),
#         date_facture=date_facture_db,
#         date_paie=date_paie_db,
#         numero_facture=fields.get("numero_facture"),
#         designation=fields.get("designation"),

#         montant_ht=parse_amount(fields.get("montant_ht")),
#         montant_tva=parse_amount(fields.get("montant_tva")),
#         montant_ttc=parse_amount(fields.get("montant_ttc")),

#         statut="brouillon",

#         if_frs=fields.get("if_frs") or fields.get("if_fiscal"),
#         ice_frs=fields.get("ice_frs") or fields.get("ice"),

#         taux_tva=parse_amount(fields.get("taux_tva")),
#         id_paie=fields.get("id_paie"),

#         ded_file_path=file_path,
#     )

#     db.add(facture)
#     db.commit()
#     db.refresh(facture)

#     return {
#         "message": "Facture uploadée et enregistrée",
#         "id": facture.id,
#         "file_path": file_path,
#         "used_gemini": used_gemini,
#         "gemini_issues": gemini_issues,
#         "ocr": {
#             "method": getattr(ocr, "method", None),
#             "pages": getattr(ocr, "pages", None),
#             "chars": getattr(ocr, "chars", None),
#             "preview": getattr(ocr, "preview", None),
#         },
#         "fields": fields,
#     }


# @router.post("/debug-extract/")
# def debug_extract(
#     file: UploadFile = File(...),
# ):
#     """
#     Debug extraction: OCR preview + champs classiques + Gemini + merged + postprocess.
#     """
#     file_path = save_upload_file(file)

#     ocr = ocr_service.extract(file_path)
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     classic_fields = to_dict(extracted)

#     used_gemini = False
#     gemini_fields: Optional[Dict[str, Any]] = None
#     gemini_issues: List[str] = []

#     merged = dict(classic_fields)

#     if should_use_gemini(ocr, classic_fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             merged = merge_fields(classic_fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_fields = None
#             gemini_issues = [f"Gemini failed: {type(e).__name__}: {e}"]
#             merged = dict(classic_fields)

#     merged["date_paie"] = merged.get("date_facture")

#     # ✅ Postprocess aussi en debug pour voir la différence
#     merged_fixed = fix_fields(dict(merged), safe_preview(ocr))

#     return {
#         "file_path": file_path,
#         "used_gemini": used_gemini,
#         "gemini_issues": gemini_issues,
#         "ocr": {
#             "method": getattr(ocr, "method", None),
#             "pages": getattr(ocr, "pages", None),
#             "chars": getattr(ocr, "chars", None),
#             "preview": getattr(ocr, "preview", None),
#         },
#         "classic_fields": classic_fields,
#         "gemini_fields": gemini_fields,
#         "merged_fields": merged,
#         "merged_fixed": merged_fixed,
#     }


# @router.get("/")
# def list_factures(db: Session = Depends(get_db)):
#     factures = db.query(Facture).order_by(Facture.id.desc()).all()

#     return [
#         {
#             "id": f.id,
#             "fournisseur": f.fournisseur,
#             "date_facture": str(f.date_facture) if f.date_facture else None,
#             "numero_facture": f.numero_facture,
#             "montant_ht": f.montant_ht,
#             "montant_tva": f.montant_tva,
#             "montant_ttc": f.montant_ttc,
#             "statut": f.statut,
#             "ice_frs": f.ice_frs,
#             "if_frs": f.if_frs,
#         }
#         for f in factures
#     ]


# @router.get("/{facture_id}")
# def get_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     return {
#         "id": facture.id,
#         "fournisseur": facture.fournisseur,
#         "date_facture": str(facture.date_facture) if facture.date_facture else None,
#         "date_paie": str(facture.date_paie) if facture.date_paie else None,
#         "numero_facture": facture.numero_facture,
#         "designation": facture.designation,
#         "montant_ht": facture.montant_ht,
#         "montant_tva": facture.montant_tva,
#         "montant_ttc": facture.montant_ttc,
#         "statut": facture.statut,
#         "if_frs": facture.if_frs,
#         "ice_frs": facture.ice_frs,
#         "taux_tva": facture.taux_tva,
#         "id_paie": facture.id_paie,
#         "ded_file_path": facture.ded_file_path,
#         "ded_pdf_path": facture.ded_pdf_path,
#         "ded_xlsx_path": facture.ded_xlsx_path,
#     }


# @router.delete("/{facture_id}")
# def delete_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     db.delete(facture)
#     db.commit()

#     return {"message": "Facture supprimée"}



























# import os
# import re
# import uuid
# from pathlib import Path
# from typing import Any, Dict, Optional, List, Tuple

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture

# from services import ocr_service
# from services import extract_fields

# from services.gemini_service import extract_invoice_fields_from_image_bytes
# from services.pdf_utils import pdf_to_png_images_bytes
# from services.validators import validate_or_fix, merge_fields

# from utils.parsers import parse_date_fr, parse_amount


# router = APIRouter(prefix="/factures", tags=["factures"])

# UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# # -------------------------
# # Helpers fichiers / types
# # -------------------------

# def save_upload_file(upload: UploadFile) -> str:
#     ext = Path(upload.filename or "").suffix.lower()
#     if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
#         raise HTTPException(status_code=400, detail=f"Extension non supportée: {ext}")

#     unique_name = f"{uuid.uuid4()}{ext}"
#     dest = UPLOAD_DIR / unique_name

#     data = upload.file.read()
#     if not data:
#         raise HTTPException(status_code=400, detail="Fichier vide")

#     with open(dest, "wb") as f:
#         f.write(data)

#     return str(dest)


# def guess_mime_type(file_path: str) -> str:
#     ext = Path(file_path).suffix.lower()
#     if ext == ".png":
#         return "image/png"
#     if ext in [".jpg", ".jpeg"]:
#         return "image/jpeg"
#     if ext == ".webp":
#         return "image/webp"
#     if ext in [".tif", ".tiff"]:
#         return "image/tiff"
#     return "application/octet-stream"


# def to_dict(obj: Any) -> Dict[str, Any]:
#     if obj is None:
#         return {}
#     if isinstance(obj, dict):
#         return obj
#     if hasattr(obj, "dict"):
#         return obj.dict()
#     if hasattr(obj, "__dict__"):
#         return dict(obj.__dict__)
#     return dict(obj)


# # -------------------------
# # Helpers OCR post-process
# # -------------------------

# def _norm_text(s: str) -> str:
#     # Normalisation simple : espaces & caractères OCR courants
#     s = s or ""
#     s = s.replace("\u00a0", " ")
#     s = re.sub(r"[ \t]+", " ", s)
#     return s.strip()


# def _extract_invoice_number_from_text(text: str) -> Optional[str]:
#     """
#     Cherche le numero de facture en priorité près des mots clés FACTURE / INVOICE.
#     Exemples attendus: 00005252/25, FA250152, F-2025-001, etc.
#     """
#     t = _norm_text(text)
#     if not t:
#         return None

#     patterns = [
#         # FACTURE N° : 00005252/25
#         r"(?:FACTURE|INVOICE)\s*(?:N[°ºO]?\s*[:\-]?\s*)([A-Z]{0,4}\d[\dA-Z\-\/]{2,})",
#         # N° FACTURE : FA250152
#         r"(?:N[°ºO]?\s*(?:FACTURE|INVOICE)\s*[:\-]?\s*)([A-Z]{0,4}\d[\dA-Z\-\/]{2,})",
#         # FACTURE : FA250152
#         r"(?:FACTURE|INVOICE)\s*[:\-]\s*([A-Z]{0,4}\d[\dA-Z\-\/]{2,})",
#     ]

#     for p in patterns:
#         m = re.search(p, t, flags=re.IGNORECASE)
#         if m:
#             cand = m.group(1).strip().rstrip(".,;")
#             # évite de confondre avec IF/ICE/Patente (souvent longs sans / ni prefix)
#             if len(cand) >= 5 and len(cand) <= 20:
#                 return cand

#     # fallback: format avec slash très typique: 00005252/25
#     m2 = re.search(r"\b(\d{4,10}\s*/\s*\d{2,4})\b", t)
#     if m2:
#         return m2.group(1).replace(" ", "")

#     return None


# def _extract_totals_from_text(text: str) -> Dict[str, Optional[float]]:
#     """
#     Essaie de récupérer HT / TVA / TTC depuis des libellés.
#     Ça marche bien sur des factures type 'MONTANT T.V.A.'.
#     """
#     t = _norm_text(text)
#     out = {"montant_ht": None, "montant_tva": None, "montant_ttc": None, "taux_tva": None}

#     def grab_amount(label_regex: str) -> Optional[float]:
#         # capture un nombre type 1 133.33 ou 1,133.33 ou 1133,33
#         m = re.search(label_regex + r"\s*[:\-]?\s*([0-9][0-9\s\.,]{1,})", t, flags=re.IGNORECASE)
#         if not m:
#             return None
#         return parse_amount(m.group(1))

#     # HT / TTC / TVA
#     out["montant_ht"] = grab_amount(r"(?:MONTANT\s*H\.?T\.?|TOTAL\s*H\.?T\.?)")
#     out["montant_ttc"] = grab_amount(r"(?:MONTANT\s*T\.?T\.?C\.?|TOTAL\s*T\.?T\.?C\.?|NET\s*A\s*PAYER)")
#     out["montant_tva"] = grab_amount(r"(?:MONTANT\s*T\.?V\.?A\.?|TOTAL\s*T\.?V\.?A\.?)")

#     # Taux TVA (ex: TVA 20% ou TAUX 20)
#     m_rate = re.search(r"(?:TVA|TAUX)\s*[:\-]?\s*(\d{1,2}(?:[.,]\d+)?)\s*%", t, flags=re.IGNORECASE)
#     if m_rate:
#         out["taux_tva"] = parse_amount(m_rate.group(1))

#     return out


# def _fix_tva_coherence(fields: Dict[str, Any], ocr_text: str) -> Tuple[Dict[str, Any], List[str]]:
#     """
#     Corrige les cas:
#     - montant_tva = 20 (c'est un taux)
#     - montant_ht/ttc présents => calcule TVA = TTC - HT
#     """
#     issues: List[str] = []
#     f = dict(fields)

#     ht = parse_amount(f.get("montant_ht"))
#     ttc = parse_amount(f.get("montant_ttc"))
#     tva = parse_amount(f.get("montant_tva"))
#     rate = parse_amount(f.get("taux_tva"))

#     # Cas classique: montant_tva == 20 -> c'est un taux
#     if tva is not None and 0 < tva <= 100 and (rate is None or rate == 0):
#         f["taux_tva"] = tva
#         f["montant_tva"] = None
#         issues.append("montant_tva ressemblait à un taux, déplacé vers taux_tva")

#         rate = parse_amount(f.get("taux_tva"))
#         tva = None

#     # Si on a HT et TTC, TVA = TTC - HT
#     if ht is not None and ttc is not None:
#         calc_tva = round(ttc - ht, 2)
#         if calc_tva >= 0:
#             # si TVA manquante ou absurde, on remplace
#             if tva is None or (0 < tva <= 100) or abs(tva - calc_tva) > 0.5:
#                 f["montant_tva"] = calc_tva
#                 issues.append("montant_tva recalculé via TTC - HT")

#     # Si toujours rien, essaie extraction depuis OCR labels
#     if parse_amount(f.get("montant_tva")) is None:
#         totals = _extract_totals_from_text(ocr_text)
#         if totals.get("montant_tva") is not None:
#             f["montant_tva"] = totals["montant_tva"]
#             issues.append("montant_tva récupéré depuis OCR (libellé MONTANT TVA)")

#     # taux_tva depuis OCR si vide
#     if (parse_amount(f.get("taux_tva")) in [None, 0]) and (rate not in [None, 0]):
#         f["taux_tva"] = rate

#     return f, issues


# def _postprocess_from_ocr(fields: Dict[str, Any], ocr: Any) -> Tuple[Dict[str, Any], List[str]]:
#     issues: List[str] = []
#     text = getattr(ocr, "preview", "") or ""

#     # Numero facture
#     if not fields.get("numero_facture"):
#         inv = _extract_invoice_number_from_text(text)
#         if inv:
#             fields["numero_facture"] = inv
#             issues.append("numero_facture récupéré via OCR regex")

#     # TVA
#     fields, tva_issues = _fix_tva_coherence(fields, text)
#     issues.extend(tva_issues)

#     return fields, issues


# # -------------------------
# # Gemini gating + wrapper safe
# # -------------------------

# def should_use_gemini(ocr: Any, fields: Dict[str, Any]) -> bool:
#     important_keys = ["numero_facture", "montant_ttc", "montant_ht", "ice_frs"]
#     null_count = sum(1 for k in important_keys if fields.get(k) in [None, "", 0])

#     chars = getattr(ocr, "chars", None)
#     low_chars = (chars is not None and chars < 700)

#     return null_count >= 2 or low_chars


# def extract_with_gemini_safe(file_path: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
#     """
#     IMPORTANT: ne lève jamais d'exception (sinon 500).
#     Retourne (fields_or_none, issues)
#     """
#     issues: List[str] = []
#     try:
#         ext = Path(file_path).suffix.lower()

#         if ext == ".pdf":
#             images = pdf_to_png_images_bytes(file_path, dpi=300, max_pages=1)
#             if not images:
#                 return None, ["Impossible de convertir le PDF en image pour Gemini"]
#             image_bytes = images[0]
#             mime_type = "image/png"
#         else:
#             with open(file_path, "rb") as f:
#                 image_bytes = f.read()
#             mime_type = guess_mime_type(file_path)

#         gemini_raw = extract_invoice_fields_from_image_bytes(image_bytes, mime_type=mime_type)
#         gemini_clean, v_issues = validate_or_fix(gemini_raw)
#         issues.extend(v_issues)
#         return gemini_clean, issues

#     except Exception as e:
#         issues.append(f"Gemini failed: {e}")
#         return None, issues


# # -------------------------
# # Endpoints
# # -------------------------

# @router.post("/upload-facture/")
# def upload_facture(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     file_path = save_upload_file(file)

#     # 1) OCR
#     ocr = ocr_service.extract(file_path)

#     # 2) Extraction classique
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     # 2.b) Postprocess OCR (fix numéro facture + TVA)
#     pp_issues: List[str] = []
#     fields, pp_issues = _postprocess_from_ocr(fields, ocr)

#     used_gemini = False
#     gemini_issues: List[str] = []
#     gemini_fields: Optional[Dict[str, Any]] = None

#     # 3) Gemini fallback (safe)
#     if should_use_gemini(ocr, fields):
#         gemini_fields, g_issues = extract_with_gemini_safe(file_path)
#         gemini_issues.extend(g_issues)
#         if gemini_fields:
#             used_gemini = True
#             fields = merge_fields(fields, gemini_fields)

#             # re-postprocess après merge (au cas où Gemini confond TVA/taux)
#             fields, extra_pp = _postprocess_from_ocr(fields, ocr)
#             pp_issues.extend(extra_pp)

#     # 4) règle métier
#     fields["date_paie"] = fields.get("date_facture")

#     # 5) conversions DB
#     date_facture_db = parse_date_fr(fields.get("date_facture"))
#     date_paie_db = parse_date_fr(fields.get("date_paie"))

#     facture = Facture(
#         fournisseur=fields.get("fournisseur"),
#         date_facture=date_facture_db,
#         date_paie=date_paie_db,
#         numero_facture=fields.get("numero_facture"),
#         designation=fields.get("designation"),

#         montant_ht=parse_amount(fields.get("montant_ht")),
#         montant_tva=parse_amount(fields.get("montant_tva")),
#         montant_ttc=parse_amount(fields.get("montant_ttc")),

#         statut="brouillon",

#         if_frs=fields.get("if_frs") or fields.get("if_fiscal"),
#         ice_frs=fields.get("ice_frs") or fields.get("ice"),

#         taux_tva=parse_amount(fields.get("taux_tva")),
#         id_paie=fields.get("id_paie"),

#         ded_file_path=file_path,
#     )

#     db.add(facture)
#     db.commit()
#     db.refresh(facture)

#     return {
#         "message": "Facture uploadée et enregistrée",
#         "id": facture.id,
#         "file_path": file_path,
#         "used_gemini": used_gemini,
#         "gemini_issues": gemini_issues + pp_issues,  # on inclut aussi les fixes OCR
#         "ocr": {
#             "method": getattr(ocr, "method", None),
#             "pages": getattr(ocr, "pages", None),
#             "chars": getattr(ocr, "chars", None),
#             "preview": getattr(ocr, "preview", None),
#         },
#         "fields": fields,
#     }


# @router.post("/debug-extract/")
# def debug_extract(file: UploadFile = File(...)):
#     file_path = save_upload_file(file)

#     ocr = ocr_service.extract(file_path)
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     fields_after_pp, pp_issues = _postprocess_from_ocr(fields, ocr)

#     gemini_fields, gemini_issues = (None, [])
#     used_gemini = False
#     merged = dict(fields_after_pp)

#     if should_use_gemini(ocr, merged):
#         gemini_fields, gemini_issues = extract_with_gemini_safe(file_path)
#         if gemini_fields:
#             used_gemini = True
#             merged = merge_fields(merged, gemini_fields)
#             merged, extra_pp = _postprocess_from_ocr(merged, ocr)
#             pp_issues.extend(extra_pp)

#     merged["date_paie"] = merged.get("date_facture")

#     return {
#         "file_path": file_path,
#         "used_gemini": used_gemini,
#         "gemini_issues": gemini_issues + pp_issues,
#         "ocr": {
#             "method": getattr(ocr, "method", None),
#             "pages": getattr(ocr, "pages", None),
#             "chars": getattr(ocr, "chars", None),
#             "preview": getattr(ocr, "preview", None),
#         },
#         "classic_fields": fields,
#         "after_postprocess": fields_after_pp,
#         "gemini_fields": gemini_fields,
#         "merged_fields": merged,
#     }


# @router.get("/")
# def list_factures(db: Session = Depends(get_db)):
#     factures = db.query(Facture).order_by(Facture.id.desc()).all()
#     return [
#         {
#             "id": f.id,
#             "fournisseur": f.fournisseur,
#             "date_facture": str(f.date_facture) if f.date_facture else None,
#             "numero_facture": f.numero_facture,
#             "montant_ht": f.montant_ht,
#             "montant_tva": f.montant_tva,
#             "montant_ttc": f.montant_ttc,
#             "statut": f.statut,
#             "ice_frs": f.ice_frs,
#             "if_frs": f.if_frs,
#         }
#         for f in factures
#     ]


# @router.get("/{facture_id}")
# def get_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     return {
#         "id": facture.id,
#         "fournisseur": facture.fournisseur,
#         "date_facture": str(facture.date_facture) if facture.date_facture else None,
#         "date_paie": str(facture.date_paie) if facture.date_paie else None,
#         "numero_facture": facture.numero_facture,
#         "designation": facture.designation,
#         "montant_ht": facture.montant_ht,
#         "montant_tva": facture.montant_tva,
#         "montant_ttc": facture.montant_ttc,
#         "statut": facture.statut,
#         "if_frs": facture.if_frs,
#         "ice_frs": facture.ice_frs,
#         "taux_tva": facture.taux_tva,
#         "id_paie": facture.id_paie,
#         "ded_file_path": facture.ded_file_path,
#         "ded_pdf_path": facture.ded_pdf_path,
#         "ded_xlsx_path": facture.ded_xlsx_path,
#     }


# @router.delete("/{facture_id}")
# def delete_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     db.delete(facture)
#     db.commit()
#     return {"message": "Facture supprimée"}














# import os
# import re
# import uuid
# from pathlib import Path
# from typing import Any, Dict, Optional, List, Tuple

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture

# from services import ocr_service
# from services import extract_fields

# from services.gemini_service import extract_invoice_fields_from_image_bytes
# from services.pdf_utils import pdf_to_png_images_bytes
# from services.validators import validate_or_fix, merge_fields

# from utils.parsers import parse_date_fr, parse_amount


# router = APIRouter(prefix="/factures", tags=["factures"])

# UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# # -------------------------
# # Helpers (I/O)
# # -------------------------

# def save_upload_file(upload: UploadFile) -> str:
#     ext = Path(upload.filename or "").suffix.lower()

#     if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
#         raise HTTPException(status_code=400, detail=f"Extension non supportée: {ext}")

#     unique_name = f"{uuid.uuid4()}{ext}"
#     dest = UPLOAD_DIR / unique_name

#     data = upload.file.read()
#     if not data:
#         raise HTTPException(status_code=400, detail="Fichier vide")

#     with open(dest, "wb") as f:
#         f.write(data)

#     return str(dest)


# def guess_mime_type(file_path: str) -> str:
#     ext = Path(file_path).suffix.lower()
#     if ext == ".png":
#         return "image/png"
#     if ext in [".jpg", ".jpeg"]:
#         return "image/jpeg"
#     if ext == ".webp":
#         return "image/webp"
#     if ext in [".tif", ".tiff"]:
#         return "image/tiff"
#     return "application/octet-stream"


# def to_dict(obj: Any) -> Dict[str, Any]:
#     if obj is None:
#         return {}
#     if isinstance(obj, dict):
#         return obj
#     if hasattr(obj, "dict"):
#         return obj.dict()
#     if hasattr(obj, "__dict__"):
#         return dict(obj.__dict__)
#     return dict(obj)


# # -------------------------
# # OCR text helpers (for post-processing)
# # -------------------------

# def _get_ocr_text(ocr: Any) -> str:
#     """
#     On se base sur ocr.preview (tu l'affiches déjà), sinon ocr.text si tu l'as,
#     sinon vide.
#     """
#     t = getattr(ocr, "text", None) or getattr(ocr, "preview", None) or ""
#     if not isinstance(t, str):
#         t = str(t)
#     # normalisation simple
#     t = t.replace("\r", "\n")
#     t = re.sub(r"[ \t]+", " ", t)
#     return t


# def _looks_like_patente_context(text: str, value: str) -> bool:
#     """
#     Si la valeur apparait près du mot "Patente" (ou "PATENTE"), c'est suspect.
#     """
#     if not text or not value:
#         return False
#     # fenêtre de contexte autour de l'occurrence
#     idx = text.lower().find(value.lower())
#     if idx == -1:
#         return False
#     window = text[max(0, idx - 40): idx + len(value) + 40].lower()
#     return "patente" in window


# def _looks_like_invoice_number(value: str) -> bool:
#     """
#     Facture: souvent alphanum ou contient / ou - (ex 00005252/25, FA250152)
#     """
#     if not value:
#         return False
#     v = value.strip()
#     if len(v) < 4:
#         return False
#     # accepte lettres/chiffres + séparateurs classiques
#     return bool(re.fullmatch(r"[A-Z0-9][A-Z0-9\/\-\._]{2,}", v, flags=re.IGNORECASE))


# def _extract_invoice_number_from_text(text: str) -> Optional[str]:
#     """
#     Cherche un numéro de facture UNIQUEMENT près de "FACTURE".
#     Ignore les zones RC/CNSS/LF/ICE/Patente.
#     """
#     if not text:
#         return None

#     lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
#     joined = "\n".join(lines)

#     # patterns centrés sur "FACTURE"
#     patterns = [
#         # FACTURE N° : 00005252/25
#         r"FACTURE\s*(?:N|N°|NO|NUM|NUMERO)?\s*[:#\-]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         # Tableau type: "FACTURE N° | 00005252/25"
#         r"FACTURE\s*(?:N|N°|NO)\s*\|?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#     ]

#     candidates: List[str] = []
#     for pat in patterns:
#         for m in re.finditer(pat, joined, flags=re.IGNORECASE):
#             cand = (m.group(1) or "").strip()
#             # filtre: évite les mentions admin
#             # si le contexte proche contient patente/rc/cnss/lf/ice, on ignore
#             start = max(0, m.start() - 60)
#             end = min(len(joined), m.end() + 60)
#             ctx = joined[start:end].lower()
#             if any(k in ctx for k in ["patente", "r.c", "rc ", "cnss", "l.f", "lf ", "ice", "if "]):
#                 continue
#             if _looks_like_invoice_number(cand):
#                 candidates.append(cand)

#     # heuristique: préfère ceux qui contiennent "/" ou lettres (souvent facture)
#     if not candidates:
#         return None

#     def score(v: str) -> Tuple[int, int]:
#         s = 0
#         if "/" in v:
#             s += 5
#         if re.search(r"[A-Z]", v, flags=re.IGNORECASE):
#             s += 3
#         if re.fullmatch(r"\d+", v):
#             s -= 2  # juste des chiffres => plus ambigu
#         return (s, len(v))

#     candidates.sort(key=score, reverse=True)
#     return candidates[0]


# def _fix_montant_tva(fields: Dict[str, Any]) -> List[str]:
#     """
#     Corrige le cas: montant_tva = 20 (taux), au lieu d'un montant.
#     """
#     issues: List[str] = []
#     ht = parse_amount(fields.get("montant_ht"))
#     ttc = parse_amount(fields.get("montant_ttc"))
#     tva = parse_amount(fields.get("montant_tva"))
#     taux = parse_amount(fields.get("taux_tva"))

#     # si TVA manquante et ht/ttc ok => calcule par différence
#     if (tva is None or tva == 0) and (ht is not None) and (ttc is not None) and ttc >= ht:
#         calc = round(ttc - ht, 2)
#         fields["montant_tva"] = calc
#         issues.append(f"montant_tva recalculé = TTC-HT ({calc})")
#         return issues

#     # cas principal: montant_tva ressemble à un taux (<=100) ET égal au taux => c'est un taux, pas un montant
#     if tva is not None and 0 < tva <= 100 and taux is not None and abs(tva - taux) < 0.001:
#         if ht is not None:
#             calc = round(ht * (taux / 100.0), 2)
#             fields["montant_tva"] = calc
#             issues.append(f"montant_tva était un taux ({tva}), corrigé via HT*taux = {calc}")
#             # si ttc existe, on peut aussi vérifier cohérence
#             if ttc is not None:
#                 expected = round(ht + calc, 2)
#                 if abs(expected - ttc) > 2.0:  # tolérance
#                     issues.append(f"Incohérence TTC (attendu ~{expected}, reçu {ttc})")
#         elif ttc is not None and ht is not None:
#             calc = round(ttc - ht, 2)
#             fields["montant_tva"] = calc
#             issues.append(f"montant_tva corrigé via TTC-HT = {calc}")

#     # cohérence finale si tout est dispo
#     ht = parse_amount(fields.get("montant_ht"))
#     ttc = parse_amount(fields.get("montant_ttc"))
#     tva = parse_amount(fields.get("montant_tva"))
#     if ht is not None and tva is not None and ttc is not None:
#         expected = round(ht + tva, 2)
#         if abs(expected - ttc) > 2.0:
#             issues.append(f"Vérifie montants: HT+TVA={expected} ≠ TTC={ttc} (tolérance dépassée)")

#     return issues


# def postprocess_fields_with_ocr(ocr: Any, fields: Dict[str, Any]) -> List[str]:
#     """
#     Post-correction:
#     - numero_facture: ne jamais prendre Patente N°
#     - montant_tva: ne pas confondre montant et taux
#     """
#     issues: List[str] = []
#     text = _get_ocr_text(ocr)

#     # --- Fix numero_facture
#     current = (fields.get("numero_facture") or "").strip()
#     # si null/vides => tente extraction
#     if not current:
#         extracted = _extract_invoice_number_from_text(text)
#         if extracted:
#             fields["numero_facture"] = extracted
#             issues.append(f"numero_facture récupéré depuis OCR: {extracted}")
#     else:
#         # si c'est le numéro qui apparait près de "Patente", on le remplace
#         if _looks_like_patente_context(text, current):
#             extracted = _extract_invoice_number_from_text(text)
#             if extracted and extracted != current:
#                 fields["numero_facture"] = extracted
#                 issues.append(f"numero_facture '{current}' semblait Patente, remplacé par '{extracted}'")
#         else:
#             # autre heuristique: si purement digits et que dans le texte on a un candidat avec / => préfère celui avec /
#             if re.fullmatch(r"\d{5,12}", current):
#                 extracted = _extract_invoice_number_from_text(text)
#                 if extracted and ("/" in extracted or re.search(r"[A-Z]", extracted, re.IGNORECASE)) and extracted != current:
#                     fields["numero_facture"] = extracted
#                     issues.append(f"numero_facture '{current}' ambigu, remplacé par '{extracted}'")

#     # --- Fix TVA (montant vs taux)
#     issues.extend(_fix_montant_tva(fields))

#     return issues


# # -------------------------
# # Gemini decision + extraction
# # -------------------------

# def should_use_gemini(ocr: Any, fields: Dict[str, Any]) -> bool:
#     """
#     Ne déclenche Gemini que si champs critiques manquants.
#     (Tu peux ajuster selon ton besoin.)
#     """
#     important_keys = ["numero_facture", "montant_ttc", "montant_ht", "ice_frs"]
#     null_count = sum(1 for k in important_keys if fields.get(k) in [None, "", 0])

#     chars = getattr(ocr, "chars", None)
#     low_chars = (chars is not None and chars < 700)

#     return null_count >= 2 or low_chars


# def extract_with_gemini(file_path: str) -> Dict[str, Any]:
#     ext = Path(file_path).suffix.lower()

#     if ext == ".pdf":
#         images = pdf_to_png_images_bytes(file_path, dpi=300, max_pages=1)
#         if not images:
#             raise HTTPException(status_code=500, detail="Impossible de convertir le PDF en image")
#         image_bytes = images[0]
#         mime_type = "image/png"
#     else:
#         with open(file_path, "rb") as f:
#             image_bytes = f.read()
#         mime_type = guess_mime_type(file_path)

#     gemini_raw = extract_invoice_fields_from_image_bytes(image_bytes, mime_type=mime_type)
#     gemini_clean, issues = validate_or_fix(gemini_raw)
#     gemini_clean["_gemini_issues"] = issues
#     return gemini_clean


# # -------------------------
# # Endpoints
# # -------------------------

# @router.post("/upload-facture/")
# def upload_facture(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     file_path = save_upload_file(file)

#     # 1) OCR
#     ocr = ocr_service.extract(file_path)

#     # 2) Extraction classique
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_issues: List[str] = []
#     post_issues: List[str] = []

#     # 3) Fallback Gemini (protégé)
#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             fields = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             # IMPORTANT: ne pas faire planter l’API
#             used_gemini = False
#             gemini_issues.append(f"Gemini failed: {e}")

#     # 4) Post-corrections basées sur OCR (résout patente vs facture, tva vs taux)
#     post_issues = postprocess_fields_with_ocr(ocr, fields)

#     # 5) Règle métier
#     fields["date_paie"] = fields.get("date_facture")

#     # 6) Conversion types pour DB
#     date_facture_db = parse_date_fr(fields.get("date_facture"))
#     date_paie_db = parse_date_fr(fields.get("date_paie"))

#     facture = Facture(
#         fournisseur=fields.get("fournisseur"),
#         date_facture=date_facture_db,
#         date_paie=date_paie_db,
#         numero_facture=fields.get("numero_facture"),
#         designation=fields.get("designation"),

#         montant_ht=parse_amount(fields.get("montant_ht")),
#         montant_tva=parse_amount(fields.get("montant_tva")),
#         montant_ttc=parse_amount(fields.get("montant_ttc")),

#         statut="brouillon",

#         if_frs=fields.get("if_frs") or fields.get("if_fiscal"),
#         ice_frs=fields.get("ice_frs") or fields.get("ice"),

#         taux_tva=parse_amount(fields.get("taux_tva")),
#         id_paie=fields.get("id_paie"),

#         ded_file_path=file_path,
#     )

#     db.add(facture)
#     db.commit()
#     db.refresh(facture)

#     return {
#         "message": "Facture uploadée et enregistrée",
#         "id": facture.id,
#         "file_path": file_path,
#         "used_gemini": used_gemini,
#         "gemini_issues": gemini_issues,
#         "post_issues": post_issues,
#         "ocr": {
#             "method": getattr(ocr, "method", None),
#             "pages": getattr(ocr, "pages", None),
#             "chars": getattr(ocr, "chars", None),
#             "preview": getattr(ocr, "preview", None),
#         },
#         "fields": fields,
#     }


# @router.post("/debug-extract/")
# def debug_extract(file: UploadFile = File(...)):
#     file_path = save_upload_file(file)

#     ocr = ocr_service.extract(file_path)
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_fields: Optional[Dict[str, Any]] = None
#     gemini_issues: List[str] = []

#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             merged = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_issues.append(f"Gemini failed: {e}")
#             merged = fields
#     else:
#         merged = fields

#     post_issues = postprocess_fields_with_ocr(ocr, merged)
#     merged["date_paie"] = merged.get("date_facture")

#     return {
#         "file_path": file_path,
#         "used_gemini": used_gemini,
#         "gemini_issues": gemini_issues,
#         "post_issues": post_issues,
#         "ocr": {
#             "method": getattr(ocr, "method", None),
#             "pages": getattr(ocr, "pages", None),
#             "chars": getattr(ocr, "chars", None),
#             "preview": getattr(ocr, "preview", None),
#         },
#         "classic_fields": fields,
#         "gemini_fields": gemini_fields,
#         "merged_fields": merged,
#     }


# @router.get("/")
# def list_factures(db: Session = Depends(get_db)):
#     factures = db.query(Facture).order_by(Facture.id.desc()).all()
#     return [
#         {
#             "id": f.id,
#             "fournisseur": f.fournisseur,
#             "date_facture": str(f.date_facture) if f.date_facture else None,
#             "numero_facture": f.numero_facture,
#             "montant_ht": f.montant_ht,
#             "montant_tva": f.montant_tva,
#             "montant_ttc": f.montant_ttc,
#             "statut": f.statut,
#             "ice_frs": f.ice_frs,
#             "if_frs": f.if_frs,
#         }
#         for f in factures
#     ]


# @router.get("/{facture_id}")
# def get_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     return {
#         "id": facture.id,
#         "fournisseur": facture.fournisseur,
#         "date_facture": str(facture.date_facture) if facture.date_facture else None,
#         "date_paie": str(facture.date_paie) if facture.date_paie else None,
#         "numero_facture": facture.numero_facture,
#         "designation": facture.designation,
#         "montant_ht": facture.montant_ht,
#         "montant_tva": facture.montant_tva,
#         "montant_ttc": facture.montant_ttc,
#         "statut": facture.statut,
#         "if_frs": facture.if_frs,
#         "ice_frs": facture.ice_frs,
#         "taux_tva": facture.taux_tva,
#         "id_paie": facture.id_paie,
#         "ded_file_path": facture.ded_file_path,
#         "ded_pdf_path": facture.ded_pdf_path,
#         "ded_xlsx_path": facture.ded_xlsx_path,
#     }


# @router.delete("/{facture_id}")
# def delete_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     db.delete(facture)
#     db.commit()
#     return {"message": "Facture supprimée"}












# routes/factures.py

import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Facture

from services import ocr_service
from services import extract_fields

from services.gemini_service import extract_invoice_fields_from_image_bytes
from services.pdf_utils import pdf_to_png_images_bytes
from services.validators import validate_or_fix, merge_fields

from utils.parsers import parse_date_fr, parse_amount

router = APIRouter(prefix="/factures", tags=["factures"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# File helpers
# -------------------------

def save_upload_file(upload: UploadFile) -> str:
    ext = Path(upload.filename or "").suffix.lower()

    if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
        raise HTTPException(status_code=400, detail=f"Extension non supportée: {ext}")

    unique_name = f"{uuid.uuid4()}{ext}"
    dest = UPLOAD_DIR / unique_name

    data = upload.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Fichier vide")

    with open(dest, "wb") as f:
        f.write(data)

    return str(dest)


def guess_mime_type(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".png":
        return "image/png"
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    if ext == ".webp":
        return "image/webp"
    if ext in [".tif", ".tiff"]:
        return "image/tiff"
    return "application/octet-stream"


def to_dict(obj: Any) -> Dict[str, Any]:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "dict"):
        return obj.dict()
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    return dict(obj)


# -------------------------
# OCR post-processing helpers (NUM FACTURE / TVA)
# -------------------------

def _get_ocr_text(ocr: Any) -> str:
    # ton ocr_service met généralement "preview" ; sinon adapte ici
    txt = getattr(ocr, "preview", None)
    if isinstance(txt, str) and txt.strip():
        return txt
    # fallback (si jamais tu as un champ "text")
    txt = getattr(ocr, "text", None)
    return txt if isinstance(txt, str) else ""


def _looks_like_invoice_number(v: str) -> bool:
    if not v:
        return False
    v = v.strip()
    # trop court / trop long
    if len(v) < 4 or len(v) > 30:
        return False
    # évite ICE/IF (souvent très longs numériques)
    if re.fullmatch(r"\d{14,20}", v):
        return False
    return True


def _looks_like_patente_context(text: str, value: str) -> bool:
    if not text or not value:
        return False
    val = re.escape(value.strip())
    # regarde la "zone" autour du numéro
    m = re.search(rf"(.{{0,80}}{val}.{{0,80}})", text, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return False
    ctx = m.group(1).lower()
    return any(k in ctx for k in ["patente", "patente.", "patente n", "patente n°", "patente.no", "patente.n"])


def _extract_invoice_number_from_text(text: str, date_facture: Optional[str] = None) -> Optional[str]:
    """
    Priorité:
      1) "FACTURE N° xxx"
      2) fallback robuste: motif "00005252/25" (numéro avec /), idéalement sur la ligne qui contient la date_facture
      3) sinon: meilleur candidat global (en évitant RC/CNSS/IF/ICE/PATENTE)
    """
    if not text:
        return None

    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    joined = "\n".join(lines)

    # 1) près du mot FACTURE
    patterns = [
        r"FACTURE\s*(?:N|N°|NO|NUM|NUMERO)?\s*[:#\-]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
        r"FACTURE\s*(?:N|N°|NO)\s*\|?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
        r"N°\s*FACTURE\s*[:#\-]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
    ]

    candidates: List[str] = []
    for pat in patterns:
        for m in re.finditer(pat, joined, flags=re.IGNORECASE):
            cand = (m.group(1) or "").strip()
            start = max(0, m.start() - 80)
            end = min(len(joined), m.end() + 80)
            ctx = joined[start:end].lower()
            if any(k in ctx for k in ["patente", "r.c", "rc ", "cnss", "l.f", "lf ", "ice", "if "]):
                continue
            if _looks_like_invoice_number(cand):
                candidates.append(cand)

    if candidates:
        def score(v: str):
            s = 0
            if "/" in v: s += 12
            if re.search(r"[A-Z]", v, flags=re.IGNORECASE): s += 5
            if re.fullmatch(r"\d+", v): s -= 2
            return (s, len(v))
        candidates.sort(key=score, reverse=True)
        return candidates[0]

    # 2) fallback "nombre/nombre" (ex: 00005252/25)
    slash_re = re.compile(r"\b(\d{4,}\/\d{2,4})\b")
    slash_candidates: List[str] = []

    if date_facture:
        for ln in lines:
            if date_facture in ln:
                for m in slash_re.finditer(ln):
                    cand = m.group(1).strip()
                    ctx = ln.lower()
                    if "patente" in ctx:
                        continue
                    slash_candidates.append(cand)

    if not slash_candidates:
        for ln in lines:
            for m in slash_re.finditer(ln):
                cand = m.group(1).strip()
                ctx = ln.lower()
                if any(k in ctx for k in ["patente", "r.c", "rc ", "cnss", "l.f", "lf ", "ice", "if "]):
                    continue
                slash_candidates.append(cand)

    if slash_candidates:
        slash_candidates.sort(key=lambda x: ("/" in x, len(x)), reverse=True)
        return slash_candidates[0]

    # 3) dernier recours: un token "style facture" pas trop long, éviter les labels fiscaux
    token_re = re.compile(r"\b([A-Z]{1,4}\d{3,}|\d{4,}[A-Z]{1,4}|\d{6,})\b")
    pool: List[Tuple[str, str]] = []
    for ln in lines:
        lnl = ln.lower()
        if any(k in lnl for k in ["patente", "r.c", "rc ", "cnss", "ice", "if ", "l.f", "lf "]):
            continue
        for m in token_re.finditer(ln):
            cand = m.group(1).strip()
            if _looks_like_invoice_number(cand):
                pool.append((cand, ln))

    if pool:
        # préfère ceux proches de la date si possible
        if date_facture:
            near = [c for c, ln in pool if date_facture in ln]
            if near:
                near.sort(key=len, reverse=True)
                return near[0]
        pool.sort(key=lambda t: len(t[0]), reverse=True)
        return pool[0][0]

    return None


def _fix_montant_tva(fields: Dict[str, Any]) -> Optional[str]:
    """
    Corrige le cas classique:
      montant_tva = 20 (taux) au lieu d'un montant.
    Stratégie:
      - si montant_tva == taux_tva et (ht & ttc) => montant_tva = ttc - ht
      - sinon si ht & taux => montant_tva = ht * taux/100
      - sinon si ttc & taux => ht = ttc/(1+taux/100) (pas demandé mais utile), montant_tva = ttc-ht
    """
    ht = parse_amount(fields.get("montant_ht"))
    ttc = parse_amount(fields.get("montant_ttc"))
    mtva = parse_amount(fields.get("montant_tva"))
    taux = parse_amount(fields.get("taux_tva"))

    if mtva is None or taux is None:
        return None

    # si mtva ressemble à un taux (ex: 20) et HT/TTC existent
    if ht is not None and ttc is not None:
        # si mtva == taux (ou très proche) => c'est un taux, pas un montant
        if abs(mtva - taux) < 0.0001 and taux in [7, 10, 14, 20]:
            fixed = round(ttc - ht, 2)
            if fixed >= 0:
                fields["montant_tva"] = fixed
                return f"montant_tva corrigé (taux détecté): {mtva} -> {fixed}"

        # si mtva est null/0 alors calcule
        if mtva in [0, None]:
            fixed = round(ttc - ht, 2)
            if fixed >= 0:
                fields["montant_tva"] = fixed
                return f"montant_tva calculé: {fixed}"

    if ht is not None and taux is not None and taux > 0 and taux <= 30:
        # cas mtva == taux (taux mal mis)
        if abs(mtva - taux) < 0.0001 and taux in [7, 10, 14, 20]:
            fixed = round(ht * (taux / 100.0), 2)
            fields["montant_tva"] = fixed
            return f"montant_tva corrigé (taux détecté): {mtva} -> {fixed}"

    if ttc is not None and taux is not None and taux > 0 and taux <= 30 and ht is None:
        ht_calc = round(ttc / (1.0 + (taux / 100.0)), 2)
        fields["montant_ht"] = ht_calc
        fields["montant_tva"] = round(ttc - ht_calc, 2)
        return f"montant_ht+montant_tva déduits depuis TTC+taux: ht={fields['montant_ht']} tva={fields['montant_tva']}"

    return None


def postprocess_fields_with_ocr(ocr: Any, fields: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    text = _get_ocr_text(ocr)

    date_facture = (fields.get("date_facture") or "").strip() or None
    current = (fields.get("numero_facture") or "").strip()

    # 1) si numero_facture vide => on tente extraire
    if not current:
        extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
        if extracted:
            fields["numero_facture"] = extracted
            issues.append(f"numero_facture récupéré depuis OCR: {extracted}")

    # 2) si numero_facture existe mais semble être une Patente => remplacer
    else:
        if _looks_like_patente_context(text, current):
            extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
            if extracted and extracted != current:
                fields["numero_facture"] = extracted
                issues.append(f"numero_facture '{current}' (Patente) remplacé par '{extracted}'")

        # 3) si seulement chiffres, et on trouve un candidat avec "/" => on préfère celui avec "/"
        elif re.fullmatch(r"\d{5,12}", current):
            extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
            if extracted and "/" in extracted and extracted != current:
                fields["numero_facture"] = extracted
                issues.append(f"numero_facture '{current}' ambigu remplacé par '{extracted}'")

    # TVA confusion fix
    msg = _fix_montant_tva(fields)
    if msg:
        issues.append(msg)

    return issues


# -------------------------
# Gemini helpers
# -------------------------

def should_use_gemini(ocr: Any, fields: Dict[str, Any]) -> bool:
    # IMPORTANT: ne pas forcer Gemini si le DNS est cassé; mais ici on décide seulement.
    important_keys = ["numero_facture", "montant_ttc", "montant_tva", "ice_frs"]
    null_count = sum(1 for k in important_keys if fields.get(k) in [None, "", 0])

    chars = getattr(ocr, "chars", None)
    low_chars = (chars is not None and chars < 700)

    return null_count >= 2 or low_chars


def extract_with_gemini(file_path: str) -> Dict[str, Any]:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        images = pdf_to_png_images_bytes(file_path, dpi=300, max_pages=1)
        if not images:
            raise HTTPException(status_code=500, detail="Impossible de convertir le PDF en image")
        image_bytes = images[0]
        mime_type = "image/png"
    else:
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        mime_type = guess_mime_type(file_path)

    gemini_raw = extract_invoice_fields_from_image_bytes(image_bytes, mime_type=mime_type)
    gemini_clean, issues = validate_or_fix(gemini_raw)
    gemini_clean["_gemini_issues"] = issues
    return gemini_clean


# -------------------------
# Endpoints
# -------------------------

@router.post("/upload-facture/")
def upload_facture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload facture -> OCR -> extraction -> fallback Gemini (si dispo) -> postprocess OCR -> DB
    """
    file_path = save_upload_file(file)

    # 1) OCR
    ocr = ocr_service.extract(file_path)

    # 2) Extraction classique
    extracted = extract_fields.extract_fields_from_ocr(ocr)
    fields = to_dict(extracted)

    used_gemini = False
    gemini_issues: List[str] = []
    post_issues: List[str] = []

    # 3) Fallback Gemini (mais NE PAS planter si DNS / clé / quota)
    if should_use_gemini(ocr, fields):
        try:
            used_gemini = True
            gemini_fields = extract_with_gemini(file_path)
            gemini_issues = gemini_fields.pop("_gemini_issues", [])
            fields = merge_fields(fields, gemini_fields)
        except Exception as e:
            # IMPORTANT: on ne casse pas l'API, on continue en OCR
            used_gemini = False
            gemini_issues = [f"Gemini failed: {e}"]

    # 4) Règle métier
    fields["date_paie"] = fields.get("date_facture")

    # 5) Post-processing OCR (corrige N° facture vs Patente + TVA)
    post_issues = postprocess_fields_with_ocr(ocr, fields)

    # 6) Conversion types pour DB
    date_facture_db = parse_date_fr(fields.get("date_facture"))
    date_paie_db = parse_date_fr(fields.get("date_paie"))

    facture = Facture(
        fournisseur=fields.get("fournisseur"),
        date_facture=date_facture_db,
        date_paie=date_paie_db,
        numero_facture=fields.get("numero_facture"),
        designation=fields.get("designation"),

        montant_ht=parse_amount(fields.get("montant_ht")),
        montant_tva=parse_amount(fields.get("montant_tva")),
        montant_ttc=parse_amount(fields.get("montant_ttc")),

        statut="brouillon",

        if_frs=fields.get("if_frs") or fields.get("if_fiscal"),
        ice_frs=fields.get("ice_frs") or fields.get("ice"),

        taux_tva=parse_amount(fields.get("taux_tva")),
        id_paie=fields.get("id_paie"),

        ded_file_path=file_path,
    )

    db.add(facture)
    db.commit()
    db.refresh(facture)

    return {
        "message": "Facture uploadée et enregistrée",
        "id": facture.id,
        "file_path": file_path,
        "used_gemini": used_gemini,
        "gemini_issues": gemini_issues,
        "post_issues": post_issues,
        "ocr": {
            "method": getattr(ocr, "method", None),
            "pages": getattr(ocr, "pages", None),
            "chars": getattr(ocr, "chars", None),
            "preview": getattr(ocr, "preview", None),
        },
        "fields": fields,
    }


@router.post("/debug-extract/")
def debug_extract(
    file: UploadFile = File(...),
):
    """
    Debug extraction: renvoie OCR preview + champs classiques + Gemini + merged + postprocess.
    """
    file_path = save_upload_file(file)

    ocr = ocr_service.extract(file_path)
    extracted = extract_fields.extract_fields_from_ocr(ocr)
    fields = to_dict(extracted)

    used_gemini = False
    gemini_fields: Optional[Dict[str, Any]] = None
    gemini_issues: List[str] = []

    merged = dict(fields)

    if should_use_gemini(ocr, fields):
        try:
            used_gemini = True
            gemini_fields = extract_with_gemini(file_path)
            gemini_issues = gemini_fields.pop("_gemini_issues", [])
            merged = merge_fields(fields, gemini_fields)
        except Exception as e:
            used_gemini = False
            gemini_issues = [f"Gemini failed: {e}"]
            merged = dict(fields)

    merged["date_paie"] = merged.get("date_facture")

    post_issues = postprocess_fields_with_ocr(ocr, merged)

    return {
        "file_path": file_path,
        "used_gemini": used_gemini,
        "gemini_issues": gemini_issues,
        "post_issues": post_issues,
        "ocr": {
            "method": getattr(ocr, "method", None),
            "pages": getattr(ocr, "pages", None),
            "chars": getattr(ocr, "chars", None),
            "preview": getattr(ocr, "preview", None),
        },
        "classic_fields": fields,
        "gemini_fields": gemini_fields,
        "merged_fields": merged,
    }


@router.get("/")
def list_factures(db: Session = Depends(get_db)):
    factures = db.query(Facture).order_by(Facture.id.desc()).all()

    return [
        {
            "id": f.id,
            "fournisseur": f.fournisseur,
            "date_facture": str(f.date_facture) if f.date_facture else None,
            "numero_facture": f.numero_facture,
            "montant_ht": f.montant_ht,
            "montant_tva": f.montant_tva,
            "montant_ttc": f.montant_ttc,
            "statut": f.statut,
            "ice_frs": f.ice_frs,
            "if_frs": f.if_frs,
        }
        for f in factures
    ]


@router.get("/{facture_id}")
def get_facture(facture_id: int, db: Session = Depends(get_db)):
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture introuvable")

    return {
        "id": facture.id,
        "fournisseur": facture.fournisseur,
        "date_facture": str(facture.date_facture) if facture.date_facture else None,
        "date_paie": str(facture.date_paie) if facture.date_paie else None,
        "numero_facture": facture.numero_facture,
        "designation": facture.designation,
        "montant_ht": facture.montant_ht,
        "montant_tva": facture.montant_tva,
        "montant_ttc": facture.montant_ttc,
        "statut": facture.statut,
        "if_frs": facture.if_frs,
        "ice_frs": facture.ice_frs,
        "taux_tva": facture.taux_tva,
        "id_paie": facture.id_paie,
        "ded_file_path": facture.ded_file_path,
        "ded_pdf_path": facture.ded_pdf_path,
        "ded_xlsx_path": facture.ded_xlsx_path,
    }


@router.delete("/{facture_id}")
def delete_facture(facture_id: int, db: Session = Depends(get_db)):
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture introuvable")

    db.delete(facture)
    db.commit()
    return {"message": "Facture supprimée"}
