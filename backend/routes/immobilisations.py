"""
routes/immobilisations.py — Endpoints pour la gestion des immobilisations
CRUD + plan d'amortissement + génération d'écritures PCM
"""
from datetime import date
from typing import Optional, List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from database import get_db
from models import Immobilisation, LigneAmortissement, Facture, Societe, Agent
from routes.deps import get_current_session, get_current_agent
from utils.logging import log_action
from services.immobilisation_service import (
    calculer_plan_amortissement,
    sauvegarder_plan,
    generer_ecriture_acquisition,
    generer_ecriture_dotation,
    calculer_taux,
)

router = APIRouter(prefix="/immobilisations", tags=["immobilisations"])

@router.get("/fix-amortissement")
def fix_database_locks(db: Session = Depends(get_db)):
    try:
        # Reset all lines that claim to be generated for 2024 and 2025
        lignes = db.query(LigneAmortissement).filter(LigneAmortissement.annee.in_([2024, 2025])).all()
        count = 0
        for ligne in lignes:
            ligne.ecriture_generee = False
            count += 1
        db.commit()
        return {"status": "success", "message": f"{count} lignes d'amortissement (2024, 2025) ont ete renitialisees avec succes ! Vous pouvez maintenant rafraichir le plan d'amortissement et voir les boutons."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/fix-2355")
def fix_2355_ghost(db: Session = Depends(get_db)):
    from models import EntryLine, JournalEntry
    try:
        # Les IDs suspects identifiés qui forment le total de 716.67 MAD
        suspect_ids = [498, 500, 502, 504]
        
        lines_to_delete = db.query(EntryLine).filter(EntryLine.id.in_(suspect_ids)).all()
        
        je_ids_to_clean = set()
        for l in lines_to_delete:
            if l.ecriture_journal_id:
                je_ids_to_clean.add(l.ecriture_journal_id)
        
        count = 0
        for je_id in je_ids_to_clean:
            # Supprimer toutes les lignes du journal (TVA + Contrepartie Fournisseur/Banque)
            all_l = db.query(EntryLine).filter(EntryLine.ecriture_journal_id == je_id).all()
            for i in all_l:
                db.delete(i)
                count += 1
            # Supprimer le journal lui-même
            je = db.query(JournalEntry).filter(JournalEntry.id == je_id).first()
            if je:
                db.delete(je)
        
        db.commit()
        if count > 0:
            return {"status": "success", "message": f"{count} lignes parasites (TVA + Contreparties) ont été supprimées. Votre TVA récupérable va maintenant tomber à 4500 MAD (le montant réel)."}
        else:
            return {"status": "success", "message": "Aucune ligne parasite trouvée avec ces IDs. Le nettoyage est peut-être déjà fait."}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Comptes PCM par défaut selon catégorie ──────────────────────────────
COMPTES_PCM_DEFAUT = {
    "CORPORELLE": {
        "compte_actif_pcm":    "2355",   # Matériel informatique (groupe 235)
        "compte_amort_pcm":    "28355",  # Amortissements matériel informatique (miroir 2355)
        "compte_dotation_pcm": "6193",   # Dotations aux amortissements corporels
    },
    "INCORPORELLE": {
        "compte_actif_pcm":   "2220",  # Brevets, marques, logiciels
        "compte_amort_pcm":   "2820",
        "compte_dotation_pcm": "6192",
    },
    "FINANCIERE": {
        "compte_actif_pcm":   "2480",  # Autres titres immobilisés
        "compte_amort_pcm":   "2880",
        "compte_dotation_pcm": "6196",
    },
}


def _immo_to_dict(immo: Immobilisation, with_plan=False) -> dict:
    """Convertit une immobilisation en dict de réponse."""
    result = {
        "id": immo.id,
        "societe_id": immo.societe_id,
        "facture_id": immo.facture_id,
        "designation": immo.designation,
        "categorie": immo.categorie,
        "date_acquisition": str(immo.date_acquisition) if immo.date_acquisition else None,
        "valeur_acquisition": float(immo.valeur_acquisition) if immo.valeur_acquisition else 0,
        "tva_acquisition": float(immo.tva_acquisition) if immo.tva_acquisition else 0,
        "duree_amortissement": immo.duree_amortissement,
        "taux_amortissement": float(immo.taux_amortissement) if immo.taux_amortissement else float(calculer_taux(immo)),
        "methode": immo.methode,
        "compte_actif_pcm": immo.compte_actif_pcm,
        "compte_amort_pcm": immo.compte_amort_pcm,
        "compte_dotation_pcm": immo.compte_dotation_pcm,
        "statut": immo.statut,
        "created_at": str(immo.created_at) if immo.created_at else None,
    }

    if with_plan:
        result["plan_amortissement"] = [
            {
                "annee": l.annee,
                "dotation_annuelle": float(l.dotation_annuelle),
                "amortissement_cumule": float(l.amortissement_cumule),
                "valeur_nette_comptable": float(l.valeur_nette_comptable),
                "ecriture_generee": l.ecriture_generee,
            }
            for l in sorted(immo.lignes_amortissement, key=lambda x: x.annee)
        ]

    return result


# ──────────────────────────────────────────────────────────────────────────
# GET /immobilisations/ — Liste
# ──────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=list)
def list_immobilisations(
    categorie: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Liste toutes les immobilisations de la société active."""
    societe_id = session.get("societe_id")
    q = db.query(Immobilisation).filter(Immobilisation.societe_id == societe_id)

    if categorie:
        q = q.filter(Immobilisation.categorie == categorie.upper())
    if statut:
        q = q.filter(Immobilisation.statut == statut.upper())

    immos = q.order_by(Immobilisation.date_acquisition.desc()).all()
    return [_immo_to_dict(i) for i in immos]


# ──────────────────────────────────────────────────────────────────────────
# POST /immobilisations/ — Créer
# ──────────────────────────────────────────────────────────────────────────
@router.post("/", response_model=dict, status_code=201)
def create_immobilisation(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
    agent: Agent = Depends(get_current_agent),
):
    """
    Crée une immobilisation.
    Peut être liée à une facture existante (facture_id) ou saisie manuellement.
    """
    societe_id = session.get("societe_id")

    # Validation des champs obligatoires
    required = ["designation", "date_acquisition", "valeur_acquisition", "duree_amortissement"]
    for field in required:
        if not payload.get(field):
            raise HTTPException(400, f"Champ obligatoire manquant : {field}")

    if int(payload["duree_amortissement"]) <= 0:
        raise HTTPException(400, "La durée d'amortissement doit être au moins 1 an")

    categorie = (payload.get("categorie") or "CORPORELLE").upper()
    defauts = COMPTES_PCM_DEFAUT.get(categorie, COMPTES_PCM_DEFAUT["CORPORELLE"])

    methode = (payload.get("methode") or "LINEAIRE").upper()

    # Parser la date
    try:
        date_acq = date.fromisoformat(payload["date_acquisition"])
    except Exception:
        raise HTTPException(400, "Format de date invalide (attendu: YYYY-MM-DD)")

    valeur = float(payload["valeur_acquisition"])
    duree = int(payload["duree_amortissement"])
    taux = round(1 / duree * (1.5 if duree <= 3 else 2 if duree <= 5 else 3) if methode == "DEGRESSIF" else 1 / duree, 4)

    immo = Immobilisation(
        societe_id=societe_id,
        facture_id=payload.get("facture_id"),
        designation=payload["designation"],
        categorie=categorie,
        date_acquisition=date_acq,
        valeur_acquisition=valeur,
        tva_acquisition=payload.get("tva_acquisition", 0),
        duree_amortissement=duree,
        taux_amortissement=taux,
        methode=methode,
        compte_actif_pcm=payload.get("compte_actif_pcm") or defauts["compte_actif_pcm"],
        compte_amort_pcm=payload.get("compte_amort_pcm") or defauts["compte_amort_pcm"],
        compte_dotation_pcm=payload.get("compte_dotation_pcm") or defauts["compte_dotation_pcm"],
        statut="ACTIF",
    )
    db.add(immo)
    db.flush()

    # Calculer et sauvegarder le plan d'amortissement
    sauvegarder_plan(immo, db)

    db.commit()
    db.refresh(immo)

    log_action(db, agent, "CREATE", "IMMOBILISATION", immo.id, f"Création de l'immobilisation '{immo.designation}'")

    return _immo_to_dict(immo, with_plan=True)


# ──────────────────────────────────────────────────────────────────────────
# GET /immobilisations/{id} — Détail
# ──────────────────────────────────────────────────────────────────────────
@router.get("/{immo_id}", response_model=dict)
def get_immobilisation(
    immo_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Retourne le détail complet d'une immobilisation avec son plan d'amortissement."""
    societe_id = session.get("societe_id")
    immo = db.query(Immobilisation).filter(
        Immobilisation.id == immo_id,
        Immobilisation.societe_id == societe_id,
    ).first()

    if not immo:
        raise HTTPException(404, "Immobilisation introuvable")

    return _immo_to_dict(immo, with_plan=True)


# ──────────────────────────────────────────────────────────────────────────
# PUT /immobilisations/{id} — Modifier
# ──────────────────────────────────────────────────────────────────────────
@router.put("/{immo_id}", response_model=dict)
def update_immobilisation(
    immo_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
    agent: Agent = Depends(get_current_agent),
):
    """Modifie une immobilisation et recalcule le plan d'amortissement."""
    societe_id = session.get("societe_id")
    immo = db.query(Immobilisation).filter(
        Immobilisation.id == immo_id,
        Immobilisation.societe_id == societe_id,
    ).first()

    if not immo:
        raise HTTPException(404, "Immobilisation introuvable")

    fields = ["designation", "categorie", "methode", "statut",
              "compte_actif_pcm", "compte_amort_pcm", "compte_dotation_pcm"]
    for f in fields:
        if f in payload:
            setattr(immo, f, payload[f])

    if "valeur_acquisition" in payload:
        immo.valeur_acquisition = float(payload["valeur_acquisition"])
    if "tva_acquisition" in payload:
        immo.tva_acquisition = float(payload["tva_acquisition"])
    if "duree_amortissement" in payload:
        immo.duree_amortissement = int(payload["duree_amortissement"])
    if "date_acquisition" in payload:
        immo.date_acquisition = date.fromisoformat(payload["date_acquisition"])

    # Recalculer le plan si nécessaire
    sauvegarder_plan(immo, db)

    db.commit()
    db.refresh(immo)

    log_action(db, agent, "UPDATE", "IMMOBILISATION", immo.id, f"Mise à jour de l'immobilisation '{immo.designation}'")

    return _immo_to_dict(immo, with_plan=True)


# ──────────────────────────────────────────────────────────────────────────
# GET /immobilisations/{id}/amortissement — Plan recalculé
# ──────────────────────────────────────────────────────────────────────────
@router.get("/{immo_id}/amortissement", response_model=dict)
def get_plan_amortissement(
    immo_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
):
    """Retourne le plan d'amortissement complet recalculé."""
    societe_id = session.get("societe_id")
    immo = db.query(Immobilisation).filter(
        Immobilisation.id == immo_id,
        Immobilisation.societe_id == societe_id,
    ).first()

    if not immo:
        raise HTTPException(404, "Immobilisation introuvable")

    plan = calculer_plan_amortissement(immo)
    return {
        "immobilisation_id": immo.id,
        "designation": immo.designation,
        "valeur_acquisition": float(immo.valeur_acquisition),
        "duree_amortissement": immo.duree_amortissement,
        "methode": immo.methode,
        "taux": float(calculer_taux(immo)),
        "plan": plan,
    }


# ──────────────────────────────────────────────────────────────────────────
# POST /immobilisations/{id}/ecriture-acquisition — Écriture acquisition
# ──────────────────────────────────────────────────────────────────────────
@router.post("/{immo_id}/ecriture-acquisition", response_model=dict)
def create_ecriture_acquisition(
    immo_id: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
    agent: Agent = Depends(get_current_agent),
):
    """Génère l'écriture comptable d'acquisition (Débit 2xxx+34552 / Crédit 4411)."""
    societe_id = session.get("societe_id")
    immo = db.query(Immobilisation).filter(
        Immobilisation.id == immo_id,
        Immobilisation.societe_id == societe_id,
    ).first()

    if not immo:
        raise HTTPException(404, "Immobilisation introuvable")

    if not immo.facture_id:
        raise HTTPException(400, "Aucune facture liée à cette immobilisation. Liez-la d'abord.")

    entry = generer_ecriture_acquisition(immo, db)

    log_action(db, agent, "GENERATION_ACQUISITION", "IMMOBILISATION", immo.id, f"Génération de l'écriture d'acquisition pour '{immo.designation}'")

    return {
        "message": "Écriture d'acquisition générée",
        "ecriture_id": entry.id,
        "journal_code": entry.journal_code,
        "total_debit": float(entry.total_debit) if entry.total_debit else 0,
        "total_credit": float(entry.total_credit) if entry.total_credit else 0,
        "entry_lines": [
            {
                "account_code": el.account_code,
                "account_label": el.account_label,
                "debit": float(el.debit),
                "credit": float(el.credit),
            }
            for el in sorted(entry.entry_lines, key=lambda x: x.line_order or 0)
        ],
    }


# ──────────────────────────────────────────────────────────────────────────
# POST /immobilisations/{id}/dotation/{annee} — Écriture dotation
# ──────────────────────────────────────────────────────────────────────────
@router.post("/{immo_id}/dotation/{annee}", response_model=dict)
def create_ecriture_dotation(
    immo_id: int,
    annee: int,
    db: Session = Depends(get_db),
    session: dict = Depends(get_current_session),
    agent: Agent = Depends(get_current_agent),
):
    """Génère l'écriture de dotation aux amortissements (Débit 6193 / Crédit 2835)."""
    societe_id = session.get("societe_id")
    immo = db.query(Immobilisation).filter(
        Immobilisation.id == immo_id,
        Immobilisation.societe_id == societe_id,
    ).first()

    if not immo:
        raise HTTPException(404, "Immobilisation introuvable")

    try:
        entry = generer_ecriture_dotation(immo, annee, db)
        log_action(db, agent, "GENERATION_DOTATION", "IMMOBILISATION", immo.id, f"Génération de la dotation aux amortissements pour l'année {annee} (Asset: {immo.designation})")
    except ValueError as e:
        raise HTTPException(400, str(e))

    return {
        "message": f"Écriture dotation {annee} générée",
        "ecriture_id": entry.id,
        "journal_code": entry.journal_code,
        "total_debit": float(entry.total_debit) if entry.total_debit else 0,
        "total_credit": float(entry.total_credit) if entry.total_credit else 0,
        "entry_lines": [
            {
                "account_code": el.account_code,
                "account_label": el.account_label,
                "debit": float(el.debit),
                "credit": float(el.credit),
            }
            for el in sorted(entry.entry_lines, key=lambda x: x.line_order or 0)
        ],
    }
