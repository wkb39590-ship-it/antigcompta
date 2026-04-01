from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import UtilisateurClient, Societe, DocumentTransmis
from schemas import UtilisateurClientOut, AgentLogin
from routes.auth import hash_password, verify_password, create_jwt_token, decode_jwt_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from fastapi import Query
from pydantic import BaseModel as PydanticBase

router = APIRouter(prefix="/client", tags=["Client Portal"])

security = HTTPBearer(auto_error=False)

class ClientProfileUpdate(PydanticBase):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[str] = None

class ClientPasswordChange(PydanticBase):
    old_password: str
    new_password: str

def get_current_client(
    token: Optional[str] = Query(None),
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> UtilisateurClient:
    actual_token = token
    if auth:
        actual_token = auth.credentials
    if not actual_token:
        raise HTTPException(status_code=401, detail="Token manquant")
    data = decode_jwt_token(actual_token)
    if data.get("role") != "client":
        raise HTTPException(status_code=403, detail="Accès réservé aux clients")
        
    client = db.query(UtilisateurClient).filter(UtilisateurClient.id == data.get("client_id")).first()
    if not client:
        raise HTTPException(status_code=401, detail="Client introuvable")
    return client

@router.post("/login")
async def client_login(payload: AgentLogin, db: Session = Depends(get_db)):
    client = db.query(UtilisateurClient).filter(UtilisateurClient.username == payload.username).first()
    
    if not client or not verify_password(payload.password, client.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")
        
    if not client.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé")
        
    token_data = {
        "client_id": client.id,
        "societe_id": client.societe_id,
        "username": client.username,
        "role": "client"
    }
    access_token = create_jwt_token(token_data)
    
    societe = db.query(Societe).filter(Societe.id == client.societe_id).first()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "client": UtilisateurClientOut.model_validate(client),
        "societe_nom": societe.raison_sociale if societe else ""
    }

@router.get("/me", response_model=UtilisateurClientOut)
async def get_client_profile(client: UtilisateurClient = Depends(get_current_client)):
    return client

@router.put("/me", response_model=UtilisateurClientOut)
async def update_client_profile(
    payload: ClientProfileUpdate,
    client: UtilisateurClient = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Mise à jour du profil client (nom, prénom, email)."""
    if payload.nom is not None:
        client.nom = payload.nom
    if payload.prenom is not None:
        client.prenom = payload.prenom
    if payload.email is not None:
        existing = db.query(UtilisateurClient).filter(
            UtilisateurClient.email == payload.email,
            UtilisateurClient.id != client.id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
        client.email = payload.email
    db.commit()
    db.refresh(client)
    return client

@router.post("/me/password")
async def change_client_password(
    payload: ClientPasswordChange,
    client: UtilisateurClient = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Changement de mot de passe client."""
    if not verify_password(payload.old_password, client.password_hash):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect.")
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit contenir au moins 6 caractères.")
    client.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"message": "Mot de passe mis à jour avec succès."}
