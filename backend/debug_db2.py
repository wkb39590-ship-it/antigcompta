from database import SessionLocal
from models import JournalEntry
import json

def run():
    db = SessionLocal()
    try:
        j = db.query(JournalEntry).filter(JournalEntry.facture_id == 30).first()
        out = {"desc": j.description, "ref": j.reference}
        with open('debug_res2.json', 'w') as f:
            json.dump(out, f, indent=2)
    except Exception as e:
        with open('debug_res2.json', 'w') as f:
            f.write(str(e))
    finally:
        db.close()

if __name__ == '__main__':
    run()
