from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import UtilisateurClient, Societe
from schemas import UtilisateurClientCreate, UtilisateurClientOut, AgentLogin
from routes.auth import hash_password, verify_password, create_jwt_token, decode_jwt_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from fastapi import Query

router = APIRouter(prefix="/client", tags=["Client Portal"])

security = HTTPBearer(auto_error=False)

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
