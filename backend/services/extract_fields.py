import re

def parse_facture_text(text: str) -> dict:
    # Nettoyage léger
    t = text.replace("\n", " ")

    # Date facture (formats possibles)
    date_match = re.search(r"(\d{2}/\d{2}/\d{4})", t)
    date_facture = date_match.group(1) if date_match else None

    # Total HT / TVA / TTC
    total_ht = re.search(r"Total\s*HT\.?\s*:\s*([\d\.,]+)", t, re.IGNORECASE)
    tva = re.search(r"TVA\s*\d+[\.,]?\d*\s*%?\s*([\d\.,]+)", t, re.IGNORECASE)
    total_ttc = re.search(r"Total\s*T\.?T\.?C\s*:\s*([\d\.,]+)", t, re.IGNORECASE)

    def to_float(x):
        if not x: 
            return None
        return float(x.replace(" ", "").replace(",", "."))

    # Fournisseur : souvent la 1ère ligne (approx)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    fournisseur = lines[0] if lines else None

    return {
        "fournisseur": fournisseur,
        "date_facture": date_facture,
        "montant_ht": to_float(total_ht.group(1)) if total_ht else None,
        "montant_tva": to_float(tva.group(1)) if tva else None,
        "montant_ttc": to_float(total_ttc.group(1)) if total_ttc else None,
        "raw_text": text
    }
