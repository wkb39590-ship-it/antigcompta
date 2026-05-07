from database import SessionLocal
from models import PcmAccount

# RÉFÉRENTIEL OFFICIEL PCM MAROC (CGNC)
PCM_DATA = [
    # CLASSE 1 : FINANCEMENT PERMANENT
    ("1111", "Capital social ou personnel", 1, "PASSIF"),
    ("1117", "Capital appelé non versé", 1, "PASSIF"),
    ("1140", "Réserves statutaires ou contractuelles", 1, "PASSIF"),
    ("1151", "Réserves facultatives", 1, "PASSIF"),
    ("1161", "Report à nouveau (solde créditeur)", 1, "PASSIF"),
    ("1169", "Report à nouveau (solde débiteur)", 1, "PASSIF"),
    ("1181", "Résultat net en instance d'affectation", 1, "PASSIF"),
    ("1191", "Résultat net de l'exercice (créditeur)", 1, "PASSIF"),
    ("1411", "Emprunts obligataires", 1, "PASSIF"),
    ("1481", "Emprunts auprès des établissements de crédit", 1, "PASSIF"),
    
    # CLASSE 2 : ACTIF IMMOBILISÉ
    ("2111", "Frais de constitution", 2, "ACTIF"),
    ("2113", "Frais d'augmentation de capital", 2, "ACTIF"),
    ("2210", "Terrains nus", 2, "ACTIF"),
    ("2230", "Terrains bâtis", 2, "ACTIF"),
    ("2311", "Terrains", 2, "ACTIF"),
    ("2321", "Bâtiments", 2, "ACTIF"),
    ("2331", "Installations techniques", 2, "ACTIF"),
    ("2332", "Matériel et outillage", 2, "ACTIF"),
    ("2340", "Matériel de transport", 2, "ACTIF"),
    ("2351", "Mobilier de bureau", 2, "ACTIF"),
    ("2352", "Matériel de bureau", 2, "ACTIF"),
    ("2355", "Matériel informatique", 2, "ACTIF"),
    ("2356", "Agencements, installations et aménagements divers", 2, "ACTIF"),
    ("2832", "Amortissements des bâtiments", 2, "ACTIF"),
    ("2833", "Amortissements du matériel et outillage", 2, "ACTIF"),
    ("2834", "Amortissements du matériel de transport", 2, "ACTIF"),
    ("2835", "Amortissements du mobilier, matériel de bureau et aménagement", 2, "ACTIF"),
    
    # CLASSE 3 : ACTIF CIRCULANT
    ("3111", "Marchandises", 3, "ACTIF"),
    ("3121", "Matières premières", 3, "ACTIF"),
    ("3122", "Matières et fournitures consommables", 3, "ACTIF"),
    ("3411", "Fournisseurs - avances et acomptes versés", 3, "TIERS"),
    ("3421", "Clients", 3, "TIERS"),
    ("3425", "Clients - effets à recevoir", 3, "TIERS"),
    ("3431", "Avances et acomptes au personnel", 3, "TIERS"),
    ("3451", "Subventions à recevoir", 3, "TIERS"),
    ("3455", "État - TVA récupérable", 3, "TIERS"),
    ("34551", "État - TVA récupérable sur immobilisations", 3, "TIERS"),
    ("34552", "État - TVA récupérable sur charges", 3, "TIERS"),
    ("3461", "Associés - comptes courants débiteurs", 3, "TIERS"),
    ("3481", "Créances sur cessions d'immobilisations", 3, "TIERS"),
    
    # CLASSE 4 : PASSIF CIRCULANT
    ("4411", "Fournisseurs", 4, "TIERS"),
    ("4413", "Fournisseurs - effets à payer", 4, "TIERS"),
    ("4418", "Fournisseurs - factures non parvenues", 4, "TIERS"),
    ("4421", "Clients - avances et acomptes reçus", 4, "TIERS"),
    ("4432", "Personnel - rémunérations dues", 4, "TIERS"),
    ("4441", "Caisse Nationale de Sécurité Sociale (CNSS)", 4, "TIERS"),
    ("4443", "Caisses de retraite", 4, "TIERS"),
    ("4445", "Mutuelles", 4, "TIERS"),
    ("4447", "Charges sociales à payer", 4, "TIERS"),
    ("4448", "Autres organismes sociaux", 4, "TIERS"),
    ("4452", "État - impôts retenus à la source", 4, "TIERS"),
    ("4453", "État - impôt sur le revenu (retenu à la source)", 4, "TIERS"),
    ("4455", "État - TVA facturée", 4, "TIERS"),
    ("4456", "État - TVA due", 4, "TIERS"),
    ("4481", "Dettes sur acquisitions d'immobilisations", 4, "TIERS"),
    
    # CLASSE 5 : TRÉSORERIE
    ("5141", "Banques (soldes débiteurs)", 5, "ACTIF"),
    ("5161", "Caisses", 5, "ACTIF"),
    ("5541", "Banques (soldes créditeurs)", 5, "PASSIF"),
    ("5900", "Virements internes", 5, "ACTIF"),
    
    # CLASSE 6 : CHARGES
    ("6111", "Achats de marchandises", 6, "CHARGE"),
    ("6114", "Variation des stocks de marchandises", 6, "CHARGE"),
    ("6121", "Achats de matières premières", 6, "CHARGE"),
    ("6122", "Achats de matières et fournitures consommables", 6, "CHARGE"),
    ("6124", "Achats de fournitures non stockables (eau, électricité)", 6, "CHARGE"),
    ("6125", "Achats de fournitures d'entretien", 6, "CHARGE"),
    ("6126", "Achats de fournitures de bureau", 6, "CHARGE"),
    ("6131", "Locations et charges locatives", 6, "CHARGE"),
    ("6132", "Redevances de crédit-bail", 6, "CHARGE"),
    ("6133", "Entretien et réparations", 6, "CHARGE"),
    ("6134", "Primes d'assurance", 6, "CHARGE"),
    ("6135", "Rémunérations d'intermédiaires et honoraires", 6, "CHARGE"),
    ("6141", "Études, recherches et documentation", 6, "CHARGE"),
    ("6142", "Transports", 6, "CHARGE"),
    ("6143", "Déplacements, missions et réceptions", 6, "CHARGE"),
    ("6144", "Publicité, publications et relations publiques", 6, "CHARGE"),
    ("6145", "Frais postaux et frais de télécommunications", 6, "CHARGE"),
    ("6147", "Services bancaires", 6, "CHARGE"),
    ("6161", "Impôts, taxes et droits d'enregistrement", 6, "CHARGE"),
    ("6171", "Rémunérations du personnel", 6, "CHARGE"),
    ("6174", "Charges sociales", 6, "CHARGE"),
    ("6191", "Dotations d'exploitation aux amortissements de l'immobilisation incorporelle", 6, "CHARGE"),
    ("6193", "Dotations d'exploitation aux amortissements des immobilisations corporelles", 6, "CHARGE"),
    
    # CLASSE 7 : PRODUITS
    ("7111", "Ventes de marchandises au Maroc", 7, "PRODUIT"),
    ("7113", "Ventes de marchandises à l'exportation", 7, "PRODUIT"),
    ("7121", "Ventes de produits finis", 7, "PRODUIT"),
    ("7124", "Ventes de services produits au Maroc", 7, "PRODUIT"),
    ("7127", "Ventes de produits résiduels", 7, "PRODUIT"),
    ("7131", "Variation des stocks de produits", 7, "PRODUIT"),
    ("7191", "Reprises sur amortissements de l'actif immobilisé", 7, "PRODUIT"),
]

def run():
    db = SessionLocal()
    try:
        print("--- SYNCHRONISATION GLOBALE PCM MAROC ---")
        for code, label, pcm_class, acc_type in PCM_DATA:
            acc = db.query(PcmAccount).filter(PcmAccount.code == code).first()
            if acc:
                if acc.label != label:
                    print(f"MAJ {code}: {acc.label} -> {label}")
                    acc.label = label
                    acc.account_type = acc_type
            else:
                print(f"ADD {code}: {label}")
                db.add(PcmAccount(
                    code=code, label=label, pcm_class=pcm_class, account_type=acc_type
                ))
        db.commit()
        print("--- TERMINÉ ---")
    except Exception as e:
        db.rollback()
        print(f"ERREUR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
