








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
# # OCR post-processing helpers (NUM FACTURE / TVA)
# # -------------------------

# def _get_ocr_text(ocr: Any) -> str:
#     # ton ocr_service met généralement "preview" ; sinon adapte ici
#     txt = getattr(ocr, "preview", None)
#     if isinstance(txt, str) and txt.strip():
#         return txt
#     # fallback (si jamais tu as un champ "text")
#     txt = getattr(ocr, "text", None)
#     return txt if isinstance(txt, str) else ""


# def _looks_like_invoice_number(v: str) -> bool:
#     if not v:
#         return False
#     v = v.strip()
#     # trop court / trop long
#     if len(v) < 4 or len(v) > 30:
#         return False
#     # évite ICE/IF (souvent très longs numériques)
#     if re.fullmatch(r"\d{14,20}", v):
#         return False
#     return True


# def _looks_like_patente_context(text: str, value: str) -> bool:
#     if not text or not value:
#         return False
#     val = re.escape(value.strip())
#     # regarde la "zone" autour du numéro
#     m = re.search(rf"(.{{0,80}}{val}.{{0,80}})", text, flags=re.IGNORECASE | re.DOTALL)
#     if not m:
#         return False
#     ctx = m.group(1).lower()
#     return any(k in ctx for k in ["patente", "patente.", "patente n", "patente n°", "patente.no", "patente.n"])


# def _extract_invoice_number_from_text(text: str, date_facture: Optional[str] = None) -> Optional[str]:
#     """
#     Priorité:
#       1) "FACTURE N° xxx"
#       2) fallback robuste: motif "00005252/25" (numéro avec /), idéalement sur la ligne qui contient la date_facture
#       3) sinon: meilleur candidat global (en évitant RC/CNSS/IF/ICE/PATENTE)
#     """
#     if not text:
#         return None

#     lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
#     joined = "\n".join(lines)

#     # 1) près du mot FACTURE
#     patterns = [
#         r"FACTURE\s*(?:N|N°|NO|NUM|NUMERO)?\s*[:#\-]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"FACTURE\s*(?:N|N°|NO)\s*\|?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#         r"N°\s*FACTURE\s*[:#\-]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
#     ]

#     candidates: List[str] = []
#     for pat in patterns:
#         for m in re.finditer(pat, joined, flags=re.IGNORECASE):
#             cand = (m.group(1) or "").strip()
#             start = max(0, m.start() - 80)
#             end = min(len(joined), m.end() + 80)
#             ctx = joined[start:end].lower()
#             if any(k in ctx for k in ["patente", "r.c", "rc ", "cnss", "l.f", "lf ", "ice", "if "]):
#                 continue
#             if _looks_like_invoice_number(cand):
#                 candidates.append(cand)

#     if candidates:
#         def score(v: str):
#             s = 0
#             if "/" in v: s += 12
#             if re.search(r"[A-Z]", v, flags=re.IGNORECASE): s += 5
#             if re.fullmatch(r"\d+", v): s -= 2
#             return (s, len(v))
#         candidates.sort(key=score, reverse=True)
#         return candidates[0]

#     # 2) fallback "nombre/nombre" (ex: 00005252/25)
#     slash_re = re.compile(r"\b(\d{4,}\/\d{2,4})\b")
#     slash_candidates: List[str] = []

#     if date_facture:
#         for ln in lines:
#             if date_facture in ln:
#                 for m in slash_re.finditer(ln):
#                     cand = m.group(1).strip()
#                     ctx = ln.lower()
#                     if "patente" in ctx:
#                         continue
#                     slash_candidates.append(cand)

#     if not slash_candidates:
#         for ln in lines:
#             for m in slash_re.finditer(ln):
#                 cand = m.group(1).strip()
#                 ctx = ln.lower()
#                 if any(k in ctx for k in ["patente", "r.c", "rc ", "cnss", "l.f", "lf ", "ice", "if "]):
#                     continue
#                 slash_candidates.append(cand)

#     if slash_candidates:
#         slash_candidates.sort(key=lambda x: ("/" in x, len(x)), reverse=True)
#         return slash_candidates[0]

#     # 3) dernier recours: un token "style facture" pas trop long, éviter les labels fiscaux
#     token_re = re.compile(r"\b([A-Z]{1,4}\d{3,}|\d{4,}[A-Z]{1,4}|\d{6,})\b")
#     pool: List[Tuple[str, str]] = []
#     for ln in lines:
#         lnl = ln.lower()
#         if any(k in lnl for k in ["patente", "r.c", "rc ", "cnss", "ice", "if ", "l.f", "lf "]):
#             continue
#         for m in token_re.finditer(ln):
#             cand = m.group(1).strip()
#             if _looks_like_invoice_number(cand):
#                 pool.append((cand, ln))

#     if pool:
#         # préfère ceux proches de la date si possible
#         if date_facture:
#             near = [c for c, ln in pool if date_facture in ln]
#             if near:
#                 near.sort(key=len, reverse=True)
#                 return near[0]
#         pool.sort(key=lambda t: len(t[0]), reverse=True)
#         return pool[0][0]

#     return None


# def _fix_montant_tva(fields: Dict[str, Any]) -> Optional[str]:
#     """
#     Corrige le cas classique:
#       montant_tva = 20 (taux) au lieu d'un montant.
#     Stratégie:
#       - si montant_tva == taux_tva et (ht & ttc) => montant_tva = ttc - ht
#       - sinon si ht & taux => montant_tva = ht * taux/100
#       - sinon si ttc & taux => ht = ttc/(1+taux/100) (pas demandé mais utile), montant_tva = ttc-ht
#     """
#     ht = parse_amount(fields.get("montant_ht"))
#     ttc = parse_amount(fields.get("montant_ttc"))
#     mtva = parse_amount(fields.get("montant_tva"))
#     taux = parse_amount(fields.get("taux_tva"))

#     if mtva is None or taux is None:
#         return None

#     # si mtva ressemble à un taux (ex: 20) et HT/TTC existent
#     if ht is not None and ttc is not None:
#         # si mtva == taux (ou très proche) => c'est un taux, pas un montant
#         if abs(mtva - taux) < 0.0001 and taux in [7, 10, 14, 20]:
#             fixed = round(ttc - ht, 2)
#             if fixed >= 0:
#                 fields["montant_tva"] = fixed
#                 return f"montant_tva corrigé (taux détecté): {mtva} -> {fixed}"

#         # si mtva est null/0 alors calcule
#         if mtva in [0, None]:
#             fixed = round(ttc - ht, 2)
#             if fixed >= 0:
#                 fields["montant_tva"] = fixed
#                 return f"montant_tva calculé: {fixed}"

#     if ht is not None and taux is not None and taux > 0 and taux <= 30:
#         # cas mtva == taux (taux mal mis)
#         if abs(mtva - taux) < 0.0001 and taux in [7, 10, 14, 20]:
#             fixed = round(ht * (taux / 100.0), 2)
#             fields["montant_tva"] = fixed
#             return f"montant_tva corrigé (taux détecté): {mtva} -> {fixed}"

#     if ttc is not None and taux is not None and taux > 0 and taux <= 30 and ht is None:
#         ht_calc = round(ttc / (1.0 + (taux / 100.0)), 2)
#         fields["montant_ht"] = ht_calc
#         fields["montant_tva"] = round(ttc - ht_calc, 2)
#         return f"montant_ht+montant_tva déduits depuis TTC+taux: ht={fields['montant_ht']} tva={fields['montant_tva']}"

#     return None


# def postprocess_fields_with_ocr(ocr: Any, fields: Dict[str, Any]) -> List[str]:
#     issues: List[str] = []
#     text = _get_ocr_text(ocr)

#     date_facture = (fields.get("date_facture") or "").strip() or None
#     current = (fields.get("numero_facture") or "").strip()

#     # 1) si numero_facture vide => on tente extraire
#     if not current:
#         extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
#         if extracted:
#             fields["numero_facture"] = extracted
#             issues.append(f"numero_facture récupéré depuis OCR: {extracted}")

#     # 2) si numero_facture existe mais semble être une Patente => remplacer
#     else:
#         if _looks_like_patente_context(text, current):
#             extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
#             if extracted and extracted != current:
#                 fields["numero_facture"] = extracted
#                 issues.append(f"numero_facture '{current}' (Patente) remplacé par '{extracted}'")

#         # 3) si seulement chiffres, et on trouve un candidat avec "/" => on préfère celui avec "/"
#         elif re.fullmatch(r"\d{5,12}", current):
#             extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
#             if extracted and "/" in extracted and extracted != current:
#                 fields["numero_facture"] = extracted
#                 issues.append(f"numero_facture '{current}' ambigu remplacé par '{extracted}'")

#     # TVA confusion fix
#     msg = _fix_montant_tva(fields)
#     if msg:
#         issues.append(msg)

#     return issues


# # -------------------------
# # Gemini helpers
# # -------------------------

# def should_use_gemini(ocr: Any, fields: Dict[str, Any]) -> bool:
#     # IMPORTANT: ne pas forcer Gemini si le DNS est cassé; mais ici on décide seulement.
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

#     # 3) Fallback Gemini (mais NE PAS planter si DNS / clé / quota)
#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             fields = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             # IMPORTANT: on ne casse pas l'API, on continue en OCR
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
# def debug_extract(
#     file: UploadFile = File(...),
# ):
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
ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]


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


# -------------------------
# OCR post-processing helpers (NUM FACTURE / TVA)
# -------------------------
def _get_ocr_text(ocr: Any) -> str:
    txt = getattr(ocr, "preview", None)
    if isinstance(txt, str) and txt.strip():
        return txt
    txt = getattr(ocr, "text", None)
    return txt if isinstance(txt, str) else ""


def _looks_like_invoice_number(v: str) -> bool:
    if not v:
        return False
    v = v.strip()
    if len(v) < 4 or len(v) > 30:
        return False
    # évite ICE (souvent 15 chiffres), etc.
    if re.fullmatch(r"\d{14,20}", v):
        return False
    return True


def _extract_invoice_number_from_text(text: str, date_facture: Optional[str] = None) -> Optional[str]:
    """
    Objectif: éviter RC/IF/ICE/CNSS/PATENTE et récupérer le N° facture.
    Priorité:
      1) "FACTURE N° xxx" (ou "Facture | 2025-416")
      2) motif "00005252/25" (numéro avec /), surtout sur la ligne qui contient la date
      3) meilleur candidat global (en évitant mots fiscaux)
    """
    if not text:
        return None

    # normalise un peu
    t = text.replace("\r", "\n")
    lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
    joined = "\n".join(lines)

    # Mots à éviter autour d'un candidat
    bad_ctx = ["patente", "r.c", "rc", "cnss", "l.f", "lf", "ice", "if", "tp"]

    # 1) Patterns "FACTURE ..."
    patterns = [
        r"\bFACTURE\b\s*(?:N|N°|NO|NUM|NUMERO)?\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
        r"\bFACTURE\b\s*\|\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
        r"\bN°\s*FACTURE\b\s*[:#\-\|]?\s*([A-Z0-9][A-Z0-9\/\-\._]{2,})",
    ]

    candidates: List[str] = []
    for pat in patterns:
        for m in re.finditer(pat, joined, flags=re.IGNORECASE):
            cand = (m.group(1) or "").strip()

            # contexte autour
            start = max(0, m.start() - 90)
            end = min(len(joined), m.end() + 90)
            ctx = joined[start:end].lower()

            if any(k in ctx for k in bad_ctx):
                continue
            if _looks_like_invoice_number(cand):
                candidates.append(cand)

    if candidates:
        def score(v: str):
            s = 0
            if "/" in v: s += 20
            if "-" in v: s += 10
            if re.search(r"[A-Z]", v, flags=re.IGNORECASE): s += 6
            if re.fullmatch(r"\d+", v): s -= 2
            return (s, len(v))

        candidates.sort(key=score, reverse=True)
        return candidates[0]

    # 2) Motif slash style 00005252/25
    slash_re = re.compile(r"\b(\d{4,}\/\d{2,4})\b")
    slash_candidates: List[str] = []

    if date_facture:
        for ln in lines:
            if date_facture in ln:
                lnl = ln.lower()
                if any(k in lnl for k in bad_ctx):
                    continue
                for m in slash_re.finditer(ln):
                    slash_candidates.append(m.group(1).strip())

    if not slash_candidates:
        for ln in lines:
            lnl = ln.lower()
            if any(k in lnl for k in bad_ctx):
                continue
            for m in slash_re.finditer(ln):
                slash_candidates.append(m.group(1).strip())

    if slash_candidates:
        slash_candidates.sort(key=len, reverse=True)
        return slash_candidates[0]

    # 3) fallback token
    token_re = re.compile(r"\b([A-Z]{1,4}\d{3,}|\d{4,}[A-Z]{1,4}|\d{6,}|\d{4}\-\d{1,6})\b")
    pool: List[Tuple[str, str]] = []

    for ln in lines:
        lnl = ln.lower()
        if any(k in lnl for k in bad_ctx):
            continue
        for m in token_re.finditer(ln):
            cand = m.group(1).strip()
            if _looks_like_invoice_number(cand):
                pool.append((cand, ln))

    if pool:
        if date_facture:
            near = [c for c, ln in pool if date_facture in ln]
            if near:
                near.sort(key=len, reverse=True)
                return near[0]
        pool.sort(key=lambda t: len(t[0]), reverse=True)
        return pool[0][0]

    return None


def _fix_tva_from_ocr_text(fields: Dict[str, Any], text: str) -> Optional[str]:
    """
    Fix OCR: "TVA 200% 828.00" => taux=20, montant=828
    + confusions: montant_tva = 20 (taux) au lieu de 828.00
    """
    if not text:
        return None

    t = text.replace("\r", "\n")
    lines = [ln.strip() for ln in t.split("\n") if ln.strip()]

    # 1) Cherche une ligne TVA et tente extraire (taux + montant)
    for ln in lines:
        if "TVA" not in ln.upper():
            continue

        # extrait un % s'il existe
        m_pct = re.search(r"(\d{1,4}(?:[.,]\d{1,2})?)\s*%", ln)
        taux = None
        if m_pct:
            raw = m_pct.group(1).replace(",", ".")
            try:
                taux = float(raw)
                # fix 200 -> 20, 2000 -> 20 ...
                while taux > 100:
                    taux /= 10.0
                if taux < 0 or taux > 100:
                    taux = None
                else:
                    taux = round(taux, 2)
            except Exception:
                taux = None

        # extrait un montant (dernier nombre "xx.xx")
        nums = re.findall(r"(\d{1,3}(?:[ .,\u00A0]\d{3})*(?:[.,]\d{2})|\d+(?:[.,]\d{2}))", ln)
        mtva = parse_amount(nums[-1]) if nums else None

        # si on a trouvé quelque chose de plausible, on met à jour
        changed = False
        if taux is not None:
            fields["taux_tva"] = taux
            changed = True
        if mtva is not None and mtva > 0:
            fields["montant_tva"] = mtva
            changed = True

        if changed:
            return f"TVA corrigée depuis OCR line: {ln}"

    # 2) Sinon, corrige la confusion classique montant_tva=taux
    ht = parse_amount(fields.get("montant_ht"))
    ttc = parse_amount(fields.get("montant_ttc"))
    mtva = parse_amount(fields.get("montant_tva"))
    taux = parse_amount(fields.get("taux_tva"))

    if mtva is None or taux is None:
        return None

    # si mtva ressemble à un taux (20) et HT/TTC existent => mtva = ttc - ht
    if ht is not None and ttc is not None:
        if abs(mtva - taux) < 0.0001 and taux <= 30:
            fixed = round(ttc - ht, 2)
            if fixed >= 0:
                fields["montant_tva"] = fixed
                return f"montant_tva corrigé (taux détecté): {mtva} -> {fixed}"

    # si HT et taux => mtva = ht*taux/100
    if ht is not None and taux is not None and 0 < taux <= 30:
        if abs(mtva - taux) < 0.0001:
            fixed = round(ht * (taux / 100.0), 2)
            fields["montant_tva"] = fixed
            return f"montant_tva recalculé via HT*taux: {mtva} -> {fixed}"

    return None


def postprocess_fields_with_ocr(ocr: Any, fields: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    text = _get_ocr_text(ocr)
    date_facture = (fields.get("date_facture") or "").strip() or None

    current = (fields.get("numero_facture") or "").strip()

    # 1) si numero_facture vide => extraire depuis OCR
    if not current:
        extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
        if extracted:
            fields["numero_facture"] = extracted
            issues.append(f"numero_facture récupéré depuis OCR: {extracted}")

    # 2) si numero_facture est numérique pur, et on voit "Patente" dans le doc + on trouve un meilleur candidat => remplacer
    else:
        if re.fullmatch(r"\d{4,12}", current) and ("patente" in (text or "").lower()):
            extracted = _extract_invoice_number_from_text(text, date_facture=date_facture)
            if extracted and extracted != current:
                fields["numero_facture"] = extracted
                issues.append(f"numero_facture '{current}' remplacé par '{extracted}' (évite Patente/RC/ICE/IF)")

    # 3) TVA fix
    msg = _fix_tva_from_ocr_text(fields, text)
    if msg:
        issues.append(msg)

    return issues


# -------------------------
# Gemini helpers
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

    # 3) Fallback Gemini (NE PAS planter si DNS / clé / quota)
    if should_use_gemini(ocr, fields):
        try:
            used_gemini = True
            gemini_fields = extract_with_gemini(file_path)
            gemini_issues = gemini_fields.pop("_gemini_issues", [])
            fields = merge_fields(fields, gemini_fields)
        except Exception as e:
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
def debug_extract(file: UploadFile = File(...)):
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
