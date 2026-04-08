"""
gemini_service.py — Extraction structurée et classification PCM via Gemini API
"""
import base64
import json
import os
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from google import genai
import time

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def _get_api_keys() -> List[str]:
    """Récupère toutes les clés Gemini définies dans le .env pour rotation."""
    keys = []
    if os.getenv("GEMINI_API_KEY"):
        keys.append(os.getenv("GEMINI_API_KEY"))
    for i in range(1, 4):
        k = os.getenv(f"GEMINI_API_KEY_{i}")
        if k and k not in keys:
            keys.append(k)
    return keys


def _client(api_key: Optional[str] = None) -> genai.Client:
    """Initialise le client avec une clé spécifique ou la première disponible."""
    key = api_key or _get_api_keys()[0]
    return genai.Client(api_key=key)


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
        "required": ["description", "quantity", "unit_price_ht", "line_amount_ht", "tva_rate", "tva_amount"]
    }
}

UNIFIED_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "header": HEADER_SCHEMA,
        "lines": LINES_SCHEMA,
    },
    "required": ["header", "lines"]
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
# Prompts
# ─────────────────────────────────────────────

HEADER_LINES_SYSTEM_PROMPT = """Tu es un expert-comptable marocain.
Extrais les données de cette facture au format JSON structuré.
TRES IMPORTANT:
1. supplier_ice (ICE fournisseur) doit contenir exactement 15 chiffres si présent.
2. client_name et client_ice doivent correspondre EXACTEMENT à ce qui est écrit sur la facture comme destinataire/client.
3. supplier_name est l'émetteur de la facture (celui qui vend ou fournit).
4. Si une information est absente de la facture, mets null.
5. Extrais TOUTES les lignes. ATTENTION : vérifie si les montants par ligne sont HT ou TTC.
   - Si la colonne est libellée 'TTC' ou si la somme des montants de ligne égale le MONTANT TTC total, alors extrais-les comme line_amount_ttc et calcule le line_amount_ht = TTC / (1 + taux_tva/100).
   - Assure la cohérence: line_amount_ht + tva_amount = line_amount_ttc.
6. invoice_type: utilise ACHAT si la facture est un achat, VENTE si c'est une vente, AVOIR pour un avoir/note de crédit, IMMOBILISATION si c'est un bien durable.
"""

HEADER_ONLY_SYSTEM_PROMPT = """Tu es un expert-comptable marocain.
Extrais uniquement les informations d'en-tête de cette facture (pas les lignes de détail).
TRES IMPORTANT:
1. supplier_ice (ICE fournisseur) doit contenir exactement 15 chiffres si présent.
2. client_name est le destinataire de la facture, supplier_name est l'émetteur.
3. Si une information est absente de la facture, mets null.
"""

LINES_ONLY_SYSTEM_PROMPT = """Tu es un expert-comptable marocain.
Extrais uniquement les lignes de produits/services de cette facture.
Pour chaque ligne, extrais: description, quantité, unité, prix unitaire HT, montant HT, taux TVA (%), montant TVA, montant TTC ligne.
ATTENTION : vérifie si les montants par ligne sont HT ou TTC. Si le montant affiché est TTC, calcule le HT correspondant pour remplir line_amount_ht.
Assure-toi que: line_amount_ht + tva_amount = line_amount_ttc.
Si une valeur est absente, mets null.
"""

CLASSIFICATION_SYSTEM_PROMPT = """Tu es un expert-comptable marocain spécialisé dans le Plan Comptable Marocain (PCM/CGNC).
Ton rôle est d'analyser une description de produit et de l'affecter au bon compte comptable.

RÈGLES DE CLASSIFICATION PCM:

1. IMMOBILISATIONS (Classe 2) — À utiliser si la description contient des biens durables > 5 000 MAD:
   - 2355 : Matériel informatique (ordinateur, serveur, laptop, PC, imprimante, scanner, écran)
   - 2340 : Matériel de transport (véhicule, camion, voiture)
   - 2350 : Matériel et outillage (machine, équipement industriel)
   - 2390 : Autres immobilisations corporelles
   - 2220 : Logiciels, licences (incorporelle)
   → IMPORTANT: Si le type_facture est IMMOBILISATION ou si la description mentionne explicitement
     "Immobilisation", utilise OBLIGATOIREMENT un compte de classe 2 (2xxx).
   → INTERDICTION STRICTE: Les matériaux de construction, de finition, peintures ou produits chimiques (ex: 'SILVER', 'VINYL', 'ENDUIT', 'VERNIS', 'PATE', 'KG', 'LITRE') NE SONT JAMAIS des immobilisations ni du matériel informatique (2355). Ces termes renvoient à des biens consommables.

2. ACHATS / CHARGES (Classe 6) — Pour les biens consommables ou services:
   - 6111 : Achats de marchandises revendues
   - 6121 : Achats de matières premières (ex: achats de matériaux, peintures, vernis, enduits, argent/silver pour production)
   - 6122 : Achats de matières et fournitures liées (fournitures consommables)
   - 6132 : Fournitures de bureau
   - 6141 : Sous-traitance
   - 6155 : Entretien et réparations
   - 6161 : Assurances
   - 6174 : Transport
   - 6185 : Frais de téléphone / abonnements
   - 6124 : Achats de matières et fournitures consommables
   - 6125 : Achats de fournitures non stockables (eau, électricité)
   - 6144 : Publicité, publications, relations publiques
   - 6145 : Déplacements, missions et réceptions
   → INDICATION: Systématiquement basculer tout achat de matériaux chimiques, de finition ou de bricolage (peinture, vernis, pâte) vers les comptes de la classe 6 (6121 ou 6122 selon la destination), pour refléter la nature réelle de l'objet.

3. PRODUITS / VENTES (Classe 7) — Pour une facture de vente:
   - 7111 : Vente de marchandises au Maroc
   - 7121 : Vente de produits finis

4. TVA (Classe 3 ou 4) — Non utilisé ici (géré par le générateur d'écritures).
"""


# ─────────────────────────────────────────────
# Helpers internes
# ─────────────────────────────────────────────

def _build_image_parts(image_data: Any, mime_type: str, max_pages: int = 3) -> list:
    """Construit la liste de parts (texte + images) pour Gemini."""
    images_list = image_data if isinstance(image_data, list) else [image_data]
    parts = []
    for img_bytes in images_list[:max_pages]:  # Paramétrable
        b64_data = base64.b64encode(img_bytes).decode("utf-8") if isinstance(img_bytes, (bytes, bytearray)) else img_bytes
        parts.append({"inline_data": {"mime_type": mime_type, "data": b64_data}})
    return parts


def _call_gemini(parts: list, schema: dict, model: str = None) -> Optional[dict]:
    """Appel générique Gemini avec rotation des clés et structured output."""
    used_model = model or DEFAULT_MODEL
    api_keys = _get_api_keys()

    if not api_keys:
        print("[Gemini] ❌ Aucune clé API disponible.")
        return None

    for key_index, current_key in enumerate(api_keys):
        for attempt in range(3):
            try:
                client = _client(current_key)
                resp = client.models.generate_content(
                    model=used_model,
                    contents=[{"role": "user", "parts": parts}],
                    config={
                        "response_mime_type": "application/json",
                        "response_json_schema": schema,
                        "temperature": 0.0,
                    },
                )
                if resp and resp.text:
                    return json.loads(resp.text)
            except Exception as e:
                err_str = str(e)
                print(f"[Gemini SDK] ⚠️ Erreur clé #{key_index} (Essai {attempt+1}/3): {err_str}")
                if "429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower() or "503" in err_str or "unavailable" in err_str.lower():
                    time.sleep(0.5)
                else:
                    time.sleep(0.1)
                continue

    return None


# ─────────────────────────────────────────────
# Fonctions publiques d'extraction
# ─────────────────────────────────────────────

def extract_invoice_full(
    image_data: Any,
    mime_type: str = "image/png",
    model: str = None,
) -> Dict[str, Any]:
    """
    Extraction unifiée Header + Lines via Gemini (structured output JSON).
    Retourne {"header": {...}, "lines": [...]}
    """
    if not image_data:
        raise ValueError("image_data is empty")

    image_parts = _build_image_parts(image_data, mime_type)
    parts = [{"text": HEADER_LINES_SYSTEM_PROMPT}] + image_parts

    data = _call_gemini(parts, UNIFIED_SCHEMA, model)

    if data:
        header = data.get("header", {})
        if header.get("supplier_name") or header.get("montant_ttc"):
            # Compatibilité legacy
            header["fournisseur"] = header.get("supplier_name")
            header["ice_frs"] = header.get("supplier_ice")
            header["if_frs"] = header.get("supplier_if")
            print(f"[Gemini] ✅ Extraction unifiée réussie: {header.get('supplier_name')} — TTC: {header.get('montant_ttc')}")
            return data

    print("[Gemini] ⚠️ Extraction unifiée vide ou échouée.")
    return {"header": {}, "lines": []}


def extract_invoice_header(
    image_data: Any,
    mime_type: str = "image/png",
    model: str = None,
) -> Dict[str, Any]:
    """
    Extraction de l'en-tête uniquement (Header) via Gemini.
    Retourne le dict header directement.
    """
    if not image_data:
        raise ValueError("image_data is empty")

    image_parts = _build_image_parts(image_data, mime_type)
    parts = [{"text": HEADER_ONLY_SYSTEM_PROMPT}] + image_parts

    result = _call_gemini(parts, HEADER_SCHEMA, model)

    if result:
        result["fournisseur"] = result.get("supplier_name")
        result["ice_frs"] = result.get("supplier_ice")
        result["if_frs"] = result.get("supplier_if")
        print(f"[Gemini] ✅ Extraction header réussie: {result.get('supplier_name')}")
        return result

    print("[Gemini] ⚠️ Extraction header échouée.")
    return {}


def extract_invoice_lines(
    image_data: Any,
    mime_type: str = "image/png",
    model: str = None,
) -> List[Dict[str, Any]]:
    """
    Extraction des lignes produits uniquement via Gemini.
    Retourne une liste de lignes.
    """
    if not image_data:
        raise ValueError("image_data is empty")

    image_parts = _build_image_parts(image_data, mime_type)
    parts = [{"text": LINES_ONLY_SYSTEM_PROMPT}] + image_parts

    result = _call_gemini(parts, LINES_SCHEMA, model)

    if result and isinstance(result, list):
        print(f"[Gemini] ✅ Extraction lignes réussie: {len(result)} lignes")
        return result

    print("[Gemini] ⚠️ Extraction lignes échouée.")
    return []


def extract_invoice_fields_from_image_bytes(
    image_bytes: bytes,
    mime_type: str = "image/png",
    model: str = None,
) -> Dict[str, Any]:
    """
    Alias compatible — extraction unifiée à partir d'un seul objet bytes.
    Retourne {"header": {...}, "lines": [...]}
    """
    return extract_invoice_full(image_bytes, mime_type=mime_type, model=model)


# ─────────────────────────────────────────────
# Classification PCM ligne par ligne
# ─────────────────────────────────────────────

def classify_product_pcm(description: str, amount: float = 0.0, invoice_type: str = "ACHAT") -> Dict[str, Any]:
    """Classifie un produit via Gemini selon le Plan Comptable Marocain."""
    if not description:
        return {}

    # Gemini ne supporte pas role "system" dans contents — on combine dans le prompt user
    prompt = f"""{CLASSIFICATION_SYSTEM_PROMPT}

RÉPONDS UNIQUEMENT AU FORMAT JSON SUIVANT:
{{
  "pcm_class": integer,
  "pcm_account_code": "string",
  "pcm_account_label": "string",
  "confidence": float,
  "reason": "string"
}}

Description: {description}
Montant: {amount} MAD
Type facture: {invoice_type}"""

    api_keys = _get_api_keys()
    for key_index, key in enumerate(api_keys):
        for attempt in range(3):
            try:
                client = _client(key)
                resp = client.models.generate_content(
                    model=DEFAULT_MODEL,
                    contents=[{"role": "user", "parts": [{"text": prompt}]}],
                    config={
                        "response_mime_type": "application/json",
                        "response_json_schema": CLASSIFICATION_SCHEMA,
                        "temperature": 0.0,
                    },
                )
                if resp and resp.text:
                    return json.loads(resp.text)
            except Exception as e:
                err_str = str(e)
                print(f"[Gemini PCM] ⚠️ Erreur clé #{key_index} (Essai {attempt+1}/3): {err_str}")
                if "429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower() or "503" in err_str or "unavailable" in err_str.lower():
                    time.sleep(0.5)
                else:
                    time.sleep(0.1)
                continue

    return {}

# ─────────────────────────────────────────────
# Relevés bancaires (Bank Statements)
# ─────────────────────────────────────────────

BANK_STATEMENT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "banque_nom": {"type": ["string", "null"]},
        "compte_bancaire": {"type": ["string", "null"]},
        "date_debut": {"type": ["string", "null"]},
        "date_fin": {"type": ["string", "null"]},
        "solde_initial": {"type": ["number", "null"]},
        "solde_final": {"type": ["number", "null"]},
        "lignes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date_operation": {"type": ["string", "null"]},
                    "date_valeur": {"type": ["string", "null"]},
                    "description": {"type": ["string", "null"]},
                    "reference": {"type": ["string", "null"]},
                    "debit": {"type": ["number", "null"]},
                    "credit": {"type": ["number", "null"]},
                },
                "required": ["date_operation", "description"]
            }
        }
    },
    "required": ["lignes"]
}

BANK_CLASSIFICATION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "pcm_account_code": {"type": ["string", "null"]},
        "pcm_account_label": {"type": ["string", "null"]},
        "confidence": {"type": ["number", "null"]},
        "reason": {"type": ["string", "null"]},
    },
    "required": ["pcm_account_code", "pcm_account_label", "confidence"]
}

def extract_bank_statement(image_data: Any, mime_type: str = "image/png", model: str = None) -> Dict[str, Any]:
    """Extraction d'un relevé bancaire via Gemini."""
    if not image_data:
        raise ValueError("image_data is empty")

    prompt = """Tu es un expert-comptable marocain.
Extrais TOUTES les transactions de ce relevé bancaire au format JSON.
Pour chaque transaction, extrais : 
- date_operation (Format DD/MM/YYYY)
- date_valeur (Format DD/MM/YYYY)
- description (Libellé de l'opération)
- reference (Numéro de chèque, virement ou référence si disponible)
- debit (Nombre positif si débit)
- credit (Nombre positif si crédit)

Extrais aussi les informations générales :
- banque_nom (Nom de la banque)
- compte_bancaire (Numéro de compte / RIB)
- date_debut et date_fin (Période du relevé)
- solde_initial et solde_final
"""
    # On autorise jusqu'à 10 pages pour un relevé
    image_parts = _build_image_parts(image_data, mime_type, max_pages=10)
    parts = [{"text": prompt}] + image_parts

    result = _call_gemini(parts, BANK_STATEMENT_SCHEMA, model)
    return result if result else {"lignes": []}

def classify_bank_transaction(description: str, debit: float = 0.0, credit: float = 0.0) -> Dict[str, Any]:
    """Suggère un compte de contrepartie pour une transaction bancaire."""
    prompt = f"Description: {description}\nDébit: {debit}\nCrédit: {credit}\nTrouve le compte du Plan Comptable Marocain le plus pertinent pour être la contrepartie."
    
    api_keys = _get_api_keys()
    used_model = DEFAULT_MODEL
    
    for key_index, key in enumerate(api_keys):
        for attempt in range(3):
            try:
                client = _client(key)
                resp = client.models.generate_content(
                    model=used_model,
                    contents=[{"role": "user", "parts": [{"text": prompt}]}],
                    config={
                        "response_mime_type": "application/json",
                        "response_json_schema": BANK_CLASSIFICATION_SCHEMA,
                        "temperature": 0.0,
                    },
                )
                if resp and resp.text:
                    return json.loads(resp.text)
            except Exception as e:
                err_str = str(e)
                print(f"[Gemini Bank] ⚠️ Erreur clé #{key_index} (Essai {attempt+1}/3): {err_str}")
                if "429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower() or "503" in err_str or "unavailable" in err_str.lower():
                    time.sleep(0.5)
                else:
                    time.sleep(0.1)
                continue
    
    return {"pcm_account_code": "47110000", "pcm_account_label": "Compte d'attente", "confidence": 0}
