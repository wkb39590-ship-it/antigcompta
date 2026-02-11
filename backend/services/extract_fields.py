


# import re
# from typing import Optional, Dict, Any


# def _normalize_text(text: str) -> str:
#     if not text:
#         return ""
#     t = text.replace("\r", "\n")
#     t = t.replace(",", ".")
#     t = re.sub(r"[ \t]+", " ", t)

#     # Corriger quelques erreurs OCR fréquentes
#     t = re.sub(r"\bFactur[eé]\b", "FACTURE", t, flags=re.IGNORECASE)
#     t = re.sub(r"\bTotat\b", "Total", t, flags=re.IGNORECASE)
#     t = re.sub(r"T\.?\s*T\.?\s*C\.?", "TTC", t, flags=re.IGNORECASE)
#     t = re.sub(r"H\.?\s*T\.?", "HT", t, flags=re.IGNORECASE)

#     # Enlever espaces entre chiffres (ex: "4 146.65" -> "4146.65")
#     t = re.sub(r"(?<=\d)\s+(?=\d)", "", t)
#     return t


# def _to_float(s: Optional[str]) -> Optional[float]:
#     if not s:
#         return None
#     s = s.strip()
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
#     m = re.search(r"(\d{2})\s*[/\-]\s*(\d{2})\s*[/\-]\s*(\d{4})", text)
#     if m:
#         dd, mm, yyyy = m.group(1), m.group(2), m.group(3)
#         return f"{dd}/{mm}/{yyyy}"
#     return None


# def _find_num_facture(text: str) -> Optional[str]:
#     # Ex: "FACTURE N° 00422/25"
#     m = re.search(r"FACTURE\s*(?:N|N°|NO|NUM|Nº)\s*[:\-]?\s*([A-Z0-9/\-]{4,20})", text, flags=re.IGNORECASE)
#     if m:
#         return m.group(1).strip()
#     return None


# def _find_totals(text: str) -> tuple[Optional[float], Optional[float], Optional[float]]:
#     # Montant HT / TVA / TTC en bas (souvent "Montant HT: 4146.65  Montant TVA: 829.35  TOTAL A PAYER (TTC): 4976.00")
#     ht = tva = ttc = None

#     m = re.search(r"Montant\s*HT\s*[:\-]?\s*([0-9]+(?:\.[0-9]{2})?)", text, flags=re.IGNORECASE)
#     if m:
#         ht = _to_float(m.group(1))

#     m = re.search(r"Montant\s*TVA\s*[:\-]?\s*([0-9]+(?:\.[0-9]{2})?)", text, flags=re.IGNORECASE)
#     if m:
#         tva = _to_float(m.group(1))

#     m = re.search(r"(?:TOTAL\s*A\s*PAYER\s*\(TTC\)|Total\s*TTC|TTC)\s*[:\-]?\s*([0-9]+(?:\.[0-9]{2})?)", text, flags=re.IGNORECASE)
#     if m:
#         ttc = _to_float(m.group(1))

#     return ht, tva, ttc


# def _find_supplier_footer_line(text: str) -> Optional[str]:
#     # On vise la ligne du bas: "RC: ... TP: ... IF: 25064554 ICE: 002035978000046"
#     lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
#     for ln in reversed(lines):
#         up = ln.upper()
#         if ("RC" in up) and ("TP" in up) and ("IF" in up) and ("ICE" in up):
#             return ln
#     return None


# def _extract_if_ice_from_footer(footer_line: str) -> tuple[Optional[str], Optional[str]]:
#     # IF: 8+ chiffres ; ICE: exactement 15 chiffres
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
#     # Exemple facture: "Sté DROGUERIE EL YOMNE SARL" en haut
#     # On prend la première ligne qui contient "Sté/STE" et "SARL"
#     lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
#     for ln in lines[:10]:
#         if re.search(r"\b(STE|STÉ|Sté)\b", ln) and re.search(r"\bSARL\b", ln, flags=re.IGNORECASE):
#             return re.sub(r"\s+", " ", ln).strip()
#     return None


# def _find_designation_fallback(text: str) -> Optional[str]:
#     # si tu n'as pas de champ clair, au pire on met "Achat fournisseur"
#     return None


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
#     if ht and tva and ht != 0:
#         taux_tva = round((float(tva) / float(ht)) * 100, 2)

#     designation = _find_designation_fallback(t)

#     return {
#         "fournisseur": fournisseur,
#         "date_facture": date_facture,
#         "numero_facture": numero_facture,
#         "designation": designation,

#         "montant_ht": ht,
#         "montant_tva": tva,
#         "montant_ttc": ttc,

#         # champs DED (FOURNISSEUR)
#         "if_frs": if_frs,
#         "ice_frs": ice_frs,
#         "taux_tva": taux_tva,
#     }



















import re
from typing import Optional, Dict, Any, Tuple


# -------------------------
# Normalisation
# -------------------------
def _normalize_text(text: str) -> str:
    if not text:
        return ""
    t = text.replace("\r", "\n")

    # Normaliser séparateur décimal
    t = t.replace(",", ".")

    # Réduire espaces
    t = re.sub(r"[ \t]+", " ", t)

    # Corrections OCR fréquentes
    t = re.sub(r"\bFactur[eé]\b", "FACTURE", t, flags=re.IGNORECASE)
    t = re.sub(r"\bTotat\b", "Total", t, flags=re.IGNORECASE)
    t = re.sub(r"T\.?\s*T\.?\s*C\.?", "TTC", t, flags=re.IGNORECASE)
    t = re.sub(r"H\.?\s*T\.?", "HT", t, flags=re.IGNORECASE)

    # IMPORTANT:
    # Enlever espaces entre chiffres (4 146.65 -> 4146.65 ; 4 976.00 -> 4976.00)
    # (garde les retours ligne inchangés)
    t = re.sub(r"(?<=\d)\s+(?=\d)", "", t)

    return t


# -------------------------
# Helpers conversion
# -------------------------
def _to_float(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None

    # 0/O confusion (ex: 4O50 -> 4050)
    s = re.sub(r"(?<=\d)[oO](?=\d)", "0", s)

    # Conserver chiffres + point uniquement (après normalisation virgule->point)
    s = re.sub(r"[^0-9.]", "", s)

    # Si trop de points: on garde le dernier comme décimal
    if s.count(".") > 1:
        parts = re.split(r"\.+", s)
        s = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return float(s)
    except Exception:
        return None


# -------------------------
# Extraction champs
# -------------------------
def _find_date_ddmmyyyy(text: str) -> Optional[str]:
    m = re.search(r"(\d{2})\s*[/\-]\s*(\d{2})\s*[/\-]\s*(\d{4})", text)
    if m:
        dd, mm, yyyy = m.group(1), m.group(2), m.group(3)
        return f"{dd}/{mm}/{yyyy}"
    return None


def _find_num_facture(text: str) -> Optional[str]:
    # Supporte plus de variantes: FACTURE N°, REF, N°
    m = re.search(
        r"(FACTURE\s*(?:N|N°|NO|NUM|Nº)|REF(?:ERENCE)?|N°)\s*[:\-]?\s*([A-Z0-9/\-]{3,30})",
        text,
        flags=re.IGNORECASE,
    )
    if m:
        return m.group(2).strip()
    return None


def _find_totals(text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Cherche HT / TVA / TTC global.
    Robuste aux variantes OCR, sauts de lignes, et formats comme 4 976.00.
    """
    ht = tva = ttc = None

    # Montant large (après normalisation, ça peut être 4976.00 ou 4976)
    AMOUNT = r"([0-9][0-9\.\s]{0,20})"

    # HT (Montant HT ou juste HT)
    m = re.search(r"(?:MONTANT\s*)?HT\s*[:\-]?\s*" + AMOUNT, text, flags=re.IGNORECASE)
    if m:
        ht = _to_float(m.group(1))

    # TVA
    m = re.search(r"(?:MONTANT\s*)?TVA\s*[:\-]?\s*" + AMOUNT, text, flags=re.IGNORECASE)
    if m:
        tva = _to_float(m.group(1))

    # TTC global (priorité)
    # On vise les libellés du type: TOTAL A PAYER (TTC), TOTAL TTC, NET A PAYER, A PAYER
    m = re.search(
        r"(TOTAL\s*A\s*PAYER\s*\(?\s*TTC\s*\)?|TOTAL\s*TTC|NET\s*A\s*PAYER|A\s*PAYER)\s*[:\-]?\s*"
        + AMOUNT,
        text,
        flags=re.IGNORECASE,
    )
    if m:
        # groupe 2 car groupe 1 = libellé
        ttc = _to_float(m.group(2))

    # Fallback : TTC = HT + TVA si TTC manquant
    if ttc is None and ht is not None and tva is not None:
        ttc = round(ht + tva, 2)

    return ht, tva, ttc


def _find_supplier_footer_line(text: str) -> Optional[str]:
    """
    Vise une ligne footer du style:
    "RC: ... TP: ... IF: 25064554 ICE: 002035978000046"
    """
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    for ln in reversed(lines):
        up = ln.upper()
        if ("IF" in up) and ("ICE" in up):
            return ln
    return None


def _extract_if_ice_from_footer(footer_line: str) -> Tuple[Optional[str], Optional[str]]:
    # IF: souvent 6-12 chiffres ; ICE: 15 chiffres
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
    """
    Exemple: "Sté DROGUERIE EL YOMNE SARL"
    On prend une ligne haute contenant STE/STÉ et SARL (ou SA).
    """
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    for ln in lines[:15]:
        if re.search(r"\b(STE|STÉ|STO|Sté)\b", ln, flags=re.IGNORECASE) and re.search(r"\b(SARL|SA)\b", ln, flags=re.IGNORECASE):
            return re.sub(r"\s+", " ", ln).strip()
    return None


def _find_designation_fallback(text: str, fournisseur: Optional[str]) -> str:
    """
    Beaucoup de factures n'ont pas une "désignation globale".
    On met un libellé utile (non-null) pour tes écritures / DED.
    """
    if fournisseur:
        return f"Achat fournisseur - {fournisseur}"
    return "Achat fournisseur"


# -------------------------
# Entrée principale
# -------------------------
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

    # Taux TVA calculé si possible
    taux_tva = None
    if ht is not None and tva is not None and ht != 0:
        taux_tva = round((float(tva) / float(ht)) * 100, 2)

    # Désignation non-null (fallback)
    designation = _find_designation_fallback(t, fournisseur)

    return {
        "fournisseur": fournisseur,
        "date_facture": date_facture,
        "numero_facture": numero_facture,
        "designation": designation,

        "montant_ht": ht,
        "montant_tva": tva,
        "montant_ttc": ttc,

        # champs DED (FOURNISSEUR)
        "if_frs": if_frs,
        "ice_frs": ice_frs,
        "taux_tva": taux_tva,
    }
