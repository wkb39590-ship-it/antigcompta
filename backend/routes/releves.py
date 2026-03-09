"""
routes/releves.py — Gestion des relevés bancaires
"""
import os
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import ReleveBancaire, LigneReleve, JournalEntry, EntryLine
from routes.deps import get_current_session
from services.gemini_service import extract_bank_statement, classify_bank_transaction
from services.pdf_utils import pdf_to_png_images_bytes

router = APIRouter(prefix="/releves", tags=["releves"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".csv", ".xlsx"]

def _guess_mime(path: str) -> str:
    ext = Path(path).suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".pdf": "application/pdf"
    }.get(ext, "application/octet-stream")

def _get_image_data(file_path: str):
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        images = pdf_to_png_images_bytes(file_path, dpi=300, max_pages=10)
        if not images:
            raise HTTPException(500, "Impossible de convertir le PDF en images")
        return images, "image/png"
    with open(file_path, "rb") as f:
        return f.read(), _guess_mime(file_path)

@router.post("/upload")
def upload_releve(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """
    Uploade un relevé et lance l'extraction si c'est une image/PDF.
    """
    societe_id = session.get("societe_id")
    if not societe_id:
        raise HTTPException(400, "Veuillez sélectionner une société")

    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, f"Extension non supportée: {ext}")
    
    data = file.file.read()
    if not data:
        raise HTTPException(400, "Fichier vide")
    
    # Save file
    file_hash = hashlib.sha256(data).hexdigest()
    name = f"{uuid.uuid4()}{ext}"
    dest = UPLOAD_DIR / name
    with open(dest, "wb") as f:
        f.write(data)

    # Check for duplicates
    dup = db.query(ReleveBancaire).filter(
        ReleveBancaire.societe_id == societe_id,
        ReleveBancaire.file_name == file.filename
    ).first()
    if dup:
        os.remove(dest)
        raise HTTPException(409, "Ce fichier a déjà été importé pour cette société.")

    # Create Releve
    releve = ReleveBancaire(
        societe_id=societe_id,
        file_path=str(dest),
        file_name=file.filename
    )
    db.add(releve)
    db.commit()
    db.refresh(releve)

    # Process extraction if PDF/Image
    if ext in [".pdf", ".png", ".jpg", ".jpeg"]:
        try:
            image_data, mime_type = _get_image_data(str(dest))
            extracted_data = extract_bank_statement(image_data, mime_type=mime_type)
            
            # Update releve header
            from utils.parsers import parse_date_fr
            releve.date_debut = parse_date_fr(extracted_data.get("date_debut"))
            releve.date_fin = parse_date_fr(extracted_data.get("date_fin"))
            releve.solde_initial = extracted_data.get("solde_initial")
            releve.solde_final = extracted_data.get("solde_final")
            releve.banque_nom = extracted_data.get("banque_nom")
            releve.compte_bancaire = extracted_data.get("compte_bancaire")

            # Create lines
            lignes_data = extracted_data.get("lignes", [])
            for row in lignes_data:
                ligne = LigneReleve(
                    releve_id=releve.id,
                    date_operation=parse_date_fr(row.get("date_operation")) or datetime.today(),
                    date_valeur=parse_date_fr(row.get("date_valeur")),
                    description=row.get("description"),
                    reference=row.get("reference"),
                    debit=row.get("debit") or 0,
                    credit=row.get("credit") or 0,
                )
                db.add(ligne)
            db.commit()
        except Exception as e:
            print(f"Erreur extraction relevé: {e}")
            pass # We still keep the releve object

    return {"message": "Relevé importé", "id": releve.id, "file_name": releve.file_name}


@router.get("/")
def list_releves(db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    societe_id = session.get("societe_id")
    if not societe_id:
        return []
    releves = db.query(ReleveBancaire).filter(ReleveBancaire.societe_id == societe_id).order_by(ReleveBancaire.created_at.desc()).all()
    result = []
    for r in releves:
        result.append({
            "id": r.id,
            "date_import": r.date_import,
            "date_debut": r.date_debut,
            "date_fin": r.date_fin,
            "solde_initial": r.solde_initial,
            "solde_final": r.solde_final,
            "banque_nom": r.banque_nom,
            "file_name": r.file_name,
            "lignes_count": len(r.lignes)
        })
    return result

@router.get("/{releve_id}")
def get_releve(releve_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    releve = db.query(ReleveBancaire).filter(ReleveBancaire.id == releve_id).first()
    if not releve or releve.societe_id != session.get("societe_id"):
        raise HTTPException(404, "Relevé introuvable")

    return {
        "id": releve.id,
        "date_import": releve.date_import,
        "date_debut": releve.date_debut,
        "date_fin": releve.date_fin,
        "solde_initial": releve.solde_initial,
        "solde_final": releve.solde_final,
        "banque_nom": releve.banque_nom,
        "file_name": releve.file_name,
        "lignes": [
            {
                "id": l.id,
                "date_operation": l.date_operation,
                "description": l.description,
                "debit": l.debit,
                "credit": l.credit,
                "is_rapproche": l.is_rapproche,
                "entry_line_id": l.entry_line_id
            } for l in sorted(releve.lignes, key=lambda x: x.id)
        ]
    }

@router.get("/suggestions/{ligne_id}")
def get_suggestions(ligne_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """
    Recherche des suggestions d'écritures pour une ligne de relevé donnée.
    """
    societe_id = session.get("societe_id")
    ligne = db.query(LigneReleve).filter(LigneReleve.id == ligne_id).first()
    if not ligne:
        raise HTTPException(404, "Ligne de relevé introuvable")
    
    # Critères : Même montant, journal BQ, pas encore rapproché
    query = db.query(EntryLine).join(JournalEntry).filter(
        JournalEntry.journal_code == 'BQ',
        EntryLine.debit == ligne.debit,
        EntryLine.credit == ligne.credit
    )
    
    # TODO: Ajouter un filtre par date (+/- 15 jours par exemple)
    
    suggestions = query.all()
    return [
        {
            "id": s.id,
            "account_code": s.account_code,
            "account_label": s.account_label,
            "debit": s.debit,
            "credit": s.credit,
            "date": s.journal_entry.entry_date,
            "description": s.journal_entry.description,
            "reference": s.journal_entry.reference
        } for s in suggestions
    ]

@router.get("/suggestions-all/{releve_id}")
def get_all_suggestions(releve_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """
    Retourne les suggestions pour toutes les lignes d'un relevé.
    Priorité : Correspondance exacte par montant dans le journal BQ.
    Puis recherche de suggestion IA si aucune correspondance exacte n'est trouvée.
    """
    releve = db.query(ReleveBancaire).filter(ReleveBancaire.id == releve_id).first()
    if not releve:
        raise HTTPException(404, "Relevé introuvable")
    
    results = {}
    for ligne in releve.lignes:
        if ligne.is_rapproche:
            continue
            
        # 1. Recherche exacte par montant (Journal BQ)
        match = db.query(EntryLine).join(JournalEntry).filter(
            JournalEntry.journal_code == 'BQ',
            JournalEntry.societe_id == releve.societe_id,
            EntryLine.debit == ligne.debit,
            EntryLine.credit == ligne.credit
        ).first()
        
        if match:
            results[ligne.id] = {
                "type": "exact",
                "entry_line_id": match.id,
                "account_code": match.account_code,
                "account_label": match.account_label,
                "description": match.journal_entry.description
            }
        else:
            # 2. IA Suggestion pour création d'écriture
            try:
                # Limitation : seulement pour les 5 premières lignes non-matchées pour éviter lenteur
                # (On pourrait augmenter ou paralléliser plus tard)
                ai_suggest = classify_bank_transaction(ligne.description, float(ligne.debit), float(ligne.credit))
                results[ligne.id] = {
                    "type": "ai",
                    "account_code": ai_suggest.get("pcm_account_code"),
                    "account_label": ai_suggest.get("pcm_account_label"),
                    "confidence": ai_suggest.get("confidence")
                }
            except Exception as e:
                print(f"Erreur IA Bulk: {e}")
                pass
            
    return results

@router.get("/suggest-account/{ligne_id}")
def suggest_account(ligne_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """
    Utilise l'IA pour suggérer un compte PCM basé sur le libellé de la ligne.
    """
    ligne = db.query(LigneReleve).filter(LigneReleve.id == ligne_id).first()
    if not ligne:
        raise HTTPException(404, "Ligne de relevé introuvable")
    
    try:
        suggestion = classify_bank_transaction(
            description=ligne.description,
            debit=float(ligne.debit),
            credit=float(ligne.credit)
        )
        return suggestion
    except Exception as e:
        print(f"Erreur AI suggestion: {e}")
        # Fallback compte d'attente
        return {
            "pcm_account_code": "47110000",
            "pcm_account_label": "Compte d'attente",
            "confidence": 0,
            "reason": "Erreur technique IA"
        }

@router.post("/rapprocher")
def rapprocher_ligne(payload: Dict[str, int], db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """
    Lie manuellement une ligne de relevé à une ligne d'écriture existante.
    """
    ligne_id = payload.get("ligne_releve_id")
    entry_line_id = payload.get("entry_line_id")
    
    ligne = db.query(LigneReleve).filter(LigneReleve.id == ligne_id).first()
    entry = db.query(EntryLine).filter(EntryLine.id == entry_line_id).first()
    
    if not ligne or not entry:
        raise HTTPException(404, "Données introuvables")
    
    ligne.is_rapproche = True
    ligne.entry_line_id = entry_line_id
    db.commit()
    return {"status": "success"}

@router.post("/generer-ecriture")
def generer_ecriture(payload: Dict[str, Any], db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """
    Génère une écriture comptable BQ complète à partir d'une ligne de relevé.
    """
    societe_id = session.get("societe_id")
    ligne_id = payload.get("ligne_releve_id")
    compte_contrepartie = payload.get("compte_contrepartie", "47110000") # Compte d'attente par défaut
    
    ligne = db.query(LigneReleve).filter(LigneReleve.id == ligne_id).first()
    if not ligne:
        raise HTTPException(404, "Ligne de relevé introuvable")

    # 1. Créer l'en-tête
    journal_entry = JournalEntry(
        journal_code='BQ',
        societe_id=societe_id,
        entry_date=ligne.date_operation,
        description=f"Rapprochement : {ligne.description}",
        reference=ligne.reference,
        total_debit=ligne.debit + ligne.credit,
        total_credit=ligne.debit + ligne.credit,
        is_validated=True
    )
    db.add(journal_entry)
    db.flush() # Pour avoir l'ID

    # 2. Ligne Banque (5141)
    banque_line = EntryLine(
        ecriture_journal_id=journal_entry.id,
        account_code="51410000",
        account_label="BANQUE",
        debit=ligne.credit, # Si crédit bancaire -> débit comptable
        credit=ligne.debit, # Si débit bancaire -> crédit comptable
    )
    db.add(banque_line)

    # 3. Ligne Contrepartie
    cp_line = EntryLine(
        ecriture_journal_id=journal_entry.id,
        account_code=compte_contrepartie,
        debit=ligne.debit,
        credit=ligne.credit,
    )
    db.add(cp_line)

    # 4. Lier
    db.flush()
    ligne.is_rapproche = True
    ligne.entry_line_id = banque_line.id
    
    db.commit()
    return {"status": "success", "journal_entry_id": journal_entry.id}
