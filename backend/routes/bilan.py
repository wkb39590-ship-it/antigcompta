from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.accounting_service import AccountingService
from services.reporting_service import ReportingService
from schemas import BilanOut
from routes.auth import get_current_agent, get_session_context
from typing import Optional
from fastapi.responses import StreamingResponse
from models import Societe

router = APIRouter(prefix="/bilan", tags=["Reporting & Bilan"])

@router.get("/comptable", response_model=BilanOut)
def get_bilan_comptable(
    annee: int,
    mois: Optional[int] = None,
    validated_only: bool = True,
    db: Session = Depends(get_db),
    context=Depends(get_session_context)
):
    """
    Retourne le bilan comptable de la société sélectionnée dans la session.
    """
    if not context or not context.get("societe_id"):
        raise HTTPException(status_code=400, detail="Aucune société sélectionnée dans la session.")
    
    societe_id = context["societe_id"]
    
    try:
        bilan = AccountingService.get_bilan_comptable(
            db, 
            societe_id=societe_id, 
            annee=annee, 
            mois=mois, 
            validated_only=validated_only
        )
        return bilan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du bilan : {str(e)}")

@router.get("/pdf")
def export_bilan_pdf(
    annee: int,
    validated_only: bool = True,
    token: str = None, # Token passé en query car téléchargement direct
    db: Session = Depends(get_db)
):
    """
    Export le bilan au format PDF (Modèle CGNC).
    """
    # Validation manuelle simplifiée du token pour le téléchargement
    from routes.auth import decode_jwt_token
    try:
        payload = decode_jwt_token(token)
        societe_id = payload.get("societe_id")
    except:
        raise HTTPException(status_code=401, detail="Session expirée ou invalide")

    if not societe_id:
        raise HTTPException(status_code=400, detail="Société non sélectionnée")

    societe = db.query(Societe).filter(Societe.id == societe_id).first()
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")

    try:
        bilan = AccountingService.get_bilan_comptable(db, societe_id, annee, validated_only=validated_only)
        
        societe_info = {
            "raison_sociale": societe.raison_sociale,
            "ice": societe.ice,
            "adresse": getattr(societe, 'adresse', 'N/A')
        }
        
        pdf_buffer = ReportingService.generate_bilan_pdf(bilan, societe_info)
        
        filename = f"Bilan_{societe.raison_sociale.replace(' ', '_')}_{annee}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur PDF : {str(e)}")
