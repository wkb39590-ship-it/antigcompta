"""
routes/societes.py — Gestion des sociétés
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import Societe, Agent, agent_societes
from routes.auth import get_current_agent

router = APIRouter(prefix="/societes", tags=["societes"])


class SocieteCreate(BaseModel):
    raison_sociale: str
    ice: Optional[str] = None
    if_fiscal: Optional[str] = None
    rc: Optional[str] = None
    adresse: Optional[str] = None


@router.get("/", response_model=list)
def list_societes(agent: Agent = Depends(get_current_agent), db: Session = Depends(get_db)):
    """Liste les sociétés du cabinet. Si non-admin, retourne seulement celles assignées à l'agent."""
    query = db.query(Societe).filter(Societe.cabinet_id == agent.cabinet_id)
    if not agent.is_admin:
        query = query.join(agent_societes).filter(agent_societes.c.agent_id == agent.id)
    societes = query.all()
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
def create_societe(data: SocieteCreate, agent: Agent = Depends(get_current_agent), db: Session = Depends(get_db)):
    """Créer une société: réservé aux admins du cabinet."""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")

    s = Societe(
        cabinet_id=agent.cabinet_id,
        raison_sociale=data.raison_sociale,
        ice=data.ice,
        if_fiscal=data.if_fiscal,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "raison_sociale": s.raison_sociale, "message": "Société créée"}


@router.get("/{societe_id}", response_model=dict)
def get_societe(societe_id: int, agent: Agent = Depends(get_current_agent), db: Session = Depends(get_db)):
    s = db.query(Societe).filter(Societe.id == societe_id).first()
    if not s:
        raise HTTPException(404, "Société introuvable")
    if s.cabinet_id != agent.cabinet_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return {
        "id": s.id,
        "raison_sociale": s.raison_sociale,
        "ice": s.ice,
        "if_fiscal": s.if_fiscal,
    }
