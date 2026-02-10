# from sqlalchemy.orm import Session
# from models import Facture
# from schemas import FactureCreate

# def create_facture(db: Session, facture: FactureCreate):
#     obj = Facture(**facture.model_dump())
#     db.add(obj)
#     db.commit()
#     db.refresh(obj)
#     return obj

# def get_factures(db: Session):
#     return db.query(Facture).order_by(Facture.id.desc()).all()




from sqlalchemy.orm import Session
from models import Facture
from schemas import FactureCreate, FactureUpdate


def get_factures(db: Session):
    return db.query(Facture).order_by(Facture.id.desc()).all()


def get_facture_by_id(db: Session, facture_id: int):
    return db.query(Facture).filter(Facture.id == facture_id).first()


def create_facture(db: Session, facture: FactureCreate):
    obj = Facture(
        fournisseur=facture.fournisseur,
        date_facture=facture.date_facture,
        montant_ht=facture.montant_ht,
        montant_tva=facture.montant_tva,
        montant_ttc=facture.montant_ttc,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_facture(db: Session, facture_id: int, facture: FactureUpdate):
    obj = get_facture_by_id(db, facture_id)
    if not obj:
        return None

    # Compatible Pydantic v1/v2
    if hasattr(facture, "model_dump"):
        data = facture.model_dump(exclude_unset=True)
    else:
        data = facture.dict(exclude_unset=True)

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
