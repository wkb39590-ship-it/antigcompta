import re
from typing import Any, Dict, Optional, Tuple

AMOUNT_RE = re.compile(r"(?<!\d)(\d{1,3}(?:[ .]\d{3})*(?:[.,]\d{2})|\d+(?:[.,]\d{2})|\d+)(?!\d)")


def extract_fields_from_ocr(ocr: Any) -> Dict[str, Any]:
    """Accept an OCRResult or raw OCR text."""
    text = ocr.text if hasattr(ocr, "text") else str(ocr)
    return parse_facture_text(text)


def _normalize_text(text: str) -> str:
    if not text:
        return ""

    normalized = text.replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\bFactur[eé]\b", "FACTURE", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bTotat\b", "Total", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"T\.?\s*T\.?\s*C\.?", "TTC", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"H\.?\s*T\.?", "HT", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"(?<=\d)\s+(?=\d)", "", normalized)
    return normalized


def _to_float(value: Optional[str]) -> Optional[float]:
    if not value:
        return None

    cleaned = str(value).strip()
    if not cleaned:
        return None

    cleaned = re.sub(r"(?<=\d)[oO](?=\d)", "0", cleaned)
    # Gérer les formats 4.300,00 ou 4 300,00
    cleaned = cleaned.replace(" ", "")
    # Si on a un point de milliers ET une virgule de décimales (ex: 4.300,00)
    if "." in cleaned and "," in cleaned:
        cleaned = cleaned.replace(".", "")
    cleaned = cleaned.replace(",", ".")
    cleaned = re.sub(r"[^0-9.]", "", cleaned)

    if cleaned.count(".") > 1:
        last_dot = cleaned.rfind(".")
        cleaned = cleaned[:last_dot].replace(".", "") + cleaned[last_dot:]

    try:
        return float(cleaned)
    except Exception:
        return None


def _find_date_ddmmyyyy(text: str) -> Optional[str]:
    injected = re.search(r"DATE_FACTURE:\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})", text, flags=re.IGNORECASE)
    if injected:
        return injected.group(1).replace("-", "/").replace(".", "/")

    match = re.search(r"\b(\d{1,2})\s*[/\-\.]\s*(\d{1,2})\s*[/\-\.]\s*(\d{2,4})\b", text)
    if not match:
        return None

    day, month, year = match.groups()
    if len(year) == 2:
        year = f"20{year}"
    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"


def _find_num_facture(text: str) -> Optional[str]:
    patterns = [
        r"\bFACTURE\s*(?:N|N°|NO|NUM(?:ERO)?|Nº)\s*[:\-]?\s*([A-Z0-9][A-Z0-9/\-\.]{2,40})\b",
        r"\b(?:REF|REFERENCE|R[ÉE]F[ÉE]RENCE)\s*[:\-]?\s*([A-Z0-9][A-Z0-9/\-\.]{2,40})\b",
        r"\b(?:N°|NO|Nº)\s*[:\-]?\s*([A-Z0-9][A-Z0-9/\-\.]{2,40})\b",
    ]
    bad_values = {"CLIENT", "CLT", "ICE", "IF", "RC", "PATENTE", "TOTAL", "TTC", "HT"}
    bad_context = re.compile(r"\b(PATENTE|RC|R\.C|CNSS|ICE|IF|I\.F|TVA|CLIENT)\b", re.IGNORECASE)

    for line in text.splitlines():
        if bad_context.search(line):
            continue
        for pattern in patterns:
            match = re.search(pattern, line, flags=re.IGNORECASE)
            if not match:
                continue
            value = match.group(1).strip(" -:./")
            if len(value) >= 3 and value.upper() not in bad_values:
                return value
    return None


def _extract_amount_near_label(text: str, label_regex: str) -> Optional[float]:
    match = re.search(label_regex + r".{0,80}?(" + AMOUNT_RE.pattern + r")", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return _to_float(match.group(1))


def _extract_tva_rate(text: str) -> Optional[float]:
    for line in text.splitlines():
        if not re.search(r"\bTVA\b", line, re.IGNORECASE):
            continue
        match = re.search(r"(\d{1,2}(?:[.,]\d{1,2})?)\s*%", line)
        if not match:
            continue
        rate = _to_float(match.group(1))
        if rate is not None and 0 <= rate <= 30:
            return rate
    return None


def _find_totals(text: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    montant_ht = _extract_amount_near_label(text, r"\b(TOTAL\s*HT|MONTANT\s*HT|HT)\b")
    montant_ttc = _extract_amount_near_label(
        text,
        r"\b(TOTAL\s*TTC|NET\s*A\s*PAYER|TOTAL\s*A\s*PAYER|MONTANT\s*TTC|A\s*PAYER)\b",
    )
    montant_tva = None

    for line in text.splitlines():
        if not re.search(r"\bTVA\b", line, re.IGNORECASE):
            continue
        values = [_to_float(raw) for raw in AMOUNT_RE.findall(line)]
        values = [value for value in values if value is not None]
        if not values:
            continue
        rate = _extract_tva_rate(line)
        monetary_values = [value for value in values if rate is None or abs(value - rate) > 0.01]
        if monetary_values:
            montant_tva = max(monetary_values)
            break

    if montant_tva is None and montant_ht is not None and montant_ttc is not None and montant_ttc >= montant_ht:
        montant_tva = round(montant_ttc - montant_ht, 2)
    if montant_ttc is None and montant_ht is not None and montant_tva is not None:
        montant_ttc = round(montant_ht + montant_tva, 2)

    return montant_ht, montant_tva, montant_ttc


def _find_supplier_footer_line(text: str) -> Optional[str]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    candidates = []

    for idx, line in enumerate(lines):
        upper = line.upper()
        if "ICE" in upper or re.search(r"\bI\.?\s*F\b", upper):
            candidates.append(" ".join(lines[idx:min(idx + 3, len(lines))]))

    for candidate in reversed(candidates):
        if "ICE" in candidate.upper() or re.search(r"\bI\.?\s*F\b", candidate, re.IGNORECASE):
            return candidate

    return None


def _find_ice_if(text: str) -> Tuple[Optional[str], Optional[str]]:
    search_space = _find_supplier_footer_line(text) or text

    supplier_if_match = re.search(r"\bI\.?\s*F\b\s*[:\-]?\s*([0-9]{4,12})\b", search_space, flags=re.IGNORECASE)
    supplier_ice_match = re.search(r"\bICE\b\s*[:\-]?\s*([0-9]{15})\b", search_space, flags=re.IGNORECASE)

    supplier_if = supplier_if_match.group(1) if supplier_if_match else None
    supplier_ice = supplier_ice_match.group(1) if supplier_ice_match else None

    if supplier_ice is None:
        all_ice = re.findall(r"\b(\d{15})\b", text)
        if all_ice:
            supplier_ice = all_ice[0]
 
    return supplier_if, supplier_ice


def _find_supplier_name(text: str) -> Optional[str]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:20]:
        upper = line.upper()
        if len(line) < 4 or len(line) > 80:
            continue
        if re.search(r"\b(FACTURE|DATE|CLIENT|DESTINATAIRE|TOTAL|TVA|TTC|HT|ICE|IF|RC)\b", upper):
            continue
        if re.search(r"\b(STE|STE\.|STÉ|ETS|ETS\.|SARL|SARLAU|SA|SAS|EURL|SNC)\b", upper):
            return re.sub(r"\s+", " ", line).strip()
        if sum(char.isalpha() for char in line) >= 8 and line == line.upper():
            return re.sub(r"\s+", " ", line).strip()
    return None


def _designation_fallback(fournisseur: Optional[str]) -> str:
    return f"Achat fournisseur - {fournisseur}" if fournisseur else "Achat fournisseur"


def parse_facture_text(text: str) -> Dict[str, Any]:
    normalized = _normalize_text(text)

    fournisseur = _find_supplier_name(normalized)
    date_facture = _find_date_ddmmyyyy(normalized)
    numero_facture = _find_num_facture(normalized)
    montant_ht, montant_tva, montant_ttc = _find_totals(normalized)
    if_frs, ice_frs = _find_ice_if(normalized)

    taux_tva = _extract_tva_rate(normalized)
    if taux_tva is None and montant_ht is not None and montant_tva is not None and montant_ht != 0:
        taux_tva = round((float(montant_tva) / float(montant_ht)) * 100, 2)

    return {
        "fournisseur": fournisseur,
        "date_facture": date_facture,
        "numero_facture": numero_facture,
        "designation": _designation_fallback(fournisseur),
        "montant_ht": montant_ht,
        "montant_tva": montant_tva,
        "montant_ttc": montant_ttc,
        "if_frs": if_frs,
        "ice_frs": ice_frs,
        "taux_tva": taux_tva,
    }
