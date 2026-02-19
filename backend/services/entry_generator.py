"""
entry_generator.py — Génération des écritures comptables PCM
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from models import Facture, InvoiceLine, JournalEntry, EntryLine


def _d(v) -> Decimal:
    """Convertit en Decimal sécurisé."""
    if v is None:
        return Decimal("0")
    return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _is_tiers_account(account_code: str) -> bool:
    """
    Vérifie si un compte est un compte de tiers (fournisseurs/clients).
    Les comptes de tiers commencent par 4 (401x, 411x, 4411, etc.)
    """
    return account_code.startswith("4") if account_code else False


def _get_tva_account(pcm_class: Optional[int], invoice_type: Optional[str]) -> str:
    """
    Détermine le compte TVA selon la classe PCM et le type de facture.
    - Classe 2 (immobilisation) → 34552
    - Classe 6 (charge) → 34551
    - Vente → 4455
    """
    if invoice_type and invoice_type.upper() == "VENTE":
        return "4455"
    if pcm_class == 2:
        return "34552"
    return "34551"


def generate_journal_entries(facture: Facture, db: Session) -> JournalEntry:
    """
    Génère les écritures comptables (brouillon) à partir des lignes classifiées.
    
    Règles PCM:
    - Achat charge (classe 6): Débit 6xxx + Débit 34551 → Crédit 4411
    - Achat immo (classe 2):   Débit 2xxx + Débit 34552 → Crédit 4411
    - Vente (classe 7):        Débit 3421 → Crédit 7xxx + Crédit 4455
    - Avoir achat:             Débit 4411 → Crédit 6xxx + Crédit 34551
    """
    # Supprimer les anciennes écritures brouillon si elles existent
    for old_entry in facture.journal_entries:
        if not old_entry.is_validated:
            db.delete(old_entry)
    db.flush()

    invoice_type = (facture.invoice_type or "ACHAT").upper()
    is_avoir = invoice_type == "AVOIR"
    is_vente = invoice_type == "VENTE"

    # Déterminer le code journal
    journal_map = {
        "ACHAT": "ACH",
        "VENTE": "VTE",
        "AVOIR": "ACH",
        "NOTE_FRAIS": "OD",
        "IMMOBILISATION": "ACH",
    }
    journal_code = journal_map.get(invoice_type, "OD")

    # Créer l'en-tête de l'écriture
    entry = JournalEntry(
        facture_id=facture.id,
        journal_code=journal_code,
        entry_date=facture.date_facture,
        reference=facture.numero_facture,
        description=f"Facture {facture.numero_facture or ''} — {facture.supplier_name or facture.fournisseur or ''}",
        is_validated=False,
    )
    db.add(entry)
    db.flush()  # pour obtenir entry.id

    entry_lines = []
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    line_order = 1

    # Tiers (fournisseur ou client)
    tiers_name = facture.supplier_name or facture.fournisseur or "Fournisseur"
    tiers_ice = facture.supplier_ice or facture.ice_frs

    if is_vente:
        # ── VENTE ────────────────────────────────────────────────
        # Débit 3421 (Client) pour le TTC total
        ttc_total = _d(facture.montant_ttc)
        client_name = facture.client_name or "Client"
        client_ice = facture.client_ice

        el = EntryLine(
            journal_entry_id=entry.id,
            line_order=line_order,
            account_code="3421",
            account_label="Clients",
            debit=ttc_total,
            credit=Decimal("0"),
            tiers_name=client_name,
            tiers_ice=client_ice,
        )
        db.add(el)
        entry_lines.append(el)
        total_debit += ttc_total
        line_order += 1

        # Crédit 7xxx par ligne + Crédit 4455 TVA
        for line in facture.lines:
            account_code = line.corrected_account_code or line.pcm_account_code or "7111"
            account_label = line.pcm_account_label or "Ventes"
            ht = _d(line.line_amount_ht)
            # Si tva_amount est vide, la calculer depuis le taux
            tva = _d(line.tva_amount)
            if tva == Decimal("0") and line.tva_rate:
                tva = ht * (_d(line.tva_rate) / Decimal("100"))

            el_ht = EntryLine(
                journal_entry_id=entry.id,
                invoice_line_id=line.id,
                line_order=line_order,
                account_code=account_code,
                account_label=account_label,
                debit=Decimal("0"),
                credit=ht,
                tiers_name=client_name,  # Ajouter le nom du client
                tiers_ice=client_ice,    # Ajouter ICE du client
            )
            db.add(el_ht)
            entry_lines.append(el_ht)
            total_credit += ht
            line_order += 1

            if tva > 0:
                el_tva = EntryLine(
                    journal_entry_id=entry.id,
                    invoice_line_id=line.id,
                    line_order=line_order,
                    account_code="4455",
                    account_label="TVA facturée",
                    debit=Decimal("0"),
                    credit=tva,
                    tiers_name=client_name,  # Ajouter aussi pour la TVA
                    tiers_ice=client_ice,     # Ajouter ICE du client
                )
                db.add(el_tva)
                entry_lines.append(el_tva)
                total_credit += tva
                line_order += 1

    elif is_avoir:
        # ── AVOIR ACHAT ──────────────────────────────────────────
        # Débit 4411 (Fournisseur) pour le TTC total
        ttc_total = _d(facture.montant_ttc)

        el = EntryLine(
            journal_entry_id=entry.id,
            line_order=line_order,
            account_code="4411",
            account_label="Fournisseurs",
            debit=ttc_total,
            credit=Decimal("0"),
            tiers_name=tiers_name,
            tiers_ice=tiers_ice,
        )
        db.add(el)
        entry_lines.append(el)
        total_debit += ttc_total
        line_order += 1

        # Crédit 6xxx + Crédit TVA par ligne
        for line in facture.lines:
            account_code = line.corrected_account_code or line.pcm_account_code or "6111"
            account_label = line.pcm_account_label or "Achats"
            ht = _d(line.line_amount_ht)
            # Si tva_amount est vide, la calculer depuis le taux
            tva = _d(line.tva_amount)
            if tva == Decimal("0") and line.tva_rate:
                tva = ht * (_d(line.tva_rate) / Decimal("100"))
            tva_account = _get_tva_account(line.pcm_class, invoice_type)

            el_ht = EntryLine(
                journal_entry_id=entry.id,
                invoice_line_id=line.id,
                line_order=line_order,
                account_code=account_code,
                account_label=account_label,
                debit=Decimal("0"),
                credit=ht,
                tiers_name=tiers_name,
                tiers_ice=tiers_ice,  # Ajouter ICE du fournisseur
            )
            db.add(el_ht)
            entry_lines.append(el_ht)
            total_credit += ht
            line_order += 1

            if tva > 0:
                el_tva = EntryLine(
                    journal_entry_id=entry.id,
                    invoice_line_id=line.id,
                    line_order=line_order,
                    account_code=tva_account,
                    account_label="TVA récupérable",
                    debit=Decimal("0"),
                    credit=tva,
                    tiers_name=tiers_name,
                    tiers_ice=tiers_ice,  # Ajouter ICE du fournisseur
                )
                db.add(el_tva)
                entry_lines.append(el_tva)
                total_credit += tva
                line_order += 1

    else:
        # ── ACHAT (charge ou immobilisation) ─────────────────────
        # Débit 6xxx ou 2xxx + Débit TVA par ligne
        for line in facture.lines:
            account_code = line.corrected_account_code or line.pcm_account_code or "6111"
            account_label = line.pcm_account_label or "Achats"
            ht = _d(line.line_amount_ht)
            # Si tva_amount est vide, la calculer depuis le taux
            tva = _d(line.tva_amount)
            if tva == Decimal("0") and line.tva_rate:
                tva = ht * (_d(line.tva_rate) / Decimal("100"))
            tva_account = _get_tva_account(line.pcm_class, invoice_type)

            el_ht = EntryLine(
                journal_entry_id=entry.id,
                invoice_line_id=line.id,
                line_order=line_order,
                account_code=account_code,
                account_label=account_label,
                debit=ht,
                credit=Decimal("0"),
                tiers_name=tiers_name,
                tiers_ice=tiers_ice,  # Ajouter ICE du fournisseur
            )
            db.add(el_ht)
            entry_lines.append(el_ht)
            total_debit += ht
            line_order += 1

            if tva > 0:
                el_tva = EntryLine(
                    journal_entry_id=entry.id,
                    invoice_line_id=line.id,
                    line_order=line_order,
                    account_code=tva_account,
                    account_label="TVA récupérable",
                    debit=tva,
                    credit=Decimal("0"),
                    tiers_name=tiers_name,
                    tiers_ice=tiers_ice,  # Ajouter ICE du fournisseur
                )
                db.add(el_tva)
                entry_lines.append(el_tva)
                total_debit += tva
                line_order += 1

        # Crédit 4411 (Fournisseur) pour le TTC total
        ttc_total = _d(facture.montant_ttc)
        el = EntryLine(
            journal_entry_id=entry.id,
            line_order=line_order,
            account_code="4411",
            account_label="Fournisseurs",
            debit=Decimal("0"),
            credit=ttc_total,
            tiers_name=tiers_name,
            tiers_ice=tiers_ice,
        )
        db.add(el)
        entry_lines.append(el)
        total_credit += ttc_total
        line_order += 1

    # Mise à jour des totaux
    entry.total_debit = total_debit
    entry.total_credit = total_credit

    # Backfill: si une ligne d'écriture référence une invoice_line_id et que
    # l'InvoiceLine n'a pas de pcm_account_code, copier l'account_code généré
    for el in entry_lines:
        try:
            if getattr(el, "invoice_line_id", None) and getattr(el, "account_code", None):
                inv = db.query(InvoiceLine).filter(InvoiceLine.id == el.invoice_line_id).first()
                if inv:
                    # n'écrase pas une correction manuelle
                    if not inv.corrected_account_code and not inv.pcm_account_code:
                        inv.pcm_account_code = el.account_code
                        # copier aussi le libellé si absent
                        if not inv.pcm_account_label and getattr(el, "account_label", None):
                            inv.pcm_account_label = el.account_label
                        db.add(inv)
        except Exception:
            # Ne pas stopper la génération d'écritures si le backfill échoue
            pass

    db.commit()
    db.refresh(entry)

    return entry


def check_balance(entry: JournalEntry) -> Dict[str, Any]:
    """Vérifie l'équilibre débit/crédit de l'écriture."""
    debit = _d(entry.total_debit)
    credit = _d(entry.total_credit)
    diff = abs(debit - credit)
    is_balanced = diff <= Decimal("0.01")

    return {
        "is_balanced": is_balanced,
        "total_debit": float(debit),
        "total_credit": float(credit),
        "difference": float(diff),
    }
