from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import SupplierMapping, PcmAccount
from routes.deps import get_current_session
from typing import List
from schemas import SupplierMappingCreate

router = APIRouter(prefix="/mappings", tags=["mappings"])

@router.get("/", response_model=List[dict])
def list_mappings(db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Liste tous les mappings appris par le cabinet actuel."""
    cabinet_id = session.get("cabinet_id")
    if not cabinet_id:
        raise HTTPException(400, "Cabinet ID manquant dans la session")
        
    mappings = db.query(SupplierMapping).filter(SupplierMapping.cabinet_id == cabinet_id).all()
    
    result = []
    for m in mappings:
        # Enrichir avec les infos du compte PCM
        account = db.query(PcmAccount).filter(PcmAccount.code == m.pcm_account_code).first()
        result.append({
            "id": m.id,
            "supplier_ice": m.supplier_ice,
            "pcm_account_code": m.pcm_account_code,
            "pcm_account_label": account.label if account else "Compte inconnu",
            "updated_at": m.updated_at
        })
    return result

@router.post("/", response_model=dict)
def create_mapping(
    data: SupplierMappingCreate, 
    db: Session = Depends(get_db), 
    session: dict = Depends(get_current_session)
):
    """Crée ou met à jour un mapping fournisseur."""
    cabinet_id = session.get("cabinet_id")
    if not cabinet_id:
        raise HTTPException(400, "Cabinet ID manquant dans la session")
        
    # Vérifier si le compte PCM existe
    account = db.query(PcmAccount).filter(PcmAccount.code == data.pcm_account_code).first()
    if not account:
        raise HTTPException(400, f"Compte PCM {data.pcm_account_code} introuvable")

    # Chercher si un mapping existe déjà pour ce cabinet et cet ICE
    mapping = db.query(SupplierMapping).filter(
        SupplierMapping.cabinet_id == cabinet_id,
        SupplierMapping.supplier_ice == data.supplier_ice
    ).first()
    
    if mapping:
        mapping.pcm_account_code = data.pcm_account_code
    else:
        mapping = SupplierMapping(
            cabinet_id=cabinet_id,
            supplier_ice=data.supplier_ice,
            pcm_account_code=data.pcm_account_code
        )
        db.add(mapping)
    
    db.commit()
    return {"message": "Mapping enregistré", "id": mapping.id}

@router.delete("/{mapping_id}")
def delete_mapping(mapping_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Supprime un mapping appris."""
    cabinet_id = session.get("cabinet_id")
    mapping = db.query(SupplierMapping).filter(
        SupplierMapping.id == mapping_id,
        SupplierMapping.cabinet_id == cabinet_id
    ).first()
    
    if not mapping:
        raise HTTPException(404, "Mapping introuvable")
        
    db.delete(mapping)
    db.commit()
    return {"message": "Mapping supprimé"}
