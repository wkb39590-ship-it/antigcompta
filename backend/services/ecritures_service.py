# # backend/services/ecritures_service.py

# from sqlalchemy.orm import Session
# from typing import List

# from models import Facture, EcritureComptable
# from services.accounting_rules import get_accounts_for_facture


# class EcrituresService:
#     @staticmethod
#     def _check_amounts(facture: Facture):
#         if facture.montant_ht is None or facture.montant_tva is None or facture.montant_ttc is None:
#             raise ValueError("La facture doit avoir montant_ht, montant_tva, montant_ttc (non null).")

#         # tolérance petite (float)
#         if abs((facture.montant_ht + facture.montant_tva) - facture.montant_ttc) > 0.01:
#             raise ValueError("Facture invalide: HT + TVA != TTC (écart > 0.01).")

#     @staticmethod
#     def generate_for_facture(db: Session, facture: Facture, replace: bool = True) -> List[EcritureComptable]:
#         """
#         Génère 3 lignes:
#         - Débit charge (HT)
#         - Débit TVA (TVA)
#         - Crédit fournisseur (TTC)

#         replace=True: supprime les anciennes écritures de la facture avant de régénérer.
#         """
#         EcrituresService._check_amounts(facture)

#         accounts = get_accounts_for_facture()

#         if replace:
#             db.query(EcritureComptable).filter(EcritureComptable.facture_id == facture.id).delete()

#         e1 = EcritureComptable(
#             facture_id=facture.id,
#             compte=accounts.compte_charge,
#             libelle=f"Achat - {facture.fournisseur or 'Fournisseur'}",
#             debit=float(facture.montant_ht),
#             credit=0.0,
#         )

#         e2 = EcritureComptable(
#             facture_id=facture.id,
#             compte=accounts.compte_tva,
#             libelle="TVA déductible",
#             debit=float(facture.montant_tva),
#             credit=0.0,
#         )

#         e3 = EcritureComptable(
#             facture_id=facture.id,
#             compte=accounts.compte_fournisseur,
#             libelle=f"Fournisseur - {facture.fournisseur or 'Fournisseur'}",
#             debit=0.0,
#             credit=float(facture.montant_ttc),
#         )

#         entries = [e1, e2, e3]

#         # Vérifier l'équilibre débit/crédit
#         total_debit = sum(x.debit for x in entries)
#         total_credit = sum(x.credit for x in entries)
#         if abs(total_debit - total_credit) > 0.01:
#             raise ValueError("Écritures non équilibrées (débit != crédit).")

#         db.add_all(entries)
#         db.commit()
#         for x in entries:
#             db.refresh(x)

#         return entries












# backend/services/ecritures_service.py

from sqlalchemy.orm import Session
from typing import List

from models import Facture, EcritureComptable
from services.accounting_rules import get_accounts_for_facture


class EcrituresService:
    @staticmethod
    def _check_amounts(facture: Facture):
        if facture.montant_ht is None or facture.montant_tva is None or facture.montant_ttc is None:
            raise ValueError("La facture doit avoir montant_ht, montant_tva, montant_ttc (non null).")

        # tolérance petite (float)
        if abs((facture.montant_ht + facture.montant_tva) - facture.montant_ttc) > 0.01:
            raise ValueError("Facture invalide: HT + TVA != TTC (écart > 0.01).")

    @staticmethod
    def generate_for_facture(db: Session, facture: Facture, replace: bool = True) -> List[EcritureComptable]:
        """
        Génère 3 lignes:
        - Débit charge (HT)
        - Débit TVA (TVA)
        - Crédit fournisseur (TTC)

        replace=True: supprime les anciennes écritures de la facture avant de régénérer.
        """
        EcrituresService._check_amounts(facture)

        accounts = get_accounts_for_facture()

        if replace:
            db.query(EcritureComptable).filter(EcritureComptable.facture_id == facture.id).delete()

        e1 = EcritureComptable(
            facture_id=facture.id,
            compte=accounts.compte_charge,
            libelle=f"Achat - {facture.fournisseur or 'Fournisseur'}",
            debit=float(facture.montant_ht),
            credit=0.0,
        )

        e2 = EcritureComptable(
            facture_id=facture.id,
            compte=accounts.compte_tva,
            libelle="TVA déductible",
            debit=float(facture.montant_tva),
            credit=0.0,
        )

        e3 = EcritureComptable(
            facture_id=facture.id,
            compte=accounts.compte_fournisseur,
            libelle=f"Fournisseur - {facture.fournisseur or 'Fournisseur'}",
            debit=0.0,
            credit=float(facture.montant_ttc),
        )

        entries = [e1, e2, e3]

        # Vérifier l'équilibre débit/crédit
        total_debit = sum(x.debit for x in entries)
        total_credit = sum(x.credit for x in entries)
        if abs(total_debit - total_credit) > 0.01:
            raise ValueError("Écritures non équilibrées (débit != crédit).")

        db.add_all(entries)
        db.commit()
        for x in entries:
            db.refresh(x)

        return entries
