



# import re
# from typing import Optional, Dict, Any, Tuple

# # IMPORTANT: accepte OCRResult ou str
# def extract_fields_from_ocr(ocr) -> Dict[str, Any]:
#     """
#     ocr peut être:
#       - OCRResult (avec .text)
#       - ou un string
#     """
#     if hasattr(ocr, "text"):
#         text = ocr.text
#     else:
#         text = str(ocr)

#     return parse_facture_text(text)


# # -------------------------
# # Normalisation
# # -------------------------
# def _normalize_text(text: str) -> str:
#     if not text:
#         return ""
#     t = text.replace("\r", "\n")
#     t = t.replace(",", ".")
#     t = re.sub(r"[ \t]+", " ", t)
#     t = re.sub(r"\bFactur[eé]\b", "FACTURE", t, flags=re.IGNORECASE)
#     t = re.sub(r"\bTotat\b", "Total", t, flags=re.IGNORECASE)
#     t = re.sub(r"T\.?\s*T\.?\s*C\.?", "TTC", t, flags=re.IGNORECASE)
#     t = re.sub(r"H\.?\s*T\.?", "HT", t, flags=re.IGNORECASE)
#     t = re.sub(r"(?<=\d)\s+(?=\d)", "", t)
#     return t


# def _to_float(s: Optional[str]) -> Optional[float]:
#     if not s:
#         return None
#     s = str(s).strip()
#     if not s:
#         return None

#     s = re.sub(r"(?<=\d)[oO](?=\d)", "0", s)
#     s = re.sub(r"[^0-9.]", "", s)

#     if s.count(".") > 1:
#         parts = re.split(r"\.+", s)
#         s = "".join(parts[:-1]) + "." + parts[-1]

#     try:
#         return float(s)
#     except Exception:
#         return None


# def _find_date_ddmmyyyy(text: str) -> Optional[str]:
#     # priorité: injection DATE_FACTURE: xx/xx/xxxx
#     m = re.search(r"DATE_FACTURE:\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})", text, flags=re.IGNORECASE)
#     if m:
#         return m.group(1).replace("-", "/").replace(".", "/")

#     m = re.search(r"(\d{2})\s*[/\-\.]\s*(\d{2})\s*[/\-\.]\s*(\d{4})", text)
#     if m:
#         return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
#     return None


# def _find_num_facture(text: str) -> Optional[str]:
#     m = re.search(
#         r"(FACTURE\s*(?:N|N°|NO|NUM|Nº)|REF(?:ERENCE)?|N°)\s*[:\-]?\s*([A-Z0-9/\-]{3,30})",
#         text,
#         flags=re.IGNORECASE,
#     )
#     if m:
#         val = m.group(2).strip()
#         # anti faux-positif simple
#         if val.upper() in ["CLIENT", "CLT"]:
#             return None
#         return val
#     return None


# def _find_totals(text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
#     ht = tva = ttc = None
#     AMOUNT = r"([0-9][0-9\.\s]{0,20})"

#     m = re.search(r"(?:MONTANT\s*)?HT\s*[:\-]?\s*" + AMOUNT, text, flags=re.IGNORECASE)
#     if m:
#         ht = _to_float(m.group(1))

#     m = re.search(r"(?:MONTANT\s*)?TVA\s*[:\-]?\s*" + AMOUNT, text, flags=re.IGNORECASE)
#     if m:
#         tva = _to_float(m.group(1))

#     m = re.search(
#         r"(TOTAL\s*A\s*PAYER\s*\(?\s*TTC\s*\)?|TOTAL\s*TTC|NET\s*A\s*PAYER|A\s*PAYER)\s*[:\-]?\s*"
#         + AMOUNT,
#         text,
#         flags=re.IGNORECASE,
#     )
#     if m:
#         ttc = _to_float(m.group(2))

#     if ttc is None and ht is not None and tva is not None:
#         ttc = round(ht + tva, 2)

#     return ht, tva, ttc


# def _find_supplier_footer_line(text: str) -> Optional[str]:
#     lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
#     for ln in reversed(lines):
#         up = ln.upper()
#         if ("IF" in up) and ("ICE" in up):
#             return ln
#     return None


# def _extract_if_ice_from_footer(footer_line: str) -> Tuple[Optional[str], Optional[str]]:
#     if_val = None
#     ice_val = None

#     m = re.search(r"\bIF\s*[:\-]?\s*([0-9]{6,12})\b", footer_line, flags=re.IGNORECASE)
#     if m:
#         if_val = m.group(1)

#     m = re.search(r"\bICE\s*[:\-]?\s*([0-9]{15})\b", footer_line, flags=re.IGNORECASE)
#     if m:
#         ice_val = m.group(1)

#     return if_val, ice_val


# def _find_supplier_name(text: str) -> Optional[str]:
#     lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
#     for ln in lines[:20]:
#         if re.search(r"\b(STE|STÉ|Sté)\b", ln, flags=re.IGNORECASE) and re.search(r"\b(SARL|SA)\b", ln, flags=re.IGNORECASE):
#             return re.sub(r"\s+", " ", ln).strip()
#     return None


# def _designation_fallback(fournisseur: Optional[str]) -> str:
#     return f"Achat fournisseur - {fournisseur}" if fournisseur else "Achat fournisseur"


# def parse_facture_text(text: str) -> Dict[str, Any]:
#     t = _normalize_text(text)

#     fournisseur = _find_supplier_name(t)
#     date_facture = _find_date_ddmmyyyy(t)
#     numero_facture = _find_num_facture(t)

#     ht, tva, ttc = _find_totals(t)

#     footer = _find_supplier_footer_line(t)
#     if_frs = ice_frs = None
#     if footer:
#         if_frs, ice_frs = _extract_if_ice_from_footer(footer)

#     taux_tva = None
#     if ht is not None and tva is not None and ht != 0:
#         taux_tva = round((float(tva) / float(ht)) * 100, 2)

#     designation = _designation_fallback(fournisseur)

#     return {
#         "fournisseur": fournisseur,
#         "date_facture": date_facture,
#         "numero_facture": numero_facture,
#         "designation": designation,
#         "montant_ht": ht,
#         "montant_tva": tva,
#         "montant_ttc": ttc,
#         "if_frs": if_frs,
#         "ice_frs": ice_frs,
#         "taux_tva": taux_tva,
#     }



















# # services/extract_fields.py
# import re
# from dataclasses import dataclass
# from typing import Any, Dict, Optional, Tuple

# from services.ocr_service import OCRResult

# AMOUNT_RE = re.compile(r"(?<!\d)(\d{1,3}(?:[ .]\d{3})*(?:[.,]\d{2})|\d+(?:[.,]\d{2})|\d+)(?!\d)")

# def _norm(text: str) -> str:
#     t = (text or "").replace("\r", "\n")
#     # uniformiser
#     t = t.replace("€", " ").replace("\t", " ")
#     # normaliser espaces
#     t = re.sub(r"[ \t]+", " ", t)
#     # enlever espaces entre chiffres (4 976,00 -> 4976,00)
#     t = re.sub(r"(?<=\d)\s+(?=\d)", "", t)
#     return t

# def _to_float(s: str) -> Optional[float]:
#     if not s:
#         return None
#     s = s.strip()
#     s = s.replace(" ", "")
#     s = s.replace(",", ".")
#     # garder digits + dot
#     s = re.sub(r"[^0-9.]", "", s)
#     if not s:
#         return None
#     # si trop de points
#     if s.count(".") > 1:
#         parts = re.split(r"\.+", s)
#         s = "".join(parts[:-1]) + "." + parts[-1]
#     try:
#         return float(s)
#     except Exception:
#         return None

# def _find_date(text: str) -> Optional[str]:
#     m = re.search(r"\b(\d{2})[\/\-.](\d{2})[\/\-.](\d{4})\b", text)
#     if m:
#         return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
#     return None

# def _find_supplier(text: str) -> Optional[str]:
#     # prend un nom “haut” en majuscules raisonnable
#     lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
#     for ln in lines[:20]:
#         if len(ln) < 4 or len(ln) > 60:
#             continue
#         # évite lignes “FACTURE”, “DATE”, etc.
#         if re.search(r"\b(FACTURE|DATE|CLIENT|TOTAL|TVA|TTC|HT)\b", ln, re.IGNORECASE):
#             continue
#         # heuristique: beaucoup de lettres
#         if sum(c.isalpha() for c in ln) >= 6:
#             return ln
#     return None

# def _find_if_ice(text: str) -> Tuple[Optional[str], Optional[str]]:
#     if_val = None
#     ice_val = None
#     # IF 6-12 chiffres
#     m = re.search(r"\bI\.?\s*F\b\s*[:\-]?\s*([0-9]{6,12})\b", text, re.IGNORECASE)
#     if m:
#         if_val = m.group(1)
#     # ICE 15 chiffres
#     m = re.search(r"\bICE\b\s*[:\-]?\s*([0-9]{15})\b", text, re.IGNORECASE)
#     if m:
#         ice_val = m.group(1)
#     return if_val, ice_val

# def _find_invoice_number(text: str) -> Optional[str]:
#     """
#     FIX: Priorise FACTURE N°.
#     Exclut Patente/RC/CNSS/ICE/IF/etc.
#     """
#     # 1) priorité FACTURE N°
#     m = re.search(
#         r"\bFACTURE\s*(?:N|N°|NO|Nº|NUM(?:ERO)?)\s*[:\-]?\s*([A-Z0-9][A-Z0-9/\-]{2,40})\b",
#         text,
#         flags=re.IGNORECASE,
#     )
#     if m:
#         cand = m.group(1).strip()
#         if cand.upper() not in {"CLIENT", "FACTURE"}:
#             return cand

#     # 2) fallback “N° ...” mais pas dans contexte légal
#     bad_ctx = re.compile(r"\b(PATENTE|RC|R\.C|CNSS|ICE|IF|I\.F|TVA|CLIENT)\b", re.IGNORECASE)
#     best = None
#     best_score = -1
#     for ln in text.splitlines():
#         if "N" not in ln.upper():
#             continue
#         if bad_ctx.search(ln):
#             continue
#         m2 = re.search(r"\b(?:N°|NO|Nº)\s*[:\-]?\s*([A-Z0-9][A-Z0-9/\-]{2,40})\b", ln, re.IGNORECASE)
#         if not m2:
#             continue
#         cand = m2.group(1).strip()
#         score = 0
#         if "/" in cand: score += 3
#         if 5 <= len(cand) <= 20: score += 2
#         if re.search(r"\d", cand): score += 1
#         if score > best_score:
#             best_score, best = score, cand
#     return best

# def _extract_amount_near_label(text: str, label_regex: str) -> Optional[float]:
#     # cherche label ... montant (sur 0-80 chars)
#     m = re.search(label_regex + r".{0,80}" + r"(" + AMOUNT_RE.pattern + r")", text, re.IGNORECASE | re.DOTALL)
#     if not m:
#         return None
#     return _to_float(m.group(1))

# def _extract_tva_rate(text: str) -> Optional[float]:
#     # “TVA 20%” “TVA : 20 %” etc.
#     m = re.search(r"\bTVA\b.{0,20}?(\d{1,2})\s*%", text, re.IGNORECASE)
#     if m:
#         try:
#             v = float(m.group(1))
#             if 0 < v <= 30:
#                 return v
#         except Exception:
#             return None
#     return None

# def _extract_totals(text: str) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
#     """
#     FIX: ne pas confondre taux TVA (20%) et montant TVA.
#     Retour: ht, montant_tva, ttc, taux_tva
#     """
#     taux = _extract_tva_rate(text)

#     # HT
#     ht = _extract_amount_near_label(text, r"\b(TOTAL\s*HT|MONTANT\s*HT|HT)\b")

#     # TTC
#     ttc = _extract_amount_near_label(text, r"\b(TOTAL\s*TTC|NET\s*A\s*PAYER|TOTAL\s*A\s*PAYER|A\s*PAYER)\b")

#     # Montant TVA (pas le taux)
#     # On cherche un montant “monétaire” proche de “TVA” MAIS on évite le pattern “TVA 20%”
#     montant_tva = None
#     # on balaie lignes
#     for ln in text.splitlines():
#         if not re.search(r"\bTVA\b", ln, re.IGNORECASE):
#             continue
#         # skip si c’est juste le taux
#         if re.search(r"\bTVA\b.{0,10}\d{1,2}\s*%", ln, re.IGNORECASE):
#             # peut contenir aussi un montant plus loin -> on continue quand même
#             pass
#         # prendre le plus grand montant sur la ligne (souvent le montant TVA)
#         nums = [ _to_float(x) for x in AMOUNT_RE.findall(ln) ]
#         nums = [n for n in nums if n is not None]
#         if nums:
#             cand = max(nums)
#             # un montant TVA réaliste n’est pas 20 quand HT est 7916.67
#             if cand is not None and cand > 50:
#                 montant_tva = cand
#                 break

#     # cohérence: si tva manque mais ht+ttc présents, calcule tva = ttc-ht (si plausible)
#     if montant_tva is None and ht is not None and ttc is not None:
#         diff = round(ttc - ht, 2)
#         if diff >= 0:
#             montant_tva = diff

#     # cohérence: si on a extrait “20” (taux) par erreur
#     if montant_tva is not None and ht is not None and ttc is not None:
#         # si montant_tva est petit (<= 30) mais ht/ttc grands => probablement taux
#         if montant_tva <= 30 and ttc > 200 and ht > 200:
#             diff = round(ttc - ht, 2)
#             if diff > 30:
#                 montant_tva = diff

#     # si taux absent, on peut le calculer
#     if taux is None and ht not in (None, 0) and montant_tva is not None:
#         taux = round((montant_tva / ht) * 100, 2)

#     return ht, montant_tva, ttc, taux

# def extract_fields_from_ocr(ocr: OCRResult) -> Dict[str, Any]:
#     t = _norm(ocr.text)

#     fournisseur = _find_supplier(t)
#     date_facture = _find_date(t)
#     numero_facture = _find_invoice_number(t)
#     if_frs, ice_frs = _find_if_ice(t)

#     ht, tva, ttc, taux = _extract_totals(t)

#     # dernière validation “TTC ≈ HT + TVA”
#     if ht is not None and tva is not None and ttc is not None:
#         if abs((ht + tva) - ttc) > max(2.0, 0.02 * ttc):
#             # si incohérent, on préfère recalculer TVA depuis HT/TTC
#             diff = round(ttc - ht, 2)
#             if diff >= 0:
#                 tva = diff

#     designation = f"Achat fournisseur - {fournisseur}" if fournisseur else "Achat fournisseur"

#     return {
#         "fournisseur": fournisseur,
#         "date_facture": date_facture,
#         "numero_facture": numero_facture,
#         "designation": designation,
#         "montant_ht": ht,
#         "montant_tva": tva,
#         "montant_ttc": ttc,
#         "if_frs": if_frs,
#         "ice_frs": ice_frs,
#         "taux_tva": taux,
#     }

















import re
from typing import Optional, Dict, Any, Tuple

# IMPORTANT: accepte OCRResult ou str
def extract_fields_from_ocr(ocr) -> Dict[str, Any]:
    """
    ocr peut être:
      - OCRResult (avec .text)
      - ou un string
    """
    if hasattr(ocr, "text"):
        text = ocr.text
    else:
        text = str(ocr)

    return parse_facture_text(text)


# -------------------------
# Normalisation
# -------------------------
def _normalize_text(text: str) -> str:
    if not text:
        return ""
    t = text.replace("\r", "\n")
    t = t.replace(",", ".")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\bFactur[eé]\b", "FACTURE", t, flags=re.IGNORECASE)
    t = re.sub(r"\bTotat\b", "Total", t, flags=re.IGNORECASE)
    t = re.sub(r"T\.?\s*T\.?\s*C\.?", "TTC", t, flags=re.IGNORECASE)
    t = re.sub(r"H\.?\s*T\.?", "HT", t, flags=re.IGNORECASE)
    t = re.sub(r"(?<=\d)\s+(?=\d)", "", t)
    return t


def _to_float(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    s = str(s).strip()
    if not s:
        return None

    s = re.sub(r"(?<=\d)[oO](?=\d)", "0", s)
    s = re.sub(r"[^0-9.]", "", s)

    if s.count(".") > 1:
        parts = re.split(r"\.+", s)
        s = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return float(s)
    except Exception:
        return None


def _find_date_ddmmyyyy(text: str) -> Optional[str]:
    # priorité: injection DATE_FACTURE: xx/xx/xxxx
    m = re.search(r"DATE_FACTURE:\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).replace("-", "/").replace(".", "/")

    m = re.search(r"(\d{2})\s*[/\-\.]\s*(\d{2})\s*[/\-\.]\s*(\d{4})", text)
    if m:
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}"
    return None


def _find_num_facture(text: str) -> Optional[str]:
    m = re.search(
        r"(FACTURE\s*(?:N|N°|NO|NUM|Nº)|REF(?:ERENCE)?|N°)\s*[:\-]?\s*([A-Z0-9/\-]{3,30})",
        text,
        flags=re.IGNORECASE,
    )
    if m:
        val = m.group(2).strip()
        # anti faux-positif simple
        if val.upper() in ["CLIENT", "CLT"]:
            return None
        return val
    return None


def _find_totals(text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    ht = tva = ttc = None
    AMOUNT = r"([0-9][0-9\.\s]{0,20})"

    m = re.search(r"(?:MONTANT\s*)?HT\s*[:\-]?\s*" + AMOUNT, text, flags=re.IGNORECASE)
    if m:
        ht = _to_float(m.group(1))

    m = re.search(r"(?:MONTANT\s*)?TVA\s*[:\-]?\s*" + AMOUNT, text, flags=re.IGNORECASE)
    if m:
        tva = _to_float(m.group(1))

    m = re.search(
        r"(TOTAL\s*A\s*PAYER\s*\(?\s*TTC\s*\)?|TOTAL\s*TTC|NET\s*A\s*PAYER|A\s*PAYER)\s*[:\-]?\s*"
        + AMOUNT,
        text,
        flags=re.IGNORECASE,
    )
    if m:
        ttc = _to_float(m.group(2))

    if ttc is None and ht is not None and tva is not None:
        ttc = round(ht + tva, 2)

    return ht, tva, ttc


def _find_supplier_footer_line(text: str) -> Optional[str]:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    for ln in reversed(lines):
        up = ln.upper()
        if ("IF" in up) and ("ICE" in up):
            return ln
    return None


def _extract_if_ice_from_footer(footer_line: str) -> Tuple[Optional[str], Optional[str]]:
    if_val = None
    ice_val = None

    m = re.search(r"\bIF\s*[:\-]?\s*([0-9]{6,12})\b", footer_line, flags=re.IGNORECASE)
    if m:
        if_val = m.group(1)

    m = re.search(r"\bICE\s*[:\-]?\s*([0-9]{15})\b", footer_line, flags=re.IGNORECASE)
    if m:
        ice_val = m.group(1)

    return if_val, ice_val


def _find_supplier_name(text: str) -> Optional[str]:
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    for ln in lines[:20]:
        if re.search(r"\b(STE|STÉ|Sté)\b", ln, flags=re.IGNORECASE) and re.search(r"\b(SARL|SA)\b", ln, flags=re.IGNORECASE):
            return re.sub(r"\s+", " ", ln).strip()
    return None


def _designation_fallback(fournisseur: Optional[str]) -> str:
    return f"Achat fournisseur - {fournisseur}" if fournisseur else "Achat fournisseur"


def parse_facture_text(text: str) -> Dict[str, Any]:
    t = _normalize_text(text)

    fournisseur = _find_supplier_name(t)
    date_facture = _find_date_ddmmyyyy(t)
    numero_facture = _find_num_facture(t)

    ht, tva, ttc = _find_totals(t)

    footer = _find_supplier_footer_line(t)
    if_frs = ice_frs = None
    if footer:
        if_frs, ice_frs = _extract_if_ice_from_footer(footer)

    taux_tva = None
    if ht is not None and tva is not None and ht != 0:
        taux_tva = round((float(tva) / float(ht)) * 100, 2)

    designation = _designation_fallback(fournisseur)

    return {
        "fournisseur": fournisseur,
        "date_facture": date_facture,
        "numero_facture": numero_facture,
        "designation": designation,
        "montant_ht": ht,
        "montant_tva": tva,
        "montant_ttc": ttc,
        "if_frs": if_frs,
        "ice_frs": ice_frs,
        "taux_tva": taux_tva,
    }
