





# # services/accounting_rules.py
# from dataclasses import dataclass
# from typing import List, Optional, Tuple


# @dataclass
# class PieceComptable:
#     operation: str              # achat | vente | banque | caisse | od
#     numero_piece: str
#     date_operation: "date"
#     designation: str
#     tiers_nom: Optional[str]
#     montant_ht: float
#     taux_tva: float
#     montant_ttc: Optional[float] = None


# def get_journal_code(operation: str) -> str:
#     op = (operation or "").lower().strip()
#     return {
#         "achat": "ACH",
#         "vente": "VTE",
#         "banque": "BQ",
#         "caisse": "CAIS",
#         "od": "OD",
#     }.get(op, "OD")


# def compute_tva_and_ttc(montant_ht: float, taux_tva: float, montant_ttc: Optional[float] = None) -> Tuple[float, float, float]:
#     ht = float(montant_ht or 0.0)
#     taux = float(taux_tva or 0.0)

#     tva = round(ht * (taux / 100.0), 2)

#     if montant_ttc is None:
#         ttc = round(ht + tva, 2)
#     else:
#         ttc = round(float(montant_ttc), 2)
#         # si ttc fourni mais incohérent, on recalc tva = ttc-ht
#         if abs((ht + tva) - ttc) > 0.5:
#             tva = round(ttc - ht, 2)

#     return ht, tva, ttc


# def generate_lines_pcm(piece: PieceComptable) -> List[dict]:
#     """
#     Règles PCM (version MVP) :
#     - achat  : 611 (D HT), 3455 (D TVA), 4411 (C TTC)
#     - vente  : 3421 (D TTC), 711 (C HT), 4455 (C TVA)
#     """
#     op = piece.operation.lower().strip()
#     ht, tva, ttc = compute_tva_and_ttc(piece.montant_ht, piece.taux_tva, piece.montant_ttc)

#     tiers = (piece.tiers_nom or "").strip() or ("Fournisseur" if op == "achat" else "Client")

#     if op == "achat":
#         return [
#             {"compte": "611", "libelle": piece.designation or "Achats", "debit": ht, "credit": 0.0},
#             {"compte": "3455", "libelle": "TVA déductible", "debit": tva, "credit": 0.0},
#             {"compte": "4411", "libelle": tiers, "debit": 0.0, "credit": ttc},
#         ]

#     if op == "vente":
#         return [
#             {"compte": "3421", "libelle": tiers, "debit": ttc, "credit": 0.0},
#             {"compte": "711", "libelle": piece.designation or "Ventes", "debit": 0.0, "credit": ht},
#             {"compte": "4455", "libelle": "TVA collectée", "debit": 0.0, "credit": tva},
#         ]

#     # pour l’instant (banque/caisse/od) => on force OD simple (à compléter plus tard)
#     # mais on ne laisse pas vide: on retourne une écriture équilibrée 0
#     return [
#         {"compte": "0000", "libelle": "OD (à paramétrer)", "debit": 0.0, "credit": 0.0},
#     ]







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


def compute_tva_and_ttc(
    montant_ht: float,
    taux_tva: float,
    montant_ttc: Optional[float] = None
) -> Tuple[float, float, float]:
    ht = float(montant_ht or 0.0)
    taux = float(taux_tva or 0.0)

    tva = round(ht * (taux / 100.0), 2)

    if montant_ttc is None:
        ttc = round(ht + tva, 2)
    else:
        ttc = round(float(montant_ttc), 2)
        # si ttc fourni mais incohérent, on recalc TVA = TTC - HT
        if abs((ht + tva) - ttc) > 0.5:
            tva = round(ttc - ht, 2)

    return ht, tva, ttc


def generate_lines_pcm(piece: PieceComptable) -> List[dict]:
    """
    Règles PCM (MVP) :
    - achat  : 611 (D HT), 3455 (D TVA), 4411 (C TTC)
    - vente  : 3421 (D TTC), 711 (C HT), 4455 (C TVA)
    """
    op = (piece.operation or "").lower().strip()
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

    # autres opérations => OD vide (à compléter plus tard)
    return [
        {"compte": "0000", "libelle": "OD (à paramétrer)", "debit": 0.0, "credit": 0.0},
    ]
