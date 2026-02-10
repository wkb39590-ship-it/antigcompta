


# import os
# import shutil
# from datetime import datetime
# from typing import Generator, Optional, Any, Dict

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
# from sqlalchemy.orm import Session

# from database import SessionLocal
# from schemas import FactureCreate, FactureOut
# import crud

# from services.ocr_service import OCRService
# from services.extract_fields import parse_facture_text

# router = APIRouter(prefix="/factures", tags=["Factures"])

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# ocr = OCRService()


# # -------------------------
# # DB Dependency
# # -------------------------
# def get_db() -> Generator[Session, None, None]:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # -------------------------
# # Helpers
# # -------------------------
# def parse_date_fr(date_str: Optional[str]):
#     """Convertit 'dd/mm/yyyy' -> date. Retourne None si invalide."""
#     if not date_str:
#         return None
#     try:
#         return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
#     except ValueError:
#         return None


# def allowed_file(filename: str) -> bool:
#     ext = os.path.splitext(filename)[1].lower()
#     return ext in [".pdf", ".png", ".jpg", ".jpeg"]


# # -------------------------
# # Routes CRUD
# # -------------------------
# @router.get("/", response_model=list[FactureOut])
# def list_factures(db: Session = Depends(get_db)):
#     return crud.get_factures(db)


# @router.post("/", response_model=FactureOut)
# def add_facture(facture: FactureCreate, db: Session = Depends(get_db)):
#     return crud.create_facture(db, facture)


# @router.get("/{facture_id}", response_model=FactureOut)
# def get_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = crud.get_facture(db, facture_id)
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")
#     return facture


# @router.put("/{facture_id}", response_model=FactureOut)
# def update_facture(
#     facture_id: int,
#     facture_data: Dict[str, Any],
#     db: Session = Depends(get_db),
# ):
#     facture = crud.update_facture(db, facture_id, facture_data)
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")
#     return facture


# @router.delete("/{facture_id}")
# def delete_facture(facture_id: int, db: Session = Depends(get_db)):
#     ok = crud.delete_facture(db, facture_id)
#     if not ok:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")
#     return {"message": "Facture supprimée", "facture_id": facture_id}


# # ✅ Route : récupérer les écritures d'une facture
# @router.get("/{facture_id}/ecritures")
# def get_ecritures(facture_id: int, db: Session = Depends(get_db)):
#     facture = crud.get_facture(db, facture_id)
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")

#     # facture.ecritures doit exister via relationship dans models.py
#     return facture.ecritures


# # -------------------------
# # Route Upload + OCR + DB
# # -------------------------
# @router.post("/upload-facture/")
# async def upload_facture(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     if not file.filename:
#         raise HTTPException(status_code=400, detail="Nom de fichier invalide")

#     if not allowed_file(file.filename):
#         raise HTTPException(
#             status_code=400,
#             detail="Format non supporté. Utilise: PDF, PNG, JPG, JPEG",
#         )

#     # 1) Sauvegarde du fichier dans uploads/
#     filename = file.filename
#     save_path = os.path.join(UPLOAD_DIR, filename)

#     try:
#         with open(save_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur sauvegarde fichier: {e}")

#     # 2) OCR (PDF ou image)
#     try:
#         text = ocr.extract_text(save_path)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur OCR: {e}")

#     # 3) Extraction des champs (regex)
#     data = parse_facture_text(text)

#     # 4) Préparer objet FactureCreate
#     facture_in = FactureCreate(
#         fournisseur=data.get("fournisseur"),
#         date_facture=parse_date_fr(data.get("date_facture")),
#         montant_ht=data.get("montant_ht"),
#         montant_tva=data.get("montant_tva"),
#         montant_ttc=data.get("montant_ttc"),
#     )

#     # 5) Sauvegarder en DB
#     try:
#         facture_db = crud.create_facture(db, facture_in)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur insertion DB: {e}")

#     # 6) Retour
#     return {
#         "message": "Facture uploadée + OCR effectué + enregistrée en DB",
#         "file_saved_as": save_path,
#         "facture": {
#             "id": facture_db.id,
#             "fournisseur": facture_db.fournisseur,
#             "date_facture": str(facture_db.date_facture) if facture_db.date_facture else None,
#             "montant_ht": facture_db.montant_ht,
#             "montant_tva": facture_db.montant_tva,
#             "montant_ttc": facture_db.montant_ttc,
#         },
#         "extracted_fields": {
#             "fournisseur": data.get("fournisseur"),
#             "date_facture": data.get("date_facture"),
#             "montant_ht": data.get("montant_ht"),
#             "montant_tva": data.get("montant_tva"),
#             "montant_ttc": data.get("montant_ttc"),
#         },
#         # "ocr_text": text  # décommente si tu veux voir tout le texte OCR dans Swagger
#     }





import os
import shutil
from datetime import datetime
from typing import Generator, Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas import FactureCreate, FactureUpdate, FactureOut, EcritureOut
import crud

from services.ocr_service import OCRService
from services.extract_fields import parse_facture_text


router = APIRouter(prefix="/factures", tags=["Factures"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ocr = OCRService()


# -------------------------
# DB Dependency
# -------------------------
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Helpers
# -------------------------
def parse_date_fr(date_str: Optional[str]):
    """Convertit 'dd/mm/yyyy' -> date. Retourne None si invalide."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in [".pdf", ".png", ".jpg", ".jpeg"]


# -------------------------
# Routes CRUD
# -------------------------
@router.get("/", response_model=list[FactureOut])
def list_factures(db: Session = Depends(get_db)):
    return crud.get_factures(db)


@router.post("/", response_model=FactureOut)
def add_facture(facture: FactureCreate, db: Session = Depends(get_db)):
    return crud.create_facture(db, facture)


@router.get("/{facture_id}", response_model=FactureOut)
def get_facture(facture_id: int, db: Session = Depends(get_db)):
    facture = crud.get_facture_by_id(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return facture


@router.put("/{facture_id}", response_model=FactureOut)
def update_facture(
    facture_id: int,
    facture_data: FactureUpdate,
    db: Session = Depends(get_db),
):
    facture = crud.update_facture(db, facture_id, facture_data)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return facture


@router.put("/{facture_id}/valider", response_model=FactureOut)
def valider_facture(facture_id: int, db: Session = Depends(get_db)):
    facture = crud.valider_facture(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return facture


@router.delete("/{facture_id}")
def delete_facture(facture_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_facture(db, facture_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return {"message": "Facture supprimée", "facture_id": facture_id}


# ✅ Route : récupérer les écritures d'une facture
@router.get("/{facture_id}/ecritures", response_model=list[EcritureOut])
def get_ecritures(facture_id: int, db: Session = Depends(get_db)):
    facture = crud.get_facture_by_id(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    return crud.get_ecritures_by_facture_id(db, facture_id)


# -------------------------
# Route Upload + OCR + DB
# -------------------------
@router.post("/upload-facture/")
async def upload_facture(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")

    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilise: PDF, PNG, JPG, JPEG",
        )

    # 1) Sauvegarde du fichier dans uploads/
    filename = file.filename
    save_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur sauvegarde fichier: {e}")

    # 2) OCR (PDF ou image)
    try:
        text = ocr.extract_text(save_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur OCR: {e}")

    # 3) Extraction des champs (regex)
    data = parse_facture_text(text)

    # 4) Préparer objet FactureCreate
    facture_in = FactureCreate(
        fournisseur=data.get("fournisseur"),
        date_facture=parse_date_fr(data.get("date_facture")),
        montant_ht=data.get("montant_ht"),
        montant_tva=data.get("montant_tva"),
        montant_ttc=data.get("montant_ttc"),
    )

    # 5) Sauvegarder en DB
    try:
        facture_db = crud.create_facture(db, facture_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur insertion DB: {e}")

    # 6) Retour
    return {
        "message": "Facture uploadée + OCR effectué + enregistrée en DB",
        "file_saved_as": save_path,
        "facture": {
            "id": facture_db.id,
            "fournisseur": facture_db.fournisseur,
            "date_facture": str(facture_db.date_facture) if facture_db.date_facture else None,
            "montant_ht": facture_db.montant_ht,
            "montant_tva": facture_db.montant_tva,
            "montant_ttc": facture_db.montant_ttc,
            "statut": facture_db.statut,
        },
        "extracted_fields": {
            "fournisseur": data.get("fournisseur"),
            "date_facture": data.get("date_facture"),
            "montant_ht": data.get("montant_ht"),
            "montant_tva": data.get("montant_tva"),
            "montant_ttc": data.get("montant_ttc"),
        },
    }
