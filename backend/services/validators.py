"""
services/validators.py — Validation et fusion des champs extraits
"""
from typing import Any, Dict, List


def validate_or_fix(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide et corrige les données extraites d'une facture.
    Retourne le dictionnaire nettoyé.
    """
    cleaned = dict(data)

    # Normaliser l'ICE (garder seulement les chiffres)
    for key in ("supplier_ice", "ice_frs", "client_ice"):
        v = cleaned.get(key)
        if v:
            digits = ''.join(c for c in str(v) if c.isdigit())
            cleaned[key] = digits if len(digits) == 15 else v

    # Normaliser les montants
    for key in ("montant_ht", "montant_tva", "montant_ttc", "taux_tva"):
        v = cleaned.get(key)
        if v is not None:
            try:
                cleaned[key] = float(v)
            except (ValueError, TypeError):
                cleaned[key] = None

    return cleaned


def merge_fields(primary: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne deux dictionnaires: les valeurs non-None de `primary` ont priorité.
    """
    result = dict(fallback)
    for k, v in primary.items():
        if v is not None:
            result[k] = v
    return result
