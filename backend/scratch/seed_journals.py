import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database import SessionLocal
from models import Societe, JournalComptable

def seed_default_journals():
    db = SessionLocal()
    try:
        societes = db.query(Societe).all()
        for soc in societes:
            print(f"Vérification des journaux pour la société : {soc.raison_sociale} (ID: {soc.id})")
            
            defaults = [
                {"code": "ACH", "label": "Journal des Achats", "type": "ACHAT"},
                {"code": "VTE", "label": "Journal des Ventes", "type": "VENTE"},
                {"code": "IMMO", "label": "Journal d'Immobilisations", "type": "IMMOBILISATION"},
                {"code": "OD", "label": "Opérations Diverses", "type": "OD"},
                {"code": "PAYE", "label": "Journal de Paie", "type": "PAIE"},
                {"code": "BQ1", "label": "Banque Populaire", "type": "BANQUE"},
                {"code": "BQ2", "label": "CIH", "type": "BANQUE"},
            ]
            
            added = 0
            for jd in defaults:
                exists = db.query(JournalComptable).filter_by(societe_id=soc.id, code=jd["code"]).first()
                if not exists:
                    nj = JournalComptable(
                        societe_id=soc.id,
                        code=jd["code"],
                        label=jd["label"],
                        type=jd["type"]
                    )
                    db.add(nj)
                    added += 1
            if added > 0:
                print(f" -> {added} journaux ajoutés.")
            else:
                print(" -> Tous les journaux sont déjà présents.")
                
        db.commit()
        print("Opération terminée avec succès !")
    except Exception as e:
        db.rollback()
        print(f"Erreur : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_default_journals()
