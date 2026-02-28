"""
routes/admin.py - Gestion des Cabinets, Agents, Sociétés et Compteurs
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List

from database import get_db
from models import Cabinet, Agent, Societe, CompteurFacturation, agents_societes, Facture, ActionLog
from schemas import (
    CabinetCreate, CabinetUpdate, CabinetOut,
    AgentOut, AgentCreate, AgentUpdate, SocieteOut, SocieteCreateUpdate,
    CompteurFacturationOut, GlobalStats, ActivityOut, ActivitiesResponse,
    ActionLogOut, ActionLogResponse
)
from routes.auth import get_current_agent, hash_password

router = APIRouter(prefix="/admin", tags=["Admin"])

# ─────────────────────────────────────────────
# UTILITAIRES DE PERMISSION
# ─────────────────────────────────────────────

def is_system_admin(agent: Agent):
    """Vérifie si l'agent est Super Admin (avec fallback explicite pour wissal)"""
    result = agent.is_super_admin or agent.username == "wissal" or agent.id == 1
    print(f"[DEBUG PERMS] User: {agent.username}, ID: {agent.id}, Super: {agent.is_super_admin}, Result: {result}")
    return result

def check_system_admin(agent: Agent, detail: str = "Accès réservé au Super Admin"):
    """Lève une exception si pas Super Admin"""
    if not is_system_admin(agent):
        print(f"[DEBUG PERMS] DENIED For {agent.username} - Detail: {detail}")
        raise HTTPException(status_code=403, detail=detail)

def log_action(db: Session, agent: Agent, action_type: str, entity_type: str, entity_id: int = None, details: str = None):
    """Enregistre une action dans l'historique"""
    try:
        log = ActionLog(
            cabinet_id=agent.cabinet_id,
            agent_id=agent.id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"[ERROR LOGGING] {str(e)}")
        db.rollback()

# ─────────────────────────────────────────────
# CABINETS
# ─────────────────────────────────────────────

@router.get("/cabinets", response_model=List[CabinetOut])
async def list_all_cabinets(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Liste tous les cabinets (Super-Admin uniquement)"""
    check_system_admin(agent, "Accès réservé au Super Admin (LIST)")
    return db.query(Cabinet).all()


@router.post("/cabinets", response_model=CabinetOut)
async def create_cabinet(
    payload: CabinetCreate, 
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Crée un nouveau cabinet (Super-Admin uniquement)"""
    check_system_admin(agent, "Accès réservé au Super Admin (CREATE)")
    
    cabinet = Cabinet(
        nom=payload.nom,
        email=payload.email,
        telephone=payload.telephone,
        adresse=payload.adresse
    )
    
    db.add(cabinet)
    db.commit()
    db.refresh(cabinet)
    
    log_action(db, agent, "CREATE", "CABINET", cabinet.id, f"Cabinet {cabinet.nom} créé")
    
    return cabinet


@router.get("/cabinets/{cabinet_id}", response_model=CabinetOut)
async def get_cabinet(
    cabinet_id: int, 
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Récupère un cabinet par ID"""
    if not is_system_admin(agent) and agent.cabinet_id != cabinet_id:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à ce cabinet")
        
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
    """Met à jour un cabinet (Super-Admin ou Admin de ce cabinet)"""
    if not is_system_admin(agent) and (not agent.is_admin or agent.cabinet_id != cabinet_id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    cabinet = db.query(Cabinet).filter(Cabinet.id == cabinet_id).first()
    if not cabinet:
        raise HTTPException(status_code=404, detail="Cabinet introuvable")
    
    # Un admin de cabinet ne peut modifier que son propre cabinet
    # Un "super-admin" (ex: id=4) pourrait tout modifier. Pour l'instant on check is_admin.
    if not agent.is_super_admin:
        raise HTTPException(status_code=403, detail="Réservé au Super Admin")

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
    """Supprime un cabinet (Super-Admin uniquement)"""
    check_system_admin(agent, "Accès réservé au Super Admin (DELETE)")
    
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
    """Liste les agents (Super-Admin pour tous, Admin pour son cabinet)"""
    if is_system_admin(agent):
        return db.query(Agent).all()
    elif agent.is_admin:
        return db.query(Agent).filter(Agent.cabinet_id == agent.cabinet_id).all()
    else:
        raise HTTPException(status_code=403, detail="Accès refusé (LIST_AGENTS)")


@router.get("/cabinets/{cabinet_id}/agents", response_model=List[AgentOut])
async def list_cabinet_agents(
    cabinet_id: int,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Liste les agents d'un cabinet"""
    if not (agent.is_admin or is_system_admin(agent)):
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
    """Crée un agent (Super-Admin peut tout, Admin restreint à son cabinet)"""
    if not is_system_admin(admin_agent) and (not admin_agent.is_admin or admin_agent.cabinet_id != cabinet_id):
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas créer d'agent pour ce cabinet")
    
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
    
    log_action(db, admin_agent, "CREATE", "AGENT", new_agent.id, f"Agent {new_agent.username} créé")
    
    return new_agent


@router.post("/cabinets/{cabinet_id}/agents/assign-societe")
async def assign_agent_to_societe(
    cabinet_id: int,
    agent_id: int = Query(...),
    societe_id: int = Query(...),
    admin_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Assigne une société à un agent (Super-Admin ou Admin du cabinet)"""
    if not is_system_admin(admin_agent) and (not admin_agent.is_admin or admin_agent.cabinet_id != cabinet_id):
        raise HTTPException(status_code=403, detail="Accès refusé (ASSIGN)")
    
    # Vérifier que l'agent et la société existent et appartiennent au cabinet
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.cabinet_id == cabinet_id).first()
    societe = db.query(Societe).filter(Societe.id == societe_id, Societe.cabinet_id == cabinet_id).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent ID {agent_id} introuvable dans ce cabinet")
    if not societe:
        raise HTTPException(status_code=404, detail=f"Société ID {societe_id} introuvable dans ce cabinet")
    
    # Vérifier si l'association existe déjà
    existing = db.query(agents_societes).filter(
        agents_societes.c.agent_id == agent_id,
        agents_societes.c.societe_id == societe_id
    ).first()
    
    if existing:
        return {"message": "L'agent est déjà assigné à cette société"}

    # Assigner
    try:
        stmt = agents_societes.insert().values(agent_id=agent_id, societe_id=societe_id)
        db.execute(stmt)
        db.commit()
        log_action(db, admin_agent, "ASSOCIATION", "AGENT_SOCIETE", agent_id, f"Agent {agent.username} associé à {societe.raison_sociale}")
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
    """Liste les sociétés (Super-Admin pour toutes, Admin pour son cabinet)"""
    if is_system_admin(agent):
        return db.query(Societe).all()
    elif agent.is_admin:
        return db.query(Societe).filter(Societe.cabinet_id == agent.cabinet_id).all()
    else:
        raise HTTPException(status_code=403, detail="Accès refusé (LIST_SOC)")


@router.post("/societes", response_model=SocieteOut)
async def create_societe_global(
    cabinet_id: int = Query(...),
    payload: SocieteCreateUpdate = ...,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Crée une société (Super-Admin peut tout, Admin restreint à son cabinet)"""
    if not is_system_admin(agent) and (not agent.is_admin or agent.cabinet_id != cabinet_id):
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas créer de société pour ce cabinet")
    
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
    
    log_action(db, agent, "CREATE", "SOCIETE", societe.id, f"Société {societe.raison_sociale} créée")
    
    return societe


@router.put("/societes/{societe_id}", response_model=SocieteOut)
async def update_societe(
    societe_id: int,
    payload: SocieteCreateUpdate,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Met à jour une société"""
    if not (agent.is_admin or is_system_admin(agent)):
        raise HTTPException(status_code=403, detail="Accès refusé (SOC_UPDATE_CHECK)")

    societe = db.query(Societe).filter(Societe.id == societe_id).first()
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")
    
    # Restriction par cabinet pour les Admins
    if not is_system_admin(agent) and agent.cabinet_id != societe.cabinet_id:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette société")
    
    if payload.raison_sociale: societe.raison_sociale = payload.raison_sociale
    if payload.ice: societe.ice = payload.ice
    if payload.if_fiscal: societe.if_fiscal = payload.if_fiscal
    if payload.rc: societe.rc = payload.rc
    if payload.patente: societe.patente = payload.patente
    if payload.adresse: societe.adresse = payload.adresse
    
    db.commit()
    db.refresh(societe)
    return societe


@router.get("/logs", response_model=ActionLogResponse)
async def get_admin_logs(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Récupère l'historique des actions (filtré par cabinet pour les admins)"""
    query = db.query(ActionLog)
    
    if not is_system_admin(agent):
        query = query.filter(ActionLog.cabinet_id == agent.cabinet_id)
    
    total = query.count()
    logs = query.order_by(ActionLog.created_at.desc()).offset(offset).limit(limit).all()
    
    # Enrichir avec les usernames
    result = []
    for log in logs:
        out = ActionLogOut.model_validate(log)
        if log.agent:
            out.agent_username = log.agent.username
        result.append(out)
        
    return {"logs": result, "total": total}


# ─────────────────────────────────────────────
# PROFIL & STATS GLOBALES
# ─────────────────────────────────────────────

@router.get("/stats/global", response_model=GlobalStats)
async def get_global_stats(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Stats globales pour Super Admin, stats filtrées pour Admin"""
    if is_system_admin(agent):
        return {
            "total_cabinets": db.query(Cabinet).count(),
            "total_agents": db.query(Agent).count(),
            "total_societes": db.query(Societe).count(),
            "total_factures": db.query(Facture).count()
        }
    elif agent.is_admin:
        cab_id = agent.cabinet_id
        return {
            "total_cabinets": 1,
            "total_agents": db.query(Agent).filter(Agent.cabinet_id == cab_id, Agent.is_admin == False).count(),
            "total_societes": db.query(Societe).filter(Societe.cabinet_id == cab_id).count(),
            "total_factures": db.query(Facture).join(Societe).filter(Societe.cabinet_id == cab_id).count()
        }
    else:
        raise HTTPException(status_code=403, detail="Accès refusé (STATS)")


@router.put("/profile", response_model=AgentOut)
async def update_admin_profile(
    payload: AgentUpdate,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Met à jour le profil de l'administrateur connecté"""
    if not (agent.is_admin or is_system_admin(agent)):
        raise HTTPException(status_code=403, detail="Accès refusé (PROFILE_UPDATE)")
    
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
    
    if not is_system_admin(agent) and agent.cabinet_id != societe.cabinet_id:
        raise HTTPException(status_code=403, detail="Accès refusé (COMPTEUR)")
    
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
    
    if not is_system_admin(agent) and agent.cabinet_id != societe.cabinet_id:
        raise HTTPException(status_code=403, detail="Accès refusé (COMPTEUR_Y)")
    
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


@router.get("/activities", response_model=ActivitiesResponse)
async def get_recent_activities(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Activités globales pour Super Admin, filtrées par cabinet pour Admin"""
    if not is_system_admin(agent) and not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé (ACTIVITIES)")
    
    activities = []
    
    # 1. Nouveaux cabinets (Seulement pour Super Admin)
    if is_system_admin(agent):
        cabinets = db.query(Cabinet).order_by(Cabinet.created_at.desc()).limit(5).all()
        for cab in cabinets:
            activities.append({
                "id": f"cab_{cab.id}",
                "type": "CABINET",
                "title": f"Nouveau cabinet **{cab.nom}** ajouté au système",
                "time": cab.created_at,
                "dot_color": "blue"
            })
    
    # 2. Factures validées récemment
    query_factures = db.query(Facture).filter(Facture.status == "VALIDATED")
    if not is_system_admin(agent):
        query_factures = query_factures.join(Societe).filter(Societe.cabinet_id == agent.cabinet_id)
    
    factures_validees = query_factures.order_by(Facture.validated_at.desc()).limit(5).all()
    for f in factures_validees:
        soc_nom = f.societe.raison_sociale if f.societe else "Inconnue"
        activities.append({
            "id": f"fac_{f.id}",
            "type": "VALIDATION",
            "title": f"Agent **{f.validated_by or 'Système'}** a validé la facture **{f.numero_facture or 'Sans N°'}** pour **{soc_nom}**",
            "time": f.validated_at or datetime.now(),
            "dot_color": "purple"
        })

    # 3. Nouvelles Sociétés
    query_soc = db.query(Societe)
    if not is_system_admin(agent):
        query_soc = query_soc.filter(Societe.cabinet_id == agent.cabinet_id)
    
    new_societes = query_soc.order_by(Societe.id.desc()).limit(5).all()
    for s in new_societes:
        activities.append({
            "id": f"soc_{s.id}",
            "type": "SOCIETE",
            "title": f"Nouvelle société **{s.raison_sociale}** ajoutée",
            "time": datetime.now(), # Idéalement s.created_at si existait
            "dot_color": "blue"
        })

    # 4. Nouveaux Agents / Administrateurs
    query_agents = db.query(Agent).filter(Agent.id != agent.id)
    if not is_system_admin(agent):
        query_agents = query_agents.filter(Agent.cabinet_id == agent.cabinet_id)
    else:
        # Super Admin voit les nouveaux admins de cabinets
        query_agents = query_agents.filter(Agent.is_admin == True, Agent.is_super_admin == False)
    
    new_agents = query_agents.order_by(Agent.id.desc()).limit(5).all()
    for a in new_agents:
        role = "Administrateur" if a.is_admin else "Agent"
        activities.append({
            "id": f"agent_{a.id}",
            "type": "AGENT",
            "title": f"Nouveau {role} **{a.username}** créé",
            "time": a.created_at or datetime.now(),
            "dot_color": "orange"
        })

    # Conversion des objets time en strings pour le frontend et tri
    # Pour le moment, on trie par ID/Time simulé si pas de created_at parfait
    activities.sort(key=lambda x: x["time"] if isinstance(x["time"], datetime) else datetime.now(), reverse=True)
    
    final_activities = []
    for act in activities[:10]: # Top 10
        # Formater le temps en texte lisible
        t = act["time"]
        time_str = "Récemment"
        if isinstance(t, datetime):
            now = datetime.now()
            diff = now - t
            if diff.days == 0:
                time_str = "Aujourd'hui"
            elif diff.days == 1:
                time_str = "Hier"
            else:
                time_str = f"Il y a {diff.days} jours"
        
        final_activities.append(ActivityOut(
            id=act["id"],
            type=act["type"],
            title=act["title"],
            time=time_str,
            dot_color=act["dot_color"]
        ))
        
    return {"activities": final_activities}
