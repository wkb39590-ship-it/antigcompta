# # routes/societes.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Societe

# router = APIRouter(prefix="/societes", tags=["societes"])


# @router.post("/")
# def create_societe(payload: dict, db: Session = Depends(get_db)):
#     raison_sociale = (payload.get("raison_sociale") or "").strip()
#     if not raison_sociale:
#         raise HTTPException(status_code=400, detail="raison_sociale est obligatoire")

#     s = Societe(
#         raison_sociale=raison_sociale,
#         ice=(payload.get("ice") or None),
#         if_fiscal=(payload.get("if_fiscal") or None),
#     )
#     db.add(s)
#     db.commit()
#     db.refresh(s)
#     return {
#         "id": s.id,
#         "raison_sociale": s.raison_sociale,
#         "ice": s.ice,
#         "if_fiscal": s.if_fiscal,
#         "created_at": s.created_at,
#     }


# @router.get("/")
# def list_societes(db: Session = Depends(get_db)):
#     rows = db.query(Societe).order_by(Societe.id.desc()).all()
#     return [
#         {
#             "id": s.id,
#             "raison_sociale": s.raison_sociale,
#             "ice": s.ice,
#             "if_fiscal": s.if_fiscal,
#             "created_at": s.created_at,
#         }
#         for s in rows
#     ]


# @router.get("/{societe_id}")
# def get_societe(societe_id: int, db: Session = Depends(get_db)):
#     s = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not s:
#         raise HTTPException(status_code=404, detail="Société introuvable")
#     return {
#         "id": s.id,
#         "raison_sociale": s.raison_sociale,
#         "ice": s.ice,
#         "if_fiscal": s.if_fiscal,
#         "created_at": s.created_at,
#     }


























# # routes/societes.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Societe
# from schemas import SocieteIn, SocieteOut

# router = APIRouter(prefix="/societes", tags=["societes"])


# @router.post("/", response_model=SocieteOut)
# def create_societe(payload: SocieteIn, db: Session = Depends(get_db)):
#     raison_sociale = (payload.raison_sociale or "").strip()
#     if not raison_sociale:
#         raise HTTPException(status_code=400, detail="raison_sociale est obligatoire")

#     s = Societe(
#         raison_sociale=raison_sociale,
#         if_fiscal=payload.if_fiscal,
#         ice=payload.ice,
#         rc=payload.rc,
#         adresse=payload.adresse,
#     )

#     db.add(s)
#     db.commit()
#     db.refresh(s)
#     return s


# @router.get("/", response_model=list[SocieteOut])
# def list_societes(db: Session = Depends(get_db)):
#     return db.query(Societe).order_by(Societe.id.desc()).all()


# @router.get("/{societe_id}", response_model=SocieteOut)
# def get_societe(societe_id: int, db: Session = Depends(get_db)):
#     s = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not s:
#         raise HTTPException(status_code=404, detail="Société introuvable")
#     return s


















# # routes/societes.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Societe
# from schemas import SocieteIn, SocieteOut

# router = APIRouter(prefix="/societes", tags=["societes"])


# @router.post("/", response_model=SocieteOut)
# def create_societe(payload: SocieteIn, db: Session = Depends(get_db)):
#     s = Societe(**payload.model_dump())
#     db.add(s)
#     db.commit()
#     db.refresh(s)
#     return s


# @router.get("/", response_model=list[SocieteOut])
# def list_societes(db: Session = Depends(get_db)):
#     return db.query(Societe).order_by(Societe.id.desc()).all()


# @router.get("/{societe_id}", response_model=SocieteOut)
# def get_societe(societe_id: int, db: Session = Depends(get_db)):
#     s = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not s:
#         raise HTTPException(status_code=404, detail="Société introuvable")
#     return s














# # routes/societes.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Societe

# router = APIRouter(prefix="/societes", tags=["societes"])


# @router.post("/")
# def create_societe(payload: dict, db: Session = Depends(get_db)):
#     # payload attendu:
#     # { "raison_sociale": "...", "if_fiscal": "...", "ice": "...", "rc": "...", "adresse": "..." }
#     s = Societe(**payload)
#     db.add(s)
#     db.commit()
#     db.refresh(s)
#     return s


# @router.get("/")
# def list_societes(db: Session = Depends(get_db)):
#     return db.query(Societe).order_by(Societe.id.desc()).all()


# @router.get("/{societe_id}")
# def get_societe(societe_id: int, db: Session = Depends(get_db)):
#     s = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not s:
#         raise HTTPException(status_code=404, detail="Société introuvable")
#     return s


# @router.delete("/{societe_id}")
# def delete_societe(societe_id: int, db: Session = Depends(get_db)):
#     s = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not s:
#         raise HTTPException(status_code=404, detail="Société introuvable")
#     db.delete(s)
#     db.commit()
#     return {"message": "Société supprimée"}












# # routes/societes.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import Societe
# from schemas import SocieteIn, SocieteOut

# router = APIRouter(prefix="/societes", tags=["societes"])


# @router.post("/", response_model=SocieteOut)
# def create_societe(payload: SocieteIn, db: Session = Depends(get_db)):
#     s = Societe(**payload.model_dump())
#     db.add(s)
#     db.commit()
#     db.refresh(s)
#     return s


# @router.get("/", response_model=list[SocieteOut])
# def list_societes(db: Session = Depends(get_db)):
#     return db.query(Societe).order_by(Societe.id.desc()).all()


# @router.get("/{societe_id}", response_model=SocieteOut)
# def get_societe(societe_id: int, db: Session = Depends(get_db)):
#     s = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not s:
#         raise HTTPException(status_code=404, detail="Société introuvable")
#     return s


# @router.delete("/{societe_id}")
# def delete_societe(societe_id: int, db: Session = Depends(get_db)):
#     s = db.query(Societe).filter(Societe.id == societe_id).first()
#     if not s:
#         raise HTTPException(status_code=404, detail="Société introuvable")

#     db.delete(s)
#     db.commit()
#     return {"message": "Société supprimée"}


















from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Societe
from schemas import SocieteIn, SocieteOut, SocieteUpdate

router = APIRouter(prefix="/societes", tags=["societes"])


@router.post("/", response_model=SocieteOut)
def create_societe(payload: SocieteIn, db: Session = Depends(get_db)):
    s = Societe(**payload.model_dump())
    db.add(s)
    try:
        db.commit()
        db.refresh(s)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")
    return s


@router.get("/", response_model=list[SocieteOut])
def list_societes(db: Session = Depends(get_db)):
    return db.query(Societe).order_by(Societe.id.desc()).all()


@router.get("/{societe_id}", response_model=SocieteOut)
def get_societe(societe_id: int, db: Session = Depends(get_db)):
    s = db.query(Societe).filter(Societe.id == societe_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Société introuvable")
    return s


@router.put("/{societe_id}", response_model=SocieteOut)
def update_societe(societe_id: int, payload: SocieteUpdate, db: Session = Depends(get_db)):
    s = db.query(Societe).filter(Societe.id == societe_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Société introuvable")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(s, k, v)

    try:
        db.commit()
        db.refresh(s)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

    return s


@router.delete("/{societe_id}")
def delete_societe(societe_id: int, db: Session = Depends(get_db)):
    s = db.query(Societe).filter(Societe.id == societe_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Société introuvable")

    db.delete(s)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur DB: {e}")

    return {"message": "Société supprimée"}
