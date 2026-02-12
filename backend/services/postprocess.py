import re
from typing import Dict, Any, Optional


def _to_float(x) -> Optional[float]:
    try:
        if x is None:
            return None
        if isinstance(x, (int, float)):
            return float(x)
        s = str(x).strip()
        if not s:
            return None
        # Support "7 916,67" -> 7916.67
        s = s.replace(" ", "").replace("\u00a0", "").replace(",", ".")
        return float(s)
    except Exception:
        return None


def clean_invoice_number(text: str) -> Optional[str]:
    if not text:
        return None

    t = text.upper()

    # On cherche plutôt près des mots "FACTURE" / "FACTURE N" / "N°"
    # mais on garde un fallback global si nécessaire.
    window_patterns = [
        r"(FACTURE\s*(N|N°|NUM|NUMÉRO|NO)?\s*[:#]?\s*)([A-Z]{1,5}[-/]?\d{3,})",
        r"(INVOICE\s*(NO|N°)?\s*[:#]?\s*)([A-Z]{1,5}[-/]?\d{3,})",
    ]

    for pat in window_patterns:
        m = re.search(pat, t, flags=re.IGNORECASE)
        if m:
            return m.group(3)

    # Fallback patterns (si OCR ne garde pas les libellés correctement)
    patterns = [
        r"\bFA[-/]?\d{3,}\b",
        r"\bFAC[-/]?\d{3,}\b",
        r"\bF[-/]?\d{5,}\b",
        r"\bINV[-/]?\d{3,}\b",
    ]
    for pat in patterns:
        m = re.search(pat, t)
        if m:
            return m.group(0)

    return None


def fix_fields(fields: Dict[str, Any], ocr_text: str) -> Dict[str, Any]:
    """
    Corrige:
    - montant_tva confondu avec taux_tva (ex: 20)
    - numero_facture faux (ex: chiffre d'ICE/RC)
    - cohérence HT/TVA/TTC
    """
    # ---------- FIX NUMERO FACTURE ----------
    num = fields.get("numero_facture")
    num_str = str(num).strip() if num is not None else ""

    # Si numero_facture = seulement chiffres -> très suspect
    if num_str and num_str.isdigit():
        good = clean_invoice_number(ocr_text)
        fields["numero_facture"] = good  # peut être None (mieux que faux)

    # Si vide -> essayer extraction OCR
    if not fields.get("numero_facture"):
        good = clean_invoice_number(ocr_text)
        if good:
            fields["numero_facture"] = good

    # ---------- FIX TVA ----------
    ht = _to_float(fields.get("montant_ht"))
    ttc = _to_float(fields.get("montant_ttc"))
    tva = _to_float(fields.get("montant_tva"))
    taux = _to_float(fields.get("taux_tva"))

    # Cas typique: montant_tva=20 (taux) au lieu d'un montant
    if ht is not None and ttc is not None:
        computed_tva = round(ttc - ht, 2)
        if computed_tva >= 0:
            if tva is None:
                fields["montant_tva"] = computed_tva
            else:
                # si tva est trop petite (10/14/20 etc)
                if tva in (10.0, 14.0, 20.0) or tva < 50:
                    fields["montant_tva"] = computed_tva

    # Si taux_tva manque mais on peut l'estimer
    ht = _to_float(fields.get("montant_ht"))
    tva = _to_float(fields.get("montant_tva"))
    if (taux is None or taux == 0) and ht and tva is not None and ht > 0:
        estimated = round((tva / ht) * 100, 2)
        # On arrondit au taux courant (20, 10, 7, 14...)
        common = [20, 10, 7, 14]
        closest = min(common, key=lambda c: abs(c - estimated))
        if abs(closest - estimated) <= 2.0:
            fields["taux_tva"] = closest

    return fields
