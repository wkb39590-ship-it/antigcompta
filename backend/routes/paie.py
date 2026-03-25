from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from database import get_db
from models import Employe, BulletinPaie, JournalEntry
from schemas import BulletinPaieOut, BulletinPaieCreate
from services.paie_service import calculer_bulletin, sauvegarder_bulletin, generer_ecriture_paie
from services.pdf_service import generer_bulletin_pdf
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
    
    # Enrichir avec les infos employeur et employé
    for b in bulletins:
        emp = b.employe
        soc = emp.societe if emp else None
        b.employe_nom = f"{emp.prenom or ''} {emp.nom}".strip() if emp else "Inconnu"
        if emp:
            b.employe_cin = emp.cin
            b.employe_cnss = emp.numero_cnss
            b.employe_date_embauche = emp.date_embauche
        if soc:
            b.societe_nom = soc.raison_sociale
            b.societe_adresse = soc.adresse
            b.societe_ice = soc.ice
            b.societe_rc = soc.rc
            b.societe_cnss = soc.cnss
    
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
    # Ajouter les infos employeur et employé pour BulletinPaieOut
    res["employe_nom"] = f"{employe.prenom or ''} {employe.nom}".strip()
    res["employe_cin"] = employe.cin
    res["employe_cnss"] = employe.numero_cnss
    res["employe_date_embauche"] = employe.date_embauche
    
    soc = employe.societe
    if soc:
        res["societe_nom"] = soc.raison_sociale
        res["societe_adresse"] = soc.adresse
        res["societe_ice"] = soc.ice
        res["societe_rc"] = soc.rc
        res["societe_cnss"] = soc.cnss
    
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
    
    emp = bulletin.employe
    soc = emp.societe if emp else None
    bulletin.employe_nom = f"{emp.prenom or ''} {emp.nom}".strip() if emp else "Inconnu"
    if emp:
        bulletin.employe_cin = emp.cin
        bulletin.employe_cnss = emp.numero_cnss
        bulletin.employe_date_embauche = emp.date_embauche
    if soc:
        bulletin.societe_nom = soc.raison_sociale
        bulletin.societe_adresse = soc.adresse
        bulletin.societe_ice = soc.ice
        bulletin.societe_rc = soc.rc
        bulletin.societe_cnss = soc.cnss
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
    
    # bulletin.statut = "VALIDE"
    # generer_ecriture_paie(bulletin, db)
    # NOTE: Saisie manuelle demandée par l'utilisateur dans le Journal Comptable
    
    db.commit()
    db.refresh(bulletin)
    emp = bulletin.employe
    soc = emp.societe if emp else None
    bulletin.employe_nom = f"{emp.prenom or ''} {emp.nom}".strip() if emp else "Inconnu"
    if emp:
        bulletin.employe_cin = emp.cin
        bulletin.employe_cnss = emp.numero_cnss
        bulletin.employe_date_embauche = emp.date_embauche
    if soc:
        bulletin.societe_nom = soc.raison_sociale
        bulletin.societe_adresse = soc.adresse
        bulletin.societe_ice = soc.ice
        bulletin.societe_rc = soc.rc
        bulletin.societe_cnss = soc.cnss
    return bulletin

@router.get("/{bulletin_id}/entries", response_model=dict)
def get_bulletin_entries(
    bulletin_id: int,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Récupère les écritures comptables associées à un bulletin."""
    societe_id = context['societe_id']
    bulletin = db.query(BulletinPaie).join(Employe).filter(
        BulletinPaie.id == bulletin_id,
        Employe.societe_id == societe_id
    ).first()
    
    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin introuvable.")
        
    if not bulletin.journal_entry_id:
        return {"journal_entry": None, "message": "Aucune écriture associée (bulletin non validé ?)"}
        
    entry = db.query(JournalEntry).filter(JournalEntry.id == bulletin.journal_entry_id).first()
    if not entry:
        return {"journal_entry": None, "message": "Écriture introuvable."}
        
    return {
        "journal_entry": {
            "id": entry.id,
            "journal_code": entry.journal_code,
            "entry_date": str(entry.entry_date) if entry.entry_date else None,
            "reference": entry.reference,
            "description": entry.description,
            "is_validated": entry.is_validated,
            "total_debit": float(entry.total_debit) if entry.total_debit else 0,
            "total_credit": float(entry.total_credit) if entry.total_credit else 0,
            "entry_lines": [
                {
                    "id": el.id,
                    "line_order": el.line_order,
                    "account_code": el.account_code,
                    "account_label": el.account_label,
                    "debit": float(el.debit),
                    "credit": float(el.credit),
                    "tiers_name": el.tiers_name,
                    "tiers_ice": el.tiers_ice,
                }
                for el in sorted(entry.entry_lines, key=lambda e: e.line_order or 0)
            ]
        }
    }

@router.get("/{bulletin_id}/pdf")
def telecharger_bulletin_pdf(
    bulletin_id: int,
    db: Session = Depends(get_db),
    context: dict = Depends(get_current_session)
):
    """Génère et retourne le bulletin de paie en PDF professionnel."""
    societe_id = context['societe_id']
    bulletin = db.query(BulletinPaie).join(Employe).filter(
        BulletinPaie.id == bulletin_id,
        Employe.societe_id == societe_id
    ).first()

    if not bulletin:
        raise HTTPException(status_code=404, detail="Bulletin introuvable.")

    employe = bulletin.employe
    societe = employe.societe if employe else None

    pdf_bytes = generer_bulletin_pdf(bulletin, employe, societe)

    nom = f"{getattr(employe, 'prenom', '') or ''} {getattr(employe, 'nom', '') or ''}".strip().replace(" ", "_")
    filename = f"Bulletin_Paie_{nom}_{bulletin.mois:02d}_{bulletin.annee}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
