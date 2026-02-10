# from pydantic import BaseModel
# from typing import Optional
# from datetime import date

# class FactureCreate(BaseModel):
#     fournisseur: Optional[str] = None
#     date_facture: Optional[date] = None
#     montant_ht: Optional[float] = None
#     montant_tva: Optional[float] = None
#     montant_ttc: Optional[float] = None

# class FactureOut(FactureCreate):
#     id: int

#     class Config:
#         from_attributes = True




from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional


class FactureBase(BaseModel):
    fournisseur: Optional[str] = None
    date_facture: Optional[date] = None
    montant_ht: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_ttc: Optional[float] = None


class FactureCreate(FactureBase):
    pass


class FactureUpdate(FactureBase):
    # Tout optionnel pour permettre update partiel
    pass


class FactureOut(FactureBase):
    id: int

    # Pydantic v2
    model_config = ConfigDict(from_attributes=True)
