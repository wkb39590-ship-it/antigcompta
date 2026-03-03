from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from database import get_db
from models import Employe, BulletinPaie
from schemas import BulletinPaieOut, BulletinPaieCreate
from services.paie_service import calculer_bulletin, sauvegarder_bulletin, generer_ecriture_paie
from routes.deps import get_current_session

router = APIRouter(prefix="/paie", tags=["paie"])

@router.get("/", response_model=List[BulletinPaieOut])
def list_bulletins(
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Liste tous les bulletins de la société active."""
    societe_id = context['societe_id']
    bulletins = db.query(BulletinPaie).join(Employe).filter(
        Employe.societe_id == societe_id
    ).order_by(BulletinPaie.annee.desc(), BulletinPaie.mois.desc()).all()
    
    # Enrichir avec le nom de l'employé
    for b in bulletins:
        b.employe_nom = f"{b.employe.prenom or ''} {b.employe.nom}".strip()
    
    return bulletins

@router.post("/calcul", response_model=BulletinPaieOut)
def simuler_calcul(
    req: BulletinPaieCreate,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Calcule un bulletin sans le sauvegarder (simulation)."""
    from datetime import datetime
    societe_id = context['societe_id']
    employe = db.query(Employe).filter(
        Employe.id == req.employe_id, 
        Employe.societe_id == societe_id
    ).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé introuvable dans cette société.")
    
    res = calculer_bulletin(
        employe=employe,
        mois=req.mois,
        annee=req.annee,
        primes=Decimal(str(req.primes or 0)),
        heures_sup=Decimal(str(req.heures_sup or 0))
    )
    
    # Ajouter les champs requis par BulletinPaieOut (simulation, non persistée)
    res["id"] = 0
    res["statut"] = "BROUILLON"
    res["created_at"] = datetime.now()
    # Ajouter un id fictif à chaque ligne (requis par LignePaieOut)
    for i, ligne in enumerate(res.get("lignes", [])):
        ligne["id"] = i + 1
    
    return BulletinPaieOut(**res)

@router.post("/", response_model=BulletinPaieOut)
def creer_bulletin(
    req: BulletinPaieCreate,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Calcule et sauvegarde un bulletin en base."""
    societe_id = context['societe_id']
    employe = db.query(Employe).filter(
        Employe.id == req.employe_id, 
        Employe.societe_id == societe_id
    ).first()
    
    if not employe:
        raise HTTPException(status_code=404, detail="Employé introuvable.")
        
    # Vérifier si un bulletin existe déjà pour ce mois/année
    existant = db.query(BulletinPaie).filter(
        BulletinPaie.employe_id == req.employe_id,
        BulletinPaie.mois == req.mois,
        BulletinPaie.annee == req.annee
    ).first()
    
    if existant:
        raise HTTPException(status_code=400, detail="Un bulletin existe déjà pour cet employé ce mois-ci.")

    bulletin = sauvegarder_bulletin(
        employe=employe,
        mois=req.mois,
        annee=req.annee,
        primes=Decimal(str(req.primes or 0)),
        heures_sup=Decimal(str(req.heures_sup or 0)),
        db=db
    )
    
    bulletin.employe_nom = f"{employe.prenom or ''} {employe.nom}".strip()
    return bulletin

@router.get("/{bulletin_id}", response_model=BulletinPaieOut)
def get_bulletin(
    bulletin_id: int,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Récupère le détail d'un bulletin."""
    societe_id = context['societe_id']
    bulletin = db.query(BulletinPaie).join(Employe).filter(
        BulletinPaie.id == bulletin_id,
        Employe.societe_id == societe_id
    ).first()
    
    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin introuvable.")
    
    bulletin.employe_nom = f"{bulletin.employe.prenom or ''} {bulletin.employe.nom}".strip()
    return bulletin

@router.post("/{bulletin_id}/validate", response_model=BulletinPaieOut)
def valider_bulletin(
    bulletin_id: int,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Valide le bulletin et génère l'écriture comptable OD."""
    societe_id = context['societe_id']
    bulletin = db.query(BulletinPaie).join(Employe).filter(
        BulletinPaie.id == bulletin_id,
        Employe.societe_id == societe_id
    ).first()
    
    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin introuvable.")
    
    if bulletin.statut == "VALIDE":
        raise HTTPException(status_code=400, detail="Bulletin déjà validé.")
        
    # Mise à jour statut
    bulletin.statut = "VALIDE"
    bulletin.valide_par = context.get('username', 'system')
    from datetime import datetime
    bulletin.valide_at = datetime.now()
    
    # Génération écriture
    generer_ecriture_paie(bulletin, db)
    
    db.commit()
    db.refresh(bulletin)
    bulletin.employe_nom = f"{bulletin.employe.prenom or ''} {bulletin.employe.nom}".strip()
    return bulletin
