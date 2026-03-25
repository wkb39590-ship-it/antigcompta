from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
import os
import shutil
from uuid import uuid4
from datetime import datetime

from models import DocumentTransmis, Societe, UtilisateurClient, Facture
from schemas import DocumentTransmisOut
from routes.auth import get_current_agent
from routes.client import get_current_client

router = APIRouter(prefix="/transmission", tags=["Transmission (Dépôt & Tableau de bord)"])

# 1. Côté Client : Uploader un document
@router.post("/upload", response_model=DocumentTransmisOut)
async def upload_document(
    file: UploadFile = File(...),
    type_document: str = Form("FACTURE_ACHAT"),
    notes: str = Form(None),
    client: UtilisateurClient = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    upload_dir = "uploads/transmission"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid4())[:8]
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
    safe_name = f"doc_{file_id}.{ext}"
    file_path = os.path.join(upload_dir, safe_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    doc = DocumentTransmis(
        societe_id=client.societe_id,
        client_id=client.id,
        file_path=file_path,
        file_name=file.filename,
        type_document=type_document,
        statut="A_TRAITER",
        notes_client=notes
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

# 2. Côté Client : Historique de ses envois
@router.get("/client/historique", response_model=list[DocumentTransmisOut])
async def get_client_historique(
    client: UtilisateurClient = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    return db.query(DocumentTransmis).filter(DocumentTransmis.client_id == client.id).order_by(DocumentTransmis.date_upload.desc()).all()


# 3. Côté Agent (Comptable) : Dashboard (Statistiques)
@router.get("/dashboard")
async def get_dashboard_stats(
    agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    # L'agent ne voit que les stats des sociétés de son cabinet
    from sqlalchemy import func
    societes_ids = [s.id for s in db.query(Societe.id).filter(Societe.cabinet_id == agent.cabinet_id).all()]
    
    if not societes_ids:
        return {"stats_par_societe": [], "total_a_traiter": 0}
        
    # Group by societe and statut
    stats = db.query(
        DocumentTransmis.societe_id,
        Societe.raison_sociale,
        DocumentTransmis.statut,
        func.count(DocumentTransmis.id).label("count")
    ).join(Societe).filter(
        DocumentTransmis.societe_id.in_(societes_ids)
    ).group_by(DocumentTransmis.societe_id, Societe.raison_sociale, DocumentTransmis.statut).all()
    
    result = {}
    total_a_traiter = 0
    for row in stats:
        soc_id = row.societe_id
        if soc_id not in result:
            result[soc_id] = {
                "societe_id": soc_id,
                "raison_sociale": row.raison_sociale,
                "A_TRAITER": 0,
                "VALIDE": 0,
                "REJETE": 0
            }
        result[soc_id][row.statut] = row.count
        if row.statut == "A_TRAITER":
            total_a_traiter += row.count
            
    return {
        "stats_par_societe": list(result.values()),
        "total_a_traiter": total_a_traiter
    }

# 4. Côté Agent : Liste des documents (file d'attente globale ou par société)
@router.get("/documents", response_model=list[DocumentTransmisOut])
async def list_documents(
    societe_id: int = None,
    statut: str = "A_TRAITER",
    agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    query = db.query(DocumentTransmis)
    
    if societe_id:
        query = query.filter(DocumentTransmis.societe_id == societe_id)
    else:
        # Restriction par cabinet
        societes_ids = [s.id for s in db.query(Societe.id).filter(Societe.cabinet_id == agent.cabinet_id).all()]
        query = query.filter(DocumentTransmis.societe_id.in_(societes_ids))
        
    if statut:
        query = query.filter(DocumentTransmis.statut == statut)
        
    return query.order_by(DocumentTransmis.date_upload.desc()).all()


# 5. Côté Agent : Accepter un document (le passe en Facture OCR)
@router.post("/{doc_id}/accepter")
async def accepter_document(
    doc_id: int,
    agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    doc = db.query(DocumentTransmis).filter(DocumentTransmis.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document introuvable")
        
    if doc.statut != "A_TRAITER":
        raise HTTPException(status_code=400, detail="Ce document est déjà traité")
        
    # Le document est accepté. Il devient une Facture à importer dans le pipeline de l'agent
    facture = Facture(
        societe_id=doc.societe_id,
        file_path=doc.file_path,
        status="IMPORTED",
        invoice_type="ACHAT" if doc.type_document == "FACTURE_ACHAT" else ("VENTE" if doc.type_document == "FACTURE_VENTE" else "AUTRE")
    )
    db.add(facture)
    db.flush() # To get the id
    
    doc.facture_id = facture.id
    doc.statut = "VALIDE"
    doc.date_traitement = datetime.utcnow()
    
    db.commit()
    return {"message": "Document accepté et transféré vers l'OCR", "facture_id": facture.id}

# 6. Côté Agent : Rejeter un document
@router.post("/{doc_id}/rejeter")
async def rejeter_document(
    doc_id: int,
    agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    doc = db.query(DocumentTransmis).filter(DocumentTransmis.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document introuvable")
        
    doc.statut = "REJETE"
    doc.date_traitement = datetime.utcnow()
    db.commit()
    return {"message": "Document rejeté"}

# 7. Côté Client : Supprimer son propre document (si en attente)
@router.delete("/{doc_id}/client")
async def client_delete_document(
    doc_id: int,
    client: UtilisateurClient = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    doc = db.query(DocumentTransmis).filter(
        DocumentTransmis.id == doc_id, 
        DocumentTransmis.client_id == client.id
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document introuvable ou accès refusé")
        
    if doc.statut != "A_TRAITER":
        raise HTTPException(status_code=400, detail="Impossible de supprimer un document déjà traité")
        
    # Optionnel: supprimer le fichier du disque
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except:
            pass
            
    db.delete(doc)
    db.commit()
    return {"message": "Document supprimé avec succès"}

