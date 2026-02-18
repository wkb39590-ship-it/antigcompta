"""
routes/pcm.py — Référentiel Plan Comptable Marocain
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import PcmAccount

router = APIRouter(prefix="/pcm", tags=["PCM"])


@router.get("/accounts", response_model=list)
def list_pcm_accounts(
    pcm_class: Optional[int] = Query(None, description="Filtrer par classe (1-8)"),
    account_type: Optional[str] = Query(None, description="CHARGE/PRODUIT/ACTIF/PASSIF/TIERS"),
    db: Session = Depends(get_db),
):
    """Retourne le référentiel des comptes PCM."""
    q = db.query(PcmAccount)
    if pcm_class is not None:
        q = q.filter(PcmAccount.pcm_class == pcm_class)
    if account_type:
        q = q.filter(PcmAccount.account_type == account_type.upper())
    accounts = q.order_by(PcmAccount.code).all()
    return [
        {
            "code": a.code,
            "label": a.label,
            "pcm_class": a.pcm_class,
            "group_code": a.group_code,
            "account_type": a.account_type,
            "is_tva_account": a.is_tva_account,
            "tva_type": a.tva_type,
        }
        for a in accounts
    ]


@router.get("/tva-rates", response_model=list)
def get_tva_rates():
    """Retourne les taux TVA valides au Maroc."""
    return [
        {"rate": 0, "label": "Exonéré"},
        {"rate": 7, "label": "7% — Eau, médicaments, transport"},
        {"rate": 10, "label": "10% — Restauration, hôtellerie"},
        {"rate": 14, "label": "14% — Transport de voyageurs"},
        {"rate": 20, "label": "20% — Taux normal"},
    ]
