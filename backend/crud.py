

# from __future__ import annotations
# from typing import Optional

# from sqlalchemy.orm import Session

# from models import Facture, EcritureComptable
# from schemas import FactureCreate, FactureUpdate


# # -------------------------
# # FACTURES
# # -------------------------
# def get_factures(db: Session):
#     return db.query(Facture).order_by(Facture.id.desc()).all()


# def get_facture_by_id(db: Session, facture_id: int):
#     return db.query(Facture).filter(Facture.id == facture_id).first()


# def get_facture(db: Session, facture_id: int):
#     return get_facture_by_id(db, facture_id)


# def create_facture(db: Session, facture: FactureCreate):
#     obj = Facture(
#         fournisseur=facture.fournisseur,
#         date_facture=facture.date_facture,
#         montant_ht=facture.montant_ht,
#         montant_tva=facture.montant_tva,
#         montant_ttc=facture.montant_ttc,

#         # ✅ AJOUT ICI
#         numero_facture=getattr(facture, "numero_facture", None),
#         designation=getattr(facture, "designation", None),
#         if_frs=getattr(facture, "if_frs", None),
#         ice_frs=getattr(facture, "ice_frs", None),
#         taux_tva=getattr(facture, "taux_tva", None),
#     )
#     db.add(obj)
#     db.commit()
#     db.refresh(obj)
#     return obj


# def update_facture(db: Session, facture_id: int, facture: FactureUpdate):
#     obj = get_facture_by_id(db, facture_id)
#     if not obj:
#         return None

#     data = facture.model_dump(exclude_unset=True) if hasattr(facture, "model_dump") else facture.dict(exclude_unset=True)

#     for key, value in data.items():
#         setattr(obj, key, value)

#     db.commit()
#     db.refresh(obj)
#     return obj


# def delete_facture(db: Session, facture_id: int):
#     obj = get_facture_by_id(db, facture_id)
#     if not obj:
#         return False
#     db.delete(obj)
#     db.commit()
#     return True


# def valider_facture(db: Session, facture_id: int):
#     obj = get_facture_by_id(db, facture_id)
#     if not obj:
#         return None
#     obj.statut = "VALIDEE"
#     db.commit()
#     db.refresh(obj)
#     return obj


# # -------------------------
# # ECRITURES COMPTABLES
# # -------------------------
# def get_ecritures_by_facture_id(db: Session, facture_id: int):
#     return (
#         db.query(EcritureComptable)
#         .filter(EcritureComptable.facture_id == facture_id)
#         .order_by(EcritureComptable.id.asc())
#         .all()
#     )


# def get_ecritures_by_facture(db: Session, facture_id: int):
#     return get_ecritures_by_facture_id(db, facture_id)


# # -------------------------
# # DED PATHS
# # -------------------------
# def set_ded_file_path(db: Session, facture_id: int, path: str):
#     obj = get_facture_by_id(db, facture_id)
#     if not obj:
#         return None
#     obj.ded_file_path = path
#     db.commit()
#     db.refresh(obj)
#     return obj


# def set_ded_paths(
#     db: Session,
#     facture_id: int,
#     xlsx_path: Optional[str] = None,
#     pdf_path: Optional[str] = None,
# ):
#     facture = get_facture_by_id(db, facture_id)
#     if not facture:
#         return None

#     if xlsx_path:
#         facture.ded_xlsx_path = xlsx_path
#         facture.ded_file_path = xlsx_path

#     if pdf_path:
#         facture.ded_pdf_path = pdf_path

#     db.commit()
#     db.refresh(facture)
#     return facture




















from __future__ import annotations
from typing import Optional

from sqlalchemy.orm import Session

from models import Facture, EcritureComptable
from schemas import FactureCreate, FactureUpdate


# -------------------------
# FACTURES
# -------------------------
def get_factures(db: Session):
    return db.query(Facture).order_by(Facture.id.desc()).all()


def get_facture_by_id(db: Session, facture_id: int):
    return db.query(Facture).filter(Facture.id == facture_id).first()


def get_facture(db: Session, facture_id: int):
    return get_facture_by_id(db, facture_id)


def create_facture(db: Session, facture: FactureCreate):
    obj = Facture(
        fournisseur=facture.fournisseur,
        date_facture=facture.date_facture,
        montant_ht=facture.montant_ht,
        montant_tva=facture.montant_tva,
        montant_ttc=facture.montant_ttc,

        # ✅ Tous les champs nécessaires
        numero_facture=facture.numero_facture,
        designation=facture.designation,
        if_frs=facture.if_frs,
        ice_frs=facture.ice_frs,
        taux_tva=facture.taux_tva,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_facture(db: Session, facture_id: int, facture: FactureUpdate):
    obj = get_facture_by_id(db, facture_id)
    if not obj:
        return None

    data = facture.model_dump(exclude_unset=True) if hasattr(facture, "model_dump") else facture.dict(exclude_unset=True)

    for key, value in data.items():
        setattr(obj, key, value)

    db.commit()
    db.refresh(obj)
    return obj


def delete_facture(db: Session, facture_id: int):
    obj = get_facture_by_id(db, facture_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


def valider_facture(db: Session, facture_id: int):
    obj = get_facture_by_id(db, facture_id)
    if not obj:
        return None
    obj.statut = "VALIDEE"
    db.commit()
    db.refresh(obj)
    return obj


# -------------------------
# ECRITURES COMPTABLES
# -------------------------
def get_ecritures_by_facture_id(db: Session, facture_id: int):
    return (
        db.query(EcritureComptable)
        .filter(EcritureComptable.facture_id == facture_id)
        .order_by(EcritureComptable.id.asc())
        .all()
    )


def get_ecritures_by_facture(db: Session, facture_id: int):
    return get_ecritures_by_facture_id(db, facture_id)