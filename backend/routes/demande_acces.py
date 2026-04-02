from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import DemandeAcces, ActionLog
from schemas import DemandeAccesCreate, DemandeAccesOut
from routes.auth import get_current_agent

router = APIRouter(prefix="/demandes-acces", tags=["Access Requests"])

@router.post("/", response_model=DemandeAccesOut, status_code=status.HTTP_201_CREATED)
def create_demande_acces(payload: DemandeAccesCreate, db: Session = Depends(get_db)):
    """
    Endpoint public pour soumettre une demande d'accès.
    """
    new_demande = DemandeAcces(
        nom_complet=payload.nom_complet,
        entreprise=payload.entreprise,
        email=payload.email,
        telephone=payload.telephone,
        message=payload.message,
        cabinet_id=payload.cabinet_id
    )
    db.add(new_demande)
    db.commit()
    db.refresh(new_demande)

    # Log de la demande (Source publique -> agent_id=None)
    try:
        log = ActionLog(
            cabinet_id=new_demande.cabinet_id,
            agent_id=None,
            action_type="CREATE",
            entity_type="DEMANDE_ACCES",
            entity_id=new_demande.id,
            details=f"Nouvelle demande d'accès : {new_demande.nom_complet} ({new_demande.entreprise})"
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"[LOG ERROR] {e}")
        db.rollback()

    return new_demande

@router.get("/", response_model=List[DemandeAccesOut])
def list_demandes_acces(
    db: Session = Depends(get_db),
    current_agent = Depends(get_current_agent) # Protégé
):
    """
    Récupère la liste des demandes (pour les admins).
    """
    if not current_agent.is_admin and not current_agent.is_super_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
        
    query = db.query(DemandeAcces)
    if not current_agent.is_super_admin:
        # Un admin de cabinet ne voit que ses demandes
        query = query.filter(DemandeAcces.cabinet_id == current_agent.cabinet_id)
        
    return query.order_by(DemandeAcces.created_at.desc()).all()

@router.patch("/{demande_id}/statut", response_model=DemandeAccesOut)
def update_statut_demande(
    demande_id: int,
    statut: str,
    db: Session = Depends(get_db),
    current_agent = Depends(get_current_agent)
):
    """
    Met à jour le statut d'une demande (traitee, rejetee, etc.)
    """
    if not current_agent.is_admin and not current_agent.is_super_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
        
    demande = db.query(DemandeAcces).filter(DemandeAcces.id == demande_id).first()
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
        
    # Sécurité : vérifier que l'admin a le droit de modifier cette demande
    # Le Super Admin ne peut pas modifier les demandes liées à un cabinet (rôle restreint au Cabinet Admin)
    # Il ne peut gérer que les demandes sans cabinet (prospects pour la plateforme)
    if current_agent.is_super_admin and demande.cabinet_id is not None:
         raise HTTPException(status_code=403, detail="Le Super Admin ne peut pas gérer les demandes destinées aux cabinets. Seul l'admin du cabinet peut le faire.")

    if not current_agent.is_super_admin and demande.cabinet_id != current_agent.cabinet_id:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette demande")
        
    demande.statut = statut
    db.commit()
    db.refresh(demande)

    # Log de l'action admin
    try:
        from routes.admin import log_action
        log_action(db, current_agent, "UPDATE", "DEMANDE_ACCES", demande.id, f"Demande d'accès de {demande.nom_complet} marquée comme {statut}")
    except Exception as e:
        print(f"[LOG ERROR] {e}")

    return demande
