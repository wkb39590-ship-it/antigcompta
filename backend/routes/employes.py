from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel

from database import get_db
from models import Employe, Societe
from routes.deps import get_current_session

router = APIRouter(prefix="/employes", tags=["employes"])


# ──────────────────────────────────────────────────────────────────────────
# SCHEMAS
# ──────────────────────────────────────────────────────────────────────────
class EmployeBase(BaseModel):
    nom: str
    prenom: Optional[str] = None
    cin: Optional[str] = None
    date_naissance: Optional[date] = None
    poste: Optional[str] = None
    date_embauche: date
    type_contrat: str = "CDI"
    salaire_base: Decimal
    nb_enfants: int = 0
    anciennete_pct: Optional[Decimal] = Decimal("0")
    numero_cnss: Optional[str] = None
    affiliee_cnss: bool = True
    statut: str = "ACTIF"

    model_config = {"from_attributes": True}

class EmployeCreate(EmployeBase):
    pass

class EmployeOut(EmployeBase):
    id: int
    societe_id: int
    created_at: datetime


# ──────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ──────────────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[EmployeOut])
def list_employes(
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Liste tous les employés de la société active."""
    societe_id = context['societe_id']
    print(f"[DEBUG] list_employes call | context_sid: {societe_id} | statut_filter: {statut}")
    query = db.query(Employe).filter(Employe.societe_id == societe_id)
    if statut:
        query = query.filter(Employe.statut == statut)
    
    results = query.order_by(Employe.nom).all()
    print(f"[DEBUG] Found {len(results)} employees for Sid {societe_id}")
    return results


@router.post("/", response_model=EmployeOut)
def create_employe(
    employe: EmployeCreate,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Crée un nouvel employé pour la société active."""
    societe_id = context['societe_id']
    
    # Vérifier l'existence de la société
    soc = db.query(Societe).filter(Societe.id == societe_id).first()
    if not soc:
        raise HTTPException(status_code=404, detail="Société introuvable.")
        
    db_employe = Employe(**employe.dict(), societe_id=societe_id)
    db.add(db_employe)
    db.commit()
    db.refresh(db_employe)
    return db_employe


@router.get("/{employe_id}", response_model=EmployeOut)
def get_employe(
    employe_id: int,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Retourne le détail d'un employé."""
    societe_id = context['societe_id']
    emp = db.query(Employe).filter(Employe.id == employe_id, Employe.societe_id == societe_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employé introuvable.")
    return emp


@router.put("/{employe_id}", response_model=EmployeOut)
def update_employe(
    employe_id: int,
    employe: EmployeCreate,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Met à jour un employé existant."""
    societe_id = context['societe_id']
    db_employe = db.query(Employe).filter(Employe.id == employe_id, Employe.societe_id == societe_id).first()
    if not db_employe:
        raise HTTPException(status_code=404, detail="Employé introuvable.")
        
    for key, value in employe.dict().items():
        setattr(db_employe, key, value)
        
    db.commit()
    db.refresh(db_employe)
    return db_employe
