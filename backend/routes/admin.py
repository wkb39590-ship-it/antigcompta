"""
routes/admin.py - Gestion des Cabinets, Agents, Sociétés et Compteurs
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List

from database import get_db
from models import Cabinet, Agent, Societe, CompteurFacturation, agent_societes, Facture
from schemas import (
    CabinetCreate, CabinetUpdate, CabinetOut,
    AgentOut, SocieteOut, SocieteCreateUpdate,
    CompteurFacturationOut
)
from routes.auth import get_current_agent, hash_password

router = APIRouter(prefix="/admin", tags=["Admin"])

# ─────────────────────────────────────────────
# CABINETS
# ─────────────────────────────────────────────

@router.post("/cabinets", response_model=CabinetOut)
async def create_cabinet(payload: CabinetCreate, db: Session = Depends(get_db)):
    """Crée un nouveau cabinet (super-admin only)"""
    # TODO: Ajouter vérification super-admin
    
    cabinet = Cabinet(
        nom=payload.nom,
        email=payload.email,
        telephone=payload.telephone,
        adresse=payload.adresse
    )
    
    db.add(cabinet)
    db.commit()
    db.refresh(cabinet)
    
    return cabinet


@router.get("/cabinets/{cabinet_id}", response_model=CabinetOut)
async def get_cabinet(cabinet_id: int, db: Session = Depends(get_db)):
    """Récupère un cabinet par ID"""
    cabinet = db.query(Cabinet).filter(Cabinet.id == cabinet_id).first()
    if not cabinet:
        raise HTTPException(status_code=404, detail="Cabinet introuvable")
    return cabinet


@router.put("/cabinets/{cabinet_id}", response_model=CabinetOut)
async def update_cabinet(
    cabinet_id: int,
    payload: CabinetUpdate,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Met à jour un cabinet (admin du cabinet uniquement)"""
    cabinet = db.query(Cabinet).filter(Cabinet.id == cabinet_id).first()
    if not cabinet:
        raise HTTPException(status_code=404, detail="Cabinet introuvable")
    
    if agent.cabinet_id != cabinet_id or not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    if payload.nom:
        cabinet.nom = payload.nom
    if payload.email:
        cabinet.email = payload.email
    if payload.telephone:
        cabinet.telephone = payload.telephone
    if payload.adresse:
        cabinet.adresse = payload.adresse
    
    db.commit()
    db.refresh(cabinet)
    return cabinet


# ─────────────────────────────────────────────
# AGENTS
# ─────────────────────────────────────────────

@router.get("/cabinets/{cabinet_id}/agents", response_model=List[AgentOut])
async def list_cabinet_agents(
    cabinet_id: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Liste les agents d'un cabinet (admin du cabinet uniquement)"""
    if agent.cabinet_id != cabinet_id or not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    agents = db.query(Agent).filter(Agent.cabinet_id == cabinet_id).all()
    return agents


@router.post("/cabinets/{cabinet_id}/agents/assign-societe")
async def assign_agent_to_societe(
    cabinet_id: int,
    agent_id: int = Query(...),
    societe_id: int = Query(...),
    admin_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Assigne une société à un agent (admin du cabinet uniquement)"""
    # Vérification d'accès
    if admin_agent.cabinet_id != cabinet_id or not admin_agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Vérifier que l'agent et la société existent et appartiennent au cabinet
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.cabinet_id == cabinet_id
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent introuvable")
    
    societe = db.query(Societe).filter(
        Societe.id == societe_id,
        Societe.cabinet_id == cabinet_id
    ).first()
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")
    
    # Assigner
    stmt = agent_societes.insert().values(agent_id=agent_id, societe_id=societe_id)
    try:
        db.execute(stmt)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Assignation déjà existante")
    
    return {"message": "Société assignée à l'agent"}


# ─────────────────────────────────────────────
# SOCIÉTÉS
# ─────────────────────────────────────────────

@router.post("/cabinets/{cabinet_id}/societes", response_model=SocieteOut)
async def create_societe(
    cabinet_id: int,
    payload: SocieteCreateUpdate,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Crée une nouvelle société dans un cabinet"""
    if agent.cabinet_id != cabinet_id or not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    societe = Societe(
        cabinet_id=cabinet_id,
        raison_sociale=payload.raison_sociale,
        ice=payload.ice,
        if_fiscal=payload.if_fiscal,
        rc=payload.rc,
        patente=payload.patente,
        adresse=payload.adresse
    )
    
    db.add(societe)
    db.commit()
    db.flush()  # Flush pour initialiser compteur
    
    # Initialiser le compteur de facturation pour l'année courante
    annee = datetime.now().year
    compteur = CompteurFacturation(
        societe_id=societe.id,
        annee=annee,
        dernier_numero=0
    )
    db.add(compteur)
    db.commit()
    db.refresh(societe)
    
    return societe


@router.get("/cabinets/{cabinet_id}/societes", response_model=List[SocieteOut])
async def list_cabinet_societes(
    cabinet_id: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Liste les sociétés d'un cabinet"""
    if agent.cabinet_id != cabinet_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    societes = db.query(Societe).filter(Societe.cabinet_id == cabinet_id).all()
    return societes


@router.put("/societes/{societe_id}", response_model=SocieteOut)
async def update_societe(
    societe_id: int,
    payload: SocieteCreateUpdate,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Met à jour une société"""
    societe = db.query(Societe).filter(Societe.id == societe_id).first()
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")
    
    if agent.cabinet_id != societe.cabinet_id or not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    if payload.raison_sociale:
        societe.raison_sociale = payload.raison_sociale
    if payload.ice:
        societe.ice = payload.ice
    if payload.if_fiscal:
        societe.if_fiscal = payload.if_fiscal
    if payload.rc:
        societe.rc = payload.rc
    if payload.patente:
        societe.patente = payload.patente
    if payload.adresse:
        societe.adresse = payload.adresse
    
    societe.updated_at = datetime.now()
    db.commit()
    db.refresh(societe)
    
    return societe


# ─────────────────────────────────────────────
# COMPTEURS DE FACTURATION
# ─────────────────────────────────────────────

@router.get("/societes/{societe_id}/compteurs")
async def get_compteurs(
    societe_id: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Récupère les compteurs de facturation pour une société"""
    societe = db.query(Societe).filter(Societe.id == societe_id).first()
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")
    
    if agent.cabinet_id != societe.cabinet_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    compteurs = db.query(CompteurFacturation).filter(
        CompteurFacturation.societe_id == societe_id
    ).order_by(CompteurFacturation.annee.desc()).all()
    
    return compteurs


@router.get("/societes/{societe_id}/compteurs/{annee}", response_model=CompteurFacturationOut)
async def get_compteur_by_annee(
    societe_id: int,
    annee: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Récupère le compteur d'une année spécifique"""
    societe = db.query(Societe).filter(Societe.id == societe_id).first()
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")
    
    if agent.cabinet_id != societe.cabinet_id:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    compteur = db.query(CompteurFacturation).filter(
        CompteurFacturation.societe_id == societe_id,
        CompteurFacturation.annee == annee
    ).first()
    
    if not compteur:
        # Créer le compteur si n'existe pas
        compteur = CompteurFacturation(
            societe_id=societe_id,
            annee=annee,
            dernier_numero=0
        )
        db.add(compteur)
        db.commit()
        db.refresh(compteur)
    
    return compteur


def get_next_invoice_number(societe_id: int, db: Session) -> str:
    """
    Génère le prochain numéro de facture pour une société
    Format: NNNNN/YY (ex: 00001/25)
    """
    annee = datetime.now().year
    annee_court = str(annee)[-2:]  # "25" pour 2025
    
    # Récupérer ou créer le compteur
    compteur = db.query(CompteurFacturation).filter(
        CompteurFacturation.societe_id == societe_id,
        CompteurFacturation.annee == annee
    ).with_for_update().first()  # Verrouiller pour éviter les race conditions
    
    if not compteur:
        compteur = CompteurFacturation(
            societe_id=societe_id,
            annee=annee,
            dernier_numero=0
        )
        db.add(compteur)
        db.flush()
    
    # Incrémenter et retourner
    compteur.dernier_numero += 1
    db.commit()
    
    numero_format = str(compteur.dernier_numero).zfill(5)
    return f"{numero_format}/{annee_court}"
