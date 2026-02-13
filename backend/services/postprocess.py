# import re
# from typing import Dict, Any, Optional


# def _to_float(x) -> Optional[float]:
#     try:
#         if x is None:
#             return None
#         if isinstance(x, (int, float)):
#             return float(x)
#         s = str(x).strip()
#         if not s:
#             return None
#         # Support "7 916,67" -> 7916.67
#         s = s.replace(" ", "").replace("\u00a0", "").replace(",", ".")
#         return float(s)
#     except Exception:
#         return None


# def clean_invoice_number(text: str) -> Optional[str]:
#     if not text:
#         return None

#     t = text.upper()

#     # On cherche plutôt près des mots "FACTURE" / "FACTURE N" / "N°"
#     # mais on garde un fallback global si nécessaire.
#     window_patterns = [
#         r"(FACTURE\s*(N|N°|NUM|NUMÉRO|NO)?\s*[:#]?\s*)([A-Z]{1,5}[-/]?\d{3,})",
#         r"(INVOICE\s*(NO|N°)?\s*[:#]?\s*)([A-Z]{1,5}[-/]?\d{3,})",
#     ]

#     for pat in window_patterns:
#         m = re.search(pat, t, flags=re.IGNORECASE)
#         if m:
#             return m.group(3)

#     # Fallback patterns (si OCR ne garde pas les libellés correctement)
#     patterns = [
#         r"\bFA[-/]?\d{3,}\b",
#         r"\bFAC[-/]?\d{3,}\b",
#         r"\bF[-/]?\d{5,}\b",
#         r"\bINV[-/]?\d{3,}\b",
#     ]
#     for pat in patterns:
#         m = re.search(pat, t)
#         if m:
#             return m.group(0)

#     return None


# def fix_fields(fields: Dict[str, Any], ocr_text: str) -> Dict[str, Any]:
#     """
#     Corrige:
#     - montant_tva confondu avec taux_tva (ex: 20)
#     - numero_facture faux (ex: chiffre d'ICE/RC)
#     - cohérence HT/TVA/TTC
#     """
#     # ---------- FIX NUMERO FACTURE ----------
#     num = fields.get("numero_facture")
#     num_str = str(num).strip() if num is not None else ""

#     # Si numero_facture = seulement chiffres -> très suspect
#     if num_str and num_str.isdigit():
#         good = clean_invoice_number(ocr_text)
#         fields["numero_facture"] = good  # peut être None (mieux que faux)

#     # Si vide -> essayer extraction OCR
#     if not fields.get("numero_facture"):
#         good = clean_invoice_number(ocr_text)
#         if good:
#             fields["numero_facture"] = good

#     # ---------- FIX TVA ----------
#     ht = _to_float(fields.get("montant_ht"))
#     ttc = _to_float(fields.get("montant_ttc"))
#     tva = _to_float(fields.get("montant_tva"))
#     taux = _to_float(fields.get("taux_tva"))

#     # Cas typique: montant_tva=20 (taux) au lieu d'un montant
#     if ht is not None and ttc is not None:
#         computed_tva = round(ttc - ht, 2)
#         if computed_tva >= 0:
#             if tva is None:
#                 fields["montant_tva"] = computed_tva
#             else:
#                 # si tva est trop petite (10/14/20 etc)
#                 if tva in (10.0, 14.0, 20.0) or tva < 50:
#                     fields["montant_tva"] = computed_tva

#     # Si taux_tva manque mais on peut l'estimer
#     ht = _to_float(fields.get("montant_ht"))
#     tva = _to_float(fields.get("montant_tva"))
#     if (taux is None or taux == 0) and ht and tva is not None and ht > 0:
#         estimated = round((tva / ht) * 100, 2)
#         # On arrondit au taux courant (20, 10, 7, 14...)
#         common = [20, 10, 7, 14]
#         closest = min(common, key=lambda c: abs(c - estimated))
#         if abs(closest - estimated) <= 2.0:
#             fields["taux_tva"] = closest

#     return fields












import re
from typing import Any, Dict, List, Optional

from utils.parsers import parse_amount

def _norm_text(s: str) -> str:
    s = s.replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    return s

def _parse_percent(val: str) -> Optional[float]:
    if not val:
        return None
    val = val.replace(",", ".")
    try:
        x = float(val)
    except Exception:
        return None
    # Fix OCR: 200% -> 20%, 2000% -> 20%, etc.
    while x is not None and x > 100:
        x = x / 10.0
    # sanity
    if x < 0 or x > 100:
        return None
    return round(x, 2)

def _find_tva_line(text: str) -> Optional[Dict[str, Any]]:
    """
    Cherche une ligne TVA qui contient souvent un taux + montant.
    Exemples attendus:
      "TVA 20.00% 828.00 DHS"
      "TVA 20%: 828,00"
      "TVA 20 % 828.00"
    """
    t = _norm_text(text)
    lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
    for ln in lines:
        if "TVA" not in ln.upper():
            continue

        # On récupère un % (si présent)
        m_pct = re.search(r"(\d{1,4}(?:[.,]\d{1,2})?)\s*%", ln)
        pct = _parse_percent(m_pct.group(1)) if m_pct else None

        # On récupère un montant (souvent à droite)
        # On prend le dernier "gros" nombre type 828.00 / 1,133.33 etc.
        nums = re.findall(r"(\d{1,3}(?:[ .,\u00A0]\d{3})*(?:[.,]\d{2})|\d+(?:[.,]\d{2}))", ln)
        amount = None
        if nums:
            # dernier nombre plausible
            amount = parse_amount(nums[-1])

        # Si OCR a collé "200%" sans point, pct sera 20.0 grâce au while >100
        if pct is not None or amount is not None:
            return {"taux_tva": pct, "montant_tva": amount, "raw": ln}

    return None

def postprocess_fields(fields: Dict[str, Any], ocr_text: str) -> (Dict[str, Any], List[str]):
    issues: List[str] = []
    out = dict(fields)

    ht = parse_amount(out.get("montant_ht"))
    ttc = parse_amount(out.get("montant_ttc"))

    # 1) Extraire TVA depuis OCR (si dispo)
    tva_line = _find_tva_line(ocr_text or "")
    if tva_line:
        if tva_line.get("taux_tva") is not None:
            out["taux_tva"] = tva_line["taux_tva"]
        if tva_line.get("montant_tva") is not None:
            out["montant_tva"] = tva_line["montant_tva"]
        issues.append(f"TVA line detected: {tva_line.get('raw')}")

    # 2) Normaliser types
    taux = out.get("taux_tva")
    taux = parse_amount(taux) if taux is not None else None
    if taux is not None:
        # si 200 -> 20 etc (encore une sécurité)
        while taux > 100:
            taux /= 10.0
        if taux < 0 or taux > 100:
            issues.append(f"Invalid taux_tva after clamp: {taux}")
            taux = None
    out["taux_tva"] = round(taux, 2) if taux is not None else None

    m_tva = parse_amount(out.get("montant_tva"))
    out["montant_tva"] = m_tva

    # 3) Corriger confusion montant_tva (ex: 20 au lieu de 828)
    # Si montant_tva est petit (<=100) MAIS HT est grand, il y a de fortes chances que ce soit un taux.
    if ht and m_tva is not None and m_tva <= 100 and (out.get("taux_tva") is None or abs(out["taux_tva"] - m_tva) < 0.01):
        # On considère que m_tva était un taux
        out["taux_tva"] = round(float(m_tva), 2)
        out["montant_tva"] = None
        issues.append("montant_tva looked like a percent; moved to taux_tva")

    # 4) Recalculer ce qui manque via HT/TTC/taux
    ht = parse_amount(out.get("montant_ht"))
    ttc = parse_amount(out.get("montant_ttc"))
    taux = out.get("taux_tva")
    m_tva = out.get("montant_tva")

    if m_tva is None:
        if ht is not None and ttc is not None and ttc >= ht:
            out["montant_tva"] = round(ttc - ht, 2)
            issues.append("montant_tva computed as TTC - HT")
        elif ht is not None and taux is not None:
            out["montant_tva"] = round(ht * (taux / 100.0), 2)
            issues.append("montant_tva computed as HT * taux_tva")

    # 5) Si taux manquant, le déduire
    ht = parse_amount(out.get("montant_ht"))
    m_tva = parse_amount(out.get("montant_tva"))
    if out.get("taux_tva") is None and ht and m_tva is not None and ht > 0:
        out["taux_tva"] = round((m_tva / ht) * 100.0, 2)
        issues.append("taux_tva computed as montant_tva / HT * 100")

    return out, issues
