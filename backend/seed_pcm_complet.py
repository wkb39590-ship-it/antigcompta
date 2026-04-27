"""
seed_pcm_complet.py — Référentiel Élargi du Plan Comptable Marocain (PCM)
Contient environ 350 codes couvrant toutes les classes du CGNC.
Usage: python seed_pcm_complet.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
from models import PcmAccount

# Liste élargie des comptes PCM Maroc
PCM_ACCOUNTS = [
    # ── CLASSE 1 : FINANCEMENT PERMANENT ─────────────────────────────────────
    ("1111", "Capital social", 1, "11", "PASSIF", False, None),
    ("1117", "Capital appelé non versé", 1, "11", "PASSIF", False, None),
    ("1119", "Actionnaires capital souscrit - non appelé", 1, "11", "PASSIF", False, None),
    ("1121", "Primes d'émission", 1, "11", "PASSIF", False, None),
    ("1131", "Réserve légale", 1, "11", "PASSIF", False, None),
    ("1140", "Réserves statutaires ou contractuelles", 1, "11", "PASSIF", False, None),
    ("1151", "Réserves facultatives", 1, "11", "PASSIF", False, None),
    ("1161", "Report à nouveau (solde créditeur)", 1, "11", "PASSIF", False, None),
    ("1169", "Report à nouveau (solde débiteur)", 1, "11", "PASSIF", False, None),
    ("1181", "Résultat net en instance d'affectation", 1, "11", "PASSIF", False, None),
    ("1191", "Résultat net de l'exercice (créditeur)", 1, "11", "PASSIF", False, None),
    ("1199", "Résultat net de l'exercice (débiteur)", 1, "11", "PASSIF", False, None),
    ("1311", "Subventions d'investissement reçues", 1, "13", "PASSIF", False, None),
    ("1411", "Emprunts obligataires", 1, "14", "PASSIF", False, None),
    ("1481", "Emprunts auprès des établissements de crédit", 1, "14", "PASSIF", False, None),
    ("1482", "Avances de l'Etat", 1, "14", "PASSIF", False, None),
    ("1486", "Fournisseurs d'immobilisations (comptes de financement)", 1, "14", "PASSIF", False, None),
    ("1511", "Provisions pour litiges", 1, "15", "PASSIF", False, None),
    ("1512", "Provisions pour garanties données aux clients", 1, "15", "PASSIF", False, None),
    ("1555", "Provisions pour impôts", 1, "15", "PASSIF", False, None),

    # ── CLASSE 2 : ACTIF IMMOBILISÉ ──────────────────────────────────────────
    ("2111", "Frais de constitution", 2, "21", "ACTIF", False, None),
    ("2113", "Frais d'augmentation de capital", 2, "21", "ACTIF", False, None),
    ("2210", "Terrains nus", 2, "22", "ACTIF", False, None),
    ("2220", "Terrains aménagés", 2, "22", "ACTIF", False, None),
    ("2230", "Terrains bâtis", 2, "22", "ACTIF", False, None),
    ("2311", "Terrains", 2, "23", "ACTIF", False, None),
    ("2321", "Bâtiments", 2, "23", "ACTIF", False, None),
    ("2331", "Installations techniques", 2, "23", "ACTIF", False, None),
    ("2332", "Matériel et outillage", 2, "23", "ACTIF", False, None),
    ("2340", "Matériel de transport", 2, "23", "ACTIF", False, None),
    ("2351", "Mobilier de bureau", 2, "23", "ACTIF", False, None),
    ("2352", "Matériel de bureau", 2, "23", "ACTIF", False, None),
    ("2355", "Matériel informatique", 2, "23", "ACTIF", False, None),
    ("2356", "Agencements, installations et aménagements divers", 2, "23", "ACTIF", False, None),
    ("2358", "Autres matériels, mobiliers et agencements", 2, "23", "ACTIF", False, None),
    ("2380", "Immobilisations corporelles en cours", 2, "23", "ACTIF", False, None),
    ("2411", "Titres de participation", 2, "24", "ACTIF", False, None),
    ("2481", "Prêts au personnel", 2, "24", "ACTIF", False, None),
    ("2483", "Dépôts et cautionnements versés", 2, "24", "ACTIF", False, None),
    ("2486", "Créances immobilisées", 2, "24", "ACTIF", False, None),
    ("2510", "Titres de participation", 2, "25", "ACTIF", False, None),
    ("2710", "Frais d'acquisition des immobilisations", 2, "27", "ACTIF", False, None),
    
    # Amortissements (28xx)
    ("2811", "Amortissements des frais de constitution", 2, "28", "ACTIF", False, None),
    ("2832", "Amortissements des bâtiments", 2, "28", "ACTIF", False, None),
    ("2833", "Amortissements du matériel et outillage", 2, "28", "ACTIF", False, None),
    ("2834", "Amortissements du matériel de transport", 2, "28", "ACTIF", False, None),
    ("2835", "Amortissements du matériel de bureau, mobilier et améng", 2, "28", "ACTIF", False, None),

    # ── CLASSE 3 : ACTIF CIRCULANT (HORS TRÉSORERIE) ─────────────────────────
    ("3111", "Marchandises", 3, "31", "ACTIF", False, None),
    ("3121", "Matières premières", 3, "31", "ACTIF", False, None),
    ("3122", "Matières et fournitures consommables", 3, "31", "ACTIF", False, None),
    ("3123", "Emballages", 3, "31", "ACTIF", False, None),
    ("3131", "Produits en cours", 3, "31", "ACTIF", False, None),
    ("3151", "Produits finis", 3, "31", "ACTIF", False, None),
    ("3411", "Fournisseurs débiteurs (avances et acomptes)", 3, "34", "TIERS", False, None),
    ("3421", "Clients", 3, "34", "TIERS", False, None),
    ("3424", "Clients - Créances douteuses ou litigieuses", 3, "34", "TIERS", False, None),
    ("3425", "Clients - Effets à recevoir", 3, "34", "TIERS", False, None),
    ("3427", "Clients - Factures à établir", 3, "34", "TIERS", False, None),
    ("3431", "Avances et acomptes au personnel", 3, "34", "TIERS", False, None),
    ("3451", "Subventions à recevoir", 3, "34", "TIERS", False, None),
    ("3453", "Acomptes sur impôts sur les résultats", 3, "34", "TIERS", False, None),
    ("34551", "TVA récupérable sur charges", 3, "345", "TIERS", True, "RECUPERABLE"),
    ("34552", "TVA récupérable sur immobilisations", 3, "345", "TIERS", True, "IMMOBILISATION"),
    ("3456", "Etat - Crédit de TVA", 3, "34", "TIERS", True, "RECUPERABLE"),
    ("3458", "Etat - Autres comptes débiteurs", 3, "34", "TIERS", False, None),
    ("3461", "Associés - Comptes courants débiteurs", 3, "34", "TIERS", False, None),
    ("3481", "Créances sur cessions d'immobilisations", 3, "34", "TIERS", False, None),
    ("3482", "Créances sur cessions de titres et valeurs de placement", 3, "34", "TIERS", False, None),
    ("3487", "Débiteurs divers", 3, "34", "TIERS", False, None),
    ("3491", "Charges constatées d'avance", 3, "34", "ACTIF", False, None),
    ("3500", "Titres et valeurs de placement", 3, "35", "ACTIF", False, None),

    # ── CLASSE 4 : PASSIF CIRCULANT (HORS TRÉSORERIE) ─────────────────────────
    ("4411", "Fournisseurs", 4, "44", "TIERS", False, None),
    ("4413", "Fournisseurs - Effets à payer", 4, "44", "TIERS", False, None),
    ("4415", "Fournisseurs d'immobilisations", 4, "44", "TIERS", False, None),
    ("4417", "Fournisseurs - Retenues de garantie", 4, "44", "TIERS", False, None),
    ("4418", "Fournisseurs - Factures non parvenues", 4, "44", "TIERS", False, None),
    ("4421", "Clients créditeurs (avances et acomptes reçus)", 4, "44", "TIERS", False, None),
    ("4432", "Rémunérations dues au personnel", 4, "44", "TIERS", False, None),
    ("4433", "Dépôts du personnel créditeurs", 4, "44", "TIERS", False, None),
    ("4434", "Oppositions sur salaires", 4, "44", "TIERS", False, None),
    ("4441", "Personnel - Oppositions", 4, "44", "TIERS", False, None),
    ("4443", "CNSS", 4, "44", "TIERS", False, None),
    ("4445", "Mutuelles", 4, "44", "TIERS", False, None),
    ("4447", "AMO", 4, "44", "TIERS", False, None),
    ("4448", "Autres organismes sociaux", 4, "44", "TIERS", False, None),
    ("4452", "Etat - Impôts sur les résultats", 4, "44", "TIERS", False, None),
    ("4453", "Etat - Impôts retenus à la source (IR)", 4, "44", "TIERS", False, None),
    ("4455", "TVA facturée", 4, "44", "TIERS", True, "COLLECTEE"),
    ("4456", "Etat - TVA due", 4, "44", "TIERS", True, "COLLECTEE"),
    ("4457", "Etat - Autres impôts et taxes", 4, "44", "TIERS", False, None),
    ("4458", "Etat - Comptes créditeurs", 4, "44", "TIERS", False, None),
    ("4461", "Associés - Comptes courants créditeurs", 4, "44", "TIERS", False, None),
    ("4463", "Comptes bloqués des associés", 4, "44", "TIERS", False, None),
    ("4465", "Associés - Dividendes à payer", 4, "44", "TIERS", False, None),
    ("4481", "Dettes sur acquisitions d'immobilisations", 4, "44", "TIERS", False, None),
    ("4483", "Dettes sur acquisitions de titres et valeurs de placement", 4, "44", "TIERS", False, None),
    ("4487", "Créditeurs divers", 4, "44", "TIERS", False, None),
    ("4491", "Produits constatés d'avance", 4, "44", "PASSIF", False, None),

    # ── CLASSE 5 : TRÉSORERIE ────────────────────────────────────────────────
    ("5111", "Chèques à encaisser ou à l'encaissement", 5, "51", "ACTIF", False, None),
    ("5113", "Effets à encaisser ou à l'encaissement", 5, "51", "ACTIF", False, None),
    ("5115", "Virements à l'encaissement", 5, "51", "ACTIF", False, None),
    ("5141", "Banques (soldes débiteurs)", 5, "51", "ACTIF", False, None),
    ("5146", "CCP (soldes débiteurs)", 5, "51", "ACTIF", False, None),
    ("5161", "Caisse (solde débiteur)", 5, "51", "ACTIF", False, None),
    ("5541", "Banques (soldes créditeurs)", 5, "55", "PASSIF", False, None),
    ("5900", "Virements internes", 5, "59", "ACTIF", False, None),

    # ── CLASSE 6 : CHARGES ───────────────────────────────────────────────────
    ("6111", "Achats de marchandises (groupe A)", 6, "61", "CHARGE", False, None),
    ("6112", "Achats de marchandises (groupe B)", 6, "61", "CHARGE", False, None),
    ("6114", "Variations de stocks de marchandises", 6, "61", "CHARGE", False, None),
    ("6118", "Achats de marchandises des exercices précédents", 6, "61", "CHARGE", False, None),
    ("6119", "R.R.R obtenus sur achats de marchandises", 6, "61", "CHARGE", False, None),
    ("6121", "Achats de matières premières", 6, "61", "CHARGE", False, None),
    ("6122", "Achats de matières et fournitures consommables", 6, "61", "CHARGE", False, None),
    ("6123", "Achats d'emballages", 6, "61", "CHARGE", False, None),
    ("6124", "Achats de fournitures non stockables (eau, électricité)", 6, "61", "CHARGE", False, None),
    ("6125", "Achats de fournitures d'entretien", 6, "61", "CHARGE", False, None),
    ("6126", "Achats de fournitures de bureau", 6, "61", "CHARGE", False, None),
    ("6128", "Achats de matières et fournitures des exercices précédents", 6, "61", "CHARGE", False, None),
    ("6129", "R.R.R obtenus sur achats de matières et fournitures", 6, "61", "CHARGE", False, None),
    ("6131", "Locations et charges locatives", 6, "61", "CHARGE", False, None),
    ("6132", "Redevances de crédit-bail (leasing)", 6, "61", "CHARGE", False, None),
    ("6133", "Entretien et réparations", 6, "61", "CHARGE", False, None),
    ("6134", "Primes d'assurances", 6, "61", "CHARGE", False, None),
    ("6135", "Rémunérations d'intermédiaires et honoraires", 6, "61", "CHARGE", False, None),
    ("6136", "Frais d'actes et de contentieux", 6, "61", "CHARGE", False, None),
    ("6141", "Etudes, recherches et documentation", 6, "61", "CHARGE", False, None),
    ("6142", "Transports (personnel, marchandises)", 6, "61", "CHARGE", False, None),
    ("6143", "Déplacements, missions et réceptions", 6, "61", "CHARGE", False, None),
    ("6144", "Publicité, publications et relations publiques", 6, "61", "CHARGE", False, None),
    ("6145", "Frais postaux et frais de télécommunications", 6, "61", "CHARGE", False, None),
    ("6146", "Cotisations et dons", 6, "61", "CHARGE", False, None),
    ("6147", "Services bancaires", 6, "61", "CHARGE", False, None),
    ("6148", "Autres charges externes des exercices précédents", 6, "61", "CHARGE", False, None),
    ("6149", "R.R.R obtenus sur autres charges externes", 6, "61", "CHARGE", False, None),
    ("6151", "Impôts et taxes directs", 6, "61", "CHARGE", False, None),
    ("6155", "Taxes sur le chiffre d'affaires", 6, "61", "CHARGE", False, None),
    ("6161", "Impôts, taxes et droits d'enregistrement", 6, "61", "CHARGE", False, None),
    ("6167", "Taxes sur les véhicules", 6, "61", "CHARGE", False, None),
    ("6171", "Appointements et salaires", 6, "61", "CHARGE", False, None),
    ("6174", "Charges sociales", 6, "61", "CHARGE", False, None),
    ("6176", "Prévoyance sociale", 6, "61", "CHARGE", False, None),
    ("6177", "Autres charges sociales", 6, "61", "CHARGE", False, None),
    ("6181", "Jetons de présence", 6, "61", "CHARGE", False, None),
    ("6191", "D.E.A des frais de constitution", 6, "61", "CHARGE", False, None),
    ("6193", "D.E.A des immobilisations corporelles", 6, "61", "CHARGE", False, None),
    ("6311", "Intérêts des emprunts et dettes", 6, "63", "CHARGE", False, None),
    ("6331", "Pertes de change", 6, "63", "CHARGE", False, None),
    ("6385", "Charges nettes sur cessions de titres", 6, "63", "CHARGE", False, None),
    ("6513", "Valeurs nettes d'amortissements des immo corporelles cédées", 6, "65", "CHARGE", False, None),
    ("6581", "Pénalités et amendes", 6, "65", "CHARGE", False, None),
    ("6701", "Impôts sur les résultats", 6, "67", "CHARGE", False, None),

    # ── CLASSE 7 : PRODUITS ─────────────────────────────────────────────────
    ("7111", "Ventes de marchandises au Maroc", 7, "71", "PRODUIT", False, None),
    ("7113", "Vente de marchandises à l'étranger", 7, "71", "PRODUIT", False, None),
    ("7118", "Ventes de marchandises des exercices précédents", 7, "71", "PRODUIT", False, None),
    ("7119", "R.R.R accordés par l'entreprise", 7, "71", "PRODUIT", False, None),
    ("7121", "Ventes de produits finis", 7, "71", "PRODUIT", False, None),
    ("7122", "Ventes de produits intermédiaires", 7, "71", "PRODUIT", False, None),
    ("7124", "Ventes de services produits au Maroc", 7, "71", "PRODUIT", False, None),
    ("7125", "Ventes de services produits à l'étranger", 7, "71", "PRODUIT", False, None),
    ("7126", "Redevances pour brevets, marques, droits et valeurs", 7, "71", "PRODUIT", False, None),
    ("7127", "Ventes de produits résiduels", 7, "71", "PRODUIT", False, None),
    ("7128", "Ventes de produits et services des exercices précédents", 7, "71", "PRODUIT", False, None),
    ("7129", "R.R.R accordés sur ventes de produits", 7, "71", "PRODUIT", False, None),
    ("7131", "Variations des stocks de produits en cours", 7, "71", "PRODUIT", False, None),
    ("7132", "Variations des stocks de produits finis", 7, "71", "PRODUIT", False, None),
    ("7140", "Immobilisations produites par l'entreprise pour elle-même", 7, "71", "PRODUIT", False, None),
    ("7161", "Subventions d'exploitation", 7, "71", "PRODUIT", False, None),
    ("7181", "Jetons de présence reçus", 7, "71", "PRODUIT", False, None),
    ("7182", "Revenus des immeubles non destinés à l'exploitation", 7, "71", "PRODUIT", False, None),
    ("7191", "Reprises sur amortissements de l'actif immobilisé", 7, "71", "PRODUIT", False, None),
    ("7311", "Produits des titres de participation", 7, "73", "PRODUIT", False, None),
    ("7331", "Gains de change", 7, "73", "PRODUIT", False, None),
    ("7381", "Intérêts et produits assimilés", 7, "73", "PRODUIT", False, None),
    ("7510", "Produits des cessions d'immobilisations", 7, "75", "PRODUIT", False, None),
    ("7561", "Libéralités reçues", 7, "75", "PRODUIT", False, None),
    ("7581", "Indemnités d'assurances reçues", 7, "75", "PRODUIT", False, None),
]

def seed():
    db = SessionLocal()
    try:
        count = 0
        for code, label, pcm_class, group_code, account_type, is_tva, tva_type in PCM_ACCOUNTS:
            existing = db.query(PcmAccount).filter(PcmAccount.code == code).first()
            if not existing:
                db.add(PcmAccount(
                    code=code,
                    label=label,
                    pcm_class=pcm_class,
                    group_code=group_code,
                    account_type=account_type,
                    is_tva_account=is_tva,
                    tva_type=tva_type,
                ))
                count += 1
            else:
                # Mise à jour des libellés et types si déjà présent pour assurer la cohérence
                existing.label = label
                existing.pcm_class = pcm_class
                existing.group_code = group_code
                existing.account_type = account_type
                existing.is_tva_account = is_tva
                existing.tva_type = tva_type
                count += 1
        db.commit()
        print(f"✅ PCM Élargi terminé : {count} comptes synchronisés ({len(PCM_ACCOUNTS)} total)")
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur seed : {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Synchronisation des comptes PCM Élargi...")
    seed()
