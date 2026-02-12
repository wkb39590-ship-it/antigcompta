import re
from math import isfinite
from typing import Any, Dict, List, Tuple, Optional


def _digits_only(s: str) -> str:
    return re.sub(r"\D", "", s)


def is_ice_ok(ice: Optional[str]) -> bool:
    if not ice:
        return False
    return len(_digits_only(ice)) == 15


def amounts_consistent(ht: Optional[float], tva: Optional[float], ttc: Optional[float]) -> bool:
    # Si incomplet, on ne bloque pas
    if ht is None or tva is None or ttc is None:
        return True
    if not all(isfinite(x) for x in [ht, tva, ttc]):
        return False
    # tolérance: max(1.0, 2% TTC)
    return abs(ttc - (ht + tva)) <= max(1.0, 0.02 * abs(ttc))


def normalize_fields(d: Dict[str, Any]) -> Dict[str, Any]:
    # Nettoyage ICE
    if d.get("ice_frs"):
        d["ice_frs"] = _digits_only(str(d["ice_frs"]))
    # Num facture trim
    if d.get("numero_facture"):
        d["numero_facture"] = str(d["numero_facture"]).strip()
    # Fournisseur trim
    if d.get("fournisseur"):
        d["fournisseur"] = str(d["fournisseur"]).strip()
    return d


def validate_or_fix(d: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Retourne (fields_corrigés, issues)
    """
    issues: List[str] = []
    d = normalize_fields(d)

    # ICE strict
    if d.get("ice_frs") and not is_ice_ok(d["ice_frs"]):
        issues.append("ICE invalid -> null")
        d["ice_frs"] = None

    # Cohérence montants
    ht = d.get("montant_ht")
    tva = d.get("montant_tva")
    ttc = d.get("montant_ttc")
    if not amounts_consistent(ht, tva, ttc):
        issues.append("Amounts inconsistent (TTC != HT + TVA) -> nullify HT/TVA (keep TTC)")
        d["montant_ht"] = None
        d["montant_tva"] = None

    # Taux TVA: bornes raisonnables
    if d.get("taux_tva") is not None:
        try:
            taux = float(d["taux_tva"])
            if taux < 0 or taux > 30:
                issues.append("taux_tva out of range -> null")
                d["taux_tva"] = None
        except Exception:
            issues.append("taux_tva not numeric -> null")
            d["taux_tva"] = None

    return d, issues


def merge_fields(primary: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Garde primary si non-null, sinon prend fallback.
    """
    out = dict(primary)
    for k, v in fallback.items():
        if out.get(k) is None and v is not None:
            out[k] = v
    return out
