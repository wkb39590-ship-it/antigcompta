"""
routes/pipeline.py — Pipeline complet de traitement des factures
POST /factures/upload
POST /factures/{id}/extract
POST /factures/{id}/classify
POST /factures/{id}/generate-entries
GET  /factures/{id}/entries
PUT  /invoice-lines/{id}
PUT  /entry-lines/{id}
POST /factures/{id}/validate
POST /factures/{id}/reject
GET  /factures/
GET  /factures/{id}
"""
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Facture, InvoiceLine, JournalEntry, EntryLine, Societe
from routes.deps import get_current_session

from services import ocr_service
from services.gemini_service import (
    extract_invoice_header,
    extract_invoice_lines,
    extract_invoice_fields_from_image_bytes,
)
from services.pdf_utils import pdf_to_png_images_bytes
from services.classification_service import classify_all_lines
from services.entry_generator import generate_journal_entries, check_balance
from services.dgi_validator import validate_dgi
from services.validators import validate_or_fix, merge_fields

from utils.parsers import parse_date_fr

router = APIRouter(prefix="/factures", tags=["pipeline"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTS = [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _save_file(upload: UploadFile) -> str:
    ext = Path(upload.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(400, f"Extension non supportée: {ext}")
    name = f"{uuid.uuid4()}{ext}"
    dest = UPLOAD_DIR / name
    data = upload.file.read()
    if not data:
        raise HTTPException(400, "Fichier vide")
    with open(dest, "wb") as f:
        f.write(data)
    return str(dest)


def _guess_mime(path: str) -> str:
    ext = Path(path).suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
    }.get(ext, "application/octet-stream")


def _get_image_data(file_path: str):
    """Retourne (image_data, mime_type) — image_data est bytes ou List[bytes] pour PDF."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        images = pdf_to_png_images_bytes(file_path, dpi=300, max_pages=10)
        if not images:
            raise HTTPException(500, "Impossible de convertir le PDF en images")
        return images, "image/png"
    with open(file_path, "rb") as f:
        return f.read(), _guess_mime(file_path)


def _get_facture_or_404(facture_id: int, db: Session) -> Facture:
    f = db.query(Facture).filter(Facture.id == facture_id).first()
    if not f:
        raise HTTPException(404, "Facture introuvable")
    return f


# ─────────────────────────────────────────────
# Étape 1 — Upload
# ─────────────────────────────────────────────

@router.post("/upload", response_model=dict)
def upload_facture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Upload un fichier facture. Crée une entrée avec statut IMPORTED.

    NOTE: This endpoint previously accepted `societe_id` as a query param.
    It now uses the `session` context (session_token) to determine the company
    and prevent clients from uploading for arbitrary sociétés.
    """
    societe_id = session.get("societe_id")
    societe = db.query(Societe).filter(Societe.id == societe_id).first()
    if not societe:
        raise HTTPException(404, "Société introuvable")

    file_path = _save_file(file)

    facture = Facture(
        societe_id=societe_id,
        file_path=file_path,
        status="IMPORTED",
        operation_type="achat",
        operation_confidence=0.5,
    )
    db.add(facture)
    db.commit()
    db.refresh(facture)

    return {
        "message": "Facture uploadée",
        "id": facture.id,
        "status": facture.status,
        "file_path": file_path,
    }


# ─────────────────────────────────────────────
# Étape 2 — Extraction OCR + Gemini
# ─────────────────────────────────────────────

@router.post("/{facture_id}/extract", response_model=dict)
def extract_facture(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """
    Lance OCR + Gemini sur la facture.
    Remplit le Tableau 1 (en-tête) et le Tableau 2 (lignes produits).
    Passe le statut à EXTRACTED.
    """
    facture = _get_facture_or_404(facture_id, db)
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")

    if not facture.file_path or not Path(facture.file_path).exists():
        raise HTTPException(400, "Fichier source introuvable")

    image_data, mime_type = _get_image_data(facture.file_path)

    # ── Extraction en-tête via Gemini ──────────────────────────
    try:
        header = extract_invoice_header(image_data, mime_type=mime_type)
        print("✅ Extraction Gemini (header) réussie")
    except Exception as e:
        print(f"❌ Erreur extraction Gemini header: {str(e)[:200]}")
        # Fallback vers l'extraction legacy Gemini
        try:
            header = extract_invoice_fields_from_image_bytes(image_data, mime_type=mime_type)
            print("✅ Extraction Gemini legacy réussie")
        except Exception as e2:
            print(f"❌ Erreur extraction Gemini legacy: {str(e2)[:200]}")
            # Fallback vers Tesseract OCR local
            try:
                ocr_text = ocr_service.extract(facture.file_path)
                print(f"✅ Extraction Tesseract OCR réussie: {ocr_text.chars} caractères")
                # Parser le texte OCR pour extraire les champs
                from services.extract_fields import parse_facture_text
                header = parse_facture_text(ocr_text.text)
                print(f"✅ Parsing OCR réussi: {list(header.keys())}")
            except Exception as e3:
                print(f"❌ Erreur extraction Tesseract: {str(e3)[:200]}")
                header = {}

    # ── Extraction lignes produits via Gemini ──────────────────
    try:
        raw_lines = extract_invoice_lines(image_data, mime_type=mime_type)
        print(f"✅ Extraction Gemini (lignes) réussie: {len(raw_lines)} lignes")
    except Exception as e:
        print(f"❌ Erreur extraction Gemini lignes: {str(e)[:200]}")
        # Fallback: créer une ligne par défaut avec le montant total
        # L'utilisateur pourra la corriger manuellement
        ht_total = header.get("montant_ht") or 0
        tva_total = header.get("montant_tva") or 0
        ttc_total = header.get("montant_ttc") or 0
        
        # Calculer le taux TVA
        tva_rate = None
        if ht_total and tva_total:
            tva_rate = round((tva_total / ht_total) * 100, 2) if ht_total > 0 else None
        
        raw_lines = [{
            "line_number": 1,
            "description": f"Achat global / Vente globale (à corriger manuellement)",
            "quantity": 1,
            "unit": "lot",
            "unit_price_ht": ht_total,
            "line_amount_ht": ht_total,
            "tva_rate": tva_rate,
            "tva_amount": tva_total,
            "line_amount_ttc": ttc_total,
        }]
        print(f"⚠️ Fallback: création ligne par défaut (Gemini non disponible)")
        print(f"   Utilisateur doit corriger manuellement les lignes")

    # ── Remplir Tableau 1 (Facture) ────────────────────────────
    facture.numero_facture = header.get("numero_facture")
    facture.date_facture = parse_date_fr(header.get("date_facture"))
    facture.due_date = parse_date_fr(header.get("due_date"))
    
    facture.supplier_name = header.get("supplier_name") or header.get("fournisseur")
    facture.supplier_ice = header.get("supplier_ice") or header.get("ice_frs")
    facture.supplier_if = header.get("supplier_if") or header.get("if_frs")
    facture.supplier_rc = header.get("supplier_rc")
    facture.supplier_address = header.get("supplier_address")

    facture.client_name = header.get("client_name")
    facture.client_ice = header.get("client_ice")
    facture.client_if = header.get("client_if")
    facture.client_address = header.get("client_address")

    # ── Déterminer le type de facture par rapport à la société ──
    # Si la facture est adressée à notre société → ACHAT
    # Si la facture est émise par notre société → VENTE
    def _clean_name(name: str) -> str:
        """Nettoie le nom pour la comparaison (supprime suffixes juridiques)"""
        import re
        if not name:
            return ""
        cleaned = name.strip().upper()
        # Supprimer les suffixes juridiques courants
        cleaned = re.sub(r'\b(STE|SARL|S\.A\.R\.L|SA|S\.A|EURL|E\.U\.R\.L|SPRL|S\.P\.R\.L|LLC|CORP|INC|LTD|SRL)\b', '', cleaned)
        # Supprimer les espaces multiples
        cleaned = ' '.join(cleaned.split())
        return cleaned.strip()
    
    societe = db.query(Societe).filter(Societe.id == facture.societe_id).first()
    invoice_type_from_gemini = header.get("invoice_type") or "ACHAT"
    
    if societe and societe.raison_sociale:
        raison_social_clean = _clean_name(societe.raison_sociale)
        client_name_clean = _clean_name(facture.client_name)
        supplier_name_clean = _clean_name(facture.supplier_name)
        
        # Si le client est notre société → c'est un ACHAT
        if client_name_clean and raison_social_clean and raison_social_clean in client_name_clean:
            facture.invoice_type = "ACHAT"
        # Si le fournisseur est notre société → c'est une VENTE
        elif supplier_name_clean and raison_social_clean and raison_social_clean in supplier_name_clean:
            facture.invoice_type = "VENTE"
        else:
            facture.invoice_type = invoice_type_from_gemini
    else:
        facture.invoice_type = invoice_type_from_gemini

    facture.montant_ht = header.get("montant_ht")
    facture.montant_tva = header.get("montant_tva")
    facture.montant_ttc = header.get("montant_ttc")
    facture.taux_tva = header.get("taux_tva")
    facture.devise = header.get("devise") or "MAD"
    facture.payment_mode = header.get("payment_mode")
    facture.payment_terms = header.get("payment_terms")

    # Legacy compat
    facture.fournisseur = facture.supplier_name
    facture.ice_frs = facture.supplier_ice
    facture.if_frs = facture.supplier_if
    facture.operation_type = "vente" if facture.invoice_type == "VENTE" else "achat"
    facture.operation_confidence = 0.9
    facture.extraction_source = "GEMINI"

    # ── ANTI-DOUBLON: Sécurité anti-saisies multiples ──────────
    # On cherche une autre facture avec le même (ICE ou Nom) + Date + TTC
    if facture.date_facture and facture.montant_ttc:
        query = db.query(Facture).filter(
            Facture.societe_id == facture.societe_id,
            Facture.id != facture.id,
            Facture.date_facture == facture.date_facture,
            Facture.montant_ttc == facture.montant_ttc
        )
        
        if facture.supplier_ice:
            query = query.filter(Facture.supplier_ice == facture.supplier_ice)
        else:
            query = query.filter(Facture.supplier_name == facture.supplier_name)
            
        duplicate = query.first()
        
        if duplicate:
            db.rollback()
            supplier_id = facture.supplier_ice or facture.supplier_name or "Inconnu"
            raise HTTPException(
                status_code=409, 
                detail=f"Doublon détecté : Cette facture (Fournisseur: {supplier_id}, Date: {facture.date_facture}, TTC: {facture.montant_ttc}) existe déjà dans ce dossier."
            )

    # ── Contrôles DGI ──────────────────────────────────────────
    dgi_flags = validate_dgi({
        "supplier_ice": facture.supplier_ice,
        "supplier_if": facture.supplier_if,
        "numero_facture": facture.numero_facture,
        "montant_ht": facture.montant_ht,
        "montant_tva": facture.montant_tva,
        "montant_ttc": facture.montant_ttc,
        "taux_tva": facture.taux_tva,
        "date_facture": facture.date_facture,
    })
    facture.set_dgi_flags(dgi_flags)

    # ── Remplir Tableau 2 (InvoiceLines) ───────────────────────
    # Supprimer les anciennes lignes
    for old_line in facture.lines:
        db.delete(old_line)
    db.flush()

    for i, raw in enumerate(raw_lines):
        line = InvoiceLine(
            facture_id=facture.id,
            line_number=raw.get("line_number") or (i + 1),
            description=raw.get("description"),
            quantity=raw.get("quantity"),
            unit=raw.get("unit"),
            unit_price_ht=raw.get("unit_price_ht"),
            line_amount_ht=raw.get("line_amount_ht"),
            tva_rate=raw.get("tva_rate"),
            tva_amount=raw.get("tva_amount"),
            line_amount_ttc=raw.get("line_amount_ttc"),
        )
        db.add(line)

    facture.status = "EXTRACTED"
    db.commit()
    db.refresh(facture)

    # Préparer tableau2 (lignes extraites)
    tableau2 = []
    for line in facture.lines:
        tableau2.append({
            "id": line.id,
            "line_number": line.line_number,
            "description": line.description,
            "quantity": float(line.quantity) if line.quantity else None,
            "unit": line.unit,
            "unit_price_ht": float(line.unit_price_ht) if line.unit_price_ht else None,
            "line_amount_ht": float(line.line_amount_ht) if line.line_amount_ht else None,
            "tva_rate": float(line.tva_rate) if line.tva_rate else None,
            "tva_amount": float(line.tva_amount) if line.tva_amount else None,
            "line_amount_ttc": float(line.line_amount_ttc) if line.line_amount_ttc else None,
        })

    return {
        "message": "Extraction terminée",
        "id": facture.id,
        "status": facture.status,
        "tableau1": {
            "numero_facture": facture.numero_facture,
            "date_facture": str(facture.date_facture) if facture.date_facture else None,
            "invoice_type": facture.invoice_type,
            "supplier_name": facture.supplier_name,
            "supplier_ice": facture.supplier_ice,
            "supplier_if": facture.supplier_if,
            "client_name": facture.client_name,
            "montant_ht": float(facture.montant_ht) if facture.montant_ht else None,
            "montant_tva": float(facture.montant_tva) if facture.montant_tva else None,
            "montant_ttc": float(facture.montant_ttc) if facture.montant_ttc else None,
            "taux_tva": float(facture.taux_tva) if facture.taux_tva else None,
            "payment_mode": facture.payment_mode,
        },
        "tableau2": tableau2,
        "tableau2_count": len(raw_lines),
        "dgi_flags": dgi_flags,
    }


# ─────────────────────────────────────────────
# Étape 3 — Classification PCM
# ─────────────────────────────────────────────

@router.post("/{facture_id}/classify", response_model=dict)
def classify_facture(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """
    Classifie chaque ligne produit dans le Plan Comptable Marocain.
    Passe le statut à CLASSIFIED.
    """
    facture = _get_facture_or_404(facture_id, db)
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")

    if facture.status not in ("EXTRACTED", "CLASSIFIED"):
        raise HTTPException(400, f"Statut invalide pour classification: {facture.status}")

    # Recharger la facture pour s'assurer que les lignes sont chargées
    db.refresh(facture)
    
    if not facture.lines:
        raise HTTPException(400, "Aucune ligne produit à classifier. Lancez d'abord /extract")

    results = classify_all_lines(facture, db)

    facture.status = "CLASSIFIED"
    db.commit()

    return {
        "message": "Classification terminée",
        "id": facture.id,
        "status": facture.status,
        "classifications": results,
    }


# ─────────────────────────────────────────────
# Étape 4 — Génération des écritures (brouillon)
# ─────────────────────────────────────────────

@router.post("/{facture_id}/generate-entries", response_model=dict)
def generate_entries(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """
    Génère le brouillon des écritures comptables PCM.
    Passe le statut à DRAFT.
    """
    facture = _get_facture_or_404(facture_id, db)
    # Enforce société isolation
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")

    if facture.status not in ("CLASSIFIED", "DRAFT"):
        raise HTTPException(400, f"Statut invalide pour génération: {facture.status}")

    entry = generate_journal_entries(facture, db)
    balance = check_balance(entry)

    facture.status = "DRAFT"
    db.commit()

    return {
        "message": "Écritures générées",
        "id": facture.id,
        "status": facture.status,
        "journal_entry_id": entry.id,
        "balance": balance,
        "entry_lines": [
            {
                "id": el.id,
                "line_order": el.line_order,
                "account_code": el.account_code,
                "account_label": el.account_label,
                "debit": float(el.debit),
                "credit": float(el.credit),
                "tiers_name": el.tiers_name,
            }
            for el in entry.entry_lines
        ],
    }


# ─────────────────────────────────────────────
# Lecture des données
# ─────────────────────────────────────────────

@router.get("/{facture_id}", response_model=dict)
def get_facture(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Retourne l'en-tête facture (Tableau 1) + flags DGI."""
    facture = _get_facture_or_404(facture_id, db)
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")
    return {
        "id": facture.id,
        "status": facture.status,
        "numero_facture": facture.numero_facture,
        "date_facture": str(facture.date_facture) if facture.date_facture else None,
        "due_date": str(facture.due_date) if facture.due_date else None,
        "invoice_type": facture.invoice_type,
        "supplier_name": facture.supplier_name,
        "supplier_ice": facture.supplier_ice,
        "supplier_if": facture.supplier_if,
        "supplier_rc": facture.supplier_rc,
        "supplier_address": facture.supplier_address,
        "client_name": facture.client_name,
        "client_ice": facture.client_ice,
        "client_if": facture.client_if,
        "client_address": facture.client_address,
        "montant_ht": float(facture.montant_ht) if facture.montant_ht else None,
        "montant_tva": float(facture.montant_tva) if facture.montant_tva else None,
        "montant_ttc": float(facture.montant_ttc) if facture.montant_ttc else None,
        "taux_tva": float(facture.taux_tva) if facture.taux_tva else None,
        "devise": facture.devise,
        "payment_mode": facture.payment_mode,
        "payment_terms": facture.payment_terms,
        "extraction_source": facture.extraction_source,
        "dgi_flags": facture.get_dgi_flags(),
        "file_path": facture.file_path,
        "created_at": str(facture.created_at) if facture.created_at else None,
    }


@router.get("/{facture_id}/lines", response_model=list)
def get_facture_lines(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Retourne les lignes produits (Tableau 2) avec classification PCM."""
    facture = _get_facture_or_404(facture_id, db)
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")
    return [
        {
            "id": line.id,
            "line_number": line.line_number,
            "description": line.description,
            "quantity": float(line.quantity) if line.quantity else None,
            "unit": line.unit,
            "unit_price_ht": float(line.unit_price_ht) if line.unit_price_ht else None,
            "line_amount_ht": float(line.line_amount_ht) if line.line_amount_ht else None,
            "tva_rate": float(line.tva_rate) if line.tva_rate else None,
            "tva_amount": float(line.tva_amount) if line.tva_amount else None,
            "line_amount_ttc": float(line.line_amount_ttc) if line.line_amount_ttc else None,
            "pcm_class": line.pcm_class,
            "pcm_account_code": line.corrected_account_code or line.pcm_account_code,
            "pcm_account_label": line.pcm_account_label,
            "classification_confidence": line.classification_confidence,
            "classification_reason": line.classification_reason,
            "is_corrected": line.is_corrected,
        }
        for line in sorted(facture.lines, key=lambda l: l.line_number or 0)
    ]


@router.get("/{facture_id}/entries", response_model=dict)
def get_facture_entries(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Retourne le brouillon des écritures comptables."""
    facture = _get_facture_or_404(facture_id, db)
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")

    entries = db.query(JournalEntry).filter(JournalEntry.facture_id == facture_id).all()
    if not entries:
        return {"journal_entries": [], "message": "Aucune écriture générée"}

    result = []
    for entry in entries:
        result.append({
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
            ],
        })

    return {"journal_entries": result}


# ─────────────────────────────────────────────
# Corrections manuelles
# ─────────────────────────────────────────────

@router.put("/invoice-lines/{line_id}", response_model=dict)
def update_invoice_line(
    line_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Permet au comptable de corriger le compte PCM d'une ligne. Vérifie l'accès à la société."""
    line = db.query(InvoiceLine).filter(InvoiceLine.id == line_id).first()
    if not line:
        raise HTTPException(404, "Ligne introuvable")
    
    # Verify the invoice owning this line belongs to the current société
    facture = db.query(Facture).filter(Facture.id == line.facture_id).first()
    if not facture:
        raise HTTPException(404, "Facture associée introuvable")
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette ligne")

    if "corrected_account_code" in payload:
        line.corrected_account_code = payload["corrected_account_code"]
        line.is_corrected = True
    # Accept frontend payload keys as aliases
    if "pcm_account_code" in payload and payload.get("pcm_account_code") is not None:
        # Update both the classified PCM code and record a manual correction
        line.pcm_account_code = payload["pcm_account_code"]
        line.corrected_account_code = payload["pcm_account_code"]
        line.is_corrected = True
    if "pcm_account_label" in payload:
        line.pcm_account_label = payload["pcm_account_label"]
    if "classification_confidence" in payload:
        try:
            line.classification_confidence = float(payload["classification_confidence"]) if payload["classification_confidence"] is not None else None
        except Exception:
            pass
    if "description" in payload:
        line.description = payload["description"]
    if "line_amount_ht" in payload:
        line.line_amount_ht = payload["line_amount_ht"]
    if "tva_rate" in payload:
        line.tva_rate = payload["tva_rate"]

    db.commit()
    return {"message": "Ligne mise à jour", "line_id": line_id}


@router.put("/entry-lines/{entry_line_id}", response_model=dict)
def update_entry_line(
    entry_line_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Permet au comptable de corriger une ligne débit/crédit. Vérifie l'accès à la société."""
    el = db.query(EntryLine).filter(EntryLine.id == entry_line_id).first()
    if not el:
        raise HTTPException(404, "Ligne d'écriture introuvable")
    
    # Verify the entry owning this line's facture belongs to the current société
    entry = db.query(JournalEntry).filter(JournalEntry.id == el.entry_id).first()
    if not entry:
        raise HTTPException(404, "Écriture associée introuvable")
    facture = db.query(Facture).filter(Facture.id == entry.facture_id).first()
    if not facture:
        raise HTTPException(404, "Facture associée introuvable")
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette ligne")

    if "account_code" in payload:
        el.account_code = payload["account_code"]
    if "account_label" in payload:
        el.account_label = payload["account_label"]
    if "debit" in payload:
        el.debit = payload["debit"]
    if "credit" in payload:
        el.credit = payload["credit"]

    db.commit()
    return {"message": "Ligne d'écriture mise à jour", "entry_line_id": entry_line_id}


# ─────────────────────────────────────────────
# Étape 5 — Validation définitive
# ─────────────────────────────────────────────

@router.post("/{facture_id}/validate", response_model=dict)
def validate_facture(
    facture_id: int,
    validated_by: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """
    Valide la facture et enregistre définitivement les écritures en base.
    Transaction atomique: si une erreur survient, tout est annulé (rollback).
    validated_by peut être un ID utilisateur (int) ou un nom d'utilisateur (string)
    """
    facture = _get_facture_or_404(facture_id, db)
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")

    if facture.status not in ("DRAFT", "CLASSIFIED"):
        raise HTTPException(400, f"Statut invalide pour validation: {facture.status}. Attendu: DRAFT")

    # Vérifier qu'il y a des écritures brouillon
    entries = db.query(JournalEntry).filter(
        JournalEntry.facture_id == facture_id,
        JournalEntry.is_validated == False
    ).all()

    if not entries:
        raise HTTPException(400, "Aucune écriture brouillon à valider. Lancez d'abord /generate-entries")

    # Vérifier l'équilibre de chaque écriture
    for entry in entries:
        balance = check_balance(entry)
        if not balance["is_balanced"]:
            raise HTTPException(422, {
                "message": "Écriture non équilibrée — validation refusée",
                "entry_id": entry.id,
                "balance": balance,
            })

    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        # Utiliser l'agent de la session si non fourni explicitement
        v_by = validated_by or session.get("username")

        # Valider toutes les écritures
        for entry in entries:
            entry.is_validated = True
            entry.validated_by = v_by
            entry.validated_at = now

        # Mettre à jour le statut de la facture
        facture.status = "VALIDATED"
        facture.validated_by = v_by
        facture.validated_at = now

        # --- FEEDBACK LOOP: Enregistrer le mapping fournisseur ---
        if facture.supplier_ice and facture.lines:
            # On prend le compte de la première ligne comme référence pour le fournisseur
            # (Souvent les factures d'un même fournisseur vont dans le même compte de charge)
            first_line = facture.lines[0]
            account_code = first_line.corrected_account_code or first_line.pcm_account_code
            
            if account_code:
                from models import SupplierMapping
                # Chercher si un mapping existe déjà
                mapping = (
                    db.query(SupplierMapping)
                    .filter(
                        SupplierMapping.cabinet_id == facture.societe.cabinet_id,
                        SupplierMapping.supplier_ice == facture.supplier_ice
                    )
                    .first()
                )
                
                if mapping:
                    mapping.pcm_account_code = account_code
                else:
                    new_mapping = SupplierMapping(
                        cabinet_id=facture.societe.cabinet_id,
                        supplier_ice=facture.supplier_ice,
                        pcm_account_code=account_code
                    )
                    db.add(new_mapping)
        # ---------------------------------------------------------

        db.commit()

        return {
            "message": "Facture validée et écritures enregistrées définitivement",
            "id": facture.id,
            "status": facture.status,
            "validated_at": str(now),
            "entries_validated": len(entries),
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Erreur lors de la validation: {e}")


@router.post("/{facture_id}/reject", response_model=dict)
def reject_facture(
    facture_id: int,
    reason: str = Query(..., description="Motif du rejet"),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Rejette la facture avec un motif."""
    facture = _get_facture_or_404(facture_id, db)
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")

    facture.status = "ERROR"
    facture.reject_reason = reason
    db.commit()

    return {
        "message": "Facture rejetée",
        "id": facture.id,
        "status": facture.status,
        "reason": reason,
    }


# ─────────────────────────────────────────────
# Liste des factures
# ─────────────────────────────────────────────

@router.get("/", response_model=list)
def list_factures(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Liste toutes les factures pour la société courante avec filtres optionnels."""
    societe_id = session.get("societe_id")
    q = db.query(Facture).filter(Facture.societe_id == societe_id)
    if status:
        q = q.filter(Facture.status == status.upper())
    factures = q.order_by(Facture.id.desc()).all()

    return [
        {
            "id": f.id,
            "status": f.status,
            "numero_facture": f.numero_facture,
            "date_facture": str(f.date_facture) if f.date_facture else None,
            "invoice_type": f.invoice_type,
            "supplier_name": f.supplier_name or f.fournisseur,
            "montant_ttc": float(f.montant_ttc) if f.montant_ttc else None,
            "devise": f.devise,
            "created_at": str(f.created_at) if f.created_at else None,
        }
        for f in factures
    ]


# ─────────────────────────────────────────────
# Aperçu du fichier
# ─────────────────────────────────────────────

@router.get("/{facture_id}/file")
def get_facture_file(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Retourne le fichier source (PDF/image) pour aperçu. Doit appartenir à la société courante."""
    facture = _get_facture_or_404(facture_id, db)
    if facture.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")
    if not facture.file_path or not Path(facture.file_path).exists():
        raise HTTPException(404, "Fichier source introuvable")
    
    file_path = Path(facture.file_path)
    media_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "image/jpeg"
    filename = f"facture_{facture_id}_{file_path.name}"
    
    return FileResponse(
        facture.file_path,
        media_type=media_type,
        filename=filename
    )
