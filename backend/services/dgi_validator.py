"""
dgi_validator.py — Contrôles DGI automatiques sur les factures marocaines
"""
import re
from typing import List, Dict, Any


def validate_dgi(facture_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Effectue les contrôles DGI sur les données d'une facture.
    Retourne une liste de flags (anomalies).

    Format d'un flag:
    {
        "code": "ICE_MISSING",
        "message": "ICE fournisseur absent",
        "severity": "ERROR" | "WARNING",
        "field": "supplier_ice"
    }
    """
    flags = []

    # ── ICE fournisseur ──────────────────────────────────────────
    ice = facture_data.get("supplier_ice") or facture_data.get("ice_frs")
    if not ice:
        flags.append({
            "code": "ICE_MISSING",
            "message": "ICE fournisseur absent (obligatoire DGI)",
            "severity": "ERROR",
            "field": "supplier_ice",
        })
    else:
        ice_clean = re.sub(r"[^0-9]", "", str(ice))
        if len(ice_clean) != 15:
            flags.append({
                "code": "ICE_INVALID",
                "message": f"ICE fournisseur invalide: doit être 15 chiffres (reçu: {len(ice_clean)})",
                "severity": "ERROR",
                "field": "supplier_ice",
            })

    # ── IF fournisseur ───────────────────────────────────────────
    if_val = facture_data.get("supplier_if") or facture_data.get("if_frs")
    if not if_val:
        flags.append({
            "code": "IF_MISSING",
            "message": "Identifiant Fiscal (IF) fournisseur absent",
            "severity": "WARNING",
            "field": "supplier_if",
        })

    # ── Numéro de facture ────────────────────────────────────────
    num = facture_data.get("numero_facture")
    if not num:
        flags.append({
            "code": "INVOICE_NUMBER_MISSING",
            "message": "Numéro de facture absent (obligatoire DGI)",
            "severity": "WARNING",
            "field": "numero_facture",
        })

    # ── Cohérence HT + TVA = TTC (En-tête) ───────────────────────
    ht = _to_float(facture_data.get("montant_ht"))
    tva = _to_float(facture_data.get("montant_tva"))
    ttc = _to_float(facture_data.get("montant_ttc"))

    if ht is not None and tva is not None and ttc is not None:
        computed = round(ht + tva, 2)
        if abs(computed - ttc) > 0.01:
            flags.append({
                "code": "AMOUNT_INCOHERENT",
                "message": f"Incohérence: HT({ht}) + TVA({tva}) = {computed} ≠ TTC({ttc})",
                "severity": "ERROR",
                "field": "montant_ttc",
            })

    # ── Cohérence En-tête vs Somme des lignes ───────────────────
    lines = facture_data.get("lines") or []
    if lines:
        sum_ht = sum(_to_float(l.get("line_amount_ht")) or 0 for l in lines)
        sum_tva = sum(_to_float(l.get("tva_amount")) or 0 for l in lines)
        sum_ttc = sum(_to_float(l.get("line_amount_ttc")) or 0 for l in lines)
        
        if ttc is not None and abs(round(sum_ttc, 2) - ttc) > 0.05:
            flags.append({
                "code": "LINES_SUM_MISMATCH",
                "message": f"Divergence: Somme des lignes({round(sum_ttc, 2)}) ≠ TTC En-tête({ttc})",
                "severity": "ERROR",
                "field": "montant_ttc",
            })
        elif tva is not None and abs(round(sum_tva, 2) - tva) > 0.05:
            flags.append({
                "code": "TVA_LINES_MISMATCH",
                "message": f"Divergence: Somme TVA lignes({round(sum_tva, 2)}) ≠ TVA En-tête({tva})",
                "severity": "WARNING",
                "field": "montant_tva",
            })

    # ── Taux TVA valide ──────────────────────────────────────────
    taux = _to_float(facture_data.get("taux_tva"))
    if taux is not None and taux not in {0, 7, 10, 14, 20}:
        flags.append({
            "code": "TVA_RATE_INVALID",
            "message": f"Taux TVA {taux}% non reconnu (valides: 0, 7, 10, 14, 20)",
            "severity": "ERROR",
            "field": "taux_tva",
        })

    # ── Date facture ─────────────────────────────────────────────
    date = facture_data.get("date_facture")
    if not date:
        flags.append({
            "code": "DATE_MISSING",
            "message": "Date de facture absente",
            "severity": "WARNING",
            "field": "date_facture",
        })

    return flags


def _to_float(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None
