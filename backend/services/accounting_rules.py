# backend/services/accounting_rules.py

from dataclasses import dataclass


@dataclass
class AccountingAccounts:
    compte_charge: str = "6111"     # Achats / charges (exemple)
    compte_tva: str = "3455"        # TVA récupérable
    compte_fournisseur: str = "4411"  # Fournisseurs


def get_accounts_for_facture() -> AccountingAccounts:
    """
    Plus tard, tu peux rendre ça dynamique (selon type facture, fournisseur, etc.)
    """
    return AccountingAccounts()
