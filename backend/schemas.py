

# from datetime import date, datetime
# from typing import Optional, List
# from pydantic import BaseModel, ConfigDict


# # -------------------------
# # SOCIETE
# # -------------------------
# class SocieteIn(BaseModel):
#     raison_sociale: str
#     if_fiscal: Optional[str] = None
#     ice: Optional[str] = None
#     rc: Optional[str] = None
#     adresse: Optional[str] = None


# class SocieteUpdate(BaseModel):
#     raison_sociale: Optional[str] = None
#     if_fiscal: Optional[str] = None
#     ice: Optional[str] = None
#     rc: Optional[str] = None
#     adresse: Optional[str] = None


# class SocieteOut(BaseModel):
#     id: int
#     raison_sociale: str
#     if_fiscal: Optional[str] = None
#     ice: Optional[str] = None
#     rc: Optional[str] = None
#     adresse: Optional[str] = None
#     created_at: datetime

#     model_config = ConfigDict(from_attributes=True)


# # -------------------------
# # FACTURE
# # -------------------------
# class FactureOut(BaseModel):
#     id: int
#     societe_id: int

#     operation_type: str
#     operation_confidence: float

#     fournisseur: Optional[str] = None
#     date_facture: Optional[date] = None
#     numero_facture: Optional[str] = None
#     designation: Optional[str] = None

#     montant_ht: Optional[float] = None
#     montant_tva: Optional[float] = None
#     montant_ttc: Optional[float] = None

#     statut: str

#     if_frs: Optional[str] = None
#     ice_frs: Optional[str] = None
#     taux_tva: Optional[float] = None
#     id_paie: Optional[str] = None
#     date_paie: Optional[date] = None

#     devise: Optional[str] = None

#     ded_file_path: Optional[str] = None
#     ded_pdf_path: Optional[str] = None
#     ded_xlsx_path: Optional[str] = None

#     model_config = ConfigDict(from_attributes=True)


# class FactureUpdate(BaseModel):
#     fournisseur: Optional[str] = None
#     date_facture: Optional[date] = None
#     numero_facture: Optional[str] = None
#     designation: Optional[str] = None

#     montant_ht: Optional[float] = None
#     montant_tva: Optional[float] = None
#     montant_ttc: Optional[float] = None

#     statut: Optional[str] = None

#     if_frs: Optional[str] = None
#     ice_frs: Optional[str] = None
#     taux_tva: Optional[float] = None
#     id_paie: Optional[str] = None
#     date_paie: Optional[date] = None

#     operation_type: Optional[str] = None
#     operation_confidence: Optional[float] = None

#     devise: Optional[str] = None

#     ded_file_path: Optional[str] = None
#     ded_pdf_path: Optional[str] = None
#     ded_xlsx_path: Optional[str] = None





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


# -------------------------
# ECRITURES (HEADER + LIGNES)
# -------------------------
class EcritureLigneOut(BaseModel):
    id: int
    ecriture_id: int
    compte: str
    libelle: Optional[str] = None
    debit: float
    credit: float

    model_config = ConfigDict(from_attributes=True)


class EcritureOut(BaseModel):
    id: int
    societe_id: int
    facture_id: int
    operation: str
    journal: str
    numero_piece: str
    date_operation: date
    tiers_nom: Optional[str] = None
    statut: str
    created_at: datetime
    validated_at: Optional[datetime] = None
    libelle: Optional[str] = None
    total_debit: float
    total_credit: float
    lignes: List[EcritureLigneOut] = []

    model_config = ConfigDict(from_attributes=True)


class GenererEcrituresResponse(BaseModel):
    facture_id: int
    journal: str
    total_debit: float
    total_credit: float
    ecriture: EcritureOut
