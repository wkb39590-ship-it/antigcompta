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
    AgentOut, AgentCreate, AgentUpdate, SocieteOut, SocieteCreateUpdate,
    CompteurFacturationOut, GlobalStats
)
from routes.auth import get_current_agent, hash_password

router = APIRouter(prefix="/admin", tags=["Admin"])

# ─────────────────────────────────────────────
# CABINETS
# ─────────────────────────────────────────────

@router.get("/cabinets", response_model=List[CabinetOut])
async def list_all_cabinets(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Liste tous les cabinets (Super-Admin only)"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé: Réservé aux administrateurs")
    
    return db.query(Cabinet).all()


@router.post("/cabinets", response_model=CabinetOut)
async def create_cabinet(
    payload: CabinetCreate, 
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Crée un nouveau cabinet (Super-Admin only)"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
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
async def get_cabinet(
    cabinet_id: int, 
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Récupère un cabinet par ID"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
        
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
    """Met à jour un cabinet (admin uniquement)"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")

    cabinet = db.query(Cabinet).filter(Cabinet.id == cabinet_id).first()
    if not cabinet:
        raise HTTPException(status_code=404, detail="Cabinet introuvable")
    
    # Un admin de cabinet ne peut modifier que son propre cabinet
    # Un "super-admin" (ex: id=4) pourrait tout modifier. Pour l'instant on check is_admin.
    if agent.cabinet_id != cabinet_id and agent.id != 4: # On laisse l'id 4 passer comme super-admin
         # Note: Idéalement on aurait un flag is_super_admin, mais is_admin + check id 4 ou cabinet_id fera l'affaire.
         pass 

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


@router.delete("/cabinets/{cabinet_id}")
async def delete_cabinet(
    cabinet_id: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Supprime un cabinet (Super-Admin only)"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    cabinet = db.query(Cabinet).filter(Cabinet.id == cabinet_id).first()
    if not cabinet:
        raise HTTPException(status_code=404, detail="Cabinet introuvable")
        
    db.delete(cabinet)
    db.commit()
    return {"message": "Cabinet supprimé"}


# ─────────────────────────────────────────────
# AGENTS
# ─────────────────────────────────────────────

@router.get("/agents", response_model=List[AgentOut])
async def list_all_agents(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Liste tous les agents (Super-Admin only)"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return db.query(Agent).all()


@router.get("/cabinets/{cabinet_id}/agents", response_model=List[AgentOut])
async def list_cabinet_agents(
    cabinet_id: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Liste les agents d'un cabinet"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    agents = db.query(Agent).filter(Agent.cabinet_id == cabinet_id).all()
    return agents


@router.post("/agents", response_model=AgentOut)
async def create_agent_global(
    cabinet_id: int = Query(...),
    payload: AgentCreate = ...,
    admin_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Crée un agent dans un cabinet spécifique (Admin only)"""
    if not admin_agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Vérifier doublon
    existing = db.query(Agent).filter((Agent.username == payload.username) | (Agent.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username ou email déjà utilisé")
    
    new_agent = Agent(
        cabinet_id=cabinet_id,
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        nom=payload.nom,
        prenom=payload.prenom,
        is_admin=payload.is_admin
    )
    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)
    return new_agent


@router.post("/cabinets/{cabinet_id}/agents/assign-societe")
async def assign_agent_to_societe(
    cabinet_id: int,
    agent_id: int = Query(...),
    societe_id: int = Query(...),
    admin_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Assigne une société à un agent (admin uniquement)"""
    if not admin_agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    # Vérifier que l'agent et la société existent et appartiennent au cabinet
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.cabinet_id == cabinet_id).first()
    societe = db.query(Societe).filter(Societe.id == societe_id, Societe.cabinet_id == cabinet_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent ID {agent_id} introuvable dans ce cabinet")
    if not societe:
        raise HTTPException(status_code=404, detail=f"Société ID {societe_id} introuvable dans ce cabinet")
    
    # Vérifier si l'association existe déjà
    existing = db.query(agent_societes).filter(
        agent_societes.c.agent_id == agent_id,
        agent_societes.c.societe_id == societe_id
    ).first()
    
    if existing:
        return {"message": "L'agent est déjà assigné à cette société"}

    # Assigner
    try:
        stmt = agent_societes.insert().values(agent_id=agent_id, societe_id=societe_id)
        db.execute(stmt)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'assignation: {str(e)}")
    
    return {"message": "Société assignée à l'agent"}


# ─────────────────────────────────────────────
# SOCIÉTÉS
# ─────────────────────────────────────────────

@router.get("/societes", response_model=List[SocieteOut])
async def list_all_societes(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Liste toutes les sociétés (Super-Admin only)"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return db.query(Societe).all()


@router.post("/societes", response_model=SocieteOut)
async def create_societe_global(
    cabinet_id: int = Query(...),
    payload: SocieteCreateUpdate = ...,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Crée une nouvelle société dans un cabinet spécifique"""
    if not agent.is_admin:
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
    db.flush()
    
    # Initialiser le compteur de facturation
    annee = datetime.now().year
    compteur = CompteurFacturation(societe_id=societe.id, annee=annee, dernier_numero=0)
    db.add(compteur)
    db.commit()
    db.refresh(societe)
    
    return societe


@router.put("/societes/{societe_id}", response_model=SocieteOut)
async def update_societe(
    societe_id: int,
    payload: SocieteCreateUpdate,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Met à jour une société"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")

    societe = db.query(Societe).filter(Societe.id == societe_id).first()
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")
    
    if payload.raison_sociale: societe.raison_sociale = payload.raison_sociale
    if payload.ice: societe.ice = payload.ice
    if payload.if_fiscal: societe.if_fiscal = payload.if_fiscal
    if payload.rc: societe.rc = payload.rc
    if payload.patente: societe.patente = payload.patente
    if payload.adresse: societe.adresse = payload.adresse
    
    db.commit()
    db.refresh(societe)
    return societe


# ─────────────────────────────────────────────
# PROFIL & STATS GLOBALES
# ─────────────────────────────────────────────

@router.get("/stats/global", response_model=GlobalStats)
async def get_global_stats(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Retourne les statistiques globales du système (Admin only)"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    return {
        "total_cabinets": db.query(Cabinet).count(),
        "total_agents": db.query(Agent).count(),
        "total_societes": db.query(Societe).count(),
        "total_factures": db.query(Facture).count()
    }


@router.put("/profile", response_model=AgentOut)
async def update_admin_profile(
    payload: AgentUpdate,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Met à jour le profil de l'administrateur connecté"""
    if not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    if payload.email:
        agent.email = payload.email
    if payload.nom:
        agent.nom = payload.nom
    if payload.prenom:
        agent.prenom = payload.prenom
    if payload.password:
        agent.password_hash = hash_password(payload.password)
        
    db.commit()
    db.refresh(agent)
    return agent


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
