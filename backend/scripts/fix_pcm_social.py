from database import SessionLocal
from models import PcmAccount

# Correction stricte de la section 44 (Dettes du passif circulant)
PCM_SECTION_44 = {
    "4411": "Fournisseurs",
    "4421": "Clients - avances et acomptes reçus",
    "4432": "Personnel - rémunérations dues", # LE SALAIRE NET
    "4441": "Caisse Nationale de Sécurité Sociale (CNSS)",
    "4443": "Caisses de retraite",
    "4445": "Mutuelles",
    "4447": "Charges sociales à payer",
    "4448": "Autres organismes sociaux",
    "4452": "État - impôts retenus à la source", # IR, etc.
    "4455": "État - TVA facturée",
    "4456": "État - TVA due",
    "4457": "État - autres impôts, taxes et versements assimilés",
}

def run():
    db = SessionLocal()
    try:
        print("--- Correction Section 44 (Organismes Sociaux & Personnel) ---")
        for code, label in PCM_SECTION_44.items():
            account = db.query(PcmAccount).filter(PcmAccount.code == code).first()
            if account:
                if account.label != label:
                    print(f"MAJ {code}: {account.label} -> {label}")
                    account.label = label
            else:
                print(f"AJOUT {code}: {label}")
                new_acc = PcmAccount(
                    code=code,
                    label=label,
                    pcm_class=4,
                    account_type="TIERS"
                )
                db.add(new_acc)
        
        db.commit()
        print("--- Correction terminée avec succès ---")
    except Exception as e:
        db.rollback()
        print(f"ERREUR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run()
