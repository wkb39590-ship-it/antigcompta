
from database import SessionLocal
from models import Societe, Employe
from datetime import date

def seed_one_employe():
    db = SessionLocal()
    try:
        # 1. Trouver la société "STE Comptoire Arrahma S.A.R.L"
        societe = db.query(Societe).filter(Societe.id == 7).first()
        if not societe:
            print("❌ Société ID 7 non trouvée.")
            return

        # 2. Vérifier si on a déjà des employés
        existing = db.query(Employe).filter(Employe.societe_id == societe.id).first()
        if existing:
            print(f"ℹ️ Un employé existe déjà ({existing.nom}). Pas d'ajout nécessaire.")
            return

        # 3. Ajouter un employé type
        nouveau = Employe(
            societe_id=societe.id,
            nom="ALAMI",
            prenom="Ahmed",
            cin="AB123456",
            date_naissance=date(1990, 5, 15),
            poste="Comptable Senior",
            date_embauche=date(2023, 1, 1),
            type_contrat="CDI",
            salaire_base=8500.00,
            nb_enfants=2,
            anciennete_pct=5.0,
            numero_cnss="112233445",
            affiliee_cnss=True,
            statut="ACTIF"
        )
        
        db.add(nouveau)
        db.commit()
        print(f"✅ Employé '{nouveau.nom} {nouveau.prenom}' ajouté avec succès à la société '{societe.raison_sociale}'.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors du seeding : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_one_employe()
