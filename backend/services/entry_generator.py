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
    is_avoir_achat = invoice_type in ["AVOIR", "AVOIR_ACHAT"]
    is_avoir_vente = invoice_type == "AVOIR_VENTE"
    is_vente = invoice_type == "VENTE"

    # Déterminer le code journal
    journal_map = {
        "ACHAT": "ACH",
        "VENTE": "VTE",
        "AVOIR": "ACH",
        "AVOIR_ACHAT": "ACH",
        "AVOIR_VENTE": "VTE",
        "NOTE_FRAIS": "OD",
        "IMMOBILISATION": "IMMO",
        "immobilisation": "IMMO",
    }
    journal_code = journal_map.get(invoice_type, "OD")

    # Déterminer le nom du tiers (doit être l'autre partie, pas la société elle-même)
    company_name = ""
    if facture.societe:
        company_name = (facture.societe.raison_sociale or "").lower().strip()
    
    sn = (facture.supplier_name or facture.fournisseur or "").lower().strip()
    cn = (facture.client_name or "").lower().strip()
    
    # Par défaut, on prend le fournisseur
    actual_tiers_name = facture.supplier_name or facture.fournisseur or "Fournisseur"
    actual_tiers_ice = facture.supplier_ice or facture.ice_frs
    
    # Si c'est une vente, on prend normalement le client
    if is_vente or is_avoir_vente:
        actual_tiers_name = facture.client_name or "Client"
        actual_tiers_ice = facture.client_ice
        
    # LOGIQUE INTELLIGENTE : Si le nom choisi semble être la société elle-même, on prend l'autre
    if company_name:
        current_choice = (actual_tiers_name or "").lower().strip()
        # Si notre choix actuel contient le nom de la société (ex: "comptoir arrahma" dans "ste comptoir arrahma")
        if company_name in current_choice or current_choice in company_name:
            # On bascule sur l'autre nom disponible
            if is_vente or is_avoir_vente:
                # Dans une vente, si le 'client' c'est nous, alors le vrai tiers est dans 'supplier_name'
                if sn and not (company_name in sn or sn in company_name):
                    actual_tiers_name = facture.supplier_name or facture.fournisseur
                    actual_tiers_ice = facture.supplier_ice or facture.ice_frs
            else:
                # Dans un achat, si le 'fournisseur' c'est nous, alors le vrai tiers est dans 'client_name'
                if cn and not (company_name in cn or cn in company_name):
                    actual_tiers_name = facture.client_name
                    actual_tiers_ice = facture.client_ice

    # Créer l'en-tête de l'écriture
    entry = JournalEntry(
        facture_id=facture.id,
        societe_id=facture.societe_id,
        journal_code=journal_code,
        entry_date=facture.date_facture,
        reference=facture.numero_facture,
        description=f"Facture {facture.numero_facture or ''} — {actual_tiers_name or ''}",
        is_validated=False,
    )
    db.add(entry)
    db.flush()  # pour obtenir entry.id

    entry_lines = []
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    line_order = 1

    if is_vente:
        # ── VENTE STANDARD ───────────────────────────────────────
        ttc_total = _d(facture.montant_ttc)

        el = EntryLine(
            ecriture_journal_id=entry.id,
            line_order=line_order,
            account_code="3421",
            account_label="Clients",
            debit=ttc_total,
            credit=Decimal("0"),
            tiers_name=actual_tiers_name,
            tiers_ice=actual_tiers_ice,
        )
        db.add(el)
        entry_lines.append(el)
        total_debit += ttc_total
        line_order += 1

        for line in facture.lines:
            raw_account = line.pcm_account_code or "7111"
            account_code = line.corrected_account_code or raw_account
            account_label = line.pcm_account_label or "Ventes"
            ht = _d(line.line_amount_ht)
            tva = _d(line.tva_amount)
            if tva == Decimal("0") and line.tva_rate and _d(line.tva_rate) > 0:
                tva = (ht * (_d(line.tva_rate) / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            el_ht = EntryLine(ecriture_journal_id=entry.id, line_order=line_order, account_code=account_code,
                              account_label=account_label, debit=Decimal("0"), credit=ht,
                              tiers_name=actual_tiers_name, tiers_ice=actual_tiers_ice)
            db.add(el_ht); entry_lines.append(el_ht); total_credit += ht; line_order += 1

            if tva > 0:
                el_tva = EntryLine(ecriture_journal_id=entry.id, line_order=line_order, account_code="4455",
                                   account_label="TVA facturée", debit=Decimal("0"), credit=tva,
                                   tiers_name=actual_tiers_name, tiers_ice=actual_tiers_ice)
                db.add(el_tva); entry_lines.append(el_tva); total_credit += tva; line_order += 1

    elif is_avoir_vente:
        # ── AVOIR CLIENT (VENTE) ─────────────────────────────────
        # Inverse de la vente : Débit 7xxx, Débit 4455, Crédit 3421
        ttc_total = _d(facture.montant_ttc)

        for line in facture.lines:
            account_code = line.corrected_account_code or line.pcm_account_code or "7111"
            account_label = line.pcm_account_label or "Ventes (Avoir)"
            ht = _d(line.line_amount_ht)
            tva = _d(line.tva_amount)
            if tva == Decimal("0") and line.tva_rate:
                tva = (ht * (_d(line.tva_rate) / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # Débit HT (Annulation vente)
            el_ht = EntryLine(ecriture_journal_id=entry.id, line_order=line_order, account_code=account_code,
                              account_label=account_label, debit=ht, credit=Decimal("0"),
                              tiers_name=actual_tiers_name, tiers_ice=actual_tiers_ice)
            db.add(el_ht); entry_lines.append(el_ht); total_debit += ht; line_order += 1

            # Débit TVA (Annulation TVA collectée)
            if tva > 0:
                el_tva = EntryLine(ecriture_journal_id=entry.id, line_order=line_order, account_code="4455",
                                   account_label="TVA facturée (Avoir)", debit=tva, credit=Decimal("0"),
                                   tiers_name=actual_tiers_name, tiers_ice=actual_tiers_ice)
                db.add(el_tva); entry_lines.append(el_tva); total_debit += tva; line_order += 1

        # Crédit 3421 (Client)
        el_client = EntryLine(ecriture_journal_id=entry.id, line_order=line_order, account_code="3421",
                              account_label="Clients (Avoir)", debit=Decimal("0"), credit=ttc_total,
                              tiers_name=actual_tiers_name, tiers_ice=actual_tiers_ice)
        db.add(el_client); entry_lines.append(el_client); total_credit += ttc_total; line_order += 1

    elif is_avoir_achat:
        # ── AVOIR FOURNISSEUR (ACHAT) ────────────────────────────
        # Inverse de l'achat : Débit 4411, Crédit 6xxx, Crédit 3455
        ttc_total = _d(facture.montant_ttc)
        el = EntryLine(ecriture_journal_id=entry.id, line_order=line_order, account_code="4411",
                       account_label="Fournisseurs (Avoir)", debit=ttc_total, credit=Decimal("0"),
                       tiers_name=actual_tiers_name, tiers_ice=actual_tiers_ice)
        db.add(el); entry_lines.append(el); total_debit += ttc_total; line_order += 1

        for line in facture.lines:
            account_code = line.corrected_account_code or line.pcm_account_code or "6111"
            account_label = line.pcm_account_label or "Achats (Avoir)"
            ht = _d(line.line_amount_ht)
            tva = _d(line.tva_amount)
            if tva == Decimal("0") and line.tva_rate:
                tva = (ht * (_d(line.tva_rate) / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            tva_account = _get_tva_account(line.pcm_class, invoice_type)

            el_ht = EntryLine(ecriture_journal_id=entry.id, line_order=line_order, account_code=account_code,
                              account_label=account_label, debit=Decimal("0"), credit=ht,
                              tiers_name=actual_tiers_name, tiers_ice=actual_tiers_ice)
            db.add(el_ht); entry_lines.append(el_ht); total_credit += ht; line_order += 1

            if tva > 0:
                el_tva = EntryLine(ecriture_journal_id=entry.id, line_order=line_order, account_code=tva_account,
                                   account_label="TVA récupérable (Avoir)", debit=Decimal("0"), credit=tva,
                                   tiers_name=actual_tiers_name, tiers_ice=actual_tiers_ice)
                db.add(el_tva); entry_lines.append(el_tva); total_credit += tva; line_order += 1

    else:
        # ── ACHAT (charge ou immobilisation) ─────────────────────
        # Débit 6xxx ou 2xxx + Débit TVA par ligne
        for line in facture.lines:
            # Sécurité: Ne pas utiliser de compte de classe 7 (Produits) pour un achat
            # sauf si l'utilisateur l'a explicitement corrigé (corrected_account_code)
            raw_account = line.pcm_account_code or "6111"
            if not line.corrected_account_code and raw_account.startswith("7"):
                account_code = "6111" # Redresser vers un compte d'achat par défaut
                account_label = "Achats de marchandises (redressé)"
            else:
                account_code = line.corrected_account_code or raw_account
                account_label = line.pcm_account_label or "Achats"

            ht = _d(line.line_amount_ht)
            
            # Priorité absolue au montant TVA extrait
            tva = _d(line.tva_amount)
            # On ne recalcule que si tva_amount est strictement nul ET qu'un taux est présent
            if tva == Decimal("0") and line.tva_rate and _d(line.tva_rate) > 0:
                tva = (ht * (_d(line.tva_rate) / Decimal("100"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
            tva_account = _get_tva_account(line.pcm_class, invoice_type)

            el_ht = EntryLine(
                ecriture_journal_id=entry.id,
                line_order=line_order,
                account_code=account_code,
                account_label=account_label,
                debit=ht,
                credit=Decimal("0"),
                tiers_name=actual_tiers_name,
                tiers_ice=actual_tiers_ice,
            )
            db.add(el_ht)
            entry_lines.append(el_ht)
            total_debit += ht
            line_order += 1

            if tva > 0:
                el_tva = EntryLine(
                    ecriture_journal_id=entry.id,
                    line_order=line_order,
                    account_code=tva_account,
                    account_label="TVA récupérable",
                    debit=tva,
                    credit=Decimal("0"),
                    tiers_name=actual_tiers_name,
                    tiers_ice=actual_tiers_ice,
                )
                db.add(el_tva)
                entry_lines.append(el_tva)
                total_debit += tva
                line_order += 1

        # Crédit 4411 (Fournisseur) pour le TTC total
        ttc_total = _d(facture.montant_ttc)
        el = EntryLine(
            ecriture_journal_id=entry.id,
            line_order=line_order,
            account_code="4411",
            account_label="Fournisseurs",
            debit=Decimal("0"),
            credit=ttc_total,
            tiers_name=actual_tiers_name,
            tiers_ice=actual_tiers_ice,
        )
        db.add(el)
        entry_lines.append(el)
        total_credit += ttc_total
        line_order += 1

    # Mise à jour des totaux
    entry.total_debit = total_debit
    entry.total_credit = total_credit


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
