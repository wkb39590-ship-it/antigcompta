"""
gemini_service.py — Extraction structurée et classification PCM via Gemini API
"""
import json
import os
from typing import Any, Dict, List, Optional

from google import genai


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _client() -> genai.Client:
    return genai.Client()


# ─────────────────────────────────────────────
# Schémas JSON pour Gemini structured output
# ─────────────────────────────────────────────

HEADER_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "numero_facture": {"type": ["string", "null"]},
        "date_facture": {"type": ["string", "null"], "description": "Format DD/MM/YYYY"},
        "due_date": {"type": ["string", "null"], "description": "Date échéance DD/MM/YYYY"},
        "invoice_type": {
            "type": ["string", "null"],
            "description": "ACHAT, VENTE, AVOIR, NOTE_FRAIS ou IMMOBILISATION"
        },
        "supplier_name": {"type": ["string", "null"]},
        "supplier_ice": {"type": ["string", "null"], "description": "ICE Maroc: exactement 15 chiffres"},
        "supplier_if": {"type": ["string", "null"]},
        "supplier_rc": {"type": ["string", "null"]},
        "supplier_address": {"type": ["string", "null"]},
        "client_name": {"type": ["string", "null"]},
        "client_ice": {"type": ["string", "null"]},
        "client_if": {"type": ["string", "null"]},
        "client_address": {"type": ["string", "null"]},
        "montant_ht": {"type": ["number", "null"]},
        "montant_tva": {"type": ["number", "null"]},
        "montant_ttc": {"type": ["number", "null"]},
        "taux_tva": {"type": ["number", "null"], "description": "7, 10, 14 ou 20"},
        "devise": {"type": ["string", "null"], "description": "MAD par défaut"},
        "payment_mode": {"type": ["string", "null"]},
        "payment_terms": {"type": ["string", "null"]},
        # Legacy compat
        "fournisseur": {"type": ["string", "null"]},
        "ice_frs": {"type": ["string", "null"]},
        "if_frs": {"type": ["string", "null"]},
    },
    "required": [
        "numero_facture", "date_facture", "invoice_type",
        "supplier_name", "supplier_ice", "supplier_if",
        "client_name", "montant_ht", "montant_tva", "montant_ttc",
        "taux_tva", "devise", "payment_mode"
    ],
}

LINES_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "lines": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "line_number": {"type": ["integer", "null"]},
                    "description": {"type": ["string", "null"]},
                    "quantity": {"type": ["number", "null"]},
                    "unit": {"type": ["string", "null"]},
                    "unit_price_ht": {"type": ["number", "null"]},
                    "line_amount_ht": {"type": ["number", "null"]},
                    "tva_rate": {"type": ["number", "null"]},
                    "tva_amount": {"type": ["number", "null"]},
                    "line_amount_ttc": {"type": ["number", "null"]},
                },
                "required": ["description", "quantity", "unit_price_ht", "line_amount_ht", "tva_rate"]
            }
        }
    },
    "required": ["lines"]
}

CLASSIFICATION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "pcm_class": {"type": ["integer", "null"], "description": "Classe PCM 1 à 8"},
        "pcm_account_code": {"type": ["string", "null"], "description": "Ex: 6111, 2355, 7111"},
        "pcm_account_label": {"type": ["string", "null"]},
        "confidence": {"type": ["number", "null"], "description": "Score 0.0 à 1.0"},
        "reason": {"type": ["string", "null"]},
    },
    "required": ["pcm_class", "pcm_account_code", "pcm_account_label", "confidence", "reason"]
}


# ─────────────────────────────────────────────
# Extraction en-tête facture
# ─────────────────────────────────────────────

HEADER_SYSTEM_PROMPT = """Tu es un moteur d'extraction de factures marocaines.
Retourne UNIQUEMENT un JSON valide conforme au schéma.
Règles:
- Si une valeur est absente => null
- date_facture au format DD/MM/YYYY
- montants: nombre décimal (ex: 10000.00). Si tu lis "10 000,00" => 10000.00
- ICE Maroc = exactement 15 chiffres (string)
- invoice_type: détermine si c'est ACHAT, VENTE, AVOIR, NOTE_FRAIS ou IMMOBILISATION
- supplier_name = nom du fournisseur (émetteur de la facture)
- client_name = nom du client (destinataire)
- Ne renvoie aucun texte hors du JSON.
"""


def extract_invoice_header(
    image_bytes: bytes,
    mime_type: str = "image/png",
    model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """Extrait les champs d'en-tête obligatoires de la facture (Tableau 1)."""
    if not image_bytes:
        raise ValueError("image_bytes is empty")

    client = _client()
    resp = client.models.generate_content(
        model=model,
        contents=[{
            "role": "user",
            "parts": [
                {"text": HEADER_SYSTEM_PROMPT},
                {"inline_data": {"mime_type": mime_type, "data": image_bytes}},
            ],
        }],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": HEADER_SCHEMA,
            "temperature": 0.0,
        },
    )
    try:
        data = json.loads(resp.text)
        # Compat legacy: si supplier_name rempli mais fournisseur vide
        if data.get("supplier_name") and not data.get("fournisseur"):
            data["fournisseur"] = data["supplier_name"]
        if data.get("supplier_ice") and not data.get("ice_frs"):
            data["ice_frs"] = data["supplier_ice"]
        if data.get("supplier_if") and not data.get("if_frs"):
            data["if_frs"] = data["supplier_if"]
        return data
    except Exception as e:
        raise RuntimeError(f"Gemini header response not valid JSON. Raw: {resp.text[:500]}") from e


# ─────────────────────────────────────────────
# Extraction lignes produits
# ─────────────────────────────────────────────

LINES_SYSTEM_PROMPT = """Tu es un moteur d'extraction de lignes de factures marocaines.
Extrait TOUTES les lignes de produits/services présentes sur la facture.
Retourne UNIQUEMENT un JSON valide avec un tableau "lines".
Règles:
- Une ligne = un produit ou service distinct
- Si une valeur est absente => null
- montants: nombre décimal (ex: 8000.00)
- tva_rate: nombre (7, 10, 14 ou 20)
- Ne renvoie aucun texte hors du JSON.
"""


def extract_invoice_lines(
    image_bytes: bytes,
    mime_type: str = "image/png",
    model: str = DEFAULT_MODEL,
) -> List[Dict[str, Any]]:
    """Extrait les lignes produits/services de la facture (Tableau 2)."""
    if not image_bytes:
        raise ValueError("image_bytes is empty")

    client = _client()
    resp = client.models.generate_content(
        model=model,
        contents=[{
            "role": "user",
            "parts": [
                {"text": LINES_SYSTEM_PROMPT},
                {"inline_data": {"mime_type": mime_type, "data": image_bytes}},
            ],
        }],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": LINES_SCHEMA,
            "temperature": 0.0,
        },
    )
    try:
        data = json.loads(resp.text)
        return data.get("lines", [])
    except Exception as e:
        raise RuntimeError(f"Gemini lines response not valid JSON. Raw: {resp.text[:500]}") from e


# ─────────────────────────────────────────────
# Classification PCM ligne par ligne
# ─────────────────────────────────────────────

CLASSIFICATION_SYSTEM_PROMPT = """Tu es un expert-comptable marocain spécialisé dans le Plan Comptable Marocain (PCM/CGNC).
Pour la description de produit/service donnée, détermine:
1. La classe PCM (1 à 8)
2. Le compte PCM précis (4 chiffres minimum)
3. Le libellé officiel du compte
4. Un score de confiance (0.0 à 1.0)
5. Une justification courte en français

Règles PCM principales:
- Classe 2: Immobilisations (biens durables > 5000 MAD ou amortissables)
  - 2355: Matériel informatique
  - 2340: Matériel de transport
  - 2321: Bâtiments
- Classe 6: Charges d'exploitation
  - 6111: Achats de marchandises
  - 6121: Achats de matières premières
  - 6123: Fournitures de bureau
  - 6132: Locations
  - 6135: Entretien et réparations
  - 6141: Primes d'assurance
  - 6152: Honoraires
  - 6161: Frais de transport
  - 6171: Frais de déplacement
- Classe 7: Produits
  - 7111: Ventes de marchandises
  - 7121: Ventes de produits finis
  - 7161: Ventes de services

Retourne UNIQUEMENT un JSON valide.
"""


def classify_invoice_line(
    description: str,
    amount_ht: Optional[float] = None,
    invoice_type: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """Classifie une ligne de facture dans le Plan Comptable Marocain."""
    context = f"Description: {description}"
    if amount_ht is not None:
        context += f"\nMontant HT: {amount_ht} MAD"
    if invoice_type:
        context += f"\nType de facture: {invoice_type}"

    client = _client()
    resp = client.models.generate_content(
        model=model,
        contents=[{
            "role": "user",
            "parts": [
                {"text": CLASSIFICATION_SYSTEM_PROMPT},
                {"text": context},
            ],
        }],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": CLASSIFICATION_SCHEMA,
            "temperature": 0.0,
        },
    )
    try:
        return json.loads(resp.text)
    except Exception as e:
        raise RuntimeError(f"Gemini classification response not valid JSON. Raw: {resp.text[:500]}") from e


# ─────────────────────────────────────────────
# Legacy: extraction depuis image bytes (compat)
# ─────────────────────────────────────────────

# JSON Schema legacy (subset)
INVOICE_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "fournisseur": {"type": ["string", "null"]},
        "date_facture": {"type": ["string", "null"], "description": "Format DD/MM/YYYY"},
        "numero_facture": {"type": ["string", "null"]},
        "montant_ht": {"type": ["number", "null"]},
        "montant_tva": {"type": ["number", "null"]},
        "montant_ttc": {"type": ["number", "null"]},
        "taux_tva": {"type": ["number", "null"]},
        "ice_frs": {"type": ["string", "null"]},
        "if_frs": {"type": ["string", "null"]},
        "devise": {"type": ["string", "null"]},
    },
    "required": [
        "fournisseur", "date_facture", "numero_facture",
        "montant_ht", "montant_tva", "montant_ttc",
        "taux_tva", "ice_frs", "if_frs", "devise",
    ],
}

SYSTEM_PROMPT = """Tu es un moteur d'extraction de factures.
Retourne UNIQUEMENT un JSON valide conforme au schéma demandé.
Règles:
- Si une valeur est absente/incertaine => null
- date_facture au format DD/MM/YYYY
- montants: nombre (ex: 10000.00). Si tu lis "10 000,00", renvoie 10000.00
- ICE Maroc = 15 chiffres (string)
- Ne renvoie aucun texte hors du JSON.
"""


def extract_invoice_fields_from_image_bytes(
    image_bytes: bytes,
    mime_type: str = "image/png",
    model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """Legacy: Envoie une image à Gemini et récupère un JSON structuré (en-tête seulement)."""
    if not image_bytes:
        raise ValueError("image_bytes is empty")

    client = _client()
    resp = client.models.generate_content(
        model=model,
        contents=[{
            "role": "user",
            "parts": [
                {"text": SYSTEM_PROMPT},
                {"inline_data": {"mime_type": mime_type, "data": image_bytes}},
            ],
        }],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": INVOICE_JSON_SCHEMA,
            "temperature": 0.0,
        },
    )
    try:
        return json.loads(resp.text)
    except Exception as e:
        raise RuntimeError(f"Gemini response is not valid JSON. Raw: {resp.text[:500]}") from e
