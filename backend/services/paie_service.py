"""
paie_service.py — Calcul des bulletins de paie selon la législation marocaine 2024
Cotisations : CNSS (4.48% salarié / 10.64% patronal), AMO (2.26% / 3.94%), IR barème progressif
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from models import Employe, BulletinPaie, LignePaie, JournalEntry, EntryLine

# ──────────────────────────────────────────────────────────────────────────
# CONSTANTES FISCALES MAROC 2024
# ──────────────────────────────────────────────────────────────────────────

# CNSS
CNSS_SALARIE_TAUX    = Decimal("0.0448")
CNSS_PATRONAL_TAUX   = Decimal("0.1064")
CNSS_PLAFOND_MENSUEL = Decimal("6000")    # MAD

# AMO (Assurance Maladie Obligatoire)
AMO_SALARIE_TAUX     = Decimal("0.0226")
AMO_PATRONAL_TAUX    = Decimal("0.0394")

# Abattement forfaitaire frais professionnels (20% du brut, plafonné à 30 000 MAD/an)
ABAT_PROF_TAUX       = Decimal("0.20")
ABAT_PROF_PLAFOND_AN = Decimal("30000")

# Déduction par enfant à charge (mensuelle)
DEDUCTION_ENFANT_MENSUELLE = Decimal("30")   # 360 MAD/an / 12
MAX_ENFANTS_DEDUCTIBLES    = 6

# Barème IR mensuel progressif (tranches en MAD, taux, abattement mensuel)
# Format: (limite_haute, taux, abattement_fixe_mensuel)
BAREME_IR_MENSUEL = [
    (Decimal("2500"),  Decimal("0"),    Decimal("0")),
    (Decimal("4166"),  Decimal("0.10"), Decimal("250")),
    (Decimal("5000"),  Decimal("0.20"), Decimal("666.67")),
    (Decimal("6666"),  Decimal("0.30"), Decimal("1166.67")),
    (Decimal("15000"), Decimal("0.34"), Decimal("1433.33")),
    (None,             Decimal("0.38"), Decimal("2033.33")),  # Tranche supérieure
]


def _d(v) -> Decimal:
    """Convertit en Decimal sécurisé."""
    return Decimal(str(v or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ──────────────────────────────────────────────────────────────────────────
# CALCUL CNSS
# ──────────────────────────────────────────────────────────────────────────
def calculer_cnss(salaire_brut: Decimal) -> Dict[str, Decimal]:
    """Calcule les cotisations CNSS (salarié + patronal) avec plafonnement."""
    base = min(salaire_brut, CNSS_PLAFOND_MENSUEL)
    salarie  = (base * CNSS_SALARIE_TAUX).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    patronal = (base * CNSS_PATRONAL_TAUX).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"base": base, "salarie": salarie, "patronal": patronal}


# ──────────────────────────────────────────────────────────────────────────
# CALCUL AMO
# ──────────────────────────────────────────────────────────────────────────
def calculer_amo(salaire_brut: Decimal) -> Dict[str, Decimal]:
    """Calcule l'AMO (salarié + patronal), sans plafond."""
    salarie  = (salaire_brut * AMO_SALARIE_TAUX).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    patronal = (salaire_brut * AMO_PATRONAL_TAUX).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"salarie": salarie, "patronal": patronal}


# ──────────────────────────────────────────────────────────────────────────
# CALCUL IR (IGR)
# ──────────────────────────────────────────────────────────────────────────
def calculer_ir(salaire_brut: Decimal, cnss_salarie: Decimal,
                amo_salarie: Decimal, nb_enfants: int = 0) -> Decimal:
    """
    Calcule l'IR (Impôt sur le Revenu) mensuel selon le barème progressif marocain.
    Base imposable = Brut - CNSS salarié - AMO salarié - Abattement frais pro (20%)
    """
    # Abattement frais professionnels (20% du brut plafonné à 30 000 MAD/an = 2 500 MAD/mois)
    abat_pro = min(
        salaire_brut * ABAT_PROF_TAUX,
        ABAT_PROF_PLAFOND_AN / 12
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Base imposable
    base_imposable = salaire_brut - cnss_salarie - amo_salarie - abat_pro

    if base_imposable <= Decimal("0"):
        return Decimal("0")

    # Barème progressif
    ir_brut = Decimal("0")
    for limite_haute, taux, abat_fixe in BAREME_IR_MENSUEL:
        if limite_haute is None or base_imposable <= limite_haute:
            ir_brut = (base_imposable * taux - abat_fixe).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            break

    ir_brut = max(ir_brut, Decimal("0"))

    # Déduction pour charges de famille
    nb_enf = min(nb_enfants, MAX_ENFANTS_DEDUCTIBLES)
    deduction_famille = DEDUCTION_ENFANT_MENSUELLE * nb_enf

    ir_net = max(ir_brut - deduction_famille, Decimal("0"))
    return ir_net.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ──────────────────────────────────────────────────────────────────────────
# CALCUL COMPLET DU BULLETIN
# ──────────────────────────────────────────────────────────────────────────
def calculer_bulletin(
    employe: Employe,
    mois: int,
    annee: int,
    primes: Decimal = Decimal("0"),
    heures_sup: Decimal = Decimal("0"),
) -> Dict[str, Any]:
    """
    Calcule l'ensemble du bulletin de paie pour un employé et un mois donné.
    Retourne un dictionnaire complet avec toutes les lignes de détail.
    """
    salaire_base = _d(employe.salaire_base)

    # Prime d'ancienneté
    anciennete_pct = _d(employe.anciennete_pct or 0)
    prime_anciennete = (salaire_base * anciennete_pct / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Autres primes et heures sup
    primes = _d(primes)
    heures_sup = _d(heures_sup)

    # Salaire brut total
    salaire_brut = salaire_base + prime_anciennete + primes + heures_sup

    # Cotisations
    cnss = calculer_cnss(salaire_brut) if employe.affiliee_cnss else {"base": Decimal("0"), "salarie": Decimal("0"), "patronal": Decimal("0")}
    amo  = calculer_amo(salaire_brut)
    ir   = calculer_ir(salaire_brut, cnss["salarie"], amo["salarie"], employe.nb_enfants or 0)

    # Totaux
    total_retenues = cnss["salarie"] + amo["salarie"] + ir
    total_patronal = cnss["patronal"] + amo["patronal"]
    salaire_net    = salaire_brut - total_retenues
    cout_total     = salaire_brut + total_patronal

    # Lignes de détail
    lignes = [
        # GAINS
        {"libelle": "Salaire de base",        "type_ligne": "GAIN",    "montant": float(salaire_base),     "taux": None,   "ordre": 1},
        {"libelle": "Prime d'ancienneté",     "type_ligne": "GAIN",    "montant": float(prime_anciennete), "taux": float(anciennete_pct / 100), "ordre": 2},
        {"libelle": "Primes/Avantages",       "type_ligne": "GAIN",    "montant": float(primes),           "taux": None,   "ordre": 3},
        {"libelle": "Heures supplémentaires", "type_ligne": "GAIN",    "montant": float(heures_sup),       "taux": None,   "ordre": 4},
        # RETENUES SALARIALES
        {"libelle": "CNSS salarié (4.48%)",   "type_ligne": "RETENUE", "montant": float(cnss["salarie"]),  "taux": 0.0448, "base_calcul": float(cnss["base"]),  "ordre": 10},
        {"libelle": "AMO salarié (2.26%)",    "type_ligne": "RETENUE", "montant": float(amo["salarie"]),   "taux": 0.0226, "base_calcul": float(salaire_brut),  "ordre": 11},
        {"libelle": "IR/IGR retenu",          "type_ligne": "RETENUE", "montant": float(ir),               "taux": None,   "ordre": 12},
    ]

    return {
        "employe_id":      employe.id,
        "employe_nom":     f"{employe.prenom or ''} {employe.nom}".strip(),
        "mois":            mois,
        "annee":           annee,
        "salaire_base":    float(salaire_base),
        "prime_anciennete":float(prime_anciennete),
        "autres_gains":    float(primes + heures_sup),
        "salaire_brut":    float(salaire_brut),
        "cnss_salarie":    float(cnss["salarie"]),
        "amo_salarie":     float(amo["salarie"]),
        "ir_retenu":       float(ir),
        "total_retenues":  float(total_retenues),
        "cnss_patronal":   float(cnss["patronal"]),
        "amo_patronal":    float(amo["patronal"]),
        "total_patronal":  float(total_patronal),
        "salaire_net":     float(salaire_net),
        "cout_total_employeur": float(cout_total),
        "lignes":          [l for l in lignes if l["montant"] > 0],
    }


# ──────────────────────────────────────────────────────────────────────────
# SAUVEGARDE EN BASE
# ──────────────────────────────────────────────────────────────────────────
def sauvegarder_bulletin(employe: Employe, mois: int, annee: int,
                         primes: Decimal, heures_sup: Decimal,
                         db: Session) -> BulletinPaie:
    """Calcule et persiste un bulletin de paie en base de données."""
    data = calculer_bulletin(employe, mois, annee, primes, heures_sup)

    bulletin = BulletinPaie(
        employe_id      = employe.id,
        mois            = mois,
        annee           = annee,
        salaire_base    = data["salaire_base"],
        prime_anciennete= data["prime_anciennete"],
        autres_gains    = data["autres_gains"],
        salaire_brut    = data["salaire_brut"],
        cnss_salarie    = data["cnss_salarie"],
        amo_salarie     = data["amo_salarie"],
        ir_retenu       = data["ir_retenu"],
        total_retenues  = data["total_retenues"],
        cnss_patronal   = data["cnss_patronal"],
        amo_patronal    = data["amo_patronal"],
        total_patronal  = data["total_patronal"],
        salaire_net     = data["salaire_net"],
        cout_total_employeur = data["cout_total_employeur"],
        statut          = "BROUILLON",
    )
    db.add(bulletin)
    db.flush()

    for l in data["lignes"]:
        db.add(LignePaie(
            bulletin_id = bulletin.id,
            libelle     = l["libelle"],
            type_ligne  = l["type_ligne"],
            montant     = l["montant"],
            taux        = l.get("taux"),
            base_calcul = l.get("base_calcul"),
            ordre       = l.get("ordre", 0),
        ))

    db.commit()
    db.refresh(bulletin)
    return bulletin


# ──────────────────────────────────────────────────────────────────────────
# GÉNÉRATION ÉCRITURE COMPTABLE OD
# ──────────────────────────────────────────────────────────────────────────
def generer_ecriture_paie(bulletin: BulletinPaie, db: Session) -> JournalEntry:
    """
    Génère l'écriture comptable de paie (journal OD).
    PCM Maroc :
      Débit  6171  Rémunérations du personnel (salaire brut)
      Débit  6174  Charges sociales patronales (CNSS + AMO patronal)
      Crédit 4441  Personnel — rémunérations dues (salaire net)
      Crédit 4443  Organismes sociaux — CNSS (part salarié + part patronal)
      Crédit 4444  État — IR retenu à la source
      Crédit 4447  Organismes sociaux — AMO (part salarié + patronal)
    """
    from decimal import Decimal as D
    _d2 = lambda v: D(str(v or 0)).quantize(D("0.01"), rounding=ROUND_HALF_UP)

    employe = bulletin.employe
    mois_label = f"{bulletin.mois:02d}/{bulletin.annee}"
    nom_emp = f"{employe.prenom or ''} {employe.nom}".strip() if employe else f"Emp#{bulletin.employe_id}"

    entry = JournalEntry(
        facture_id  = None,
        journal_code= "OD",
        entry_date  = date(bulletin.annee, bulletin.mois, 28),  # Fin de mois approx.
        reference   = f"PAIE-{bulletin.id}-{mois_label}",
        description = f"Bulletin de paie {mois_label} — {nom_emp}",
        is_validated= False,
    )
    db.add(entry)
    db.flush()

    brut     = _d2(bulletin.salaire_brut)
    net      = _d2(bulletin.salaire_net)
    cnss_s   = _d2(bulletin.cnss_salarie)
    amo_s    = _d2(bulletin.amo_salarie)
    ir       = _d2(bulletin.ir_retenu)
    cnss_p   = _d2(bulletin.cnss_patronal)
    amo_p    = _d2(bulletin.amo_patronal)
    pat_total= _d2(bulletin.total_patronal)

    lines = [
        # Débits
        (1,  "6171", "Rémunérations du personnel",         brut,      D("0")),
        (2,  "6174", "Charges sociales patronales (CNSS+AMO)", pat_total, D("0")),
        # Crédits
        (3,  "4441", f"Salaire net à payer — {nom_emp}",   D("0"), net),
        (4,  "4443", "CNSS — part salarié",                D("0"), cnss_s),
        (5,  "4443", "CNSS — part patronale",              D("0"), cnss_p),
        (6,  "4447", "AMO — part salarié",                 D("0"), amo_s),
        (7,  "4447", "AMO — part patronale",               D("0"), amo_p),
        (8,  "4444", "IR/IGR retenu à la source",          D("0"), ir),
    ]

    total_debit = sum(l[3] for l in lines)
    total_credit = sum(l[4] for l in lines)

    for order, acct, lbl, deb, cre in lines:
        if deb > 0 or cre > 0:
            db.add(EntryLine(
                ecriture_journal_id = entry.id,
                line_order = order,
                account_code = acct,
                account_label = lbl,
                debit = deb,
                credit = cre,
                tiers_name = nom_emp if "4441" in acct else None,
            ))

    entry.total_debit  = total_debit
    entry.total_credit = total_credit

    bulletin.journal_entry_id = entry.id
    db.commit()
    db.refresh(entry)
    return entry
