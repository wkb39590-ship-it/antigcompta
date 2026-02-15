# services/operation_detector.py
import re
from typing import Optional, Tuple


def _norm(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("s.a.r.l", "sarl").replace("s.a.", "sa").replace("&", " ")
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    return s.strip()


def _same_id(a: Optional[str], b: Optional[str]) -> bool:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a or not b:
        return False
    return a == b


def detect_operation_type(
    societe_ice: Optional[str],
    societe_if: Optional[str],
    societe_nom: Optional[str],
    tiers_ice: Optional[str],
    tiers_if: Optional[str],
    tiers_nom: Optional[str],
) -> Tuple[str, float]:
    """
    On suppose que les champs extraits "fournisseur/ice_frs/if_frs" correspondent au vendeur (émetteur).
    - Si le vendeur == société => c'est une VENTE (facture émise par la société)
    - Sinon => ACHAT (facture reçue par la société)
    """
    # Match fort par ICE/IF
    if _same_id(tiers_ice, societe_ice) or _same_id(tiers_if, societe_if):
        return "vente", 0.95

    # Match "soft" par nom
    n_soc = _norm(societe_nom)
    n_tiers = _norm(tiers_nom)

    if n_soc and n_tiers:
        # si le nom société est contenu dans le nom tiers => vente probable
        if n_soc in n_tiers or n_tiers in n_soc:
            return "vente", 0.70

    # Default: achat (la plupart des factures qu'on saisit sont reçues)
    return "achat", 0.40
