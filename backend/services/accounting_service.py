from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from decimal import Decimal
from typing import List, Dict, Any
from models import EntryLine, JournalEntry, PcmAccount
from datetime import date

# Groupement par Rubriques selon le Plan Comptable Marocain (CGNC)
PCM_RUBRIQUES = {
    # ACTIF IMMOBILISÉ
    "21": "IMMOBILISATIONS INCORPORELLES",
    "22": "IMMOBILISATIONS CORPORELLES",
    "23": "IMMOBILISATIONS CORPORELLES",
    "24": "IMMOBILISATIONS FINANCIERES",
    "25": "IMMOBILISATIONS FINANCIERES",
    "27": "ECARTS DE CONVERSION - ACTIF",
    
    # ACTIF CIRCULANT
    "31": "STOCKS",
    "34": "CREANCES DE L'ACTIF CIRCULANT",
    "35": "TITRES ET VALEURS DE PLACEMENT",
    "37": "ECARTS DE CONVERSION - ACTIF (CIRCULANT)",
    
    # TRESORERIE ACTIF
    "51": "TRESORERIE - ACTIF",
    
    # FINANCEMENT PERMANENT
    "11": "CAPITAUX PROPRES",
    "13": "CAPITAUX PROPRES ASSIMILES",
    "14": "DETTES DE FINANCEMENT",
    "15": "PROVISIONS DURABLES POUR RISQUES ET CHARGES",
    "17": "ECARTS DE CONVERSION - PASSIF",
    
    # PASSIF CIRCULANT
    "44": "DETTES DU PASSIF CIRCULANT",
    "45": "AUTRES PROVISIONS POUR RISQUES ET CHARGES",
    "47": "ECARTS DE CONVERSION - PASSIF (CIRCULANT)",
    
    # TRESORERIE PASSIF
    "55": "TRESORERIE - PASSIF"
}

class AccountingService:
    @staticmethod
    def get_balance_generale(db: Session, societe_id: int, annee: int, mois: int = None, validated_only: bool = True) -> List[Dict[str, Any]]:
        """
        Retourne la balance générale en distinguant deux logiques :
        - Comptes de BILAN (classe 2, 3, 4, 5) : soldes CUMULATIFS depuis l'origine jusqu'à
          la fin de l'exercice demandé (ou du mois demandé). Un bien acquis en 2024 doit
          apparaître dans le bilan 2025 avec son montant total.
        - Comptes de GESTION (classe 6, 7) : uniquement les mouvements de l'année en cours
          pour le calcul du résultat de l'exercice.
        """
        from sqlalchemy import and_, or_

        base_filter = [JournalEntry.societe_id == societe_id]
        if validated_only:
            base_filter.append(JournalEntry.is_validated == True)

        # ── 1. Comptes de BILAN : cumulatif jusqu'à la fin de l'exercice ──────
        # On prend tous les mouvements dont la date est <= 31/12/annee (ou <= fin du mois)
        if mois:
            from datetime import date
            import calendar
            last_day = calendar.monthrange(annee, mois)[1]
            date_limite = date(annee, mois, last_day)
        else:
            from datetime import date
            date_limite = date(annee, 12, 31)

        bilan_query = db.query(
            EntryLine.account_code,
            func.max(EntryLine.account_label).label('account_label'),
            func.sum(EntryLine.debit).label('total_debit'),
            func.sum(EntryLine.credit).label('total_credit')
        ).join(JournalEntry).filter(
            *base_filter,
            JournalEntry.entry_date <= date_limite,
            # Classes de bilan : comptes commençant par 2, 3, 4 ou 5
            or_(
                EntryLine.account_code.like('2%'),
                EntryLine.account_code.like('3%'),
                EntryLine.account_code.like('4%'),
                EntryLine.account_code.like('5%'),
            )
        ).group_by(EntryLine.account_code)

        # ── 2. Comptes de GESTION : uniquement l'exercice en cours ────────────
        gestion_query = db.query(
            EntryLine.account_code,
            func.max(EntryLine.account_label).label('account_label'),
            func.sum(EntryLine.debit).label('total_debit'),
            func.sum(EntryLine.credit).label('total_credit')
        ).join(JournalEntry).filter(
            *base_filter,
            extract('year', JournalEntry.entry_date) == annee,
            # Classes de gestion : comptes commençant par 6 ou 7
            or_(
                EntryLine.account_code.like('6%'),
                EntryLine.account_code.like('7%'),
            )
        ).group_by(EntryLine.account_code)

        if mois:
            gestion_query = gestion_query.filter(
                extract('month', JournalEntry.entry_date) == mois
            )

        # ── 3. Résultats ANTÉRIEURS (Report à nouveau) ────────────
        # Cumul de la classe 6 et 7 pour toutes les années < annee
        cumul_anterieur_query = db.query(
            func.sum(EntryLine.debit).label('total_debit'),
            func.sum(EntryLine.credit).label('total_credit')
        ).join(JournalEntry).filter(
            *base_filter,
            extract('year', JournalEntry.entry_date) < annee,
            or_(
                EntryLine.account_code.like('6%'),
                EntryLine.account_code.like('7%'),
            )
        ).first()

        resultat_anterieur = Decimal("0")
        if cumul_anterieur_query:
            prod_ant = Decimal(str(cumul_anterieur_query.total_credit or 0))
            charg_ant = Decimal(str(cumul_anterieur_query.total_debit or 0))
            resultat_anterieur = prod_ant - charg_ant

        # ── Fusion des deux résultats ─────────────────────────────────────────
        # ── Fusion des deux résultats ─────────────────────────────────────────
        balance_dict = {}
        
        # 1. Ajouter les résultats du bilan
        for r in bilan_query.all():
            if r.account_code not in balance_dict:
                balance_dict[r.account_code] = {
                    "account_code": r.account_code,
                    "account_label": r.account_label,
                    "total_debit": Decimal(str(r.total_debit or 0)),
                    "total_credit": Decimal(str(r.total_credit or 0))
                }
            else:
                balance_dict[r.account_code]["total_debit"] += Decimal(str(r.total_debit or 0))
                balance_dict[r.account_code]["total_credit"] += Decimal(str(r.total_credit or 0))
            
        # 2. Ajouter les résultats de gestion
        for r in gestion_query.all():
            if r.account_code not in balance_dict:
                balance_dict[r.account_code] = {
                    "account_code": r.account_code,
                    "account_label": r.account_label,
                    "total_debit": Decimal(str(r.total_debit or 0)),
                    "total_credit": Decimal(str(r.total_credit or 0))
                }
            else:
                balance_dict[r.account_code]["total_debit"] += Decimal(str(r.total_debit or 0))
                balance_dict[r.account_code]["total_credit"] += Decimal(str(r.total_credit or 0))
            
        balance = list(balance_dict.values())
        return balance, resultat_anterieur

    @staticmethod
    def get_bilan_comptable(db: Session, societe_id: int, annee: int, mois: int = None, validated_only: bool = True) -> Dict[str, Any]:
        """
        Génère le Bilan Comptable (CGNC Maroc) avec intégration des amortissements et du résultat.
        """
        balance, resultat_anterieur = AccountingService.get_balance_generale(db, societe_id, annee, mois, validated_only)
        
        actif_data = {} 
        passif_data = {}
        total_produits = Decimal("0")
        total_charges = Decimal("0")

        # Catégorisation avec reclassement
        for line in balance:
            code = line["account_code"]
            debit = line["total_debit"]
            credit = line["total_credit"]
            solde_debit = debit - credit
            solde_credit = credit - debit

            # CPC (Calcul du Résultat)
            if code.startswith('6'):
                total_charges += solde_debit
                continue
            if code.startswith('7'):
                total_produits += solde_credit
                continue

            rubric_code = code[:2]
            
            # Reclassements intelligents
            if code.startswith('51') and solde_debit < 0:
                rubric_code = "55"
            elif code.startswith('342') and solde_debit < 0:
                rubric_code = "44"
            elif code.startswith('441') and solde_credit < 0:
                rubric_code = "34"

            # Amortissements et Provisions (28, 29, 39)
            # On les mappe sur leur rubrique d'origine (ex: 283 -> 23)
            # RÈGLE: 28xx -> Rubrique 2.x
            is_amort = code.startswith(('28', '29', '39'))
            if is_amort:
                target_rub = code[0] + code[2] if len(code) >= 3 else rubric_code
                if target_rub not in actif_data: actif_data[target_rub] = []
                actif_data[target_rub].append({**line, "is_amort": True})
            else:
                # Affectation Standard
                is_actif = rubric_code in ["21", "22", "23", "24", "25", "27", "31", "34", "35", "37", "51"]
                if is_actif:
                    if rubric_code not in actif_data: actif_data[rubric_code] = []
                    actif_data[rubric_code].append({**line, "is_amort": False})
                else:
                    if rubric_code not in passif_data: passif_data[rubric_code] = []
                    passif_data[rubric_code].append(line)

        # Calcul du résultat final
        resultat = total_produits - total_charges
        
        # ──────────────────────────────────────────────────────────────────────
        # CONSTRUCTION ACTIF
        # ──────────────────────────────────────────────────────────────────────
        final_actif = []
        total_actif_net = Decimal("0")
        
        actif_rubriques_order = ["21", "22", "23", "24", "25", "27", "31", "34", "35", "37", "51"]
        for rub_code in actif_rubriques_order:
            lines = actif_data.get(rub_code, [])
            if not lines:
                continue
                
            rub_brut = Decimal("0")
            rub_amort = Decimal("0")
            rub_lines = []
            
            for l in lines:
                code_l = l["account_code"]
                if l.get("is_amort"):
                    val_amort = l["total_credit"] - l["total_debit"]
                    rub_amort += val_amort
                    rub_lines.append({
                        "account_code": code_l,
                        "account_label": l["account_label"],
                        "brut": Decimal("0"),
                        "amortissement": val_amort,
                        "net": -val_amort,
                        "type": "DEBIT"
                    })
                else:
                    val_brut = l["total_debit"] - l["total_credit"]
                    rub_brut += val_brut
                    rub_lines.append({
                        "account_code": code_l,
                        "account_label": l["account_label"],
                        "brut": val_brut,
                        "amortissement": Decimal("0"),
                        "net": val_brut,
                        "type": "DEBIT"
                    })
            
            net_section = rub_brut - rub_amort
            total_actif_net += net_section
            final_actif.append({
                "libelle": PCM_RUBRIQUES.get(rub_code, f"RUBRIQUE {rub_code}"),
                "lignes": rub_lines,
                "total_brut": rub_brut,
                "total_amortissement": rub_amort,
                "total": net_section
            })

        # ──────────────────────────────────────────────────────────────────────
        # CONSTRUCTION PASSIF
        # ──────────────────────────────────────────────────────────────────────
        final_passif = []
        total_passif = Decimal("0")
        
        passif_rubriques_order = ["11", "13", "14", "15", "17", "44", "45", "47", "55"]
        for rub_code in passif_rubriques_order:
            lines = passif_data.get(rub_code, [])
            
            # Intégrer le résultat dans Capitaux Propres (11)
            if rub_code == "11":
                # Résultat de l'exercice
                lines.append({
                    "account_code": "1191",
                    "account_label": "Résultat net de l'exercice",
                    "total_debit": Decimal("0") if resultat >= 0 else -resultat,
                    "total_credit": resultat if resultat >= 0 else Decimal("0")
                })
                # Report à nouveau (Résultats des années antérieures)
                if resultat_anterieur != 0:
                    lines.append({
                        "account_code": "116",
                        "account_label": "Report à nouveau (exercices antérieurs)",
                        "total_debit": Decimal("0") if resultat_anterieur >= 0 else -resultat_anterieur,
                        "total_credit": resultat_anterieur if resultat_anterieur >= 0 else Decimal("0")
                    })

            if not lines:
                continue
                
            rub_total_net = Decimal("0")
            rub_lines = []
            
            for l in lines:
                val_net = l["total_credit"] - l["total_debit"]
                rub_total_net += val_net
                rub_lines.append({
                    "account_code": l["account_code"],
                    "account_label": l["account_label"],
                    "brut": Decimal("0"),
                    "amortissement": Decimal("0"),
                    "net": val_net,
                    "type": "CREDIT"
                })
            
            total_passif += rub_total_net
            final_passif.append({
                "libelle": PCM_RUBRIQUES.get(rub_code, f"RUBRIQUE {rub_code}"),
                "lignes": rub_lines,
                "total": rub_total_net
            })

        return {
            "societe_id": societe_id,
            "annee": annee,
            "actif": final_actif,
            "passif": final_passif,
            "total_actif": total_actif_net,
            "total_passif": total_passif,
            "resultat": resultat,
            "is_balanced": abs(total_actif_net - total_passif) < Decimal("0.05")
        }
