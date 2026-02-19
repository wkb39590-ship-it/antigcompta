"""
gemini_service.py — Extraction structurée et classification PCM via Gemini API
"""
import json
import os
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

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

HEADER_SYSTEM_PROMPT = """Tu es un moteur d'extraction de factures marocaines spécialisé dans les documents comptables.
Ton objectif: extraire PRÉCISÉMENT tous les champs d'en-tête d'une facture.

CHAMPS À EXTRAIRE ABSOLUMENT:
1. ENTÊTE (bloc supérieur)
   - numero_facture: Le numéro ou référence unique de la facture (ex: "FAC-2024-001", "N°12345")
   - date_facture: Date d'émission (DD/MM/YYYY ou jour/mois/année en français)

2. PARTIES (corps du document)
   - supplier_name: NOM/RAISON SOCIALE du fournisseur/vendeur (celui qui émet la facture)
   - supplier_ice: ICE du fournisseur (15 chiffres exactement)
   - supplier_if: Identifiant Fiscal du fournisseur
   - supplier_rc: Registre de Commerce du fournisseur
   - client_name: NOM/RAISON SOCIALE du client/acheteur (celui qui reçoit)
   - client_ice: ICE du client
   - client_if: IF du client

3. MONTANTS (section "Total" ou "Résumé")
   - montant_ht: Sous-total / Total HT (avant TVA)
   - montant_tva: Montant TVA
   - montant_ttc: Total TTC (après TVA)
   - taux_tva: Taux de TVA (7, 10, 14 ou 20 en %)

4. AUTRES
   - devise: Devise (MAD par défaut)
   - invoice_type: ACHAT ou VENTE selon le contexte
   - payment_mode: Mode de paiement (Chèque, Virement, Espèces, etc)
   - payment_terms: Conditions de paiement (À la livraison, 30 jours, etc)

RÈGLES DE PARSING:
- Si une valeur est absente => null (JAMAIS de chaîne vide)
- Montants: transformer "10 000,00" ou "10.000,00" en 10000.00 (nombre décimal)
- ICE: extraire exactement 15 chiffres consécutifs, ignorer les espaces/tirets
- Dates: Chercher les formats "05/06/2025", "5 juin 2025", "JUIN 2025" => DD/MM/YYYY
- Numéro facture: Chercher "FACTURE", "N°", "Ref", "Invoice #", etc.

ATTENTION: Ne renvoie RIEN d'autre que le JSON valide. Pas de commentaires, pas d'explications.
"""


def _extract_ice_from_text(text: str) -> Optional[str]:
    """Extrait un ICE (15 chiffres) du texte."""
    match = re.search(r'\b(\d{15})\b', text)
    if match:
        return match.group(1)
    return None


def _parse_montant(text: str) -> Optional[float]:
    """Parse un montant au format français (10 000,00 ou 10.000,00)."""
    if not text:
        return None
    text = str(text).strip()
    # Remplacer espaces et points par rien, virgule par point
    text = text.replace(' ', '').replace('.', '')
    text = text.replace(',', '.')
    try:
        return float(text)
    except:
        return None


def _extract_invoice_header_fallback(ocr_text: str) -> Dict[str, Any]:
    """Fallback: extrait l'en-tête facture via parsing du texte OCR."""
    print("[Fallback OCR] Extraction des champs de la facture...")
    
    result = {
        "numero_facture": None,
        "date_facture": None,
        "invoice_type": "ACHAT",
        "supplier_name": None,
        "supplier_ice": None,
        "supplier_if": None,
        "supplier_rc": None,
        "client_name": None,
        "client_ice": None,
        "client_if": None,
        "montant_ht": None,
        "montant_tva": None,
        "montant_ttc": None,
        "taux_tva": None,
        "devise": "MAD",
        "payment_mode": None,
        "payment_terms": None,
    }
    
    lines = ocr_text.split('\n')
    
    # Chercher le numéro de facture
    for line in lines:
        if re.search(r'\b(?:facture|ref|n°|invoice|numéro)\b', line, re.IGNORECASE):
            # Extraire tout après le mot-clé jusqu'au premier espace/tiret significatif
            match = re.search(r'(?:facture|ref|n°|invoice|numéro)\s*:?\s*([A-Z0-9\-/\.]+)', line, re.IGNORECASE)
            if match:
                invoice_num = match.group(1).strip(' \t\n')
                if len(invoice_num) > 2 and len(invoice_num) < 50:
                    result["numero_facture"] = invoice_num
                    print(f"[OCR] Numéro facture trouvé: {invoice_num}")
                    break
    
    # Chercher la date (DD/MM/YYYY ou variations)
    for line in lines:
        match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4}|\d{2})', line)
        if match:
            day, month, year = match.groups()
            year = "20" + year if len(year) == 2 else year
            result["date_facture"] = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
            print(f"[OCR] Date facture trouvée: {result['date_facture']}")
            break
    
    # Chercher les ICE (supplier et client)
    ice_matches = re.findall(r'\b(\d{15})\b', ocr_text)
    ice_matches = list(dict.fromkeys(ice_matches))  # Dédupliquer
    if ice_matches:
        result["supplier_ice"] = ice_matches[0]
        print(f"[OCR] Supplier ICE trouvé: {ice_matches[0]}")
        if len(ice_matches) > 1:
            result["client_ice"] = ice_matches[1]
            print(f"[OCR] Client ICE trouvé: {ice_matches[1]}")
    
    # Chercher les montants de façon intelligente
    # Chercher les lignes avec "HT", "TVA", "TTC", "Total"
    montant_ht = None
    montant_tva = None
    montant_ttc = None
    
    for line in lines:
        line_upper = line.upper()
        
        # Chercher "HT" ou "SANS TVA"
        if re.search(r'\b(?:ht|sans tva|before tax)\b', line_upper):
            match = re.search(r'(?:ht|sans tva)[\s:]*([0-9,.\s]+)', line, re.IGNORECASE)
            if match:
                val = _parse_montant(match.group(1))
                if val and val > 0:
                    montant_ht = val
                    print(f"[OCR] Montant HT trouvé: {val}")
        
        # Chercher "TVA"
        if re.search(r'\b(?:tva|tax)\b', line_upper) and not re.search(r'(?:taux|rate|%)', line, re.IGNORECASE):
            match = re.search(r'(?:tva|tax)[\s:]*([0-9,.\s]+)', line, re.IGNORECASE)
            if match:
                val = _parse_montant(match.group(1))
                if val and val > 0:
                    montant_tva = val
                    print(f"[OCR] Montant TVA trouvé: {val}")
        
        # Chercher "TTC" ou "TOTAL"
        if re.search(r'\b(?:ttc|total|amount due|montant total)\b', line_upper):
            match = re.search(r'(?:ttc|total|amount due|montant total)[\s:]*([0-9,.\s]+)', line, re.IGNORECASE)
            if match:
                val = _parse_montant(match.group(1))
                if val and val > 0:
                    montant_ttc = val
                    print(f"[OCR] Montant TTC trouvé: {val}")
        
        # Chercher le taux TVA
        if re.search(r'(?:taux|rate|tva)\s*\(?\d', line, re.IGNORECASE):
            tva_match = re.search(r'(\d+(?:[.,]\d{1,2})?)\s*%', line)
            if tva_match:
                tva_str = tva_match.group(1).replace(',', '.')
                result["taux_tva"] = float(tva_str)
                print(f"[OCR] Taux TVA trouvé: {result['taux_tva']}%")
    
    # Fallback si pas trouvé avec labels: chercher les nombres importants
    if not montant_ht and not montant_tva and not montant_ttc:
        print("[OCR] Fallback: extraction des nombre importants...")
        # Chercher les nombres décimaux importants
        montants = re.findall(r'\b(\d+[.,]\d{2})\b', ocr_text)
        if montants:
            vals = []
            for m in montants:
                val = _parse_montant(m)
                if val and val > 0 and val < 1000000:  # Montants raisonnables
                    vals.append(val)
            
            vals = sorted(set(vals))  # Dédupliquer et trier
            print(f"[OCR] Nombres trouvés: {vals}")
            
            # Généralement: HT < TVA < TTC
            if len(vals) >= 3:
                montant_ht = vals[0]
                montant_tva = vals[1]
                montant_ttc = vals[2]
            elif len(vals) == 2:
                montant_ht = vals[0]
                montant_ttc = vals[1]
                # Calculer TVA
                montant_tva = montant_ttc - montant_ht if montant_ttc > montant_ht else 0
    
    # Vérifier cohérence HT + TVA = TTC
    if montant_ht and montant_tva and montant_ttc:
        calculated_ttc = montant_ht + montant_tva
        if abs(calculated_ttc - montant_ttc) > 0.1:  # Tolérance 0.10 MAD
            print(f"[OCR] ⚠️ Incohérence montants: {montant_ht} + {montant_tva} = {calculated_ttc} ≠ {montant_ttc}")
            # Corriger: utiliser le TTC en priorité, recalculer TVA
            if not montant_tva:
                montant_tva = montant_ttc - montant_ht
    
    result["montant_ht"] = montant_ht
    result["montant_tva"] = montant_tva
    result["montant_ttc"] = montant_ttc
    
    print(f"[OCR] Résumé: HT={montant_ht}, TVA={montant_tva}, TTC={montant_ttc}")
    return result


def extract_invoice_header(
    image_bytes: bytes,
    mime_type: str = "image/png",
    model: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """Extrait les champs d'en-tête obligatoires de la facture (Tableau 1).
    Essaie Gemini en premier, puis fallback OCR."""
    if not image_bytes:
        raise ValueError("image_bytes is empty")

    # Essayer Gemini
    try:
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
        data = json.loads(resp.text)
        
        # Si Gemini a extrait au moins numero_facture + supplier_name, c'est bon
        if data.get("numero_facture") and data.get("supplier_name"):
            print("[Gemini] ✅ Extraction réussie")
            # Compat legacy
            if data.get("supplier_name") and not data.get("fournisseur"):
                data["fournisseur"] = data["supplier_name"]
            if data.get("supplier_ice") and not data.get("ice_frs"):
                data["ice_frs"] = data["supplier_ice"]
            if data.get("supplier_if") and not data.get("if_frs"):
                data["if_frs"] = data["supplier_if"]
            return data
        else:
            print("[Gemini] ⚠️ Réponse incomplète (fields manquants)")
    except Exception as e:
        print(f"[Gemini] ❌ Erreur: {str(e)[:100]}")
    
    # Fallback: OCR + parsing
    print("[Pipeline] Utilisant fallback OCR + parsing...")
    try:
        from services import ocr_service
        from pathlib import Path
        import tempfile
        
        # Sauvegarder les bytes en fichier temporaire
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name
        
        try:
            ocr_result = ocr_service.extract(tmp_path)
            ocr_text = ocr_result.text if hasattr(ocr_result, 'text') else str(ocr_result)
            return _extract_invoice_header_fallback(ocr_text)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        print(f"[Fallback OCR] Erreur: {str(e)[:100]}")
        # Dernier fallback: retourner un dictionnaire vide complété
        return {
            "numero_facture": None,
            "date_facture": None,
            "invoice_type": "ACHAT",
            "supplier_name": None,
            "supplier_ice": None,
            "supplier_if": None,
            "supplier_rc": None,
            "client_name": None,
            "client_ice": None,
            "client_if": None,
            "montant_ht": 0,
            "montant_tva": 0,
            "montant_ttc": 0,
            "taux_tva": 0,
            "devise": "MAD",
            "payment_mode": None,
            "payment_terms": None,
        }


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
