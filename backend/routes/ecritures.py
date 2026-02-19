



# # routes/ecritures.py
# from datetime import datetime, date
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from database import get_db
# from models import EcritureComptable, EcritureLigne, Facture
# from schemas import PieceComptableIn, EcritureOut
# from services.accounting_rules import compute_tva_and_ttc, get_journal_code, generate_lines_pcm

# router = APIRouter(prefix="/ecritures", tags=["ecritures"])


# @router.post("/generer", response_model=EcritureOut)
# def generer_ecriture(payload: PieceComptableIn, db: Session = Depends(get_db)):
#     """
#     Génération d'écriture:
#     - si facture_id est fourni -> on prend societe_id depuis la facture (IMPORTANT)
#     - sinon saisie manuelle -> societe_id doit être fourni
#     """

#     f = None
#     if payload.facture_id is not None:
#         f = db.query(Facture).filter(Facture.id == payload.facture_id).first()
#         if not f:
#             raise HTTPException(status_code=404, detail="Facture introuvable")

#     # ✅ Fix: societe_id obligatoire pour ecritures_comptables
#     societe_id = None
#     if f is not None:
#         societe_id = f.societe_id
#     else:
#         societe_id = payload.societe_id

#     if societe_id is None:
#         raise HTTPException(status_code=400, detail="societe_id est obligatoire (via facture_id ou payload.societe_id)")

#     montant_tva, montant_ttc = compute_tva_and_ttc(
#         montant_ht=payload.montant_ht,
#         taux_tva=payload.taux_tva,
#         montant_ttc=payload.montant_ttc,
#     )

#     journal = get_journal_code(payload.operation)
#     date_ecriture = payload.date_ecriture or date.today()

#     libelle = f"{payload.operation.capitalize()} - {payload.tiers_nom or ''} - {payload.numero_piece}".strip(" -")

#     e = EcritureComptable(
#         societe_id=societe_id,
#         facture_id=payload.facture_id,
#         operation=payload.operation,
#         numero_piece=payload.numero_piece,
#         date_operation=payload.date_operation,
#         tiers_nom=payload.tiers_nom,
#         statut="brouillon",
#         libelle=libelle,
#         journal=journal,
#         date_ecriture=date_ecriture,
#     )

#     lignes_in = generate_lines_pcm(
#         operation=payload.operation,
#         tiers_nom=payload.tiers_nom,
#         designation=payload.designation,
#         montant_ht=payload.montant_ht,
#         montant_tva=montant_tva,
#         montant_ttc=montant_ttc,
#     )

#     e.total_debit = round(sum(l.debit for l in lignes_in), 2)
#     e.total_credit = round(sum(l.credit for l in lignes_in), 2)
#     e.lignes = [EcritureLigne(**l.model_dump()) for l in lignes_in]

#     db.add(e)
#     db.commit()
#     db.refresh(e)

#     if payload.auto_validate:
#         if abs((e.total_debit or 0) - (e.total_credit or 0)) > 0.01:
#             raise HTTPException(status_code=400, detail="Ecriture non équilibrée (debit != credit)")
#         e.statut = "validee"
#         e.validated_at = datetime.utcnow()
#         db.commit()
#         db.refresh(e)

#     return e









from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Facture, EcritureComptable, EcritureLigne
from routes.deps import get_current_session
from schemas import GenererEcrituresResponse, EcritureLigneOut
from services.accounting_rules import PieceComptable, generate_lines_pcm, get_journal_code

router = APIRouter(prefix="/ecritures", tags=["ecritures"])


@router.get("/facture/{facture_id}", response_model=list[EcritureLigneOut])
def list_ecritures_facture(facture_id: int, db: Session = Depends(get_db), session: dict = Depends(get_current_session)):
    """Liste les écritures d'une facture. Vérifie l'accès à la société."""
    f = db.query(Facture).filter(Facture.id == facture_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture introuvable")
    if f.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")

    header = (
        db.query(EcritureComptable)
        .filter(EcritureComptable.facture_id == facture_id)
        .order_by(EcritureComptable.id.desc())
        .first()
    )

    if not header:
        return []

    lignes = (
        db.query(EcritureLigne)
        .filter(EcritureLigne.ecriture_id == header.id)
        .order_by(EcritureLigne.id.asc())
        .all()
    )
    return lignes


@router.post("/generer", response_model=GenererEcrituresResponse)
def generer_ecritures_pcm(
    facture_id: int = Query(..., description="ID de la facture"),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    f = db.query(Facture).filter(Facture.id == facture_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Facture introuvable")
    if f.societe_id != session.get("societe_id"):
        raise HTTPException(status_code=403, detail="Accès refusé à cette facture")

    # contrôles cahier des charges
    if not f.numero_facture:
        raise HTTPException(status_code=422, detail="Numéro de facture obligatoire")
    if not f.date_facture:
        raise HTTPException(status_code=422, detail="Date d'opération obligatoire (date_facture)")
    if f.montant_ht is None or f.montant_ttc is None:
        raise HTTPException(status_code=422, detail="Montants HT/TTC obligatoires")

    piece = PieceComptable(
        operation=f.operation_type,
        numero_piece=f.numero_facture,
        date_operation=f.date_facture,
        designation=f.designation or "",
        tiers_nom=f.fournisseur,
        montant_ht=float(f.montant_ht or 0),
        taux_tva=float(f.taux_tva or 20),
        montant_ttc=float(f.montant_ttc or 0),
    )

    journal_code = get_journal_code(piece.operation)
    lines = generate_lines_pcm(piece)

    total_debit = round(sum(float(l.get("debit", 0) or 0) for l in lines), 2)
    total_credit = round(sum(float(l.get("credit", 0) or 0) for l in lines), 2)

    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Écriture non équilibrée (partie double non respectée)",
                "total_debit": total_debit,
                "total_credit": total_credit,
                "lines": lines,
            },
        )

    # ✅ supprimer ancienne écriture header (cascade supprime lignes)
    old_headers = db.query(EcritureComptable).filter(EcritureComptable.facture_id == facture_id).all()
    for h in old_headers:
        db.delete(h)
    db.flush()

    header = EcritureComptable(
        societe_id=f.societe_id,
        facture_id=f.id,
        operation=piece.operation,
        journal=journal_code,
        numero_piece=piece.numero_piece,
        date_operation=piece.date_operation,
        tiers_nom=piece.tiers_nom,
        statut="brouillon",
        libelle=f"{piece.operation.upper()} - {(piece.tiers_nom or '').strip()} - {piece.numero_piece}".strip(" -"),
        total_debit=total_debit,
        total_credit=total_credit,
    )

    db.add(header)
    db.flush()  # pour header.id

    for l in lines:
        db.add(
            EcritureLigne(
                ecriture_id=header.id,
                compte=l["compte"],
                libelle=l.get("libelle"),
                debit=float(l.get("debit", 0) or 0),
                credit=float(l.get("credit", 0) or 0),
            )
        )

    db.commit()
    db.refresh(header)

    return {
        "facture_id": f.id,
        "journal": journal_code,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "ecriture": header,
    }
