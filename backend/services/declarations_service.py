
# # valider facture ⇒ (1) check champs ⇒ (2) générer écritures EcrituresService.generate_for_facture() ⇒ (3) créer/ajouter ligne DGI ⇒ (4) recalcul totaux ⇒ (5) commit dans route.


# # backend/services/declarations_service.py

# from typing import Optional, Tuple
# from sqlalchemy.orm import Session
# from sqlalchemy import func

# from models import Facture, DeclarationMensuelle, DeclarationLigne



# class DeclarationsService:
#     @staticmethod
#     def _get_year_month(facture: Facture) -> Tuple[int, int]:
#         if not facture.date_facture:
#             raise ValueError("date_facture est obligatoire pour créer/mettre à jour la déclaration mensuelle.")
#         return facture.date_facture.year, facture.date_facture.month

#     @staticmethod
#     def get_or_create_month(db: Session, annee: int, mois: int) -> DeclarationMensuelle:
#         decl = (
#             db.query(DeclarationMensuelle)
#             .filter(DeclarationMensuelle.annee == annee, DeclarationMensuelle.mois == mois)
#             .first()
#         )
#         if decl:
#             return decl

#         decl = DeclarationMensuelle(annee=annee, mois=mois, statut="brouillon")
#         db.add(decl)
#         db.commit()
#         db.refresh(decl)
#         return decl

#     @staticmethod
#     def upsert_ligne_for_facture(db: Session, facture: Facture) -> DeclarationLigne:
#         annee, mois = DeclarationsService._get_year_month(facture)
#         decl = DeclarationsService.get_or_create_month(db, annee, mois)

#         # ligne existante ?
#         ligne = db.query(DeclarationLigne).filter(DeclarationLigne.facture_id == facture.id).first()

#         payload = dict(
#             declaration_id=decl.id,
#             facture_id=facture.id,
#             fact_num=facture.numero_facture,
#             designation=facture.designation,
#             m_ht=float(facture.montant_ht or 0),
#             tva=float(facture.montant_tva or 0),
#             m_ttc=float(facture.montant_ttc or 0),
#             if_frs=facture.if_frs,
#             lib_frss=facture.fournisseur,
#             ice_frs=facture.ice_frs,
#             taux=facture.taux_tva,
#             date_pai=facture.date_paie,
#             date_fac=facture.date_facture,
#         )

#         if ligne:
#             # si la facture change de mois => déplacer la ligne
#             for k, v in payload.items():
#                 setattr(ligne, k, v)
#         else:
#             ligne = DeclarationLigne(**payload)
#             db.add(ligne)

#         db.commit()
#         db.refresh(ligne)

#         # recalcul totaux
#         DeclarationsService.recompute_totals(db, decl.id)
#         db.refresh(decl)

#         return ligne

#     @staticmethod
#     def recompute_totals(db: Session, declaration_id: int) -> None:
#         sums = (
#             db.query(
#                 func.coalesce(func.sum(DeclarationLigne.m_ht), 0.0),
#                 func.coalesce(func.sum(DeclarationLigne.tva), 0.0),
#                 func.coalesce(func.sum(DeclarationLigne.m_ttc), 0.0),
#             )
#             .filter(DeclarationLigne.declaration_id == declaration_id)
#             .one()
#         )
#         total_ht, total_tva, total_ttc = sums

#         db.query(DeclarationMensuelle).filter(DeclarationMensuelle.id == declaration_id).update(
#             dict(total_ht=float(total_ht), total_tva=float(total_tva), total_ttc=float(total_ttc))
#         )
#         db.commit()













# # backend/services/declarations_service.py

# from typing import Tuple
# from sqlalchemy.orm import Session
# from sqlalchemy import func

# from models import Facture, DeclarationMensuelle, DeclarationLigne


# class DeclarationsService:
#     @staticmethod
#     def _get_year_month(facture: Facture) -> Tuple[int, int]:
#         if not facture.date_facture:
#             raise ValueError("date_facture est obligatoire pour créer/mettre à jour la déclaration mensuelle.")
#         return facture.date_facture.year, facture.date_facture.month

#     @staticmethod
#     def get_or_create_month(db: Session, annee: int, mois: int) -> DeclarationMensuelle:
#         decl = (
#             db.query(DeclarationMensuelle)
#             .filter(DeclarationMensuelle.annee == annee, DeclarationMensuelle.mois == mois)
#             .first()
#         )
#         if decl:
#             return decl

#         decl = DeclarationMensuelle(annee=annee, mois=mois, statut="brouillon", total_ht=0, total_tva=0, total_ttc=0)
#         db.add(decl)
#         db.commit()
#         db.refresh(decl)
#         return decl

#     @staticmethod
#     def upsert_ligne_for_facture(db: Session, facture: Facture) -> DeclarationLigne:
#         if not facture.id:
#             raise ValueError("facture.id est NULL (la facture doit être enregistrée en DB avant d'ajouter la déclaration).")

#         annee, mois = DeclarationsService._get_year_month(facture)
#         decl = DeclarationsService.get_or_create_month(db, annee, mois)

#         # 🔥 IMPORTANT: on cherche une ligne existante POUR CETTE FACTURE
#         ligne = db.query(DeclarationLigne).filter(DeclarationLigne.facture_id == facture.id).first()

#         payload = dict(
#             declaration_id=decl.id,
#             facture_id=facture.id,  # ✅ PAS NULL
#             fact_num=facture.numero_facture,
#             designation=facture.designation,
#             m_ht=float(facture.montant_ht or 0),
#             tva=float(facture.montant_tva or 0),
#             m_ttc=float(facture.montant_ttc or 0),
#             if_frs=facture.if_frs,
#             lib_frss=facture.fournisseur,
#             ice_frs=facture.ice_frs,
#             taux=float(facture.taux_tva or 0),
#             date_pai=facture.date_paie,
#             date_fac=facture.date_facture,
#         )

#         if ligne:
#             # update
#             for k, v in payload.items():
#                 setattr(ligne, k, v)
#         else:
#             ligne = DeclarationLigne(**payload)
#             db.add(ligne)

#         db.commit()
#         db.refresh(ligne)

#         # recalcul totaux
#         DeclarationsService.recompute_totals(db, decl.id)
#         db.refresh(decl)

#         return ligne

#     @staticmethod
#     def recompute_totals(db: Session, declaration_id: int) -> None:
#         total_ht, total_tva, total_ttc = (
#             db.query(
#                 func.coalesce(func.sum(DeclarationLigne.m_ht), 0.0),
#                 func.coalesce(func.sum(DeclarationLigne.tva), 0.0),
#                 func.coalesce(func.sum(DeclarationLigne.m_ttc), 0.0),
#             )
#             .filter(DeclarationLigne.declaration_id == declaration_id)
#             .one()
#         )

#         db.query(DeclarationMensuelle).filter(DeclarationMensuelle.id == declaration_id).update(
#             dict(
#                 total_ht=float(total_ht),
#                 total_tva=float(total_tva),
#                 total_ttc=float(total_ttc),
#             )
#         )
#         db.commit()















# # services/declarations_service.py
# from __future__ import annotations

# from typing import Tuple
# from sqlalchemy.orm import Session
# from sqlalchemy import func

# from models import Facture, DeclarationMensuelle, DeclarationLigne


# class DeclarationsService:
#     @staticmethod
#     def _get_year_month(facture: Facture) -> Tuple[int, int]:
#         if not facture.date_facture:
#             raise ValueError("date_facture obligatoire")
#         return facture.date_facture.year, facture.date_facture.month

#     @staticmethod
#     def get_or_create_month(db: Session, annee: int, mois: int) -> DeclarationMensuelle:
#         decl = (
#             db.query(DeclarationMensuelle)
#             .filter(DeclarationMensuelle.annee == annee, DeclarationMensuelle.mois == mois)
#             .first()
#         )
#         if decl:
#             return decl

#         decl = DeclarationMensuelle(annee=annee, mois=mois, statut="brouillon", total_ht=0, total_tva=0, total_ttc=0)
#         db.add(decl)
#         db.commit()
#         db.refresh(decl)
#         return decl

#     @staticmethod
#     def upsert_ligne_for_facture(db: Session, facture: Facture) -> Tuple[DeclarationMensuelle, DeclarationLigne]:
#         annee, mois = DeclarationsService._get_year_month(facture)
#         decl = DeclarationsService.get_or_create_month(db, annee, mois)

#         # ✅ Anti-doublon: chercher par (declaration_id, facture_id)
#         ligne = (
#             db.query(DeclarationLigne)
#             .filter(
#                 DeclarationLigne.declaration_id == decl.id,
#                 DeclarationLigne.facture_id == facture.id,
#             )
#             .first()
#         )

#         payload = dict(
#             declaration_id=decl.id,
#             facture_id=facture.id,
#             fact_num=facture.numero_facture,
#             designation=facture.designation,
#             m_ht=float(facture.montant_ht or 0),
#             tva=float(facture.montant_tva or 0),
#             m_ttc=float(facture.montant_ttc or 0),
#             if_frs=facture.if_frs,
#             lib_frss=facture.fournisseur,
#             ice_frs=facture.ice_frs,
#             taux=float(facture.taux_tva or 0),
#             date_pai=facture.date_paie,
#             date_fac=facture.date_facture,
#         )

#         if ligne:
#             for k, v in payload.items():
#                 setattr(ligne, k, v)
#         else:
#             ligne = DeclarationLigne(**payload)
#             db.add(ligne)

#         db.commit()
#         db.refresh(ligne)

#         DeclarationsService.recompute_totals(db, decl.id)
#         db.refresh(decl)
#         return decl, ligne

#     @staticmethod
#     def recompute_totals(db: Session, declaration_id: int) -> None:
#         total_ht, total_tva, total_ttc = (
#             db.query(
#                 func.coalesce(func.sum(DeclarationLigne.m_ht), 0.0),
#                 func.coalesce(func.sum(DeclarationLigne.tva), 0.0),
#                 func.coalesce(func.sum(DeclarationLigne.m_ttc), 0.0),
#             )
#             .filter(DeclarationLigne.declaration_id == declaration_id)
#             .one()
#         )

#         db.query(DeclarationMensuelle).filter(DeclarationMensuelle.id == declaration_id).update(
#             dict(total_ht=float(total_ht), total_tva=float(total_tva), total_ttc=float(total_ttc))
#         )
#         db.commit()









from typing import Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Facture, DeclarationMensuelle, DeclarationLigne


class DeclarationsService:

    # -------------------------------------------------
    # Extraire année/mois depuis la facture
    # -------------------------------------------------
    @staticmethod
    def _get_year_month(facture: Facture) -> Tuple[int, int]:
        if not facture.date_facture:
            raise ValueError("date_facture est obligatoire.")
        return facture.date_facture.year, facture.date_facture.month


    # -------------------------------------------------
    # Récupérer ou créer déclaration mensuelle
    # -------------------------------------------------
    @staticmethod
    def get_or_create_month(db: Session, annee: int, mois: int) -> DeclarationMensuelle:

        decl = (
            db.query(DeclarationMensuelle)
            .filter(
                DeclarationMensuelle.annee == annee,
                DeclarationMensuelle.mois == mois,
            )
            .first()
        )

        if decl:
            return decl

        # ⚠️ IMPORTANT : PAS DE "statut" ici
        decl = DeclarationMensuelle(
            annee=annee,
            mois=mois,
            total_ht=0.0,
            total_tva=0.0,
            total_ttc=0.0,
        )

        db.add(decl)
        db.commit()
        db.refresh(decl)

        return decl


    # -------------------------------------------------
    # Ajouter / mettre à jour ligne déclaration
    # -------------------------------------------------
    @staticmethod
    def upsert_ligne_for_facture(db: Session, facture: Facture):

        annee, mois = DeclarationsService._get_year_month(facture)
        decl = DeclarationsService.get_or_create_month(db, annee, mois)

        # Vérifie si la ligne existe déjà
        ligne = (
            db.query(DeclarationLigne)
            .filter(DeclarationLigne.facture_id == facture.id)
            .first()
        )

        payload = dict(
            declaration_id=decl.id,
            facture_id=facture.id,
            fact_num=facture.numero_facture,
            designation=facture.designation,
            m_ht=float(facture.montant_ht or 0),
            tva=float(facture.montant_tva or 0),
            m_ttc=float(facture.montant_ttc or 0),
            if_frs=facture.if_frs,
            lib_frss=facture.fournisseur,
            ice_frs=facture.ice_frs,
            taux=facture.taux_tva,
            date_pai=facture.date_paie,
            date_fac=facture.date_facture,
        )

        if ligne:
            # Update existante
            for k, v in payload.items():
                setattr(ligne, k, v)
        else:
            # Nouvelle ligne
            ligne = DeclarationLigne(**payload)
            db.add(ligne)

        db.commit()
        db.refresh(ligne)

        # Recalculer totaux
        DeclarationsService.recompute_totals(db, decl.id)
        db.refresh(decl)

        return decl, ligne


    # -------------------------------------------------
    # Recalcul totaux mensuels
    # -------------------------------------------------
    @staticmethod
    def recompute_totals(db: Session, declaration_id: int):

        sums = (
            db.query(
                func.coalesce(func.sum(DeclarationLigne.m_ht), 0.0),
                func.coalesce(func.sum(DeclarationLigne.tva), 0.0),
                func.coalesce(func.sum(DeclarationLigne.m_ttc), 0.0),
            )
            .filter(DeclarationLigne.declaration_id == declaration_id)
            .one()
        )

        total_ht, total_tva, total_ttc = sums

        db.query(DeclarationMensuelle).filter(
            DeclarationMensuelle.id == declaration_id
        ).update(
            {
                "total_ht": float(total_ht),
                "total_tva": float(total_tva),
                "total_ttc": float(total_ttc),
            }
        )

        db.commit()
