"""
routes/journaux.py — Journal comptable PCM Maroc
Consultation et export des écritures par journal (ACH / VTE / OD / BQ)
"""
import csv
import io
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from database import get_db
from models import JournalEntry, EntryLine, Facture
from routes.deps import get_current_session

router = APIRouter(prefix="/journaux", tags=["journaux"])

# Codes journal disponibles
CODES_JOURNAL = {
    "ACH": "Journal des Achats",
    "VTE": "Journal des Ventes",
    "OD":  "Opérations Diverses",
    "BQ":  "Banque",
}


def _entry_to_dict(entry: JournalEntry) -> dict:
    """Convertit une écriture journal en dict de réponse."""
    return {
        "id": entry.id,
        "journal_code": entry.journal_code,
        "journal_label": CODES_JOURNAL.get(entry.journal_code, entry.journal_code),
        "entry_date": str(entry.entry_date) if entry.entry_date else None,
        "reference": entry.reference,
        "description": entry.description,
        "is_validated": entry.is_validated,
        "total_debit": float(entry.total_debit) if entry.total_debit else 0.0,
        "total_credit": float(entry.total_credit) if entry.total_credit else 0.0,
        "facture_id": entry.facture_id,
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
            for el in sorted(entry.entry_lines, key=lambda x: x.line_order or 0)
        ],
    }


def _build_query(db: Session, societe_id: int, journal_code: Optional[str],
                 date_debut: Optional[date], date_fin: Optional[date],
                 valide_seulement: bool):
    """Construit la requête de récupération des écritures."""
    # On filtre par société directement sur l'écriture
    q = db.query(JournalEntry).filter(JournalEntry.societe_id == societe_id)

    if valide_seulement:
        q = q.filter(JournalEntry.is_validated == True)

    if journal_code:
        q = q.filter(JournalEntry.journal_code == journal_code.upper())

    if date_debut:
        q = q.filter(JournalEntry.entry_date >= date_debut)

    if date_fin:
        q = q.filter(JournalEntry.entry_date <= date_fin)

    return q.order_by(JournalEntry.entry_date.asc(), JournalEntry.id.asc())


# ──────────────────────────────────────────────────────────────────────────
# GET /journaux/ — Liste des écritures
# ──────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=dict)
def list_journal(
    journal_code: Optional[str] = Query(None, description="ACH | VTE | OD | BQ"),
    date_debut: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    date_fin: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    valide_seulement: bool = Query(True, description="N'afficher que les écritures validées"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """
    Liste les écritures du journal comptable.
    Filtrable par code journal, période, et statut de validation.
    """
    societe_id = session.get("societe_id")

    if journal_code and journal_code.upper() not in CODES_JOURNAL:
        raise HTTPException(400, f"Code journal invalide. Valeurs acceptées : {list(CODES_JOURNAL.keys())}")

    q = _build_query(db, societe_id, journal_code, date_debut, date_fin, valide_seulement)

    total = q.count()
    entries = q.offset((page - 1) * per_page).limit(per_page).all()

    # Calcul des totaux pour la page
    total_debit = sum(float(e.total_debit or 0) for e in entries)
    total_credit = sum(float(e.total_credit or 0) for e in entries)

    return {
        "journal_code": journal_code,
        "journal_label": CODES_JOURNAL.get(journal_code, "Tous les journaux") if journal_code else "Tous les journaux",
        "date_debut": str(date_debut) if date_debut else None,
        "date_fin": str(date_fin) if date_fin else None,
        "total_ecritures": total,
        "page": page,
        "per_page": per_page,
        "total_debit": round(total_debit, 2),
        "total_credit": round(total_credit, 2),
        "equilibre": round(abs(total_debit - total_credit), 2) <= 0.01,
        "ecritures": [_entry_to_dict(e) for e in entries],
    }


# ──────────────────────────────────────────────────────────────────────────
# GET /journaux/totaux — Totaux par journal
# ──────────────────────────────────────────────────────────────────────────
@router.get("/totaux", response_model=dict)
def get_totaux_par_journal(
    annee: Optional[int] = Query(None, description="Année comptable"),
    mois: Optional[int] = Query(None, ge=1, le=12, description="Mois (1-12)"),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Retourne les totaux débit/crédit par journal pour une période."""
    societe_id = session.get("societe_id")

    date_debut = None
    date_fin = None

    if annee and mois:
        import calendar
        last_day = calendar.monthrange(annee, mois)[1]
        date_debut = date(annee, mois, 1)
        date_fin = date(annee, mois, last_day)
    elif annee:
        date_debut = date(annee, 1, 1)
        date_fin = date(annee, 12, 31)

    totaux = {}
    for code, label in CODES_JOURNAL.items():
        q = _build_query(db, societe_id, code, date_debut, date_fin, valide_seulement=True)
        entries = q.all()
        debit = sum(float(e.total_debit or 0) for e in entries)
        credit = sum(float(e.total_credit or 0) for e in entries)
        totaux[code] = {
            "journal_code": code,
            "journal_label": label,
            "nb_ecritures": len(entries),
            "total_debit": round(debit, 2),
            "total_credit": round(credit, 2),
            "equilibre": round(abs(debit - credit), 2) <= 0.01,
        }

    return {
        "periode": f"{annee or 'Toutes les années'}" + (f"/{mois:02d}" if mois else ""),
        "totaux_par_journal": totaux,
    }


# ──────────────────────────────────────────────────────────────────────────
# GET /journaux/export — Export CSV du journal
# ──────────────────────────────────────────────────────────────────────────
@router.get("/export")
def export_journal_csv(
    journal_code: Optional[str] = Query(None, description="ACH | VTE | OD | BQ"),
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Exporte le journal comptable au format CSV."""
    societe_id = session.get("societe_id")

    q = _build_query(db, societe_id, journal_code, date_debut, date_fin, valide_seulement=True)
    entries = q.all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")

    # En-tête CSV
    writer.writerow([
        "Journal", "Date", "N° Pièce", "Libellé", "Compte", "Libellé Compte",
        "Débit", "Crédit", "Tiers", "ICE Tiers"
    ])

    for entry in entries:
        for el in sorted(entry.entry_lines, key=lambda x: x.line_order or 0):
            writer.writerow([
                entry.journal_code,
                str(entry.entry_date) if entry.entry_date else "",
                entry.reference or "",
                entry.description or "",
                el.account_code or "",
                el.account_label or "",
                str(float(el.debit)).replace(".", ",") if el.debit else "0,00",
                str(float(el.credit)).replace(".", ",") if el.credit else "0,00",
                el.tiers_name or "",
                el.tiers_ice or "",
            ])

    output.seek(0)
    jcode = journal_code or "ALL"
    filename = f"journal_{jcode}_{date.today().isoformat()}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ──────────────────────────────────────────────────────────────────────────
# POST /journaux/{entry_id}/valider — Validation manuelle
# ──────────────────────────────────────────────────────────────────────────
@router.post("/{entry_id}/valider")
def validate_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Valide manuellement une écriture journalière."""
    societe_id = session.get("societe_id")
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.societe_id == societe_id
    ).first()

    if not entry:
        raise HTTPException(404, "Écriture introuvable")

    if entry.is_validated:
        return {"message": "Écriture déjà validée", "id": entry.id}

    entry.is_validated = True
    entry.validated_at = func.now()
    entry.validated_by = session.get("username", "system")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(400, f"Erreur lors de la validation : {e}")

    return {"message": "Écriture validée avec succès", "id": entry.id}
