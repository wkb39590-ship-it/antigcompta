"""
routes/auth.py - Authentification et gestion de session multi-cabinet
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from database import get_db
from models import Cabinet, Agent, Societe, Facture, agent_societes
from schemas import (
    AgentCreate, AgentLogin, AgentLoginResponse,
    AgentOut, CabinetOut, SocieteOut,
    SelectSocieteRequest, SessionContext, AgentStats
)


router = APIRouter(prefix="/auth", tags=["Authentication"])

# ─────────────────────────────────────────────
# Utilitaires
# ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hache un mot de passe avec PBKDF2"""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, pwd_hash: str) -> bool:
    """Vérifie un mot de passe contre son hash"""
    try:
        salt, hash_part = pwd_hash.split('$')
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return computed_hash.hex() == hash_part
    except:
        return False


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un JWT token simple (à remplacer par PyJWT en production)"""
    import json
    import base64
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=8)
    
    data.update({"exp": expire.isoformat()})
    token = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    return token


def decode_jwt_token(token: str) -> dict:
    """Décode un JWT token simple"""
    import json
    import base64
    
    try:
        data = json.loads(base64.urlsafe_b64decode(token).decode())
        exp = datetime.fromisoformat(data.get("exp", ""))
        if exp < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expiré")
        return data
    except:
        raise HTTPException(status_code=401, detail="Token invalide")


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer(auto_error=False)

def get_current_agent(
    token: Optional[str] = Query(None),
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Agent:
    """Valide le token JWT (depuis Header ou Query) et retourne l'Agent courant"""
    actual_token = token
    if auth:
        actual_token = auth.credentials
        
    if not actual_token:
        raise HTTPException(status_code=401, detail="Token manquant")
        
    data = decode_jwt_token(actual_token)
    agent = db.query(Agent).filter(Agent.id == data.get("agent_id")).first()
    if not agent or not agent.is_active:
        raise HTTPException(status_code=401, detail="Agent non trouvé ou inactif")
    return agent


# ─────────────────────────────────────────────
# Routes d'authentification
# ─────────────────────────────────────────────

@router.post("/login", response_model=AgentLoginResponse)
async def login(payload: AgentLogin, db: Session = Depends(get_db)):
    """
    Authentifie un agent et retourne un JWT token + liste des cabinets
    
    Flux:
    1. Chercher l'agent par username
    2. Vérifier le mot de passe
    3. Retourner token + cabinets accessibles
    """
    agent = db.query(Agent).filter(Agent.username == payload.username).first()
    
    if not agent or not verify_password(payload.password, agent.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides"
        )
    
    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent désactivé"
        )
    
    # Créer le token JWT
    token_data = {
        "agent_id": agent.id,
        "cabinet_id": agent.cabinet_id,
        "username": agent.username,
        "is_admin": agent.is_admin
    }
    access_token = create_jwt_token(token_data)
    
    # Récupérer le cabinet
    cabinet = db.query(Cabinet).filter(Cabinet.id == agent.cabinet_id).first()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "agent": agent,
        "cabinets": [cabinet] if cabinet else []
    }


@router.post("/register", response_model=AgentOut)
async def register_agent(
    cabinet_id: int = Query(...),
    payload: AgentCreate = ...,
    db: Session = Depends(get_db)
):
    """
    Enregistre un nouvel agent dans un cabinet
    Seul un Admin peut créer des agents
    """
    # Vérifier que le cabinet existe
    cabinet = db.query(Cabinet).filter(Cabinet.id == cabinet_id).first()
    if not cabinet:
        raise HTTPException(status_code=404, detail="Cabinet introuvable")
    
    # Vérifier que l'username/email ne existe pas déjà
    existing = db.query(Agent).filter(
        (Agent.username == payload.username) | (Agent.email == payload.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username ou email déjà utilisé")
    
    # Créer le nouvel agent
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


@router.post("/select-societe")
async def select_societe(
    payload: SelectSocieteRequest,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
) -> dict:
    """
    Permet à l'agent de choisir une société et créer son contexte de session
    
    Réponse:
    {
        "session_token": "...",
        "societe": SocieteOut,
        "context": SessionContext
    }
    """
    # Valider l'agent (déjà fait par la dépendance agent)
    
    # ✅ VÉRIFICATION CRITIQUE: L'agent ne peut sélectionner que dans SON cabinet
    if agent.cabinet_id != payload.cabinet_id:
        raise HTTPException(status_code=403, detail="Cabinet non autorisé")
    
    # Vérifier que la société appartient au cabinet
    societe = db.query(Societe).filter(
        Societe.id == payload.societe_id,
        Societe.cabinet_id == payload.cabinet_id
    ).first()
    
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")
    
    # Vérifier que l'agent a accès à cette société
    has_access = db.query(agent_societes).filter(
        agent_societes.c.agent_id == agent.id,
        agent_societes.c.societe_id == societe.id
    ).first()
    
    if not has_access and not agent.is_admin:
        raise HTTPException(status_code=403, detail="Accès refusé à cette société")
    
    # Créer un nouveau token avec le contexte societe
    session_data = {
        "agent_id": agent.id,
        "cabinet_id": payload.cabinet_id,
        "societe_id": payload.societe_id,
        "username": agent.username,
        "societe_raison_sociale": societe.raison_sociale
    }
    session_token = create_jwt_token(session_data)
    
    return {
        "session_token": session_token,
        "societe": SocieteOut.model_validate(societe),
        "context": SessionContext(**session_data)
    }


@router.get("/me", response_model=AgentOut)
async def get_current_user(agent: Agent = Depends(get_current_agent)):
    """Retourne l'agent actuel"""
    return agent


@router.get("/stats", response_model=AgentStats)
async def get_agent_stats(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """Calcule les statistiques pour l'agent courant"""
    # Nombre de factures validées par cet agent
    total_validees = db.query(Facture).filter(Facture.validated_by == agent.username).count()
    
    # Nombre de sociétés associées à cet agent
    total_societes = len(agent.societes)
    
    return {
        "total_factures_validees": total_validees,
        "total_societes_gerees": total_societes,
        "cabinet_nom": agent.cabinet.nom if agent.cabinet else "Sans cabinet"
    }



@router.post("/logout")
async def logout():
    """
    Logout (client-side: supprimer le token du localStorage)
    """
    return {"message": "Déconnexion réussie"}


@router.get("/societes", response_model=list[SocieteOut])
async def list_societes(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Lister les sociétés accessibles par l'agent (dans son cabinet)
    Si admin: toutes les sociétés du cabinet
    Sinon: sociétés assignées à l'agent
    """
    query = db.query(Societe).filter(Societe.cabinet_id == agent.cabinet_id)
    
    if not agent.is_admin:
        # Filtrer par les sociétés assignées à cet agent
        query = query.join(agent_societes).filter(agent_societes.c.agent_id == agent.id)
    
    societes = query.all()
    return societes
