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
    lines = text.splitlines()
    # Recherche spécifique format tableau (Arrahma)
    for i, line in enumerate(lines):
        if re.search(r"Facture\s+Date", line, re.IGNORECASE) and i + 1 < len(lines):
            next_line = lines[i+1].strip().split()
            if len(next_line) >= 2:
                date_val = next_line[1]
                if re.match(r"\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}", date_val):
                    return date_val.replace("-", "/").replace(".", "/")

    # Recherche spécifique "Date" suivi d'une date
    match = re.search(r"Date\s*[\n\r\t]*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})", text, re.IGNORECASE)
    if match:
        return match.group(1).replace("-", "/").replace(".", "/")

    # Recherche standard
    match = re.search(r"\b(\d{1,2})\s*[/\-\.]\s*(\d{1,2})\s*[/\-\.]\s*(\d{2,4})\b", text)
    if not match:
        return None

    day, month, year = match.groups()
    if len(year) == 2: year = f"20{year}"
    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"


def _find_num_facture(text: str) -> Optional[str]:
    lines = text.splitlines()
    
    # Recherche spécifique format tableau (Arrahma) : Facture Date ...
    for i, line in enumerate(lines[:30]):
        if re.search(r"Facture\s+Date", line, re.IGNORECASE) and i + 1 < len(lines):
            next_line = lines[i+1].strip().split()
            if len(next_line) >= 1:
                val = next_line[0]
                if any(char.isdigit() for char in val) and len(val) >= 3:
                    return val

    # Patterns plus larges
    patterns = [
        r"Facture\s*[\n\r\t]*([A-Z0-9/\-\.]{3,20})", 
        r"N[°º.o]?\s*[:\-]?\s*([A-Z0-9/\-\.]{3,20})",
    ]
    
    for pattern in patterns:
        for line_idx, line in enumerate(lines[:30]):
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if any(char.isdigit() for char in val) and len(val) >= 3:
                    return val
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
    # On cherche d'abord l'ICE du FOURNISSEUR (Arrahma)
    # Si on est dans une VENTE, Arrahma est le fournisseur.
    
    ice_matches = re.findall(r"ICE\s*[:\-]?\s*(\d{15})", text, re.IGNORECASE)
    if_matches = re.findall(r"IF\s*[:\-]?\s*(\d{4,12})", text, re.IGNORECASE)
    
    # Sur votre facture, Arrahma (002012861000010) est en haut.
    # Shemadri (003272689000032) est plus bas.
    
    ice_frs = ice_matches[0] if len(ice_matches) > 0 else None
    if_frs = if_matches[0] if len(if_matches) > 0 else None
    
    return if_frs, ice_frs


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
    
    # Détection du type (AVOIR)
    invoice_type = "ACHAT"
    if re.search(r"\b(AVOIR|NOTE\s*DE\s*CR[EÉ]DIT|RETOUR)\b", normalized, re.IGNORECASE):
        invoice_type = "AVOIR"

    date_facture = _find_date_ddmmyyyy(normalized)
    numero_facture = _find_num_facture(normalized)
    montant_ht, montant_tva, montant_ttc = _find_totals(normalized)
    
    # ICE/IF
    if_frs, ice_frs = _find_ice_if(normalized)
    
    # Recherche d'un deuxième ICE (Client)
    ice_matches = re.findall(r"ICE\s*[:\-]?\s*(\d{15})", normalized, re.IGNORECASE)
    ice_client = None
    if len(ice_matches) >= 2:
        # Si le premier est le fournisseur, le deuxième est probablement le client
        ice_client = ice_matches[1]
    elif len(ice_matches) == 1 and fournisseur is None:
        # Si on n'a qu'un ICE et pas de fournisseur, c'est peut-être celui du client
        pass

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
        "client_ice": ice_client,
        "taux_tva": taux_tva,
        "invoice_type": invoice_type,
    }
