import re
from datetime import datetime, date
from typing import Optional


def parse_date_fr(s: str | None) -> Optional[date]:
    """
    Accepte: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
    """
    if not s:
        return None
    s = s.strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def parse_amount(s) -> Optional[float]:
    """
    Accepte: "10 000,00" -> 10000.00
    """
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)

    s = str(s)
    # garder chiffres/virgule/point/espace
    s = re.sub(r"[^\d,.\s]", "", s)
    # retirer espaces dans nombres
    s = re.sub(r"(?<=\d)\s+(?=\d)", "", s)
    # virgule -> point
    s = s.replace(",", ".")
    # si plusieurs points, garder le dernier comme décimal
    if s.count(".") > 1:
        parts = s.split(".")
        s = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(s)
    except ValueError:
        return None
