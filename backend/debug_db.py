from database import SessionLocal
from models import EntryLine, JournalEntry, Facture
import json

def run():
    db = SessionLocal()
    try:
        results = db.query(EntryLine).join(JournalEntry).filter((EntryLine.credit == 5600) | (EntryLine.debit == 5600)).all()
        out = []
        for r in results:
            j = r.journal_entry
            row = {
                'id': r.id, 
                'debit': float(r.debit) if r.debit else 0, 
                'credit': float(r.credit) if r.credit else 0, 
                'account': r.account_code, 
                'societe_id': j.societe_id, 
                'date': str(j.entry_date)
            }
            if j.facture_id:
                f = db.query(Facture).get(j.facture_id)
                row['facture_id'] = j.facture_id
                row['numero'] = f.numero_facture
            out.append(row)
        with open('debug_res.json', 'w') as f:
            json.dump(out, f, indent=2)
    except Exception as e:
        with open('debug_res.json', 'w') as f:
            f.write(str(e))
    finally:
        db.close()

if __name__ == '__main__':
    run()
