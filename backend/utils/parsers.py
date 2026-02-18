"""
utils/parsers.py — Utilitaires de parsing pour les données de factures
"""
import re
from datetime import date
from typing import Optional


def parse_date_fr(value: Optional[str]) -> Optional[date]:
    """
    Parse une date au format DD/MM/YYYY ou YYYY-MM-DD.
    Retourne None si la valeur est invalide ou absente.
    """
    if not value:
        return None

    value = str(value).strip()

    # Format DD/MM/YYYY
    m = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', value)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None

    # Format YYYY-MM-DD
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', value)
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
