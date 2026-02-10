



# from datetime import date
# from pydantic import BaseModel, ConfigDict
# from typing import Optional


# class FactureBase(BaseModel):
#     fournisseur: Optional[str] = None
#     date_facture: Optional[date] = None
#     montant_ht: Optional[float] = None
#     montant_tva: Optional[float] = None
#     montant_ttc: Optional[float] = None


# class FactureCreate(FactureBase):
#     pass


# class FactureUpdate(FactureBase):
#     # Tout optionnel pour permettre update partiel
#     pass


# class FactureOut(FactureBase):
#     id: int

#     # Pydantic v2
#     model_config = ConfigDict(from_attributes=True)





from datetime import date
from typing import Optional, List
from pydantic import BaseModel


class FactureBase(BaseModel):
    fournisseur: Optional[str] = None
    date_facture: Optional[date] = None
    montant_ht: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_ttc: Optional[float] = None


class FactureCreate(FactureBase):
    pass


class FactureUpdate(FactureBase):
    # on autorise aussi la modification du statut
    statut: Optional[str] = None


class FactureOut(FactureBase):
    id: int
    statut: Optional[str] = None

    class Config:
        from_attributes = True  # Pydantic v2 (équiv. orm_mode v1)


# ---- Ecritures ----
class EcritureOut(BaseModel):
    id: int
    facture_id: int
    compte: Optional[str] = None
    libelle: Optional[str] = None
    debit: Optional[float] = None
    credit: Optional[float] = None

    class Config:
        from_attributes = True
