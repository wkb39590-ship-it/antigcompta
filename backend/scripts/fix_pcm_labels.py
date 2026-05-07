from database import SessionLocal
from models import PcmAccount

OFFICIAL_PCM = {
    # CLASSE 1
    "1111": "Capital social ou personnel",
    "1117": "Capital souscrit, non appelé",
    "1411": "Emprunts obligataires",
    "1481": "Emprunts auprès des établissements de crédit",
    
    # CLASSE 2
    "2111": "Frais préliminaires",
    "2220": "Brevets, marques, droits et valeurs similaires",
    "2311": "Terrains nus",
    "2321": "Bâtiments",
    "2332": "Matériel et outillage",
    "2340": "Matériel de transport",
    "2351": "Mobilier de bureau",
    "2352": "Matériel de bureau",
    "2355": "Matériel informatique",
    "2356": "Agencements, installations et aménagements divers",
    "2832": "Amortissements des bâtiments",
    "2833": "Amortissements du matériel et outillage",
    "2834": "Amortissements du matériel de transport",
    "2835": "Amortissements du mobilier, matériel de bureau et aménagement",
    
    # CLASSE 3
    "3111": "Marchandises",
    "3121": "Matières premières",
    "3411": "Fournisseurs - Avances et acomptes versés",
    "3421": "Clients",
    "3425": "Clients - Effets à recevoir",
    "3455": "État - TVA récupérable",
    "34551": "État - TVA récupérable sur immobilisations",
    "34552": "État - TVA récupérable sur charges",
    "3461": "Associés - Comptes courants",
    "3911": "Provisions pour dépréciation des marchandises",
    
    # CLASSE 4
    "4411": "Fournisseurs",
    "4421": "Clients - Avances et acomptes reçus",
    "4432": "Fournisseurs - Effets à payer",
    "4441": "Personnel - Rémunérations dues",
    "4443": "Organismes sociaux (CNSS...)",
    "4444": "État - Impôt sur le revenu retenu à la source",
    "4455": "État - TVA facturée",
    "4456": "État - TVA due",
    "4481": "Dettes sur acquisitions d'immobilisations",
    
    # CLASSE 5
    "5141": "Banques (soldes débiteurs)",
    "5161": "Caisses",
    "5541": "Banques (soldes créditeurs)",
    
    # CLASSE 6
    "6111": "Achats de marchandises",
    "6121": "Achats de matières premières",
    "6125": "Achats de fournitures non stockables (eau, électricité...)",
    "6131": "Locations et charges locatives",
    "6133": "Entretien et réparations",
    "6134": "Primes d'assurance",
    "6141": "Études, recherches et documentation",
    "6142": "Transports",
    "6143": "Déplacements, missions et réceptions",
    "6144": "Publicité, publications et relations publiques",
    "6145": "Frais postaux et frais de télécommunications",
    "6147": "Services bancaires",
    "6151": "Impôts et taxes directs",
    "6161": "Impôts et taxes indirects",
    "6171": "Rémunérations du personnel",
    "6174": "Charges sociales",
    "6191": "Dotations d'exploitation aux amortissements de l'immobilisation incorporelle",
    "6193": "Dotations d'exploitation aux amortissements des immobilisations corporelles",
    
    # CLASSE 7
    "7111": "Ventes de marchandises au Maroc",
    "7121": "Ventes de produits finis",
    "7124": "Ventes de produits accessoires",
    "7127": "Ventes de déchets et rebuts",
    "7131": "Variation des stocks de produits",
}

def run():
    db = SessionLocal()
    count = 0
    try:
        for code, label in OFFICIAL_PCM.items():
            account = db.query(PcmAccount).filter(PcmAccount.code == code).first()
            if account:
                if account.label != label:
                    print(f"Update {code}: {account.label} -> {label}")
                    account.label = label
                    count += 1
            else:
                # Si le compte n'existe pas, on peut éventuellement le créer
                print(f"Adding missing account {code}: {label}")
                new_acc = PcmAccount(
                    code=code,
                    label=label,
                    pcm_class=int(code[0]),
                    account_type="CHARGE" if code.startswith("6") else "PRODUIT" if code.startswith("7") else "BILAN"
                )
                db.add(new_acc)
                count += 1
        
        db.commit()
        print(f"FINISHED: {count} modifications effectuées.")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
