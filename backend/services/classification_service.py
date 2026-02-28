"""
classification_service.py — Classification PCM ligne par ligne
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from models import InvoiceLine, Facture, SupplierMapping, PcmAccount
from services.gemini_service import classify_invoice_line


def classify_all_lines(facture: Facture, db: Session) -> List[dict]:
    """
    Classifie chaque ligne de la facture dans le Plan Comptable Marocain.
    Met à jour les champs PCM dans invoice_lines.
    Utilise SupplierMapping (Feedback Loop) si disponible, sinon Gemini.
    """
    results = []
    
    # 1. Chercher si un mapping existe pour ce fournisseur dans ce cabinet
    mapping = None
    if facture.supplier_ice:
        mapping = (
            db.query(SupplierMapping)
            .filter(
                SupplierMapping.cabinet_id == facture.societe.cabinet_id,
                SupplierMapping.supplier_ice == facture.supplier_ice
            )
            .first()
        )

    for line in facture.lines:
        if not line.description:
            continue

        try:
            # 2. Si un mapping existe, on l'utilise directement (Feedback Loop)
            if mapping:
                account = db.query(PcmAccount).filter(PcmAccount.code == mapping.pcm_account_code).first()
                if account:
                    line.pcm_class = account.pcm_class
                    line.pcm_account_code = account.code
                    line.pcm_account_label = account.label
                    line.classification_confidence = 1.0
                    line.classification_reason = f"Appris via l'ICE fournisseur: {facture.supplier_ice}"
                else:
                    # Fallback au cas où le compte aurait disparu du PCM
                    mapping = None

            # 3. Sinon, on appelle l'IA (Gemini)
            if not mapping:
                classification = classify_invoice_line(
                    description=line.description,
                    amount_ht=float(line.line_amount_ht) if line.line_amount_ht else None,
                    invoice_type=facture.invoice_type,
                )

                line.pcm_class = classification.get("pcm_class")
                line.pcm_account_code = classification.get("pcm_account_code")
                line.pcm_account_label = classification.get("pcm_account_label")
                line.classification_confidence = classification.get("confidence")
                line.classification_reason = classification.get("reason")

            results.append({
                "line_id": line.id,
                "description": line.description,
                "pcm_class": line.pcm_class,
                "pcm_account_code": line.pcm_account_code,
                "pcm_account_label": line.pcm_account_label,
                "confidence": line.classification_confidence,
                "reason": line.classification_reason,
            })

        except Exception as e:
            results.append({
                "line_id": line.id,
                "description": line.description,
                "error": str(e),
            })

    # Sauvegarde des modifications en base de données
    db.commit()
    return results
