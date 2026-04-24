from fastapi import APIRouter, Depends, HTTPException, status
import difflib
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import DemandeAcces, ActionLog
from schemas import DemandeAccesCreate, DemandeAccesOut, DemandeAccesValidation, DemandeAccesUpdate
from routes.auth import get_current_agent

router = APIRouter(prefix="/demandes-acces", tags=["Access Requests"])

@router.post("/", response_model=DemandeAccesOut, status_code=status.HTTP_201_CREATED)
def create_demande_acces(payload: DemandeAccesCreate, db: Session = Depends(get_db)):
    """
    Endpoint public pour soumettre une demande d'accès.
    """
    cabinet_to_assign = payload.cabinet_id
    
    if cabinet_to_assign is None and payload.nom_cabinet:
        from models import Cabinet
        cabinets = db.query(Cabinet).all()
        cab_names = [c.nom for c in cabinets]
        # Recherche tolérante aux fautes de frappe avec difflib
        matches = difflib.get_close_matches(payload.nom_cabinet, cab_names, n=1, cutoff=0.5)
        if matches:
            matched_cab = next(c for c in cabinets if c.nom == matches[0])
            cabinet_to_assign = matched_cab.id

    new_demande = DemandeAcces(
        nom_complet=payload.nom_complet,
        entreprise=payload.entreprise,
        email=payload.email,
        telephone=payload.telephone,
        message=payload.message,
        cabinet_id=cabinet_to_assign
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


@router.get("/cabinets", response_model=List[dict])
def list_public_cabinets(db: Session = Depends(get_db)):
    """Retourne la liste des cabinets pour le formulaire de demande d'accès public"""
    from models import Cabinet
    cabinets = db.query(Cabinet.id, Cabinet.nom).all()
    return [{"id": c.id, "nom": c.nom} for c in cabinets]


@router.patch("/{demande_id}/statut", response_model=DemandeAccesOut)
def update_statut_demande(
    demande_id: int,
    payload: DemandeAccesValidation,
    db: Session = Depends(get_db),
    current_agent = Depends(get_current_agent)
):
    """
    Met à jour le statut d'une demande (traitee, rejetee, etc.)
    Si statut=traitee, crée automatiquement la Societe et l'UtilisateurClient.
    """
    from models import Societe, UtilisateurClient
    from routes.auth import hash_password

    if not current_agent.is_admin and not current_agent.is_super_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")

    demande = db.query(DemandeAcces).filter(DemandeAcces.id == demande_id).first()
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    # Sécurité : seul l'admin du cabinet peut gérer les demandes de son cabinet
    if current_agent.is_super_admin and demande.cabinet_id is not None:
        raise HTTPException(status_code=403, detail="Le Super Admin ne peut pas gérer les demandes destinées aux cabinets.")

    if not current_agent.is_super_admin and demande.cabinet_id != current_agent.cabinet_id:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette demande")

    demande.statut = payload.statut

    # Provisionnement auto lors de l'acceptation
    generated_username = None
    generated_password = None

    if payload.statut == 'traitee' and payload.username and payload.password:
        # Vérifier que le username n'existe pas déjà
        existing = db.query(UtilisateurClient).filter(UtilisateurClient.username == payload.username).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Le nom d'utilisateur '{payload.username}' est déjà pris.")

        # Créer la Société si elle n'existe pas
        societe = db.query(Societe).filter(
            Societe.raison_sociale == demande.entreprise,
            Societe.cabinet_id == demande.cabinet_id
        ).first()
        if not societe:
            societe = Societe(
                raison_sociale=demande.entreprise,
                cabinet_id=demande.cabinet_id
            )
            db.add(societe)
            db.flush()  # Obtenir l'id sans commit

        # Créer le compte UtilisateurClient
        new_client = UtilisateurClient(
            societe_id=societe.id,
            username=payload.username,
            email=demande.email,
            nom=demande.nom_complet.split(' ', 1)[-1] if ' ' in demande.nom_complet else '',
            prenom=demande.nom_complet.split(' ', 1)[0],
            password_hash=hash_password(payload.password),
            is_active=True
        )
        db.add(new_client)
        generated_username = payload.username
        generated_password = payload.password

    db.commit()
    db.refresh(demande)

    # Log de l'action admin
    try:
        from routes.admin import log_action
        log_action(db, current_agent, "UPDATE", "DEMANDE_ACCES", demande.id,
                   f"Demande d'accès de {demande.nom_complet} marquée comme {payload.statut}" +
                   (f" — Compte créé: {generated_username}" if generated_username else ""))
    except Exception as e:
        print(f"[LOG ERROR] {e}")

    # Construire la réponse avec les credentials générés
    result = DemandeAccesOut.model_validate(demande)
    result.generated_username = generated_username
    result.generated_password = generated_password
    return result


@router.put("/{demande_id}", response_model=DemandeAccesOut)
def update_demande_acces(
    demande_id: int,
    payload: DemandeAccesUpdate,
    db: Session = Depends(get_db),
    current_agent = Depends(get_current_agent)
):
    """
    Modifie les informations d'une demande d'accès existante.
    """
    if not current_agent.is_admin and not current_agent.is_super_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")

    demande = db.query(DemandeAcces).filter(DemandeAcces.id == demande_id).first()
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    if not current_agent.is_super_admin and demande.cabinet_id != current_agent.cabinet_id:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette demande")

    if payload.nom_complet is not None:
        demande.nom_complet = payload.nom_complet
    if payload.entreprise is not None:
        demande.entreprise = payload.entreprise
    if payload.email is not None:
        demande.email = payload.email
    if payload.telephone is not None:
        demande.telephone = payload.telephone
    if payload.message is not None:
        demande.message = payload.message

    db.commit()
    db.refresh(demande)

    try:
        from routes.admin import log_action
        log_action(db, current_agent, "UPDATE", "DEMANDE_ACCES", demande.id,
                   f"Modification de la demande d'accès de {demande.nom_complet}")
    except Exception as e:
        print(f"[LOG ERROR] {e}")

    return demande


@router.delete("/{demande_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_demande_acces(
    demande_id: int,
    db: Session = Depends(get_db),
    current_agent = Depends(get_current_agent)
):
    """
    Supprime définitivement une demande d'accès.
    """
    if not current_agent.is_admin and not current_agent.is_super_admin:
        raise HTTPException(status_code=403, detail="Accès refusé")

    demande = db.query(DemandeAcces).filter(DemandeAcces.id == demande_id).first()
    if not demande:
        raise HTTPException(status_code=404, detail="Demande non trouvée")

    if not current_agent.is_super_admin and demande.cabinet_id != current_agent.cabinet_id:
        raise HTTPException(status_code=403, detail="Vous n'avez pas accès à cette demande")

    nom = demande.nom_complet
    db.delete(demande)
    db.commit()

    try:
        from routes.admin import log_action
        log_action(db, current_agent, "DELETE", "DEMANDE_ACCES", demande_id,
                   f"Suppression de la demande d'accès de {nom}")
    except Exception as e:
        print(f"[LOG ERROR] {e}")
