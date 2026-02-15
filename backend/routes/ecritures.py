




# # routes/ecritures.py
# from datetime import datetime
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import EcritureComptable

# router = APIRouter(prefix="/ecritures", tags=["ecritures"])


# @router.post("/{ecriture_id}/valider")
# def valider_ecriture(ecriture_id: int, db: Session = Depends(get_db)):
#     e = db.query(EcritureComptable).filter(EcritureComptable.id == ecriture_id).first()
#     if not e:
#         raise HTTPException(status_code=404, detail="Ecriture introuvable")

#     if abs((e.total_debit or 0) - (e.total_credit or 0)) > 0.01:
#         raise HTTPException(status_code=400, detail="Ecriture non équilibrée (debit != credit)")

#     e.statut = "validee"
#     e.validated_at = datetime.utcnow()

#     db.commit()
#     db.refresh(e)
#     return {"message": "Ecriture validée", "id": e.id, "validated_at": e.validated_at}



























# # routes/ecritures.py
# from datetime import datetime
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import EcritureComptable, Facture
# from schemas import PieceComptableIn, EcritureOut
# from services.ecritures_service import EcrituresService

# router = APIRouter(prefix="/ecritures", tags=["ecritures"])


# @router.post("/generer", response_model=EcritureOut)
# def generer_ecriture(payload: PieceComptableIn, db: Session = Depends(get_db)):
#     """
#     Saisie + Imputation automatique selon PCM:
#     - achat => 611 / 3455 / 4411
#     - vente => 3421 / 711 / 4455
#     """

#     # si on veut générer depuis une facture existante
#     if payload.facture_id is not None:
#         f = db.query(Facture).filter(Facture.id == payload.facture_id).first()
#         if not f:
#             raise HTTPException(status_code=404, detail="Facture introuvable")

#         e = EcrituresService.generate_for_facture(db, f, replace=True)

#         if payload.auto_validate:
#             if abs((e.total_debit or 0) - (e.total_credit or 0)) > 0.01:
#                 raise HTTPException(status_code=400, detail="Ecriture non équilibrée (debit != credit)")
#             e.statut = "validee"
#             e.validated_at = datetime.utcnow()
#             db.commit()
#             db.refresh(e)

#         return e

#     # sinon génération depuis saisie manuelle
#     # ⚠️ ton modèle impose facture_id NOT NULL => on doit soit fournir facture_id, soit rendre nullable.
#     raise HTTPException(
#         status_code=400,
#         detail="facture_id est obligatoire (ton modèle EcritureComptable.facture_id est NOT NULL).",
#     )


# @router.post("/{ecriture_id}/valider")
# def valider_ecriture(ecriture_id: int, db: Session = Depends(get_db)):
#     e = db.query(EcritureComptable).filter(EcritureComptable.id == ecriture_id).first()
#     if not e:
#         raise HTTPException(status_code=404, detail="Ecriture introuvable")

#     if abs((e.total_debit or 0) - (e.total_credit or 0)) > 0.01:
#         raise HTTPException(status_code=400, detail="Ecriture non équilibrée (debit != credit)")

#     e.statut = "validee"
#     e.validated_at = datetime.utcnow()

#     db.commit()
#     db.refresh(e)
#     return {"message": "Ecriture validée", "id": e.id, "validated_at": e.validated_at}














# from datetime import datetime
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import EcritureComptable, Facture
# from schemas import PieceComptableIn, EcritureOut
# from services.ecritures_service import EcrituresService

# router = APIRouter(prefix="/ecritures", tags=["ecritures"])


# @router.post("/generer", response_model=EcritureOut)
# def generer_ecriture(payload: PieceComptableIn, db: Session = Depends(get_db)):
#     # Générer depuis facture
#     if payload.facture_id is not None:
#         f = db.query(Facture).filter(Facture.id == payload.facture_id).first()
#         if not f:
#             raise HTTPException(status_code=404, detail="Facture introuvable")

#         e = EcrituresService.generate_for_facture(db, f, replace=True, date_ecriture=payload.date_ecriture)

#         if payload.auto_validate:
#             if abs((e.total_debit or 0) - (e.total_credit or 0)) > 0.01:
#                 raise HTTPException(status_code=400, detail="Ecriture non équilibrée (debit != credit)")
#             e.statut = "validee"
#             e.validated_at = datetime.utcnow()
#             db.commit()
#             db.refresh(e)

#         return e

#     # Sinon : saisie manuelle (pas encore supportée car facture_id NOT NULL)
#     raise HTTPException(
#         status_code=400,
#         detail="facture_id est obligatoire (EcritureComptable.facture_id est NOT NULL).",
#     )


# @router.post("/{ecriture_id}/valider")
# def valider_ecriture(ecriture_id: int, db: Session = Depends(get_db)):
#     e = db.query(EcritureComptable).filter(EcritureComptable.id == ecriture_id).first()
#     if not e:
#         raise HTTPException(status_code=404, detail="Ecriture introuvable")

#     if abs((e.total_debit or 0) - (e.total_credit or 0)) > 0.01:
#         raise HTTPException(status_code=400, detail="Ecriture non équilibrée (debit != credit)")

#     e.statut = "validee"
#     e.validated_at = datetime.utcnow()

#     db.commit()
#     db.refresh(e)
#     return {"message": "Ecriture validée", "id": e.id, "validated_at": e.validated_at}











# routes/ecritures.py
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import EcritureComptable, EcritureLigne, Facture
from schemas import PieceComptableIn, EcritureOut
from services.accounting_rules import compute_tva_and_ttc, get_journal_code, generate_lines_pcm

router = APIRouter(prefix="/ecritures", tags=["ecritures"])


@router.post("/generer", response_model=EcritureOut)
def generer_ecriture(payload: PieceComptableIn, db: Session = Depends(get_db)):
    """
    Génération d'écriture:
    - si facture_id est fourni -> on prend societe_id depuis la facture (IMPORTANT)
    - sinon saisie manuelle -> societe_id doit être fourni
    """

    f = None
    if payload.facture_id is not None:
        f = db.query(Facture).filter(Facture.id == payload.facture_id).first()
        if not f:
            raise HTTPException(status_code=404, detail="Facture introuvable")

    # ✅ Fix: societe_id obligatoire pour ecritures_comptables
    societe_id = None
    if f is not None:
        societe_id = f.societe_id
    else:
        societe_id = payload.societe_id

    if societe_id is None:
        raise HTTPException(status_code=400, detail="societe_id est obligatoire (via facture_id ou payload.societe_id)")

    montant_tva, montant_ttc = compute_tva_and_ttc(
        montant_ht=payload.montant_ht,
        taux_tva=payload.taux_tva,
        montant_ttc=payload.montant_ttc,
    )

    journal = get_journal_code(payload.operation)
    date_ecriture = payload.date_ecriture or date.today()

    libelle = f"{payload.operation.capitalize()} - {payload.tiers_nom or ''} - {payload.numero_piece}".strip(" -")

    e = EcritureComptable(
        societe_id=societe_id,
        facture_id=payload.facture_id,
        operation=payload.operation,
        numero_piece=payload.numero_piece,
        date_operation=payload.date_operation,
        tiers_nom=payload.tiers_nom,
        statut="brouillon",
        libelle=libelle,
        journal=journal,
        date_ecriture=date_ecriture,
    )

    lignes_in = generate_lines_pcm(
        operation=payload.operation,
        tiers_nom=payload.tiers_nom,
        designation=payload.designation,
        montant_ht=payload.montant_ht,
        montant_tva=montant_tva,
        montant_ttc=montant_ttc,
    )

    e.total_debit = round(sum(l.debit for l in lignes_in), 2)
    e.total_credit = round(sum(l.credit for l in lignes_in), 2)
    e.lignes = [EcritureLigne(**l.model_dump()) for l in lignes_in]

    db.add(e)
    db.commit()
    db.refresh(e)

    if payload.auto_validate:
        if abs((e.total_debit or 0) - (e.total_credit or 0)) > 0.01:
            raise HTTPException(status_code=400, detail="Ecriture non équilibrée (debit != credit)")
        e.statut = "validee"
        e.validated_at = datetime.utcnow()
        db.commit()
        db.refresh(e)

    return e
