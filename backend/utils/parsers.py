"""
utils/parsers.py — Utilitaires de parsing pour les données de factures
"""
import re
from datetime import date
from typing import Optional


def parse_date_fr(value: Optional[str]) -> Optional[date]:
    """
    Parse une date au format DD/MM/YYYY, DD.MM.YYYY, DD-MM-YYYY ou YYYY-MM-DD.
    Gère aussi les années sur 2 chiffres.
    """
    if not value:
        return None

    # Nettoyage
    s = str(value).strip().replace(".", "/").replace("-", "/").replace(" ", "/")
    
    # Format DD/MM/YYYY
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{2,4})$', s)
    if m:
        try:
            day = int(m.group(1))
            month = int(m.group(2))
            year = int(m.group(3))
            if year < 100:
                year += 2000
            return date(year, month, day)
        except ValueError:
            return None

    # Format YYYY/MM/DD
    m = re.match(r'^(\d{4})/(\d{2})/(\d{2})$', s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None

    return None


def parse_amount(value) -> Optional[float]:
    """
    Parse un montant depuis une chaîne ou un nombre.
    Gère les formats: "10 000,00", "10.000,00", "10000.00"
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    # Supprimer les espaces et remplacer la virgule décimale
    s = re.sub(r'\s', '', s)
    s = s.replace(',', '.')
    # Si plusieurs points, garder seulement le dernier comme décimal
    parts = s.split('.')
    if len(parts) > 2:
        s = ''.join(parts[:-1]) + '.' + parts[-1]
    try:
        return float(s)
    except ValueError:
        return None
