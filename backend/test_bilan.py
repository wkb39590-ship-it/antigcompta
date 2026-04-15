from database import SessionLocal
from services.accounting_service import AccountingService
from decimal import Decimal

def test_bilan():
    db = SessionLocal()
    try:
        # On cherche une société qui a des écritures
        from models import JournalEntry
        first_entry = db.query(JournalEntry).first()
        if not first_entry:
            print("Aucune écriture trouvée en base pour tester.")
            return

        societe_id = first_entry.societe_id
        annee = first_entry.entry_date.year

        print(f"--- Test Bilan pour Société {societe_id} en {annee} ---")
        
        bilan = AccountingService.get_bilan_comptable(db, societe_id, annee, validated_only=False)
        
        print(f"Résultat de l'exercice : {bilan['resultat']} MAD")
        print(f"Total Actif : {bilan['total_actif']} MAD")
        print(f"Total Passif (avec résultat) : {bilan['total_passif']} MAD")
        
        if bilan['is_balanced']:
            print("[\u2705] Le bilan est équilibré !")
        else:
            print("[\u274c] ERREUR : Le bilan n'est pas équilibré.")
            print(f"Différence : {bilan['total_actif'] - bilan['total_passif']}")

    finally:
        db.close()

if __name__ == "__main__":
    test_bilan()
