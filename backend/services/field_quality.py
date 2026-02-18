



# import re
# from math import isfinite
# from typing import Any, Dict, List, Tuple, Optional


# def _digits_only(s: str) -> str:
#     return re.sub(r"\D", "", s)


# def is_ice_ok(ice: Optional[str]) -> bool:
#     if not ice:
#         return False
#     return len(_digits_only(ice)) == 15


# def amounts_consistent(ht: Optional[float], tva: Optional[float], ttc: Optional[float]) -> bool:
#     if ht is None or tva is None or ttc is None:
#         return True
#     try:
#         if not all(isfinite(float(x)) for x in [ht, tva, ttc]):
#             return False
#     except Exception:
#         return False

#     ttc_abs = abs(float(ttc))
#     return abs(float(ttc) - (float(ht) + float(tva))) <= max(1.0, 0.02 * ttc_abs)


# def normalize_fields(d: Dict[str, Any]) -> Dict[str, Any]:
#     if d.get("ice_frs"):
#         d["ice_frs"] = _digits_only(str(d["ice_frs"]))
#     if d.get("numero_facture"):
#         d["numero_facture"] = str(d["numero_facture"]).strip()
#     if d.get("fournisseur"):
#         d["fournisseur"] = str(d["fournisseur"]).strip()
#     return d


# def validate_or_fix(d: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
#     issues: List[str] = []
#     d = normalize_fields(d)

#     if d.get("ice_frs") and not is_ice_ok(d["ice_frs"]):
#         issues.append("ICE invalide -> supprimé")
#         d["ice_frs"] = None

#     ht = d.get("montant_ht")
#     tva = d.get("montant_tva")
#     ttc = d.get("montant_ttc")
#     if not amounts_consistent(ht, tva, ttc):
#         issues.append("Montants incohérents (TTC != HT + TVA) -> HT/TVA annulés")
#         d["montant_ht"] = None
#         d["montant_tva"] = None

#     if d.get("taux_tva") is not None:
#         try:
#             taux = float(d["taux_tva"])
#             if taux < 0 or taux > 30:
#                 issues.append("taux_tva hors limites -> null")
#                 d["taux_tva"] = None
#         except Exception:
#             issues.append("taux_tva invalide -> null")
#             d["taux_tva"] = None

#     return d, issues











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
    if ht is None or tva is None or ttc is None:
        return True
    try:
        if not all(isfinite(float(x)) for x in [ht, tva, ttc]):
            return False
    except Exception:
        return False

    ttc_abs = abs(float(ttc))
    return abs(float(ttc) - (float(ht) + float(tva))) <= max(1.0, 0.02 * ttc_abs)


def normalize_fields(d: Dict[str, Any]) -> Dict[str, Any]:
    if d.get("ice_frs"):
        d["ice_frs"] = _digits_only(str(d["ice_frs"]))
    if d.get("numero_facture"):
        d["numero_facture"] = str(d["numero_facture"]).strip()
    if d.get("fournisseur"):
        d["fournisseur"] = str(d["fournisseur"]).strip()
    return d


def validate_or_fix(d: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    issues: List[str] = []
    d = normalize_fields(d)

    if d.get("ice_frs") and not is_ice_ok(d["ice_frs"]):
        issues.append("ICE invalide -> supprimé")
        d["ice_frs"] = None

    ht = d.get("montant_ht")
    tva = d.get("montant_tva")
    ttc = d.get("montant_ttc")
    if not amounts_consistent(ht, tva, ttc):
        issues.append("Montants incohérents (TTC != HT + TVA) -> HT/TVA annulés")
        d["montant_ht"] = None
        d["montant_tva"] = None

    if d.get("taux_tva") is not None:
        try:
            taux = float(d["taux_tva"])
            if taux < 0 or taux > 30:
                issues.append("taux_tva hors limites -> null")
                d["taux_tva"] = None
        except Exception:
            issues.append("taux_tva invalide -> null")
            d["taux_tva"] = None

    return d, issues
