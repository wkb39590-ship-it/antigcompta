

























# # routes/factures.py
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
# # File helpers
# # -------------------------
# ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]


# def save_upload_file(upload: UploadFile) -> str:
#     ext = Path(upload.filename or "").suffix.lower()
#     if ext not in ALLOWED_EXTS:
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
# # OCR post-processing helpers (NUM FACTURE / TVA)
# # -------------------------
# def _get_ocr_text(ocr: Any) -> str:
#     txt = getattr(ocr, "preview", None)
#     if isinstance(txt, str) and txt.strip():
#         return txt
#     txt = getattr(ocr, "text", None)
#     return txt if isinstance(txt, str) else ""


# def _looks_like_invoice_number(v: str) -> bool:
#     if not v:
#         return False
#     v = v.strip()
#     if len(v) < 4 or len(v) > 30:
#         return False
#     # évite ICE (souvent 15 chiffres), etc.
#     if re.fullmatch(r"\d{14,20}", v):
#         return False
#     return True


# def _extract_invoice_number_from_text(text: str, date_facture: Optional[str] = None) -> Optional[str]:
#     """
#     Objectif: éviter RC/IF/ICE/CNSS/PATENTE et récupérer le N° facture.
#     Priorité:
#       1) "FACTURE N° xxx" (ou "Facture | 2025-416")
#       2) motif "00005252/25" (numéro avec /), surtout sur la ligne qui contient la date
#       3) meilleur candidat global (en évitant mots fiscaux)
#     """
#     if not text:
#         return None

#     # normalise un peu
#     t = text.replace("\r", "\n")
#     lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
#     joined = "\n".join(lines)

#     # Mots à éviter autour d'un candidat
#     bad_ctx = ["patente", "r.c", "rc", "cnss", "l.f", "lf", "ice", "if", "tp"]

#     # 1) Patterns "FACTURE ..."
#     patterns = [
#         r"\bFACTURE\b\s*(?:N|N°|NO|NUM|NUMERO)?\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"\bFACTURE\b\s*\|\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"\bN°\s*FACTURE\b\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#     ]

#     candidates: List[str] = []
#     for pat in patterns:
#         for m in re.finditer(pat, joined, flags=re.IGNORECASE):
#             cand = (m.group(1) or "").strip()

#             # contexte autour
#             start = max(0, m.start() - 90)
#             end = min(len(joined), m.end() + 90)
#             ctx = joined[start:end].lower()

#             if any(k in ctx for k in bad_ctx):
#                 continue
#             if _looks_like_invoice_number(cand):
#                 candidates.append(cand)

#     if candidates:
#         def score(v: str):
#             s = 0
#             if "/" in v: s += 20
#             if "-" in v: s += 10
#             if re.search(r"[A-Z]", v, flags=re.IGNORECASE): s += 6
#             if re.fullmatch(r"\d+", v): s -= 2
#             return (s, len(v))

#         candidates.sort(key=score, reverse=True)
#         return candidates[0]

#     # 2) Motif slash style 00005252/25
#     slash_re = re.compile(r"\b(\d{4,}\/\d{2,4})\b")
#     slash_candidates: List[str] = []

#     if date_facture:
#         for ln in lines:
#             if date_facture in ln:
#                 lnl = ln.lower()
#                 if any(k in lnl for k in bad_ctx):
#                     continue
#                 for m in slash_re.finditer(ln):
#                     slash_candidates.append(m.group(1).strip())

#     if not slash_candidates:
#         for ln in lines:
#             lnl = ln.lower()
#             if any(k in lnl for k in bad_ctx):
#                 continue
#             for m in slash_re.finditer(ln):
#                 slash_candidates.append(m.group(1).strip())

#     if slash_candidates:
#         slash_candidates.sort(key=len, reverse=True)
#         return slash_candidates[0]

#     # 3) fallback token
#     token_re = re.compile(r"\b([A-Z]{1,4}\d{3,}|\d{4,}[A-Z]{1,4}|\d{6,}|\d{4}\-\d{1,6})\b")
#     pool: List[Tuple[str, str]] = []

#     for ln in lines:
#         lnl = ln.lower()
#         if any(k in lnl for k in bad_ctx):
#             continue
#         for m in token_re.finditer(ln):
#             cand = m.group(1).strip()
#             if _looks_like_invoice_number(cand):
#                 pool.append((cand, ln))

#     if pool:
#         if date_facture:
#             near = [c for c, ln in pool if date_facture in ln]
#             if near:
#                 near.sort(key=len, reverse=True)
#                 return near[0]
#         pool.sort(key=lambda t: len(t[0]), reverse=True)
#         return pool[0][0]

#     return None


# def _fix_tva_from_ocr_text(fields: Dict[str, Any], text: str) -> Optional[str]:
#     """
#     Fix OCR: "TVA 200% 828.00" => taux=20, montant=828
#     + confusions: montant_tva = 20 (taux) au lieu de 828.00
#     """
#     if not text:
#         return None

#     t = text.replace("\r", "\n")
#     lines = [ln.strip() for ln in t.split("\n") if ln.strip()]

#     # 1) Cherche une ligne TVA et tente extraire (taux + montant)
#     for ln in lines:
#         if "TVA" not in ln.upper():
#             continue

#         # extrait un % s'il existe
#         m_pct = re.search(r"(\d{1,4}(?:[.,]\d{1,2})?)\s*%", ln)
#         taux = None
#         if m_pct:
#             raw = m_pct.group(1).replace(",", ".")
#             try:
#                 taux = float(raw)
#                 # fix 200 -> 20, 2000 -> 20 ...
#                 while taux > 100:
#                     taux /= 10.0
#                 if taux < 0 or taux > 100:
#                     taux = None
#                 else:
#                     taux = round(taux, 2)
#             except Exception:
#                 taux = None

#         # extrait un montant (dernier nombre "xx.xx")
#         nums = re.findall(r"(\d{1,3}(?:[ .,\u00A0]\d{3})*(?:[.,]\d{2})|\d+(?:[.,]\d{2}))", ln)
#         mtva = parse_amount(nums[-1]) if nums else None

#         # si on a trouvé quelque chose de plausible, on met à jour
#         changed = False
#         if taux is not None:
#             fields["taux_tva"] = taux
#             changed = True
#         if mtva is not None and mtva > 0:
#             fields["montant_tva"] = mtva
#             changed = True

#         if changed:
#             return f"TVA corrigée depuis OCR line: {ln}"

#     # 2) Sinon, corrige la confusion classique montant_tva=taux
#     ht = parse_amount(fields.get("montant_ht"))
#     ttc = parse_amount(fields.get("montant_ttc"))
#     mtva = parse_amount(fields.get("montant_tva"))
#     taux = parse_amount(fields.get("taux_tva"))

#     if mtva is None or taux is None:
#         return None

#     # si mtva ressemble à un taux (20) et HT/TTC existent => mtva = ttc - ht
#     if ht is not None and ttc is not None:
#         if abs(mtva - taux) < 0.0001 and taux <= 30:
#             fixed = round(ttc - ht, 2)
#             if fixed >= 0:
#                 fields["montant_tva"] = fixed
#                 return f"montant_tva corrigé (taux détecté): {mtva} -> {fixed}"

#     # si HT et taux => mtva = ht*taux/100
#     if ht is not None and taux is not None and 0 < taux <= 30:
#         if abs(mtva - taux) < 0.0001:
#             fixed = round(ht * (taux / 100.0), 2)
#             fields["montant_tva"] = fixed
#             return f"montant_tva recalculé via HT*taux: {mtva} -> {fixed}"

#     return None


# def postprocess_fields_with_ocr(ocr: Any, fields: Dict[str, Any]) -> List[str]:
#     issues: List[str] = []
#     text = _get_ocr_text(ocr)
#     date_facture = (fields.get("date_facture") or "").strip() or None

#     current = (fields.get("numero_facture") or "").strip()

#     # 1) si numero_facture vide => extraire depuis OCR
#     if not current:
#         extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
#         if extracted:
#             fields["numero_facture"] = extracted
#             issues.append(f"numero_facture récupéré depuis OCR: {extracted}")

#     # 2) si numero_facture est numérique pur, et on voit "Patente" dans le doc + on trouve un meilleur candidat => remplacer
#     else:
#         if re.fullmatch(r"\d{4,12}", current) and ("patente" in (text or "").lower()):
#             extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
#             if extracted and extracted != current:
#                 fields["numero_facture"] = extracted
#                 issues.append(f"numero_facture '{current}' remplacé par '{extracted}' (évite Patente/RC/ICE/IF)")

#     # 3) TVA fix
#     msg = _fix_tva_from_ocr_text(fields, text)
#     if msg:
#         issues.append(msg)

#     return issues


# # -------------------------
# # Gemini helpers
# # -------------------------
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
#     Upload facture -> OCR -> extraction -> fallback Gemini (si dispo) -> postprocess OCR -> DB
#     """
#     file_path = save_upload_file(file)

#     # 1) OCR
#     ocr = ocr_service.extract(file_path)

#     # 2) Extraction classique
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_issues: List[str] = []
#     post_issues: List[str] = []

#     # 3) Fallback Gemini (NE PAS planter si DNS / clé / quota)
#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             fields = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_issues = [f"Gemini failed: {e}"]

#     # 4) Règle métier
#     fields["date_paie"] = fields.get("date_facture")

#     # 5) Post-processing OCR (corrige N° facture vs Patente + TVA)
#     post_issues = postprocess_fields_with_ocr(ocr, fields)

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
#     """
#     Debug extraction: renvoie OCR preview + champs classiques + Gemini + merged + postprocess.
#     """
#     file_path = save_upload_file(file)

#     ocr = ocr_service.extract(file_path)
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_fields: Optional[Dict[str, Any]] = None
#     gemini_issues: List[str] = []

#     merged = dict(fields)

#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             merged = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_issues = [f"Gemini failed: {e}"]
#             merged = dict(fields)

#     merged["date_paie"] = merged.get("date_facture")
#     post_issues = postprocess_fields_with_ocr(ocr, merged)

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





# # routes/factures.py
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

# ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]


# def save_upload_file(upload: UploadFile) -> str:
#     ext = Path(upload.filename or "").suffix.lower()
#     if ext not in ALLOWED_EXTS:
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
# # OCR post-processing helpers
# # -------------------------
# def _get_ocr_text(ocr: Any) -> str:
#     txt = getattr(ocr, "preview", None)
#     if isinstance(txt, str) and txt.strip():
#         return txt
#     txt = getattr(ocr, "text", None)
#     return txt if isinstance(txt, str) else ""


# def _looks_like_invoice_number(v: str) -> bool:
#     if not v:
#         return False
#     v = v.strip()
#     if len(v) < 4 or len(v) > 30:
#         return False
#     if re.fullmatch(r"\d{14,20}", v):
#         return False
#     return True


# def _extract_invoice_number_from_text(text: str, date_facture: Optional[str] = None) -> Optional[str]:
#     if not text:
#         return None

#     t = text.replace("\r", "\n")
#     lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
#     joined = "\n".join(lines)

#     bad_ctx = ["patente", "r.c", "rc", "cnss", "l.f", "lf", "ice", "if", "tp"]

#     patterns = [
#         r"\bFACTURE\b\s*(?:N|N°|NO|NUM|NUMERO)?\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"\bFACTURE\b\s*\|\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"\bN°\s*FACTURE\b\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#     ]

#     candidates: List[str] = []
#     for pat in patterns:
#         for m in re.finditer(pat, joined, flags=re.IGNORECASE):
#             cand = (m.group(1) or "").strip()
#             start = max(0, m.start() - 90)
#             end = min(len(joined), m.end() + 90)
#             ctx = joined[start:end].lower()

#             if any(k in ctx for k in bad_ctx):
#                 continue
#             if _looks_like_invoice_number(cand):
#                 candidates.append(cand)

#     if candidates:
#         def score(v: str):
#             s = 0
#             if "/" in v:
#                 s += 20
#             if "-" in v:
#                 s += 10
#             if re.search(r"[A-Z]", v, flags=re.IGNORECASE):
#                 s += 6
#             if re.fullmatch(r"\d+", v):
#                 s -= 2
#             return (s, len(v))

#         candidates.sort(key=score, reverse=True)
#         return candidates[0]

#     return None


# def postprocess_fields_with_ocr(ocr: Any, fields: Dict[str, Any]) -> List[str]:
#     issues: List[str] = []
#     text = _get_ocr_text(ocr)
#     date_facture = (fields.get("date_facture") or "").strip() or None

#     current = (fields.get("numero_facture") or "").strip()
#     if not current:
#         extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
#         if extracted:
#             fields["numero_facture"] = extracted
#             issues.append(f"numero_facture récupéré depuis OCR: {extracted}")

#     return issues


# # -------------------------
# # Gemini helpers
# # -------------------------
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
#     file_path = save_upload_file(file)

#     # 1) OCR
#     ocr = ocr_service.extract(file_path)

#     # 2) Extraction classique
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_issues: List[str] = []
#     post_issues: List[str] = []

#     # 3) Fallback Gemini
#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             fields = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_issues = [f"Gemini failed: {e}"]

#     # 4) Règle métier
#     fields["date_paie"] = fields.get("date_facture")

#     # ✅ Champs NOT NULL
#     societe_id = 1
#     operation_type = "achat"

#     # ✅ Nouvelle colonne NOT NULL
#     # - si Gemini a été utilisé => plus confiant
#     operation_confidence = 0.85 if used_gemini else 0.60

#     # Pour afficher dans "fields" comme tu veux
#     fields["operation_type"] = operation_type
#     fields["operation_confidence"] = operation_confidence

#     # 5) Post-processing OCR
#     post_issues = postprocess_fields_with_ocr(ocr, fields)

#     # 6) Conversion types pour DB
#     date_facture_db = parse_date_fr(fields.get("date_facture"))
#     date_paie_db = parse_date_fr(fields.get("date_paie"))

#     facture = Facture(
#         societe_id=societe_id,
#         operation_type=operation_type,
#         operation_confidence=operation_confidence,

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

#     try:
#         db.add(facture)
#         db.commit()
#         db.refresh(facture)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

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


# @router.get("/")
# def list_factures(db: Session = Depends(get_db)):
#     factures = db.query(Facture).order_by(Facture.id.desc()).all()
#     return [
#         {
#             "id": f.id,
#             "societe_id": f.societe_id,
#             "operation_type": f.operation_type,
#             "operation_confidence": f.operation_confidence,
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




















# # routes/factures.py
# import os
# import re
# import uuid
# from pathlib import Path
# from typing import Any, Dict, Optional, List, Tuple

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture, Societe

# from services import ocr_service
# from services import extract_fields
# from services.gemini_service import extract_invoice_fields_from_image_bytes
# from services.pdf_utils import pdf_to_png_images_bytes
# from services.validators import validate_or_fix, merge_fields

# from utils.parsers import parse_date_fr, parse_amount

# router = APIRouter(prefix="/factures", tags=["factures"])

# UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]


# def save_upload_file(upload: UploadFile) -> str:
#     ext = Path(upload.filename or "").suffix.lower()
#     if ext not in ALLOWED_EXTS:
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
# # Helpers ICE -> achat/vente
# # -------------------------
# def _norm_ice(v: Optional[str]) -> str:
#     return (v or "").replace(" ", "").replace("\n", "").replace("\t", "").strip()


# def infer_operation_from_ice(societe_ice: Optional[str], facture_ice: Optional[str]) -> Tuple[str, float]:
#     s_ice = _norm_ice(societe_ice)
#     f_ice = _norm_ice(facture_ice)

#     if s_ice and f_ice:
#         # même ICE => facture émise par la société => vente
#         if s_ice == f_ice:
#             return "vente", 0.95
#         return "achat", 0.95

#     # ICE manquant => décision incertaine
#     return "achat", 0.60


# # -------------------------
# # OCR post-processing helpers
# # -------------------------
# def _get_ocr_text(ocr: Any) -> str:
#     txt = getattr(ocr, "preview", None)
#     if isinstance(txt, str) and txt.strip():
#         return txt
#     txt = getattr(ocr, "text", None)
#     return txt if isinstance(txt, str) else ""


# def _looks_like_invoice_number(v: str) -> bool:
#     if not v:
#         return False
#     v = v.strip()
#     if len(v) < 4 or len(v) > 30:
#         return False
#     if re.fullmatch(r"\d{14,20}", v):
#         return False
#     return True


# def _extract_invoice_number_from_text(text: str, date_facture: Optional[str] = None) -> Optional[str]:
#     if not text:
#         return None

#     t = text.replace("\r", "\n")
#     lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
#     joined = "\n".join(lines)

#     bad_ctx = ["patente", "r.c", "rc", "cnss", "l.f", "lf", "ice", "if", "tp"]

#     patterns = [
#         r"\bFACTURE\b\s*(?:N|N°|NO|NUM|NUMERO)?\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"\bFACTURE\b\s*\|\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"\bN°\s*FACTURE\b\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#     ]

#     candidates: List[str] = []
#     for pat in patterns:
#         for m in re.finditer(pat, joined, flags=re.IGNORECASE):
#             cand = (m.group(1) or "").strip()
#             start = max(0, m.start() - 90)
#             end = min(len(joined), m.end() + 90)
#             ctx = joined[start:end].lower()

#             if any(k in ctx for k in bad_ctx):
#                 continue
#             if _looks_like_invoice_number(cand):
#                 candidates.append(cand)

#     if candidates:
#         def score(v: str):
#             s = 0
#             if "/" in v:
#                 s += 20
#             if "-" in v:
#                 s += 10
#             if re.search(r"[A-Z]", v, flags=re.IGNORECASE):
#                 s += 6
#             if re.fullmatch(r"\d+", v):
#                 s -= 2
#             return (s, len(v))

#         candidates.sort(key=score, reverse=True)
#         return candidates[0]

#     return None


# def postprocess_fields_with_ocr(ocr: Any, fields: Dict[str, Any]) -> List[str]:
#     issues: List[str] = []
#     text = _get_ocr_text(ocr)
#     date_facture = (fields.get("date_facture") or "").strip() or None

#     current = (fields.get("numero_facture") or "").strip()
#     if not current:
#         extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
#         if extracted:
#             fields["numero_facture"] = extracted
#             issues.append(f"numero_facture récupéré depuis OCR: {extracted}")

#     return issues


# # -------------------------
# # Gemini helpers
# # -------------------------
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
#     societe_id: int = Query(..., description="ID de la société (entreprise) créée avant l'upload"),
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

#     # 3) Fallback Gemini
#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             fields = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_issues = [f"Gemini failed: {e}"]

#     # 4) Règle métier
#     fields["date_paie"] = fields.get("date_facture")

#     # ✅ charger la société
#     soc = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not soc:
#         raise HTTPException(status_code=400, detail="Société introuvable. Crée la société avant l’upload.")

#     # ✅ déterminer achat/vente depuis ICE
#     facture_ice = fields.get("ice_frs") or fields.get("ice")
#     operation_type, operation_confidence = infer_operation_from_ice(soc.ice, facture_ice)

#     fields["operation_type"] = operation_type
#     fields["operation_confidence"] = operation_confidence

#     # 5) post-processing OCR
#     post_issues = postprocess_fields_with_ocr(ocr, fields)

#     # 6) Conversion types pour DB
#     date_facture_db = parse_date_fr(fields.get("date_facture"))
#     date_paie_db = parse_date_fr(fields.get("date_paie"))

#     facture = Facture(
#         societe_id=societe_id,
#         operation_type=operation_type,
#         operation_confidence=operation_confidence,

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

#     try:
#         db.add(facture)
#         db.commit()
#         db.refresh(facture)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

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


# @router.get("/")
# def list_factures(db: Session = Depends(get_db)):
#     factures = db.query(Facture).order_by(Facture.id.desc()).all()
#     return [
#         {
#             "id": f.id,
#             "societe_id": f.societe_id,
#             "operation_type": f.operation_type,
#             "operation_confidence": f.operation_confidence,
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

















# # routes/factures.py
# import os
# import re
# import uuid
# from pathlib import Path
# from typing import Any, Dict, Optional, List

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture, Societe

# from services import ocr_service
# from services import extract_fields
# from services.gemini_service import extract_invoice_fields_from_image_bytes
# from services.pdf_utils import pdf_to_png_images_bytes
# from services.validators import validate_or_fix, merge_fields

# from utils.parsers import parse_date_fr, parse_amount

# router = APIRouter(prefix="/factures", tags=["factures"])

# UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]


# def save_upload_file(upload: UploadFile) -> str:
#     ext = Path(upload.filename or "").suffix.lower()
#     if ext not in ALLOWED_EXTS:
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


# def _get_ocr_text(ocr: Any) -> str:
#     txt = getattr(ocr, "preview", None)
#     if isinstance(txt, str) and txt.strip():
#         return txt
#     txt = getattr(ocr, "text", None)
#     return txt if isinstance(txt, str) else ""


# def _looks_like_invoice_number(v: str) -> bool:
#     if not v:
#         return False
#     v = v.strip()
#     if len(v) < 4 or len(v) > 30:
#         return False
#     if re.fullmatch(r"\d{14,20}", v):
#         return False
#     return True


# def _extract_invoice_number_from_text(text: str, date_facture: Optional[str] = None) -> Optional[str]:
#     if not text:
#         return None

#     t = text.replace("\r", "\n")
#     lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
#     joined = "\n".join(lines)

#     bad_ctx = ["patente", "r.c", "rc", "cnss", "l.f", "lf", "ice", "if", "tp"]

#     patterns = [
#         r"\bFACTURE\b\s*(?:N|N°|NO|NUM|NUMERO)?\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"\bFACTURE\b\s*\|\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"\bN°\s*FACTURE\b\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#     ]

#     candidates: List[str] = []
#     for pat in patterns:
#         for m in re.finditer(pat, joined, flags=re.IGNORECASE):
#             cand = (m.group(1) or "").strip()
#             start = max(0, m.start() - 90)
#             end = min(len(joined), m.end() + 90)
#             ctx = joined[start:end].lower()
#             if any(k in ctx for k in bad_ctx):
#                 continue
#             if _looks_like_invoice_number(cand):
#                 candidates.append(cand)

#     if candidates:
#         candidates.sort(key=len, reverse=True)
#         return candidates[0]

#     return None


# def postprocess_fields_with_ocr(ocr: Any, fields: Dict[str, Any]) -> List[str]:
#     issues: List[str] = []
#     text = _get_ocr_text(ocr)
#     date_facture = (fields.get("date_facture") or "").strip() or None

#     current = (fields.get("numero_facture") or "").strip()
#     if not current:
#         extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
#         if extracted:
#             fields["numero_facture"] = extracted
#             issues.append(f"numero_facture récupéré depuis OCR: {extracted}")

#     return issues


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


# @router.post("/upload-facture/")
# def upload_facture(
#     societe_id: int = Query(..., description="ID de la société (obligatoire)"),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     # ✅ Vérifier société
#     soc = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not soc:
#         raise HTTPException(status_code=404, detail="Société introuvable")

#     file_path = save_upload_file(file)

#     # 1) OCR
#     ocr = ocr_service.extract(file_path)

#     # 2) Extraction classique
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_issues: List[str] = []
#     post_issues: List[str] = []

#     # 3) Fallback Gemini
#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             fields = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_issues = [f"Gemini failed: {e}"]

#     # 4) règle métier: date_paie = date_facture
#     fields["date_paie"] = fields.get("date_facture")

#     # 5) Post-processing OCR
#     post_issues = postprocess_fields_with_ocr(ocr, fields)

#     # 6) ✅ Déterminer ACHAT/VENTE via ICE
#     ice_facture = (fields.get("ice_frs") or fields.get("ice") or "").strip()
#     ice_societe = (soc.ice or "").strip()

#     if ice_facture and ice_societe and ice_facture == ice_societe:
#         operation_type = "vente"
#         operation_confidence = 0.99
#     else:
#         operation_type = "achat"
#         operation_confidence = 0.85

#     fields["operation_type"] = operation_type
#     fields["operation_confidence"] = operation_confidence

#     # 7) Conversion types DB
#     date_facture_db = parse_date_fr(fields.get("date_facture"))
#     date_paie_db = parse_date_fr(fields.get("date_paie"))

#     facture = Facture(
#         societe_id=societe_id,
#         operation_type=operation_type,
#         operation_confidence=operation_confidence,

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
#         ice_frs=ice_facture or None,

#         taux_tva=parse_amount(fields.get("taux_tva")),
#         id_paie=fields.get("id_paie"),

#         ded_file_path=file_path,
#     )

#     try:
#         db.add(facture)
#         db.commit()
#         db.refresh(facture)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

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


# @router.get("/")
# def list_factures(db: Session = Depends(get_db)):
#     factures = db.query(Facture).order_by(Facture.id.desc()).all()
#     return [
#         {
#             "id": f.id,
#             "societe_id": f.societe_id,
#             "operation_type": f.operation_type,
#             "operation_confidence": f.operation_confidence,
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
#     f = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not f:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     return {
#         "id": f.id,
#         "societe_id": f.societe_id,
#         "operation_type": f.operation_type,
#         "operation_confidence": f.operation_confidence,
#         "fournisseur": f.fournisseur,
#         "date_facture": str(f.date_facture) if f.date_facture else None,
#         "date_paie": str(f.date_paie) if f.date_paie else None,
#         "numero_facture": f.numero_facture,
#         "designation": f.designation,
#         "montant_ht": f.montant_ht,
#         "montant_tva": f.montant_tva,
#         "montant_ttc": f.montant_ttc,
#         "statut": f.statut,
#         "if_frs": f.if_frs,
#         "ice_frs": f.ice_frs,
#         "taux_tva": f.taux_tva,
#         "ded_file_path": f.ded_file_path,
#         "ded_pdf_path": f.ded_pdf_path,
#         "ded_xlsx_path": f.ded_xlsx_path,
#     }


# @router.delete("/{facture_id}")
# def delete_facture(facture_id: int, db: Session = Depends(get_db)):
#     f = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not f:
#         raise HTTPException(status_code=404, detail="Facture introuvable")
#     db.delete(f)
#     db.commit()
#     return {"message": "Facture supprimée"}















# # routes/factures.py
# import os
# import re
# import uuid
# from pathlib import Path
# from typing import Any, Dict, Optional, List, Tuple

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture, Societe

# from services import ocr_service
# from services import extract_fields
# from services.gemini_service import extract_invoice_fields_from_image_bytes
# from services.pdf_utils import pdf_to_png_images_bytes
# from services.validators import validate_or_fix, merge_fields

# from utils.parsers import parse_date_fr, parse_amount

# router = APIRouter(prefix="/factures", tags=["factures"])

# UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]


# # -------------------------
# # Helpers
# # -------------------------
# def save_upload_file(upload: UploadFile) -> str:
#     ext = Path(upload.filename or "").suffix.lower()
#     if ext not in ALLOWED_EXTS:
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


# def normalize_ice(v: Optional[str]) -> Optional[str]:
#     if not v:
#         return None
#     # garde uniquement chiffres
#     digits = re.sub(r"\D+", "", str(v))
#     return digits or None


# def _get_ocr_text(ocr: Any) -> str:
#     txt = getattr(ocr, "preview", None)
#     if isinstance(txt, str) and txt.strip():
#         return txt
#     txt = getattr(ocr, "text", None)
#     return txt if isinstance(txt, str) else ""


# # -------------------------
# # OCR post-processing: facture number (simple)
# # -------------------------
# def _looks_like_invoice_number(v: str) -> bool:
#     if not v:
#         return False
#     v = v.strip()
#     if len(v) < 4 or len(v) > 30:
#         return False
#     # évite ICE (souvent 15+ chiffres)
#     if re.fullmatch(r"\d{14,20}", v):
#         return False
#     return True


# def _extract_invoice_number_from_text(text: str, date_facture: Optional[str] = None) -> Optional[str]:
#     if not text:
#         return None

#     t = text.replace("\r", "\n")
#     lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
#     joined = "\n".join(lines)

#     bad_ctx = ["patente", "r.c", "rc", "cnss", "l.f", "lf", "ice", "if", "tp"]

#     patterns = [
#         r"\bFACTURE\b\s*(?:N|N°|NO|NUM|NUMERO)?\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"\bN°\s*FACTURE\b\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#     ]

#     candidates: List[str] = []
#     for pat in patterns:
#         for m in re.finditer(pat, joined, flags=re.IGNORECASE):
#             cand = (m.group(1) or "").strip()

#             start = max(0, m.start() - 90)
#             end = min(len(joined), m.end() + 90)
#             ctx = joined[start:end].lower()

#             if any(k in ctx for k in bad_ctx):
#                 continue
#             if _looks_like_invoice_number(cand):
#                 candidates.append(cand)

#     if candidates:
#         # score basique: préfère slash ou lettres
#         def score(v: str):
#             s = 0
#             if "/" in v:
#                 s += 20
#             if "-" in v:
#                 s += 10
#             if re.search(r"[A-Z]", v, flags=re.IGNORECASE):
#                 s += 6
#             return (s, len(v))

#         candidates.sort(key=score, reverse=True)
#         return candidates[0]

#     return None


# def postprocess_fields_with_ocr(ocr: Any, fields: Dict[str, Any]) -> List[str]:
#     issues: List[str] = []
#     text = _get_ocr_text(ocr)
#     date_facture = (fields.get("date_facture") or "").strip() or None

#     current = (fields.get("numero_facture") or "").strip()
#     if not current:
#         extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
#         if extracted:
#             fields["numero_facture"] = extracted
#             issues.append(f"numero_facture récupéré depuis OCR: {extracted}")

#     return issues


# # -------------------------
# # TVA fix (IMPORTANT)
# # -------------------------
# def fix_tva_fields(fields: Dict[str, Any]) -> List[str]:
#     """
#     Corrige le cas classique:
#       montant_tva = 20 (taux) au lieu du montant.
#     Règle la plus fiable:
#       si HT et TTC existent => TVA = TTC - HT
#     """
#     issues: List[str] = []

#     ht = parse_amount(fields.get("montant_ht"))
#     ttc = parse_amount(fields.get("montant_ttc"))
#     mtva = parse_amount(fields.get("montant_tva"))
#     taux = parse_amount(fields.get("taux_tva"))

#     if ht is None or ttc is None:
#         return issues

#     computed = round(ttc - ht, 2)
#     if computed < 0:
#         return issues

#     # si mtva est vide OU ressemble à un taux (20) => corriger
#     if mtva is None:
#         fields["montant_tva"] = computed
#         issues.append(f"montant_tva fixé via TTC-HT: {computed}")
#         return issues

#     if taux is not None and abs(mtva - taux) < 0.0001:
#         fields["montant_tva"] = computed
#         issues.append(f"montant_tva corrigé (était taux {mtva}) -> {computed}")
#         return issues

#     # optionnel: si mtva est très petit vs computed, on corrige
#     if mtva >= 0 and computed > 0 and (mtva < computed * 0.2):
#         fields["montant_tva"] = computed
#         issues.append(f"montant_tva corrigé (trop petit) {mtva} -> {computed}")

#     return issues


# # -------------------------
# # Gemini helpers
# # -------------------------
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
# # Achat / Vente via ICE (ta règle métier)
# # -------------------------
# def decide_operation_type_and_confidence(
#     societe: Societe,
#     fields: Dict[str, Any],
#     used_gemini: bool,
# ) -> Tuple[str, float]:
#     """
#     Règle:
#       si ICE facture == ICE société -> vente
#       sinon -> achat
#     """
#     soc_ice = normalize_ice(societe.ice)

#     # on prend l'ICE extrait depuis facture (souvent "ice_frs" chez toi)
#     invoice_ice = normalize_ice(fields.get("ice_frs") or fields.get("ice"))

#     if not soc_ice or not invoice_ice:
#         # ICE manquant => on ne peut pas trancher à 100%
#         op = "achat"
#         conf = 0.55 if not used_gemini else 0.65
#         return op, conf

#     if invoice_ice == soc_ice:
#         op = "vente"
#         conf = 0.95 if used_gemini else 0.85
#         return op, conf

#     op = "achat"
#     conf = 0.90 if used_gemini else 0.80
#     return op, conf


# # -------------------------
# # Endpoints
# # -------------------------
# @router.post("/upload-facture/")
# def upload_facture(
#     societe_id: int = Form(...),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     """
#     Upload facture -> OCR -> extraction -> fallback Gemini -> corrections -> achat/vente via ICE -> DB
#     """
#     # 0) récupérer la société
#     societe = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not societe:
#         raise HTTPException(status_code=404, detail="Société introuvable (societe_id invalide)")

#     # 1) save
#     file_path = save_upload_file(file)

#     # 2) OCR
#     ocr = ocr_service.extract(file_path)

#     # 3) extraction classique
#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_issues: List[str] = []
#     post_issues: List[str] = []

#     # 4) fallback Gemini
#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             fields = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_issues = [f"Gemini failed: {e}"]

#     # 5) règle métier date_paie
#     fields["date_paie"] = fields.get("date_facture")

#     # 6) post OCR (num facture)
#     post_issues.extend(postprocess_fields_with_ocr(ocr, fields))

#     # 7) FIX TVA (TON PROBLÈME)
#     post_issues.extend(fix_tva_fields(fields))

#     # 8) achat / vente via ICE (TA RÈGLE)
#     operation_type, operation_confidence = decide_operation_type_and_confidence(societe, fields, used_gemini)
#     fields["operation_type"] = operation_type
#     fields["operation_confidence"] = operation_confidence

#     # 9) conversion types DB
#     date_facture_db = parse_date_fr(fields.get("date_facture"))
#     date_paie_db = parse_date_fr(fields.get("date_paie"))

#     facture = Facture(
#         societe_id=societe_id,
#         operation_type=operation_type,
#         operation_confidence=operation_confidence,

#         fournisseur=fields.get("fournisseur"),
#         date_facture=date_facture_db,
#         date_paie=date_paie_db,

#         numero_facture=fields.get("numero_facture"),
#         designation=fields.get("designation") or ("Achat fournisseur" if operation_type == "achat" else "Vente client"),

#         montant_ht=parse_amount(fields.get("montant_ht")),
#         montant_tva=parse_amount(fields.get("montant_tva")),
#         montant_ttc=parse_amount(fields.get("montant_ttc")),

#         statut="brouillon",

#         if_frs=fields.get("if_frs") or fields.get("if_fiscal"),
#         ice_frs=fields.get("ice_frs") or fields.get("ice"),

#         taux_tva=parse_amount(fields.get("taux_tva")),
#         id_paie=fields.get("id_paie"),

#         ded_file_path=file_path,
#         ded_pdf_path=fields.get("ded_pdf_path"),
#         ded_xlsx_path=fields.get("ded_xlsx_path"),
#     )

#     try:
#         db.add(facture)
#         db.commit()
#         db.refresh(facture)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

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
# def debug_extract(
#     societe_id: int = Form(...),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     """
#     Debug extraction: renvoie OCR preview + champs classiques + Gemini + merged + fixes.
#     """
#     societe = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not societe:
#         raise HTTPException(status_code=404, detail="Société introuvable (societe_id invalide)")

#     file_path = save_upload_file(file)
#     ocr = ocr_service.extract(file_path)

#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_fields: Optional[Dict[str, Any]] = None
#     gemini_issues: List[str] = []

#     merged = dict(fields)

#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             merged = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_issues = [f"Gemini failed: {e}"]
#             merged = dict(fields)

#     merged["date_paie"] = merged.get("date_facture")

#     post_issues: List[str] = []
#     post_issues.extend(postprocess_fields_with_ocr(ocr, merged))
#     post_issues.extend(fix_tva_fields(merged))

#     op_type, op_conf = decide_operation_type_and_confidence(societe, merged, used_gemini)
#     merged["operation_type"] = op_type
#     merged["operation_confidence"] = op_conf

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
#             "societe_id": f.societe_id,
#             "operation_type": f.operation_type,
#             "operation_confidence": f.operation_confidence,
#             "fournisseur": f.fournisseur,
#             "date_facture": str(f.date_facture) if f.date_facture else None,
#             "numero_facture": f.numero_facture,
#             "montant_ht": f.montant_ht,
#             "montant_tva": f.montant_tva,
#             "montant_ttc": f.montant_ttc,
#             "statut": f.statut,
#             "ice_frs": f.ice_frs,
#             "if_frs": f.if_frs,
#             "taux_tva": f.taux_tva,
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
#         "societe_id": facture.societe_id,
#         "operation_type": facture.operation_type,
#         "operation_confidence": facture.operation_confidence,
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













import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Facture, Societe

from services import ocr_service
from services import extract_fields
from services.gemini_service import extract_invoice_fields_from_image_bytes
from services.pdf_utils import pdf_to_png_images_bytes
from services.validators import validate_or_fix, merge_fields

from utils.parsers import parse_date_fr, parse_amount

from schemas import FactureOut, FactureUpdate

router = APIRouter(prefix="/factures", tags=["factures"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]


# -------------------------
# Helpers
# -------------------------
def save_upload_file(upload: UploadFile) -> str:
    ext = Path(upload.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTS:
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


def to_float(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return parse_amount(v)


def normalize_ice(v: Optional[str]) -> Optional[str]:
    if not v:
        return None
    s = str(v)
    s = re.sub(r"[^0-9]", "", s)
    return s or None


# -------------------------
# TVA correction (FIX BUG)
# -------------------------
def fix_tva_fields(fields: Dict[str, Any]) -> List[str]:
    issues: List[str] = []

    ht = to_float(fields.get("montant_ht"))
    ttc = to_float(fields.get("montant_ttc"))
    mtva = to_float(fields.get("montant_tva"))
    taux = to_float(fields.get("taux_tva"))

    if ht is None or ttc is None:
        return issues

    computed = round(ttc - ht, 2)
    if computed < 0:
        return issues

    # si montant_tva absent -> fixer
    if mtva is None:
        fields["montant_tva"] = computed
        issues.append(f"montant_tva fixé via TTC-HT: {computed}")
        return issues

    # cas classique: montant_tva = taux (20)
    if taux is not None and abs(mtva - taux) < 1e-6:
        fields["montant_tva"] = computed
        issues.append(f"montant_tva corrigé (était taux {mtva}) -> {computed}")
        return issues

    return issues


# -------------------------
# Gemini
# -------------------------
def should_use_gemini(ocr: Any, fields: Dict[str, Any]) -> bool:
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
# Determine achat/vente via ICE
# -------------------------
def decide_operation_type(societe: Societe, fields: Dict[str, Any], used_gemini: bool) -> Tuple[str, float]:
    soc_ice = normalize_ice(societe.ice)
    inv_ice = normalize_ice(fields.get("ice_frs"))

    # règle métier: si ICE facture == ICE société => vente
    if soc_ice and inv_ice and soc_ice == inv_ice:
        return "vente", 1.0

    # sinon achat
    conf = 0.85 if used_gemini else 0.60
    return "achat", conf


# -------------------------
# Endpoints
# -------------------------
@router.post("/upload-facture/", response_model=dict)
def upload_facture(
    file: UploadFile = File(...),
    societe_id: int = Query(..., description="ID de la société (obligatoire)"),
    db: Session = Depends(get_db),
):
    societe = db.query(Societe).filter(Societe.id == societe_id).first()
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")

    file_path = save_upload_file(file)

    # OCR
    ocr = ocr_service.extract(file_path)

    # extraction classique
    extracted = extract_fields.extract_fields_from_ocr(ocr)
    fields = to_dict(extracted)

    used_gemini = False
    gemini_issues: List[str] = []
    post_issues: List[str] = []

    # Gemini fallback
    if should_use_gemini(ocr, fields):
        try:
            used_gemini = True
            gemini_fields = extract_with_gemini(file_path)
            gemini_issues = gemini_fields.pop("_gemini_issues", [])
            fields = merge_fields(fields, gemini_fields)
        except Exception as e:
            used_gemini = False
            gemini_issues = [f"Gemini failed: {e}"]

    # Règle métier: date_paie = date_facture
    fields["date_paie"] = fields.get("date_facture")

    # ✅ Fix TVA
    post_issues.extend(fix_tva_fields(fields))

    # ✅ achat/vente via ICE société vs ICE facture
    operation_type, operation_confidence = decide_operation_type(societe, fields, used_gemini)
    fields["operation_type"] = operation_type
    fields["operation_confidence"] = operation_confidence

    # Conversion
    date_facture_db = parse_date_fr(fields.get("date_facture"))
    date_paie_db = parse_date_fr(fields.get("date_paie"))

    facture = Facture(
        societe_id=societe.id,
        operation_type=operation_type,
        operation_confidence=operation_confidence,

        fournisseur=fields.get("fournisseur"),
        date_facture=date_facture_db,
        date_paie=date_paie_db,
        numero_facture=fields.get("numero_facture"),
        designation=fields.get("designation") or ("Achat fournisseur" if operation_type == "achat" else "Vente client"),

        montant_ht=to_float(fields.get("montant_ht")),
        montant_tva=to_float(fields.get("montant_tva")),
        montant_ttc=to_float(fields.get("montant_ttc")),

        statut="brouillon",

        if_frs=fields.get("if_frs") or fields.get("if_fiscal"),
        ice_frs=fields.get("ice_frs") or fields.get("ice"),

        taux_tva=to_float(fields.get("taux_tva")),
        id_paie=fields.get("id_paie"),

        ded_file_path=file_path,
        ded_pdf_path=fields.get("ded_pdf_path"),
        ded_xlsx_path=fields.get("ded_xlsx_path"),
    )

    try:
        db.add(facture)
        db.commit()
        db.refresh(facture)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

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


@router.get("/", response_model=list[FactureOut])
def list_factures(db: Session = Depends(get_db)):
    return db.query(Facture).order_by(Facture.id.desc()).all()


@router.get("/{facture_id}", response_model=FactureOut)
def get_facture(facture_id: int, db: Session = Depends(get_db)):
    f = db.query(Facture).filter(Facture.id == facture_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture introuvable")
    return f


@router.put("/{facture_id}", response_model=FactureOut)
def update_facture(facture_id: int, payload: FactureUpdate, db: Session = Depends(get_db)):
    f = db.query(Facture).filter(Facture.id == facture_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture introuvable")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(f, k, v)

    try:
        db.commit()
        db.refresh(f)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

    return f


@router.delete("/{facture_id}")
def delete_facture(facture_id: int, db: Session = Depends(get_db)):
    f = db.query(Facture).filter(Facture.id == facture_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture introuvable")

    db.delete(f)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

    return {"message": "Facture supprimée"}
