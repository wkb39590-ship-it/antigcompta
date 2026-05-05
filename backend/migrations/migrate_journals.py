
import sys
import os

# Ajouter le chemin du backend pour l'import
sys.path.append(os.getcwd())

from database import SessionLocal, engine
from models import Base, Societe, JournalComptable

def migrate():
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        toutes_societes = db.query(Societe).all()
        print(f"Migration de {len(toutes_societes)} sociétés...")
        
        default_journals = [
            {"code": "ACH", "label": "Journal des Achats", "type": "ACHAT"},
            {"code": "VTE", "label": "Journal des Ventes", "type": "VENTE"},
            {"code": "OD", "label": "Opérations Diverses", "type": "OD"},
            {"code": "BQ", "label": "Banque Général", "type": "BANQUE"},
            {"code": "IMMO", "label": "Journal des Immobilisations", "type": "OD"},
            {"code": "PAYE", "label": "Journal de Paie", "type": "PAIE"},
        ]
        
        for soc in toutes_societes:
            # Vérifier si les journaux existent déjà
            existants = db.query(JournalComptable).filter(JournalComptable.societe_id == soc.id).all()
            codes_existants = [j.code for j in existants]
            
            for dj in default_journals:
                if dj["code"] not in codes_existants:
                    nouveau = JournalComptable(
                        societe_id=soc.id,
                        code=dj["code"],
                        label=dj["label"],
                        type=dj["type"]
                    )
                    db.add(nouveau)
                    print(f"  + Journal {dj['code']} ajouté pour {soc.raison_sociale}")
        
        db.commit()
        print("Migration terminée avec succès.")
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la migration : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
