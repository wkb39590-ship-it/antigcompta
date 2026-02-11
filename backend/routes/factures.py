


# import os
# import shutil
# from datetime import datetime
# from typing import Generator, Optional

# from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
# from fastapi.responses import FileResponse
# from sqlalchemy.orm import Session

# from database import SessionLocal
# from schemas import FactureCreate, FactureUpdate, FactureOut, EcritureOut
# import crud

# from services.ocr_service import OCRService
# from services.extract_fields import parse_facture_text
# from services.ecritures_service import EcrituresService
# from services.ded_export_service import generate_ded_xlsx, generate_ded_pdf

# router = APIRouter(prefix="/factures", tags=["Factures"])

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# ocr = OCRService()


# def get_db() -> Generator[Session, None, None]:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# def parse_date_fr(date_str: Optional[str]):
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
# # CRUD
# # -------------------------
# @router.get("/", response_model=list[FactureOut])
# def list_factures(db: Session = Depends(get_db)):
#     return crud.get_factures(db)


# @router.post("/", response_model=FactureOut, status_code=status.HTTP_201_CREATED)
# def add_facture(facture: FactureCreate, db: Session = Depends(get_db)):
#     return crud.create_facture(db, facture)


# @router.get("/{facture_id}", response_model=FactureOut)
# def get_facture(facture_id: int, db: Session = Depends(get_db)):
#     facture = crud.get_facture_by_id(db, facture_id)
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")
#     return facture


# @router.put("/{facture_id}", response_model=FactureOut)
# def update_facture(facture_id: int, facture_data: FactureUpdate, db: Session = Depends(get_db)):
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


# # -------------------------
# # Écritures
# # -------------------------
# @router.get("/{facture_id}/ecritures", response_model=list[EcritureOut])
# def get_ecritures(facture_id: int, db: Session = Depends(get_db)):
#     facture = crud.get_facture_by_id(db, facture_id)
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")
#     return crud.get_ecritures_by_facture_id(db, facture_id)


# @router.post("/{facture_id}/generate-ecritures", response_model=list[EcritureOut])
# def generate_ecritures(facture_id: int, db: Session = Depends(get_db)):
#     facture = crud.get_facture_by_id(db, facture_id)
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")

#     try:
#         return EcrituresService.generate_for_facture(db, facture, replace=True)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur génération écritures: {e}")


# # -------------------------
# # Validation + auto génération (écritures + DED)
# # -------------------------
# @router.put("/{facture_id}/valider", response_model=FactureOut)
# def valider_facture(
#     facture_id: int,
#     generate_ecritures: bool = Query(True),
#     generate_ded: bool = Query(True),
#     db: Session = Depends(get_db),
# ):
#     facture = crud.get_facture_by_id(db, facture_id)
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")

#     facture = crud.valider_facture(db, facture_id)

#     if generate_ecritures:
#         EcrituresService.generate_for_facture(db, facture, replace=True)

#     if generate_ded:
#         if facture.montant_ht is None or facture.montant_tva is None or facture.montant_ttc is None:
#             raise HTTPException(status_code=400, detail="Montants manquants: impossible de générer le DED")

#         xlsx_path = generate_ded_xlsx(facture)
#         pdf_path = generate_ded_pdf(facture)

#         facture.ded_xlsx_path = xlsx_path
#         facture.ded_pdf_path = pdf_path
#         facture.ded_file_path = xlsx_path  # compat ancien

#         db.commit()
#         db.refresh(facture)

#     return facture


# # -------------------------
# # DED manuel + Download
# # -------------------------
# @router.post("/{facture_id}/ded/generate", response_model=FactureOut)
# def generate_ded_for_facture(
#     facture_id: int,
#     format: str = Query("both", pattern="^(pdf|xlsx|both)$"),
#     db: Session = Depends(get_db),
# ):
#     facture = crud.get_facture_by_id(db, facture_id)
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")

#     if facture.statut != "VALIDEE":
#         raise HTTPException(status_code=400, detail="La facture doit être VALIDEE avant génération DED")

#     if facture.montant_ht is None or facture.montant_tva is None or facture.montant_ttc is None:
#         raise HTTPException(status_code=400, detail="Montants manquants: impossible de générer le DED")

#     if format in ("xlsx", "both"):
#         facture.ded_xlsx_path = generate_ded_xlsx(facture)
#         facture.ded_file_path = facture.ded_xlsx_path

#     if format in ("pdf", "both"):
#         facture.ded_pdf_path = generate_ded_pdf(facture)

#     db.commit()
#     db.refresh(facture)
#     return facture


# @router.get("/{facture_id}/ded/download")
# def download_ded_for_facture(
#     facture_id: int,
#     format: str = Query("xlsx", pattern="^(pdf|xlsx)$"),
#     db: Session = Depends(get_db),
# ):
#     facture = crud.get_facture_by_id(db, facture_id)
#     if not facture:
#         raise HTTPException(status_code=404, detail="Facture non trouvée")

#     path = facture.ded_pdf_path if format == "pdf" else facture.ded_xlsx_path
#     if not path or not os.path.exists(path):
#         raise HTTPException(status_code=404, detail="Fichier DED non trouvé. Génère-le d'abord.")

#     filename = os.path.basename(path)
#     media_type = "application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     return FileResponse(path=path, filename=filename, media_type=media_type)


# # -------------------------
# # Upload + OCR + extraction + DB
# # -------------------------
# @router.post("/upload-facture/")
# async def upload_facture(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     if not file.filename:
#         raise HTTPException(status_code=400, detail="Nom de fichier invalide")

#     if not allowed_file(file.filename):
#         raise HTTPException(status_code=400, detail="Format non supporté. Utilise: PDF, PNG, JPG, JPEG")

#     save_path = os.path.join(UPLOAD_DIR, file.filename)

#     try:
#         with open(save_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur sauvegarde fichier: {e}")

#     try:
#         text = ocr.extract_text(save_path)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur OCR: {e}")

#     data = parse_facture_text(text)

#     facture_in = FactureCreate(
#         fournisseur=data.get("fournisseur"),
#         date_facture=parse_date_fr(data.get("date_facture")),
#         montant_ht=data.get("montant_ht"),
#         montant_tva=data.get("montant_tva"),
#         montant_ttc=data.get("montant_ttc"),

#         numero_facture=data.get("numero_facture"),
#         designation=data.get("designation"),

#         # champs DED (FOURNISSEUR)
#         if_frs=data.get("if_frs"),
#         ice_frs=data.get("ice_frs"),
#         taux_tva=data.get("taux_tva"),
#     )

#     try:
#         facture_db = crud.create_facture(db, facture_in)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur insertion DB: {e}")

#     return {
#         "message": "Facture uploadée + OCR effectué + enregistrée en DB",
#         "file_saved_as": save_path,
#         "facture": facture_db,      # FastAPI va sérialiser via FactureOut
#         "extracted_fields": data,   # debug
#         # "ocr_preview": text[:1200],
#     }















import os
import shutil
from datetime import datetime
from typing import Generator, Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import SessionLocal
from schemas import FactureCreate, FactureUpdate, FactureOut, EcritureOut
import crud

from services.ocr_service import OCRService
from services.extract_fields import parse_facture_text
from services.ecritures_service import EcrituresService
from services.ded_export_service import generate_ded_xlsx, generate_ded_pdf

router = APIRouter(prefix="/factures", tags=["Factures"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ocr = OCRService()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def parse_date_fr(date_str: Optional[str]):
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
# CRUD
# -------------------------
@router.get("/", response_model=list[FactureOut])
def list_factures(db: Session = Depends(get_db)):
    return crud.get_factures(db)


@router.post("/", response_model=FactureOut, status_code=status.HTTP_201_CREATED)
def add_facture(facture: FactureCreate, db: Session = Depends(get_db)):
    return crud.create_facture(db, facture)


@router.get("/{facture_id}", response_model=FactureOut)
def get_facture(facture_id: int, db: Session = Depends(get_db)):
    facture = crud.get_facture_by_id(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return facture


# ✅ PATCH partiel (corrige uniquement les champs envoyés)
@router.patch("/{facture_id}", response_model=FactureOut)
def patch_facture(facture_id: int, facture_data: FactureUpdate, db: Session = Depends(get_db)):
    facture = crud.get_facture_by_id(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    # Bloquer si déjà validée
    if (facture.statut or "").lower() == "validee":
        raise HTTPException(status_code=400, detail="Facture déjà validée, modification interdite")

    # Appliquer uniquement les champs envoyés (FastAPI/Pydantic v2)
    data = facture_data.model_dump(exclude_unset=True)

    # Si rien envoyé
    if not data:
        return facture

    # Patch via crud si tu veux, sinon patch direct ici
    for k, v in data.items():
        setattr(facture, k, v)

    # Recalcul taux si HT/TVA modifiés et taux pas envoyé
    if ("montant_ht" in data or "montant_tva" in data) and ("taux_tva" not in data):
        if facture.montant_ht is not None and facture.montant_tva is not None and facture.montant_ht != 0:
            facture.taux_tva = round((facture.montant_tva / facture.montant_ht) * 100, 2)

    # Recalcul TTC si HT/TVA modifiés et TTC pas envoyé
    if ("montant_ht" in data or "montant_tva" in data) and ("montant_ttc" not in data):
        if facture.montant_ht is not None and facture.montant_tva is not None:
            facture.montant_ttc = round(facture.montant_ht + facture.montant_tva, 2)

    db.commit()
    db.refresh(facture)
    return facture


# ⚠️ garder PUT si tu veux, mais je déconseille car Swagger va t'écraser avec 0/string.
# Si tu veux garder PUT, fais-le appeler PATCH logic :
@router.put("/{facture_id}", response_model=FactureOut)
def update_facture(facture_id: int, facture_data: FactureUpdate, db: Session = Depends(get_db)):
    # déléguer vers le patch partiel
    return patch_facture(facture_id, facture_data, db)


@router.delete("/{facture_id}")
def delete_facture(facture_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_facture(db, facture_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return {"message": "Facture supprimée", "facture_id": facture_id}


# -------------------------
# Écritures
# -------------------------
@router.get("/{facture_id}/ecritures", response_model=list[EcritureOut])
def get_ecritures(facture_id: int, db: Session = Depends(get_db)):
    facture = crud.get_facture_by_id(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return crud.get_ecritures_by_facture_id(db, facture_id)


@router.post("/{facture_id}/generate-ecritures", response_model=list[EcritureOut])
def generate_ecritures(facture_id: int, db: Session = Depends(get_db)):
    facture = crud.get_facture_by_id(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    # option: empêcher génération si validée (ton choix)
    # if (facture.statut or "").lower() == "validee":
    #     raise HTTPException(status_code=400, detail="Facture déjà validée")

    try:
        return EcrituresService.generate_for_facture(db, facture, replace=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération écritures: {e}")


# -------------------------
# Validation + auto génération (écritures + DED)
# -------------------------
@router.post("/{facture_id}/valider", response_model=FactureOut)
def valider_facture(
    facture_id: int,
    generate_ecritures: bool = Query(True),
    generate_ded: bool = Query(True),
    db: Session = Depends(get_db),
):
    facture = crud.get_facture_by_id(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    # Déjà validée -> on renvoie directement
    if (facture.statut or "").lower() == "validee":
        return facture

    # Mettre statut "validee"
    facture.statut = "validee"
    db.commit()
    db.refresh(facture)

    if generate_ecritures:
        EcrituresService.generate_for_facture(db, facture, replace=True)

    if generate_ded:
        if facture.montant_ht is None or facture.montant_tva is None or facture.montant_ttc is None:
            raise HTTPException(status_code=400, detail="Montants manquants: impossible de générer le DED")

        xlsx_path = generate_ded_xlsx(facture)
        pdf_path = generate_ded_pdf(facture)

        facture.ded_xlsx_path = xlsx_path
        facture.ded_pdf_path = pdf_path
        facture.ded_file_path = xlsx_path

        db.commit()
        db.refresh(facture)

    return facture


# -------------------------
# DED manuel + Download
# -------------------------
@router.post("/{facture_id}/ded/generate", response_model=FactureOut)
def generate_ded_for_facture(
    facture_id: int,
    format: str = Query("both", pattern="^(pdf|xlsx|both)$"),
    db: Session = Depends(get_db),
):
    facture = crud.get_facture_by_id(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    # ✅ statut cohérent
    if (facture.statut or "").lower() != "validee":
        raise HTTPException(status_code=400, detail="La facture doit être validée avant génération DED")

    if facture.montant_ht is None or facture.montant_tva is None or facture.montant_ttc is None:
        raise HTTPException(status_code=400, detail="Montants manquants: impossible de générer le DED")

    if format in ("xlsx", "both"):
        facture.ded_xlsx_path = generate_ded_xlsx(facture)
        facture.ded_file_path = facture.ded_xlsx_path

    if format in ("pdf", "both"):
        facture.ded_pdf_path = generate_ded_pdf(facture)

    db.commit()
    db.refresh(facture)
    return facture


@router.get("/{facture_id}/ded/download")
def download_ded_for_facture(
    facture_id: int,
    format: str = Query("xlsx", pattern="^(pdf|xlsx)$"),
    db: Session = Depends(get_db),
):
    facture = crud.get_facture_by_id(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    path = facture.ded_pdf_path if format == "pdf" else facture.ded_xlsx_path
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Fichier DED non trouvé. Génère-le d'abord.")

    filename = os.path.basename(path)
    media_type = "application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return FileResponse(path=path, filename=filename, media_type=media_type)


# -------------------------
# Upload + OCR + extraction + DB
# -------------------------
@router.post("/upload-facture/")
async def upload_facture(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")

    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Format non supporté. Utilise: PDF, PNG, JPG, JPEG")

    save_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur sauvegarde fichier: {e}")

    try:
        text = ocr.extract_text(save_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur OCR: {e}")

    data = parse_facture_text(text)

    facture_in = FactureCreate(
        fournisseur=data.get("fournisseur"),
        date_facture=parse_date_fr(data.get("date_facture")),
        montant_ht=data.get("montant_ht"),
        montant_tva=data.get("montant_tva"),
        montant_ttc=data.get("montant_ttc"),
        numero_facture=data.get("numero_facture"),
        designation=data.get("designation"),
        if_frs=data.get("if_frs"),
        ice_frs=data.get("ice_frs"),
        taux_tva=data.get("taux_tva"),
        statut="brouillon",
    )

    try:
        facture_db = crud.create_facture(db, facture_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur insertion DB: {e}")

    return {
        "message": "Facture uploadée + OCR effectué + enregistrée en DB",
        "file_saved_as": save_path,
        "facture": facture_db,
        "extracted_fields": data,
    }
