


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
#     if_frs: Optional[str] = None
#     ice_frs: Optional[str] = None
#     taux_tva: Optional[float] = None
#     id_paie: Optional[str] = None
#     date_paie: Optional[date] = None

#     ded_file_path: Optional[str] = None
#     ded_pdf_path: Optional[str] = None
#     ded_xlsx_path: Optional[str] = None


# class FactureCreate(FactureBase):
#     """
#     Pour créer une facture (upload/OCR).
#     Tout est optional car l'OCR peut rater des champs.
#     """
#     pass


# class FactureUpdate(BaseModel):
#     """
#     IMPORTANT: Update partiel (PATCH)
#     -> on envoie uniquement les champs à corriger.
#     """
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















# # schemas.py
# from datetime import date
# from typing import Optional

# from pydantic import BaseModel, Field, ConfigDict


# # -------------------------
# # SOCIETE
# # -------------------------
# class SocieteIn(BaseModel):
#     raison_sociale: str = Field(..., example="string")
#     if_fiscal: Optional[str] = Field(None, example="string")
#     ice: Optional[str] = Field(None, example="string")
#     rc: Optional[str] = Field(None, example="string")
#     adresse: Optional[str] = Field(None, example="string")

#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "raison_sociale": "string",
#                 "if_fiscal": "string",
#                 "ice": "string",
#                 "rc": "string",
#                 "adresse": "string",
#             }
#         }
#     )


# class SocieteOut(SocieteIn):
#     id: int
#     model_config = ConfigDict(from_attributes=True)


# # -------------------------
# # FACTURE
# # -------------------------
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
#     if_frs: Optional[str] = None
#     ice_frs: Optional[str] = None
#     taux_tva: Optional[float] = None
#     id_paie: Optional[str] = None
#     date_paie: Optional[date] = None

#     ded_file_path: Optional[str] = None
#     ded_pdf_path: Optional[str] = None
#     ded_xlsx_path: Optional[str] = None


# class FactureCreate(FactureBase):
#     """Tout optionnel, car OCR peut rater."""
#     pass


# class FactureUpdate(BaseModel):
#     """PATCH partiel."""
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

















from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# -------------------------
# SOCIETE
# -------------------------
class SocieteIn(BaseModel):
    raison_sociale: str
    if_fiscal: Optional[str] = None
    ice: Optional[str] = None
    rc: Optional[str] = None
    adresse: Optional[str] = None


class SocieteUpdate(BaseModel):
    raison_sociale: Optional[str] = None
    if_fiscal: Optional[str] = None
    ice: Optional[str] = None
    rc: Optional[str] = None
    adresse: Optional[str] = None


class SocieteOut(BaseModel):
    id: int
    raison_sociale: str
    if_fiscal: Optional[str] = None
    ice: Optional[str] = None
    rc: Optional[str] = None
    adresse: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# FACTURE
# -------------------------
class FactureOut(BaseModel):
    id: int
    societe_id: int

    operation_type: str
    operation_confidence: float

    fournisseur: Optional[str] = None
    date_facture: Optional[date] = None
    numero_facture: Optional[str] = None
    designation: Optional[str] = None

    montant_ht: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_ttc: Optional[float] = None

    statut: str

    if_frs: Optional[str] = None
    ice_frs: Optional[str] = None
    taux_tva: Optional[float] = None
    id_paie: Optional[str] = None
    date_paie: Optional[date] = None

    devise: Optional[str] = None

    ded_file_path: Optional[str] = None
    ded_pdf_path: Optional[str] = None
    ded_xlsx_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FactureUpdate(BaseModel):
    fournisseur: Optional[str] = None
    date_facture: Optional[date] = None
    numero_facture: Optional[str] = None
    designation: Optional[str] = None

    montant_ht: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_ttc: Optional[float] = None

    statut: Optional[str] = None

    if_frs: Optional[str] = None
    ice_frs: Optional[str] = None
    taux_tva: Optional[float] = None
    id_paie: Optional[str] = None
    date_paie: Optional[date] = None

    operation_type: Optional[str] = None
    operation_confidence: Optional[float] = None

    devise: Optional[str] = None

    ded_file_path: Optional[str] = None
    ded_pdf_path: Optional[str] = None
    ded_xlsx_path: Optional[str] = None
