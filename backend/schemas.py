


# from datetime import date
# from typing import Optional
# from pydantic import BaseModel, ConfigDict


# class FactureBase(BaseModel):
#     fournisseur: Optional[str] = None
#     date_facture: Optional[date] = None

#     montant_ht: Optional[float] = None
#     montant_tva: Optional[float] = None
#     montant_ttc: Optional[float] = None

#     statut: Optional[str] = "brouillon"

#     numero_facture: Optional[str] = None
#     designation: Optional[str] = None

#     # DED
#     if_frs: Optional[str] = None     # IF SOCIETE (émetteur) (compat DB)
#     ice_frs: Optional[str] = None    # ICE fournisseur
#     taux_tva: Optional[float] = None
#     id_paie: Optional[str] = None
#     date_paie: Optional[date] = None

#     ded_file_path: Optional[str] = None
#     ded_pdf_path: Optional[str] = None
#     ded_xlsx_path: Optional[str] = None


# class FactureCreate(FactureBase):
#     pass


# class FactureUpdate(BaseModel):
#     fournisseur: Optional[str] = None
#     date_facture: Optional[date] = None
#     montant_ht: Optional[float] = None
#     montant_tva: Optional[float] = None
#     montant_ttc: Optional[float] = None
#     statut: Optional[str] = None

#     numero_facture: Optional[str] = None
#     designation: Optional[str] = None

#     if_frs: Optional[str] = None
#     ice_frs: Optional[str] = None
#     taux_tva: Optional[float] = None
#     id_paie: Optional[str] = None
#     date_paie: Optional[date] = None

#     ded_file_path: Optional[str] = None
#     ded_pdf_path: Optional[str] = None
#     ded_xlsx_path: Optional[str] = None


# class FactureOut(FactureBase):
#     id: int
#     model_config = ConfigDict(from_attributes=True)


# class EcritureOut(BaseModel):
#     id: int
#     facture_id: int
#     compte: str
#     libelle: Optional[str] = None
#     debit: float
#     credit: float
#     model_config = ConfigDict(from_attributes=True)
















from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FactureBase(BaseModel):
    fournisseur: Optional[str] = None
    date_facture: Optional[date] = None

    montant_ht: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_ttc: Optional[float] = None

    statut: Optional[str] = "brouillon"

    numero_facture: Optional[str] = None
    designation: Optional[str] = None

    # DED
    if_frs: Optional[str] = None
    ice_frs: Optional[str] = None
    taux_tva: Optional[float] = None
    id_paie: Optional[str] = None
    date_paie: Optional[date] = None

    ded_file_path: Optional[str] = None
    ded_pdf_path: Optional[str] = None
    ded_xlsx_path: Optional[str] = None


class FactureCreate(FactureBase):
    """
    Pour créer une facture (upload/OCR).
    Tout est optional car l'OCR peut rater des champs.
    """
    pass


class FactureUpdate(BaseModel):
    """
    IMPORTANT: Update partiel (PATCH)
    -> on envoie uniquement les champs à corriger.
    """
    fournisseur: Optional[str] = None
    date_facture: Optional[date] = None

    montant_ht: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_ttc: Optional[float] = None

    statut: Optional[str] = None

    numero_facture: Optional[str] = None
    designation: Optional[str] = None

    if_frs: Optional[str] = None
    ice_frs: Optional[str] = None
    taux_tva: Optional[float] = None
    id_paie: Optional[str] = None
    date_paie: Optional[date] = None

    ded_file_path: Optional[str] = None
    ded_pdf_path: Optional[str] = None
    ded_xlsx_path: Optional[str] = None


class FactureOut(FactureBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class EcritureOut(BaseModel):
    id: int
    facture_id: int
    compte: str
    libelle: Optional[str] = None
    debit: float
    credit: float
    model_config = ConfigDict(from_attributes=True)
