"""
routes/societes.py — Gestion des sociétés
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import Societe

router = APIRouter(prefix="/societes", tags=["societes"])


class SocieteCreate(BaseModel):
    raison_sociale: str
    ice: Optional[str] = None
    if_fiscal: Optional[str] = None
    rc: Optional[str] = None
    adresse: Optional[str] = None


@router.get("/", response_model=list)
def list_societes(db: Session = Depends(get_db)):
    societes = db.query(Societe).all()
    return [
        {
            "id": s.id,
            "raison_sociale": s.raison_sociale,
            "ice": s.ice,
            "if_fiscal": s.if_fiscal,
        }
        for s in societes
    ]


@router.post("/", response_model=dict)
def create_societe(data: SocieteCreate, db: Session = Depends(get_db)):
    s = Societe(
        raison_sociale=data.raison_sociale,
        ice=data.ice,
        if_fiscal=data.if_fiscal,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "raison_sociale": s.raison_sociale, "message": "Société créée"}


@router.get("/{societe_id}", response_model=dict)
def get_societe(societe_id: int, db: Session = Depends(get_db)):
    s = db.query(Societe).filter(Societe.id == societe_id).first()
    if not s:
        raise HTTPException(404, "Société introuvable")
    return {
        "id": s.id,
        "raison_sociale": s.raison_sociale,
        "ice": s.ice,
        "if_fiscal": s.if_fiscal,
    }
