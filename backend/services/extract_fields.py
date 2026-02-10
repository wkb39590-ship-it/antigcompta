


# import re

# def _to_float(s: str):
#     if s is None:
#         return None
#     s = s.replace(" ", "")
#     s = s.replace(",", ".")
#     try:
#         return float(s)
#     except:
#         return None

# def parse_facture_text(text: str):
#     data = {
#         "fournisseur": None,
#         "date_facture": None,
#         "montant_ht": None,
#         "montant_tva": None,
#         "montant_ttc": None,
#     }

#     # Fournisseur (ex: première ligne "STE ...")
#     m = re.search(r"^(STE\s+[^\n]+)", text, flags=re.MULTILINE | re.IGNORECASE)
#     if m:
#         data["fournisseur"] = m.group(1).strip()

#     # Date (dd/mm/yyyy)
#     m = re.search(r"(\d{2}/\d{2}/\d{4})", text)
#     if m:
#         data["date_facture"] = m.group(1)

#     # Total HT (gère: Total H.T. : 4140.00)
#     m = re.search(r"Total\s*H\.?\s*T\.?\s*\.?\s*[:\-]?\s*([0-9]+[.,][0-9]+)", text, flags=re.IGNORECASE)
#     if m:
#         data["montant_ht"] = _to_float(m.group(1))

#     # TVA (gère: "TVA 20.00% 828.00" ou "TVA ... : 828.00")
#     m = re.search(r"TVA\s*(?:\d+[.,]?\d*\s*%?)?\s*[:\-]?\s*([0-9]+[.,][0-9]+)", text, flags=re.IGNORECASE)
#     if m:
#         data["montant_tva"] = _to_float(m.group(1))

#     # Total TTC (gère: Total T.T.C : 4968.00)
#     m = re.search(r"Total\s*T\.?\s*T\.?\s*C\.?\s*[:\-]?\s*([0-9]+[.,][0-9]+)", text, flags=re.IGNORECASE)
#     if m:
#         data["montant_ttc"] = _to_float(m.group(1))

#     return data







# import re
# from typing import Optional, Dict, Any


# def _to_float(s: Optional[str]) -> Optional[float]:
#     if not s:
#         return None
#     s = s.replace(" ", "").replace("\u00A0", "")  # espaces + espaces insécables
#     s = s.replace(",", ".")
#     # garder uniquement chiffres et point
#     s = re.sub(r"[^0-9.]", "", s)
#     try:
#         return float(s)
#     except Exception:
#         return None


# def _norm(text: str) -> str:
#     """Normalisation légère pour aider les regex (OCR image = caractères bizarres)."""
#     if not text:
#         return ""
#     t = text
#     t = t.replace("\u00A0", " ")
#     # OCR confond souvent O/0, I/1, l/1 dans des zones numériques
#     # (on évite de tout casser : on ne remplace que dans un contexte 'date' plus bas)
#     return t


# def parse_facture_text(text: str) -> Dict[str, Any]:
#     t = _norm(text)

#     data: Dict[str, Any] = {
#         "fournisseur": None,
#         "date_facture": None,
#         "montant_ht": None,
#         "montant_tva": None,
#         "montant_ttc": None,
#     }

#     # -------------------------
#     # Fournisseur
#     # -------------------------
#     # Cas 1: ligne qui commence par "STE ..."
#     m = re.search(r"^\s*(STE\s+[^\n\r]+)", t, flags=re.MULTILINE | re.IGNORECASE)
#     if m:
#         data["fournisseur"] = m.group(1).strip()
#     else:
#         # Cas 2: OCR colle les mots : "STEComptoireArrahma..."
#         m = re.search(r"\bSTE\s*([A-Z0-9].{2,50})", t, flags=re.IGNORECASE)
#         if m:
#             data["fournisseur"] = ("STE " + m.group(1)).strip()

#     # -------------------------
#     # Date facture
#     # -------------------------
#     # Les images OCR ratent souvent "16/12/2025" en "16/12/202S" ou "16/1Z/2025"
#     # On accepte donc:
#     # - jour/mois : 2 chiffres (avec confusions I/l -> 1, O -> 0, Z -> 2, S -> 5)
#     # - année : 4 "chiffres" tolérants (S->5, O->0, I->1, Z->2)
#     date_pat = r"(?P<d>\d{1,2})\s*[/\-\.]\s*(?P<m>\d{1,2})\s*[/\-\.]\s*(?P<y>[0-9SZOIl]{4})"
#     dm = re.search(date_pat, t, flags=re.IGNORECASE)
#     if dm:
#         d = dm.group("d")
#         mth = dm.group("m")
#         y = dm.group("y")

#         # corriger les confusions OCR dans l'année
#         y = (
#             y.replace("S", "5")
#             .replace("Z", "2")
#             .replace("O", "0")
#             .replace("I", "1")
#             .replace("l", "1")
#         )

#         # sécurité: année doit être 4 chiffres après correction
#         if re.fullmatch(r"\d{4}", y):
#             # normaliser jj/mm/aaaa
#             try:
#                 dd = int(d)
#                 mm = int(mth)
#                 if 1 <= dd <= 31 and 1 <= mm <= 12:
#                     data["date_facture"] = f"{dd:02d}/{mm:02d}/{y}"
#             except Exception:
#                 pass

#     # Si la date est sur une ligne "Facture Date ..." dans le header, elle peut être loin
#     # On tente aussi une recherche plus simple dd/mm/yyyy
#     if data["date_facture"] is None:
#         m2 = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", t)
#         if m2:
#             data["date_facture"] = m2.group(1)

#     # -------------------------
#     # Montants (HT / TVA / TTC)
#     # -------------------------
#     # On accepte 4140.00 / 4140,00 / 4 140.00
#     money = r"([0-9]{1,3}(?:[ \u00A0]?[0-9]{3})*(?:[.,][0-9]{2})?)"

#     # Total HT (Total H.T / Total HT / Totat HT ...)
#     m = re.search(
#         rf"(?:Total|Totat)\s*H\.?\s*T\.?\s*\.?\s*[:\-]?\s*{money}",
#         t,
#         flags=re.IGNORECASE,
#     )
#     if m:
#         data["montant_ht"] = _to_float(m.group(1))

#     # TVA (TVA 20% 828.00 / TVA : 828.00 / TVA 20.00% 828.00)
#     m = re.search(
#         rf"TVA\s*(?:\d+[.,]?\d*\s*%?)?\s*[:\-]?\s*{money}",
#         t,
#         flags=re.IGNORECASE,
#     )
#     if m:
#         data["montant_tva"] = _to_float(m.group(1))

#     # Total TTC (Total T.T.C / Total TTC / Total T.TC)
#     m = re.search(
#         rf"Total\s*T\.?\s*T\.?\s*C\.?\s*[:\-]?\s*{money}",
#         t,
#         flags=re.IGNORECASE,
#     )
#     if m:
#         data["montant_ttc"] = _to_float(m.group(1))

#     # Bonus: si TTC est trouvé mais HT est None, parfois HT est sur "Total H.T. :"
#     # (déjà fait), sinon on ne force pas.

#     return data


















import re
from typing import Optional, Dict, Any


def _normalize_text(text: str) -> str:
    if not text:
        return ""

    t = text.replace("\r", "\n")
    t = t.replace(",", ".")
    t = re.sub(r"[ \t]+", " ", t)

    # corrections OCR fréquentes
    t = re.sub(r"\bTotat\b", "Total", t, flags=re.IGNORECASE)
    t = re.sub(r"T\.?\s*T\.?\s*C\.?", "TTC", t, flags=re.IGNORECASE)
    t = re.sub(r"H\.?\s*T\.?", "HT", t, flags=re.IGNORECASE)

    # enlever espaces au milieu des chiffres: "4 140.00" -> "4140.00"
    t = re.sub(r"(?<=\d)\s+(?=\d)", "", t)

    return t


def _to_float(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None

    # O->0 dans un contexte numérique
    s = re.sub(r"(?<=\d)[oO](?=\d)", "0", s)

    # garder chiffres et points
    s = re.sub(r"[^0-9.]", "", s)

    # si plusieurs points, garder le dernier comme décimal
    if s.count(".") > 1:
        parts = re.split(r"\.+", s)
        s = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return float(s)
    except Exception:
        return None


def _find_date(text: str) -> Optional[str]:
    # 1) dd/mm/yyyy avec tolérance: espaces + / ou -
    m = re.search(r"(\d{2})\s*[/\-]\s*(\d{2})\s*[/\-]\s*(\d{4})", text)
    if m:
        dd, mm, yyyy = m.group(1), m.group(2), m.group(3)
        return f"{dd}/{mm}/{yyyy}"

    # 2) yyyy-mm-dd (fallback)
    m = re.search(r"\b(\d{4})\s*[-/]\s*(\d{2})\s*[-/]\s*(\d{2})\b", text)
    if m:
        yyyy, mm, dd = m.group(1), m.group(2), m.group(3)
        return f"{dd}/{mm}/{yyyy}"

    return None



def _find_line_amount(lines: list[str], must_have_regex: str) -> Optional[float]:
    """
    Cherche une ligne qui contient le label (ex: Total HT)
    et qui ressemble à la zone des totaux (souvent ":" ou "DHS").
    Prend le DERNIER montant de la ligne.
    """
    pat = re.compile(must_have_regex, flags=re.IGNORECASE)

    for line in lines:
        if not pat.search(line):
            continue

        # pour éviter l'entête du tableau ("Total HT Total TTC TVA%")
        # on exige un ":" OU "DHS" OU "DH"
        if (":" not in line) and ("DHS" not in line.upper()) and ("DH" not in line.upper()):
            continue

        # extraire tous les montants style 4140.00 / 4968.00
        nums = re.findall(r"\b\d{1,6}(?:\.\d{2})\b", line)
        vals = [v for v in (_to_float(x) for x in nums) if v is not None]

        if not vals:
            continue

        # sur les lignes des totaux, le montant est souvent le dernier nombre
        return vals[-1]

    return None


def _find_tva_amount(lines: list[str]) -> Optional[float]:
    """
    Ligne TVA: "TVA 20.00% 828.00 DHS" -> prendre 828.00 (dernier montant)
    Évite de prendre 20.00.
    """
    for line in lines:
        if not re.search(r"\bTVA\b", line, flags=re.IGNORECASE):
            continue

        # doit avoir DH/DHS ou ":" sinon risque d'être colonne TVA%
        if (":" not in line) and ("DHS" not in line.upper()) and ("DH" not in line.upper()):
            continue

        nums = re.findall(r"\b\d{1,6}(?:\.\d{2})\b", line)
        vals = [v for v in (_to_float(x) for x in nums) if v is not None]
        if not vals:
            continue

        # ex: [20.00, 828.00] -> prendre le dernier
        return vals[-1]

    return None


def parse_facture_text(text: str) -> Dict[str, Any]:
    t = _normalize_text(text)
    lines = [ln.strip() for ln in t.split("\n") if ln.strip()]

    data: Dict[str, Any] = {
        "fournisseur": None,
        "date_facture": None,
        "montant_ht": None,
        "montant_tva": None,
        "montant_ttc": None,
    }

    # Fournisseur (première ligne "STE ...")
    m = re.search(r"^(STE\s+[^\n]{3,80})$", t, flags=re.MULTILINE | re.IGNORECASE)
    if m:
        data["fournisseur"] = m.group(1).strip()

    # Date
    data["date_facture"] = _find_date(t)

    # Montants (lignes de totaux)
    data["montant_ht"] = _find_line_amount(lines, r"\bTotal\b.*\bHT\b")
    data["montant_ttc"] = _find_line_amount(lines, r"\bTotal\b.*\bTTC\b")
    data["montant_tva"] = _find_tva_amount(lines)

    # Fallback: Net à payer ≈ TTC
    if data["montant_ttc"] is None:
        net = _find_line_amount(lines, r"\bNet\b.*\bpayer\b")
        if net is not None:
            data["montant_ttc"] = net

    # Fallback calcul HT = TTC - TVA
    if data["montant_ht"] is None and data["montant_ttc"] is not None and data["montant_tva"] is not None:
        data["montant_ht"] = round(float(data["montant_ttc"] - data["montant_tva"]), 2)

    return data
