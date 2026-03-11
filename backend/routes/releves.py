"""
routes/releves.py — Gestion des relevés bancaires
"""
import os
import uuid
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import re

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
            print(f"DEBUG: Data extraite: {extracted_data}")
            
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
    Amélioration : Filtre par date (+/- 15 jours) et calcul de pertinence par texte.
    """
    societe_id = session.get("societe_id")
    ligne = db.query(LigneReleve).filter(LigneReleve.id == ligne_id).first()
    if not ligne:
        raise HTTPException(404, "Ligne de relevé introuvable")
    
    # 1. Définir la plage de dates
    try:
        base_date = datetime.strptime(ligne.date_operation, "%Y-%m-%d")
    except:
        base_date = datetime.now()
    
    date_min = (base_date - timedelta(days=15)).strftime("%Y-%m-%d")
    date_max = (base_date + timedelta(days=15)).strftime("%Y-%m-%d")

    # 2. Requête filtrée par montant et date
    query = db.query(EntryLine).join(JournalEntry).filter(
        JournalEntry.societe_id == societe_id,
        JournalEntry.journal_code == 'BQ',
        EntryLine.debit == ligne.debit,
        EntryLine.credit == ligne.credit,
        JournalEntry.entry_date >= date_min,
        JournalEntry.entry_date <= date_max
    )
    
    suggestions = query.all()

    # 3. Calculer un score de pertinence basé sur le texte
    def calculate_score(s: EntryLine, bank_desc: str) -> float:
        score = 0.0
        s_desc = (s.journal_entry.description or "").upper()
        s_ref = (s.journal_entry.reference or "").upper()
        bank_desc = bank_desc.upper()
        
        # Reels matches (mots clés ou numéros complexes)
        bank_words = set(re.findall(r'\w+', bank_desc))
        s_words = set(re.findall(r'\w+', s_desc + " " + s_ref))
        
        overlap = bank_words.intersection(s_words)
        # On ignore les mots trop courts (< 3 car) sauf si c'est des chiffres
        meaningful_overlap = [w for w in overlap if len(w) > 2 or w.isdigit()]
        score += len(meaningful_overlap) * 10
        
        # Bonus si exact string match partiel
        if s_ref and s_ref in bank_desc: score += 50
        if s_desc and (s_desc in bank_desc or bank_desc in s_desc): score += 30
        
        return score

    # Transformer et trier
    results = []
    for s in suggestions:
        score = calculate_score(s, ligne.description)
        results.append({
            "id": s.id,
            "account_code": s.account_code,
            "account_label": s.account_label,
            "debit": s.debit,
            "credit": s.credit,
            "date": s.journal_entry.entry_date,
            "description": s.journal_entry.description,
            "reference": s.journal_entry.reference,
            "score": score
        })
    
    # Trier par score décroissant, puis par date
    results.sort(key=lambda x: (x["score"], x["date"]), reverse=True)
    
    return results

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
            
        # 1. Recherche exacte par montant + date + texte (Journal BQ)
        try:
            base_date = datetime.strptime(ligne.date_operation, "%Y-%m-%d")
            date_min = (base_date - timedelta(days=20)).strftime("%Y-%m-%d")
            date_max = (base_date + timedelta(days=20)).strftime("%Y-%m-%d")
        except:
            date_min, date_max = None, None

        q = db.query(EntryLine).join(JournalEntry).filter(
            JournalEntry.journal_code == 'BQ',
            JournalEntry.societe_id == releve.societe_id,
            EntryLine.debit == ligne.debit,
            EntryLine.credit == ligne.credit
        )
        if date_min:
            q = q.filter(JournalEntry.entry_date >= date_min, JournalEntry.entry_date <= date_max)
        
        potential_matches = q.all()
        
        # Trouver le meilleur match parmi les potentiels
        best_match = None
        max_score = -1.0
        
        bank_desc = (ligne.description or "").upper()
        bank_numbers = set(re.findall(r'\d+', bank_desc))

        for m in potential_matches:
            score = 0
            m_desc = (m.journal_entry.description or "").upper()
            m_ref = (m.journal_entry.reference or "").upper()
            
            # Match référence ou numéro (très fort)
            for num in bank_numbers:
                if len(num) > 3: # On ignore les petits chiffres
                    if num in m_desc or num in m_ref:
                        score += 100
            
            # Match texte
            if m_desc in bank_desc or bank_desc in m_desc:
                score += 50
            
            if score > max_score:
                max_score = score
                best_match = m

        # On ne valide le match automatique que si le score est suffisant (> 40)
        # ou s'il n'y a qu'un seul match possible et que la date est proche
        if best_match and (max_score > 40 or len(potential_matches) == 1):
            results[ligne.id] = {
                "type": "exact",
                "entry_line_id": best_match.id,
                "account_code": best_match.account_code,
                "account_label": best_match.account_label,
                "description": best_match.journal_entry.description,
                "score": max_score
            }
        else:
            # 2. IA Suggestion pour création d'écriture
            try:
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

@router.delete("/{releve_id}")
def delete_releve(releve_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """
    Supprime un relevé, ses lignes (via cascade) et le fichier physique.
    """
    releve = db.query(ReleveBancaire).filter(ReleveBancaire.id == releve_id).first()
    if not releve or releve.societe_id != session.get("societe_id"):
        raise HTTPException(404, "Relevé introuvable")

    # 1. Supprimer le fichier physique s'il existe
    if releve.file_path and os.path.exists(releve.file_path):
        try:
            os.remove(releve.file_path)
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {releve.file_path}: {e}")

    # 2. Supprimer de la base (la cascade supprimera les LigneReleve automatiquement)
    db.delete(releve)
    db.commit()

    return {"status": "success", "message": "Relevé supprimé avec succès"}

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
