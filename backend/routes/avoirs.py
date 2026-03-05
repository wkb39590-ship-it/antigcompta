"""
routes/avoirs.py — Endpoints dédiés aux avoirs (avoir achat / avoir vente)
Filtrage, consultation et validation des avoirs dans le pipeline PCM.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Facture, JournalEntry, EntryLine
from routes.deps import get_current_session
from services.entry_generator import generate_journal_entries, check_balance

router = APIRouter(prefix="/avoirs", tags=["avoirs"])


def _facture_to_avoir_dict(f: Facture) -> dict:
    """Convertit une facture avoir en dictionnaire de réponse."""
    entries = [e for e in f.journal_entries if e.is_validated]
    draft_entries = [e for e in f.journal_entries if not e.is_validated]

    return {
        "id": f.id,
        "numero_avoir": f.numero_facture,
        "date_avoir": str(f.date_facture) if f.date_facture else None,
        "type_avoir": f.invoice_type,  # AVOIR
        "fournisseur": f.supplier_name or f.fournisseur,
        "client": f.client_name,
        "ice_fournisseur": f.supplier_ice,
        "montant_ht": float(f.montant_ht) if f.montant_ht else None,
        "montant_tva": float(f.montant_tva) if f.montant_tva else None,
        "montant_ttc": float(f.montant_ttc) if f.montant_ttc else None,
        "taux_tva": float(f.taux_tva) if f.taux_tva else None,
        "devise": f.devise or "MAD",
        "status": f.status,
        "validated_at": str(f.validated_at) if f.validated_at else None,
        "validated_by": f.validated_by,
        "has_entries": len(entries) > 0,
        "has_draft_entries": len(draft_entries) > 0,
        "created_at": str(f.created_at) if f.created_at else None,
    }


# ──────────────────────────────────────────────────────────────────────────
# GET /avoirs/ — Liste des avoirs de la société
# ──────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=list)
def list_avoirs(
    status: Optional[str] = Query(None, description="Filtrer par statut (VALIDATED, DRAFT, etc.)"),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Liste tous les avoirs (achat et vente) de la société active."""
    societe_id = session.get("societe_id")

    query = db.query(Facture).filter(
        Facture.societe_id == societe_id,
        Facture.invoice_type.in_(["AVOIR", "AVOIR_ACHAT", "AVOIR_VENTE"]),
    )

    if status:
        query = query.filter(Facture.status == status.upper())

    avoirs = query.order_by(Facture.date_facture.desc()).all()
    return [_facture_to_avoir_dict(a) for a in avoirs]


# ──────────────────────────────────────────────────────────────────────────
# GET /avoirs/{id} — Détail d'un avoir
# ──────────────────────────────────────────────────────────────────────────
@router.get("/{avoir_id}", response_model=dict)
def get_avoir(
    avoir_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Retourne le détail d'un avoir avec ses écritures comptables."""
    societe_id = session.get("societe_id")
    avoir = db.query(Facture).filter(
        Facture.id == avoir_id,
        Facture.societe_id == societe_id,
        Facture.invoice_type.in_(["AVOIR", "AVOIR_ACHAT", "AVOIR_VENTE"]),
    ).first()

    if not avoir:
        raise HTTPException(404, "Avoir introuvable")

    result = _facture_to_avoir_dict(avoir)

    # Ajouter les lignes de la facture
    result["lignes"] = [
        {
            "id": l.id,
            "description": l.description,
            "quantity": float(l.quantity) if l.quantity else None,
            "line_amount_ht": float(l.line_amount_ht) if l.line_amount_ht else None,
            "tva_rate": float(l.tva_rate) if l.tva_rate else None,
            "tva_amount": float(l.tva_amount) if l.tva_amount else None,
            "pcm_account_code": l.corrected_account_code or l.pcm_account_code,
            "pcm_account_label": l.pcm_account_label,
        }
        for l in sorted(avoir.lines, key=lambda x: x.line_number or 0)
    ]

    # Ajouter les écritures comptables
    result["ecritures"] = []
    for entry in avoir.journal_entries:
        result["ecritures"].append({
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
                }
                for el in sorted(entry.entry_lines, key=lambda x: x.line_order or 0)
            ],
        })

    return result


# ──────────────────────────────────────────────────────────────────────────
# POST /avoirs/{id}/generate-entries — Générer les écritures de l'avoir
# ──────────────────────────────────────────────────────────────────────────
@router.post("/{avoir_id}/generate-entries", response_model=dict)
def generate_avoir_entries(
    avoir_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Génère les écritures comptables de l'avoir (brouillon)."""
    societe_id = session.get("societe_id")
    avoir = db.query(Facture).filter(
        Facture.id == avoir_id,
        Facture.societe_id == societe_id,
        Facture.invoice_type.in_(["AVOIR", "AVOIR_ACHAT", "AVOIR_VENTE"]),
    ).first()

    if not avoir:
        raise HTTPException(404, "Avoir introuvable")

    if avoir.status not in ("CLASSIFIED", "DRAFT"):
        raise HTTPException(400, f"Statut invalide pour génération: {avoir.status}")

    entry = generate_journal_entries(avoir, db)
    balance = check_balance(entry)
    avoir.status = "DRAFT"
    db.commit()

    return {
        "message": "Écritures avoir générées",
        "avoir_id": avoir_id,
        "balance": balance,
        "ecriture_id": entry.id,
    }


# ──────────────────────────────────────────────────────────────────────────
# POST /avoirs/{id}/validate — Valider l'avoir et ses écritures
# ──────────────────────────────────────────────────────────────────────────
@router.post("/{avoir_id}/validate", response_model=dict)
def validate_avoir(
    avoir_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Valide définitivement les écritures d'un avoir."""
    from datetime import datetime, timezone
    societe_id = session.get("societe_id")
    avoir = db.query(Facture).filter(
        Facture.id == avoir_id,
        Facture.societe_id == societe_id,
        Facture.invoice_type.in_(["AVOIR", "AVOIR_ACHAT", "AVOIR_VENTE"]),
    ).first()

    if not avoir:
        raise HTTPException(404, "Avoir introuvable")

    if avoir.status != "DRAFT":
        raise HTTPException(400, f"L'avoir doit être en statut DRAFT pour être validé")

    entries = db.query(JournalEntry).filter(
        JournalEntry.facture_id == avoir_id,
        JournalEntry.is_validated == False,
    ).all()

    if not entries:
        raise HTTPException(400, "Aucune écriture brouillon. Lancez d'abord /generate-entries")

    for entry in entries:
        balance = check_balance(entry)
        if not balance["is_balanced"]:
            raise HTTPException(422, {"message": "Écriture non équilibrée", "balance": balance})

    now = datetime.now(timezone.utc)
    v_by = session.get("username")

    for entry in entries:
        entry.is_validated = True
        entry.validated_by = v_by
        entry.validated_at = now

    avoir.status = "VALIDATED"
    avoir.validated_by = v_by
    avoir.validated_at = now
    db.commit()

    return {
        "message": "Avoir validé avec succès",
        "avoir_id": avoir_id,
        "status": avoir.status,
        "validated_at": str(now),
    }
