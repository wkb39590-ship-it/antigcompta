from database import SessionLocal
from models import JournalEntry

def list_entries():
    db = SessionLocal()
    entries = db.query(JournalEntry).all()
    print(f"Total écritures: {len(entries)}")
    for e in entries:
        print(f"ID: {e.id} | Journal: {e.journal_code} | Ref: {e.reference} | Validé: {e.is_validated}")
    db.close()

if __name__ == "__main__":
    list_entries()
