import sys
import os

# Ajouter le chemin du backend pour les imports
sys.path.append(os.getcwd())

from database import SessionLocal
from models import JournalEntry
from datetime import datetime

from database import SessionLocal
from models import JournalEntry, Immobilisation
from datetime import datetime

def fix_dotations():
    db = SessionLocal()
    try:
        # Trouver toutes les écritures de dotation
        entries = db.query(JournalEntry).filter(
            JournalEntry.journal_code == "OD",
            JournalEntry.reference.like("DOT-%")
        ).all()
        
        print(f"Trouvé {len(entries)} écritures de dotation.")
        
        for entry in entries:
            # Tenter de récupérer l'id immo depuis la référence DOT-{id immo}-{année}
            parts = entry.reference.split("-")
            if len(parts) >= 2:
                try:
                    immo_id = int(parts[1])
                    immo = db.query(Immobilisation).filter(Immobilisation.id == immo_id).first()
                    if immo and not entry.societe_id:
                        entry.societe_id = immo.societe_id
                        print(f"Populé societe_id={immo.societe_id} pour {entry.reference}")
                except ValueError:
                    pass
            
            if not entry.is_validated:
                entry.is_validated = True
                entry.validated_at = datetime.now()
                entry.validated_by = "system_fix"
                print(f"Validation de l'écriture : {entry.reference}")
            
        db.commit()
        print("Correction terminée avec succès.")
    except Exception as e:
        db.rollback()
        print(f"Erreur lors de la correction : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_dotations()
