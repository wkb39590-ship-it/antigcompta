from database import SessionLocal
from models import JournalEntry, JournalComptable, EntryLine
import sys

def fix():
    db = SessionLocal()
    try:
        # Fix JournalEntry societe_id
        count = db.query(JournalEntry).filter(JournalEntry.societe_id == None).update({JournalEntry.societe_id: 1})
        print(f"Fixed {count} JournalEntry records.")
        
        # Verify journals
        journals = db.query(JournalComptable).filter(JournalComptable.societe_id == 1).all()
        print(f"Found {len(journals)} journals for societe_id=1")
        for j in journals:
            print(f"  - {j.code}: {j.label}")
            
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix()
