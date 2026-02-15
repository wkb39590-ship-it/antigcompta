# # backend/services/accounting_rules.py
# from dataclasses import dataclass
# from typing import List, Literal, Optional, Tuple
# from datetime import date

# OperationType = Literal["achat", "vente", "banque", "caisse", "od"]

# @dataclass
# class PieceComptable:
#     operation: OperationType
#     numero_piece: str
#     date_operation: date
#     designation: str

#     # tiers
#     tiers_nom: Optional[str] = None

#     # montants
#     montant_ht: float = 0.0
#     taux_tva: float = 20.0  # défaut Maroc 20%

#     # optionnel si on veut forcer TTC
#     montant_ttc: Optional[float] = None


# @dataclass
# class EcritureLine:
#     compte: str
#     intitule: str
#     debit: float
#     credit: float


# def _round2(x: float) -> float:
#     return round(float(x or 0.0), 2)


# def compute_tva_and_ttc(montant_ht: float, taux_tva: float, montant_ttc: Optional[float] = None) -> Tuple[float, float]:
#     ht = _round2(montant_ht)
#     taux = float(taux_tva or 0.0)

#     if montant_ttc is not None:
#         ttc = _round2(montant_ttc)
#         tva = _round2(ttc - ht)
#         return tva, ttc

#     tva = _round2(ht * (taux / 100.0))
#     ttc = _round2(ht + tva)
#     return tva, ttc


# def get_journal_code(operation: OperationType) -> str:
#     return {
#         "achat": "ACH",
#         "vente": "VTE",
#         "banque": "BQ",
#         "caisse": "CA",
#         "od": "OD",
#     }.get(operation, "OD")


# def generate_lines_pcm(piece: PieceComptable) -> List[EcritureLine]:
#     """
#     Règles PCM simplifiées (Maroc):
#     - Achat:
#         Débit 611 (Charges/Achats) : HT
#         Débit 3455 (TVA récupérable) : TVA
#         Crédit 4411 (Fournisseurs) : TTC
#     - Vente:
#         Débit 3421 (Clients) : TTC
#         Crédit 711 (Ventes) : HT
#         Crédit 4455 (TVA collectée) : TVA
#     """

#     if not piece.numero_piece:
#         raise ValueError("Numéro de pièce obligatoire (numéro facture / pièce).")
#     if not piece.date_operation:
#         raise ValueError("Date d'opération obligatoire.")
#     if piece.montant_ht is None:
#         raise ValueError("montant_ht obligatoire.")
#     if float(piece.montant_ht) < 0:
#         raise ValueError("montant_ht invalide (négatif).")

#     tva, ttc = compute_tva_and_ttc(piece.montant_ht, piece.taux_tva, piece.montant_ttc)

#     designation = (piece.designation or "").strip() or "Opération"
#     tiers = (piece.tiers_nom or "").strip()

#     ht = _round2(piece.montant_ht)
#     tva = _round2(tva)
#     ttc = _round2(ttc)

#     if piece.operation == "achat":
#         return [
#             EcritureLine("611", f"Achats/Charges - {designation}", debit=ht, credit=0.0),
#             EcritureLine("3455", "TVA récupérable", debit=tva, credit=0.0),
#             EcritureLine("4411", f"Fournisseurs {tiers}".strip(), debit=0.0, credit=ttc),
#         ]

#     if piece.operation == "vente":
#         return [
#             EcritureLine("3421", f"Clients {tiers}".strip(), debit=ttc, credit=0.0),
#             EcritureLine("711", f"Ventes - {designation}", debit=0.0, credit=ht),
#             EcritureLine("4455", "TVA collectée", debit=0.0, credit=tva),
#         ]

#     # Banque / Caisse / OD : on laisse OD générique (à étendre plus tard)
#     # Ici on crée juste une OD équilibrée “placeholder” si besoin
#     raise ValueError(f"Operation non supportée pour génération automatique: {piece.operation}")















# services/accounting_rules.py
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class PieceComptable:
    operation: str              # achat | vente | banque | caisse | od
    numero_piece: str
    date_operation: "date"
    designation: str
    tiers_nom: Optional[str]
    montant_ht: float
    taux_tva: float
    montant_ttc: Optional[float] = None


def get_journal_code(operation: str) -> str:
    op = (operation or "").lower().strip()
    return {
        "achat": "ACH",
        "vente": "VTE",
        "banque": "BQ",
        "caisse": "CAIS",
        "od": "OD",
    }.get(op, "OD")


def compute_tva_and_ttc(montant_ht: float, taux_tva: float, montant_ttc: Optional[float] = None) -> Tuple[float, float, float]:
    ht = float(montant_ht or 0.0)
    taux = float(taux_tva or 0.0)

    tva = round(ht * (taux / 100.0), 2)

    if montant_ttc is None:
        ttc = round(ht + tva, 2)
    else:
        ttc = round(float(montant_ttc), 2)
        # si ttc fourni mais incohérent, on recalc tva = ttc-ht
        if abs((ht + tva) - ttc) > 0.5:
            tva = round(ttc - ht, 2)

    return ht, tva, ttc


def generate_lines_pcm(piece: PieceComptable) -> List[dict]:
    """
    Règles PCM (version MVP) :
    - achat  : 611 (D HT), 3455 (D TVA), 4411 (C TTC)
    - vente  : 3421 (D TTC), 711 (C HT), 4455 (C TVA)
    """
    op = piece.operation.lower().strip()
    ht, tva, ttc = compute_tva_and_ttc(piece.montant_ht, piece.taux_tva, piece.montant_ttc)

    tiers = (piece.tiers_nom or "").strip() or ("Fournisseur" if op == "achat" else "Client")

    if op == "achat":
        return [
            {"compte": "611", "libelle": piece.designation or "Achats", "debit": ht, "credit": 0.0},
            {"compte": "3455", "libelle": "TVA déductible", "debit": tva, "credit": 0.0},
            {"compte": "4411", "libelle": tiers, "debit": 0.0, "credit": ttc},
        ]

    if op == "vente":
        return [
            {"compte": "3421", "libelle": tiers, "debit": ttc, "credit": 0.0},
            {"compte": "711", "libelle": piece.designation or "Ventes", "debit": 0.0, "credit": ht},
            {"compte": "4455", "libelle": "TVA collectée", "debit": 0.0, "credit": tva},
        ]

    # pour l’instant (banque/caisse/od) => on force OD simple (à compléter plus tard)
    # mais on ne laisse pas vide: on retourne une écriture équilibrée 0
    return [
        {"compte": "0000", "libelle": "OD (à paramétrer)", "debit": 0.0, "credit": 0.0},
    ]
