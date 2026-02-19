






# import os
# import re
# import uuid
# from pathlib import Path
# from typing import Any, Dict, Optional, List, Tuple

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Facture, Societe, EcritureComptable

# from services import ocr_service
# from services import extract_fields
# from services.gemini_service import extract_invoice_fields_from_image_bytes
# from services.pdf_utils import pdf_to_png_images_bytes
# from services.validators import validate_or_fix, merge_fields

# from services.accounting_rules import PieceComptable, generate_lines_pcm, get_journal_code

# from utils.parsers import parse_date_fr, parse_amount
# from schemas import FactureOut, FactureUpdate

# router = APIRouter(prefix="/factures", tags=["factures"])

# UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
# UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]
# ALLOWED_STATUTS = {"brouillon", "validee"}


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


# def to_float(v):
#     if v is None:
#         return None
#     if isinstance(v, (int, float)):
#         return float(v)
#     return parse_amount(v)


# def normalize_ice(v: Optional[str]) -> Optional[str]:
#     if not v:
#         return None
#     s = str(v)
#     s = re.sub(r"[^0-9]", "", s)
#     return s or None


# # -------------------------
# # TVA correction
# # -------------------------
# def fix_tva_fields(fields: Dict[str, Any]) -> List[str]:
#     issues: List[str] = []

#     ht = to_float(fields.get("montant_ht"))
#     ttc = to_float(fields.get("montant_ttc"))
#     mtva = to_float(fields.get("montant_tva"))
#     taux = to_float(fields.get("taux_tva"))

#     if ht is None or ttc is None:
#         return issues

#     computed = round(ttc - ht, 2)
#     if computed < 0:
#         return issues

#     if mtva is None:
#         fields["montant_tva"] = computed
#         issues.append(f"montant_tva fixé via TTC-HT: {computed}")
#         return issues

#     if taux is not None and abs(mtva - taux) < 1e-6:
#         fields["montant_tva"] = computed
#         issues.append(f"montant_tva corrigé (était taux {mtva}) -> {computed}")
#         return issues

#     return issues


# # -------------------------
# # Gemini
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
# # Determine achat/vente via ICE
# # -------------------------
# def decide_operation_type(societe: Societe, fields: Dict[str, Any], used_gemini: bool) -> Tuple[str, float]:
#     soc_ice = normalize_ice(societe.ice)
#     inv_ice = normalize_ice(fields.get("ice_frs"))

#     if soc_ice and inv_ice and soc_ice == inv_ice:
#         return "vente", 1.0

#     conf = 0.85 if used_gemini else 0.60
#     return "achat", conf


# # -------------------------
# # Validation rules
# # -------------------------
# def validate_facture_business_rules(f: Facture) -> List[str]:
#     errors: List[str] = []

#     if not f.societe_id:
#         errors.append("societe_id manquant")

#     if not f.operation_type or f.operation_type not in {"achat", "vente"}:
#         errors.append("operation_type invalide (doit être 'achat' ou 'vente')")

#     if f.date_facture is None:
#         errors.append("date_facture manquante (date d'opération)")

#     if f.numero_facture in [None, ""]:
#         errors.append("numero_facture manquant")

#     if f.montant_ht is None:
#         errors.append("montant_ht manquant")
#     if f.montant_ttc is None:
#         errors.append("montant_ttc manquant")

#     if f.montant_ht is not None and f.montant_ttc is not None:
#         computed_tva = round(float(f.montant_ttc) - float(f.montant_ht), 2)
#         if computed_tva < 0:
#             errors.append("montants incohérents: TTC < HT")
#         else:
#             if f.montant_tva is None:
#                 f.montant_tva = computed_tva
#             else:
#                 if abs(float(f.montant_tva) - computed_tva) > 0.02:
#                     errors.append(f"montant_tva incohérent: attendu {computed_tva}, reçu {f.montant_tva}")

#     return errors


# # -------------------------
# # Endpoints
# # -------------------------
# @router.post("/upload-facture/", response_model=dict)
# def upload_facture(
#     file: UploadFile = File(...),
#     societe_id: int = Query(..., description="ID de la société (obligatoire)"),
#     db: Session = Depends(get_db),
# ):
#     societe = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not societe:
#         raise HTTPException(status_code=404, detail="Société introuvable")

#     file_path = save_upload_file(file)

#     ocr = ocr_service.extract(file_path)

#     extracted = extract_fields.extract_fields_from_ocr(ocr)
#     fields = to_dict(extracted)

#     used_gemini = False
#     gemini_issues: List[str] = []
#     post_issues: List[str] = []

#     if should_use_gemini(ocr, fields):
#         try:
#             used_gemini = True
#             gemini_fields = extract_with_gemini(file_path)
#             gemini_issues = gemini_fields.pop("_gemini_issues", [])
#             fields = merge_fields(fields, gemini_fields)
#         except Exception as e:
#             used_gemini = False
#             gemini_issues = [f"Gemini failed: {e}"]

#     fields["date_paie"] = fields.get("date_facture")
#     post_issues.extend(fix_tva_fields(fields))

#     operation_type, operation_confidence = decide_operation_type(societe, fields, used_gemini)
#     fields["operation_type"] = operation_type
#     fields["operation_confidence"] = operation_confidence

#     date_facture_db = parse_date_fr(fields.get("date_facture"))
#     date_paie_db = parse_date_fr(fields.get("date_paie"))

#     facture = Facture(
#         societe_id=societe.id,
#         operation_type=operation_type,
#         operation_confidence=operation_confidence,

#         fournisseur=fields.get("fournisseur"),
#         date_facture=date_facture_db,
#         date_paie=date_paie_db,
#         numero_facture=fields.get("numero_facture"),
#         designation=fields.get("designation") or ("Achat fournisseur" if operation_type == "achat" else "Vente client"),

#         montant_ht=to_float(fields.get("montant_ht")),
#         montant_tva=to_float(fields.get("montant_tva")),
#         montant_ttc=to_float(fields.get("montant_ttc")),

#         statut="brouillon",

#         if_frs=fields.get("if_frs") or fields.get("if_fiscal"),
#         ice_frs=fields.get("ice_frs") or fields.get("ice"),

#         taux_tva=to_float(fields.get("taux_tva")),
#         id_paie=fields.get("id_paie"),

#         devise=fields.get("devise"),

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


# @router.get("/", response_model=list[FactureOut])
# def list_factures(db: Session = Depends(get_db)):
#     return db.query(Facture).order_by(Facture.id.desc()).all()


# @router.get("/{facture_id}", response_model=FactureOut)
# def get_facture(facture_id: int, db: Session = Depends(get_db)):
#     f = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not f:
#         raise HTTPException(status_code=404, detail="Facture introuvable")
#     return f


# @router.put("/{facture_id}", response_model=FactureOut)
# def update_facture(facture_id: int, payload: FactureUpdate, db: Session = Depends(get_db)):
#     f = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not f:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     data = payload.model_dump(exclude_unset=True)
#     for k, v in data.items():
#         setattr(f, k, v)

#     try:
#         db.commit()
#         db.refresh(f)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

#     return f


# @router.delete("/{facture_id}")
# def delete_facture(facture_id: int, db: Session = Depends(get_db)):
#     f = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not f:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     db.delete(f)
#     try:
#         db.commit()
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

#     return {"message": "Facture supprimée"}


# # ✅ afficher les écritures d'une facture
# @router.get("/{facture_id}/ecritures", response_model=list[dict])
# def list_ecritures_facture(facture_id: int, db: Session = Depends(get_db)):
#     f = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not f:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     return [
#         {
#             "compte": e.compte,
#             "libelle": e.libelle,
#             "debit": e.debit,
#             "credit": e.credit,
#             "journal": getattr(e, "journal", None),
#             "date_operation": str(getattr(e, "date_operation", None)) if getattr(e, "date_operation", None) else None,
#             "numero_piece": getattr(e, "numero_piece", None),
#         }
#         for e in f.ecritures
#     ]


# @router.post("/{facture_id}/valider", response_model=FactureOut)
# def valider_facture(facture_id: int, db: Session = Depends(get_db)):
#     f = db.query(Facture).filter(Facture.id == facture_id).first()
#     if not f:
#         raise HTTPException(status_code=404, detail="Facture introuvable")

#     if f.statut == "validee":
#         return f

#     if f.statut not in ALLOWED_STATUTS:
#         raise HTTPException(status_code=400, detail=f"Statut actuel invalide: {f.statut}")

#     # contrôle de pièce obligatoire (cahier des charges)
#     if not f.numero_facture:
#         raise HTTPException(status_code=422, detail="Numéro de facture obligatoire")
#     if not f.date_facture:
#         raise HTTPException(status_code=422, detail="Date d'opération obligatoire (date_facture)")

#     errors = validate_facture_business_rules(f)
#     if errors:
#         raise HTTPException(status_code=422, detail={"message": "Validation refusée", "errors": errors})

#     f.statut = "validee"

#     # ✅ Génération PCM selon operation_type
#     piece = PieceComptable(
#         operation=f.operation_type,
#         numero_piece=f.numero_facture,
#         date_operation=f.date_facture,
#         designation=f.designation or "",
#         tiers_nom=f.fournisseur,
#         montant_ht=float(f.montant_ht or 0),
#         taux_tva=float(f.taux_tva or 20),
#         montant_ttc=float(f.montant_ttc or 0),
#     )

#     journal_code = get_journal_code(piece.operation)
#     lines = generate_lines_pcm(piece)

#     # sécurité partie double
#     total_debit = round(sum(float(l.get("debit", 0) or 0) for l in lines), 2)
#     total_credit = round(sum(float(l.get("credit", 0) or 0) for l in lines), 2)
#     if abs(total_debit - total_credit) > 0.01:
#         raise HTTPException(
#             status_code=422,
#             detail={
#                 "message": "Écriture non équilibrée",
#                 "total_debit": total_debit,
#                 "total_credit": total_credit,
#                 "lines": lines,
#             },
#         )

#     # idempotence: supprimer anciennes écritures
#     f.ecritures.clear()

#     for l in lines:
#         db.add(EcritureComptable(
#             facture_id=f.id,
#             journal=journal_code,
#             date_operation=piece.date_operation,
#             numero_piece=piece.numero_piece,
#             compte=l["compte"],
#             libelle=l.get("libelle"),
#             debit=float(l.get("debit", 0) or 0),
#             credit=float(l.get("credit", 0) or 0),
#         ))

#     try:
#         db.commit()
#         db.refresh(f)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

#     return f























# routes/factures.py
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Facture, Societe, EcritureComptable, EcritureLigne
from routes.deps import get_current_session

from services import ocr_service
from services import extract_fields
from services.gemini_service import extract_invoice_fields_from_image_bytes
from services.pdf_utils import pdf_to_png_images_bytes
from services.validators import validate_or_fix, merge_fields

from utils.parsers import parse_date_fr, parse_amount

from schemas import FactureOut, FactureUpdate, EcritureLigneOut

router = APIRouter(prefix="/factures", tags=["factures"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]
ALLOWED_STATUTS = {"brouillon", "validee"}


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
# TVA correction
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

    conf = 0.85 if used_gemini else 0.60
    return "achat", conf


# -------------------------
# Validation rules
# -------------------------
def validate_facture_business_rules(f: Facture) -> List[str]:
    errors: List[str] = []

    if not f.societe_id:
        errors.append("societe_id manquant")

    if not f.operation_type or f.operation_type not in {"achat", "vente"}:
        errors.append("operation_type invalide (doit être 'achat' ou 'vente')")

    if f.date_facture is None:
        errors.append("date_facture manquante")

    if f.numero_facture in [None, ""]:
        errors.append("numero_facture manquant")

    if f.montant_ht is None:
        errors.append("montant_ht manquant")
    if f.montant_ttc is None:
        errors.append("montant_ttc manquant")

    # cohérence TVA
    if f.montant_ht is not None and f.montant_ttc is not None:
        computed_tva = round(float(f.montant_ttc) - float(f.montant_ht), 2)
        if computed_tva < 0:
            errors.append("montants incohérents: TTC < HT")
        else:
            if f.montant_tva is None:
                f.montant_tva = computed_tva
            else:
                if abs(float(f.montant_tva) - computed_tva) > 0.02:
                    errors.append(f"montant_tva incohérent: attendu {computed_tva}, reçu {f.montant_tva}")

    return errors


# -------------------------
# Endpoints Factures
# -------------------------
@router.post("/upload-facture/", response_model=dict)
def upload_facture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Upload a new facture. Requires valid session_token in Authorization header."""
    societe_id = session.get("societe_id")
    if not societe_id:
        raise HTTPException(status_code=400, detail="societe_id manquant dans le contexte de session")
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

    # règle métier: date_paie = date_facture
    fields["date_paie"] = fields.get("date_facture")

    # fix TVA
    post_issues.extend(fix_tva_fields(fields))

    # achat/vente via ICE société vs ICE facture
    operation_type, operation_confidence = decide_operation_type(societe, fields, used_gemini)
    fields["operation_type"] = operation_type
    fields["operation_confidence"] = operation_confidence

    # conversion types
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

        status="IMPORTED",  # Changed from statut="brouillon"

        if_frs=fields.get("if_frs") or fields.get("if_fiscal"),
        ice_frs=fields.get("ice_frs") or fields.get("ice"),

        taux_tva=to_float(fields.get("taux_tva")),
        id_paie=fields.get("id_paie"),

        devise=fields.get("devise"),

        file_path=file_path,
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
def list_factures(db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """List factures for the current société (from session_token)."""
    societe_id = session.get("societe_id")
    return db.query(Facture).filter(Facture.societe_id == societe_id).order_by(Facture.id.desc()).all()


@router.get("/{facture_id}", response_model=FactureOut)
def get_facture(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Get facture details. Must belong to current société."""
    societe_id = session.get("societe_id")
    f = db.query(Facture).filter(Facture.id == facture_id, Facture.societe_id == societe_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture introuvable ou accès refusé")
    return f


@router.put("/{facture_id}", response_model=FactureOut)
def update_facture(facture_id: int, payload: FactureUpdate, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Update facture. Must belong to current société."""
    societe_id = session.get("societe_id")
    f = db.query(Facture).filter(Facture.id == facture_id, Facture.societe_id == societe_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture introuvable ou accès refusé")

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
def delete_facture(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Delete facture. Must belong to current société."""
    societe_id = session.get("societe_id")
    f = db.query(Facture).filter(Facture.id == facture_id, Facture.societe_id == societe_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture introuvable ou accès refusé")

    db.delete(f)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

    return {"message": "Facture supprimée"}




# -------------------------
# ✅ NEW: ecritures d'une facture (lignes PCM)
# -------------------------
@router.get("/{facture_id}/ecritures", response_model=list[EcritureLigneOut])
def list_ecritures_for_facture(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """List ecritures (lines) for a facture. Must belong to current société."""
    societe_id = session.get("societe_id")
    
    # vérifier facture
    f = db.query(Facture).filter(Facture.id == facture_id, Facture.societe_id == societe_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture introuvable ou accès refusé")

    # récupérer les headers liés à la facture
    headers = (
        db.query(EcritureComptable)
        .filter(EcritureComptable.facture_id == facture_id)
        .order_by(EcritureComptable.id.desc())
        .all()
    )
    if not headers:
        return []

    header_ids = [h.id for h in headers]

    # récupérer les lignes liées à ces headers
    lignes = (
        db.query(EcritureLigne)
        .filter(EcritureLigne.ecriture_id.in_(header_ids))
        .order_by(EcritureLigne.id.asc())
        .all()
    )

    return lignes
