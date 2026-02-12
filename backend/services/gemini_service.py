import json
import os
from typing import Any, Dict, Optional

from google import genai


# Modèle recommandé (rapide et suffisant pour extraction)
# Tu peux remplacer par un autre modèle Gemini selon ton besoin.
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


# JSON Schema (subset supporté par Gemini structured output)
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
        "ice_frs": {"type": ["string", "null"], "description": "ICE Maroc: 15 chiffres"},
        "if_frs": {"type": ["string", "null"]},
        "devise": {"type": ["string", "null"], "description": "MAD/DH/EUR/... si présent"},
    },
    "required": [
        "fournisseur",
        "date_facture",
        "numero_facture",
        "montant_ht",
        "montant_tva",
        "montant_ttc",
        "taux_tva",
        "ice_frs",
        "if_frs",
        "devise",
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


def _client() -> genai.Client:
    # Le SDK lit automatiquement GEMINI_API_KEY si défini.
    # Sinon, tu peux le passer ici: genai.Client(api_key="...")
    return genai.Client()


def extract_invoice_fields_from_image_bytes(
    image_bytes: bytes,
    mime_type: str = "image/png",
    model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """
    Envoie une image à Gemini et récupère un JSON structuré.
    """
    if not image_bytes:
        raise ValueError("image_bytes is empty")

    client = _client()

    resp = client.models.generate_content(
        model=model,
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"inline_data": {"mime_type": mime_type, "data": image_bytes}},
                ],
            }
        ],
        config={
            "response_mime_type": "application/json",
            "response_json_schema": INVOICE_JSON_SCHEMA,
            # petits garde-fous
            "temperature": 0.0,
        },
    )

    # Gemini renvoie un JSON texte (syntactiquement valide) si structured output OK.
    try:
        return json.loads(resp.text)
    except Exception as e:
        # debug utile si jamais la réponse n'est pas du JSON strict
        raise RuntimeError(f"Gemini response is not valid JSON. Raw: {resp.text[:500]}") from e
