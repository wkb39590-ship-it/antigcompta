"""
immobilisation_service.py — Calcul plan d'amortissement & écritures PCM
Supporte méthodes linéaire et dégressive (CGNC Maroc)
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from models import Immobilisation, LigneAmortissement, JournalEntry, EntryLine


def _d(v) -> Decimal:
    """Convertit en Decimal sécurisé."""
    if v is None:
        return Decimal("0")
    return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculer_taux(immo: Immobilisation) -> Decimal:
    """Calcule le taux d'amortissement selon la méthode."""
    if immo.duree_amortissement <= 0:
        return Decimal("0")
    taux_lineaire = Decimal("1") / Decimal(str(immo.duree_amortissement))
    if (immo.methode or "LINEAIRE").upper() == "DEGRESSIF":
        # Coefficients fiscaux marocains : durée <= 3 ans → x1.5, <= 5 ans → x2, > 5 ans → x3
        duree = immo.duree_amortissement
        if duree <= 3:
            coeff = Decimal("1.5")
        elif duree <= 5:
            coeff = Decimal("2")
        else:
            coeff = Decimal("3")
        return (taux_lineaire * coeff).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return taux_lineaire.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def calculer_plan_amortissement(immo: Immobilisation) -> List[Dict[str, Any]]:
    """
    Calcule le plan d'amortissement complet pour une immobilisation.
    Retourne une liste de dicts par année : annee, dotation, cumul, vnc.
    """
    valeur = _d(immo.valeur_acquisition)
    duree = immo.duree_amortissement
    methode = (immo.methode or "LINEAIRE").upper()
    annee_base = immo.date_acquisition.year if immo.date_acquisition else 2025

    plan = []
    cumul = Decimal("0")
    vnc = valeur  # Valeur Nette Comptable de départ

    for i in range(duree):
        annee = annee_base + i

        if methode == "DEGRESSIF":
            taux = calculer_taux(immo)
            dotation = (vnc * taux).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            # Dernière année : on amortit le reste
            if i == duree - 1:
                dotation = vnc
        else:
            # Linéaire : dotation constante = Valeur / Durée
            dotation = (valeur / Decimal(str(duree))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            # Dernière année : ajustement arrondi
            if i == duree - 1:
                dotation = valeur - cumul

        cumul += dotation
        vnc -= dotation

        plan.append({
            "annee": annee,
            "dotation_annuelle": float(dotation),
            "amortissement_cumule": float(cumul),
            "valeur_nette_comptable": float(max(vnc, Decimal("0"))),
        })

    return plan


def sauvegarder_plan(immo: Immobilisation, db: Session) -> List[LigneAmortissement]:
    """Sauvegarde le plan d'amortissement calculé en base de données."""
    # Supprimer les anciennes lignes
    for old in immo.lignes_amortissement:
        db.delete(old)
    db.flush()

    plan = calculer_plan_amortissement(immo)
    lignes = []
    for ligne in plan:
        l = LigneAmortissement(
            immobilisation_id=immo.id,
            annee=ligne["annee"],
            dotation_annuelle=ligne["dotation_annuelle"],
            amortissement_cumule=ligne["amortissement_cumule"],
            valeur_nette_comptable=ligne["valeur_nette_comptable"],
            ecriture_generee=False,
        )
        db.add(l)
        lignes.append(l)

    db.flush()
    return lignes


def generer_ecriture_acquisition(immo: Immobilisation, db: Session) -> JournalEntry:
    """
    Génère l'écriture comptable d'acquisition d'immobilisation.
    PCM Maroc :
      Débit  2xxx (Actif immobilisé)
      Débit  34552 (TVA récupérable sur immobilisations)
      Crédit 4411 (Fournisseur)
    """
    valeur = _d(immo.valeur_acquisition)
    tva = _d(immo.tva_acquisition)
    ttc = valeur + tva

    compte_actif = immo.compte_actif_pcm or "2355"

    entry = JournalEntry(
        societe_id=immo.societe_id,
        facture_id=immo.facture_id,
        journal_code="ACH",
        entry_date=immo.date_acquisition,
        reference=f"IMMO-{immo.id}",
        description=f"Acquisition immobilisation : {immo.designation}",
        is_validated=False,
    )
    db.add(entry)
    db.flush()

    lines = []
    order = 1

    # Débit compte actif immobilisé
    lines.append(EntryLine(
        ecriture_journal_id=entry.id,
        line_order=order,
        account_code=compte_actif,
        account_label=f"Immobilisation — {immo.designation}",
        debit=valeur,
        credit=Decimal("0"),
    ))
    order += 1

    # Débit TVA sur immobilisations (si applicable)
    if tva > Decimal("0"):
        lines.append(EntryLine(
            ecriture_journal_id=entry.id,
            line_order=order,
            account_code="34552",
            account_label="TVA récupérable sur immobilisations",
            debit=tva,
            credit=Decimal("0"),
        ))
        order += 1

    # Crédit fournisseur
    lines.append(EntryLine(
        ecriture_journal_id=entry.id,
        line_order=order,
        account_code="4411",
        account_label="Fournisseurs",
        debit=Decimal("0"),
        credit=ttc,
    ))

    for l in lines:
        db.add(l)

    entry.total_debit = valeur + tva
    entry.total_credit = ttc
    db.commit()
    db.refresh(entry)
    return entry


def generer_ecriture_dotation(immo: Immobilisation, annee: int, db: Session) -> JournalEntry:
    """
    Génère l'écriture de dotation aux amortissements pour une année.
    PCM Maroc :
      Débit  6193 (Dotations aux amortissements)
      Crédit 28xx (Amortissements cumulés)
    """
    # Trouver la ligne du plan pour cette année
    ligne = next(
        (l for l in immo.lignes_amortissement if l.annee == annee), None
    )
    if not ligne:
        # Recalculer si pas encore sauvegardé
        plan = calculer_plan_amortissement(immo)
        ligne_dict = next((p for p in plan if p["annee"] == annee), None)
        if not ligne_dict:
            raise ValueError(f"Aucune ligne d'amortissement pour l'année {annee}")
        dotation = _d(ligne_dict["dotation_annuelle"])
    else:
        dotation = _d(ligne.dotation_annuelle)

    compte_dotation = immo.compte_dotation_pcm or "6193"
    compte_amort = immo.compte_amort_pcm or "2835"

    from datetime import date
    entry = JournalEntry(
        societe_id=immo.societe_id,
        facture_id=immo.facture_id,
        journal_code="OD",
        entry_date=date(annee, 12, 31),
        reference=f"DOT-{immo.id}-{annee}",
        description=f"Dotation amortissement {annee} — {immo.designation}",
        is_validated=False,
    )
    db.add(entry)
    db.flush()

    db.add(EntryLine(
        ecriture_journal_id=entry.id,
        line_order=1,
        account_code=compte_dotation,
        account_label="Dotations aux amortissements",
        debit=dotation,
        credit=Decimal("0"),
    ))
    db.add(EntryLine(
        ecriture_journal_id=entry.id,
        line_order=2,
        account_code=compte_amort,
        account_label="Amortissements cumulés",
        debit=Decimal("0"),
        credit=dotation,
    ))

    entry.total_debit = dotation
    entry.total_credit = dotation

    # Marquer la ligne comme traitée
    if ligne:
        ligne.ecriture_generee = True

    db.commit()
    db.refresh(entry)
    return entry
