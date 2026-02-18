"""
classification_service.py — Classification PCM ligne par ligne
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from models import InvoiceLine, Facture
from services.gemini_service import classify_invoice_line


def classify_all_lines(facture: Facture, db: Session) -> List[dict]:
    """
    Classifie chaque ligne de la facture dans le Plan Comptable Marocain.
    Met à jour les champs PCM dans invoice_lines.
    Retourne la liste des résultats de classification.
    """
    results = []

    for line in facture.lines:
        if not line.description:
            continue

        try:
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

    db.commit()
    return results
