import sys
sys.path.insert(0, '/app')
from database import SessionLocal
from models import ReleveBancaire, EntryLine, JournalEntry
from sqlalchemy import or_

def run():
    db = SessionLocal()
    releve_id = 20
    releve = db.query(ReleveBancaire).get(releve_id)
    out = {}
    for ligne in releve.lignes:
        amount_val = float(ligne.debit or 0.0) + float(ligne.credit or 0.0)
        if amount_val != 5600.0:
            continue
            
        q = db.query(EntryLine).join(JournalEntry).filter(
            or_(JournalEntry.societe_id == releve.societe_id, JournalEntry.societe_id == None),
            or_(EntryLine.debit == amount_val, EntryLine.credit == amount_val),
            or_(EntryLine.account_code.startswith('3'), EntryLine.account_code.startswith('4'), EntryLine.account_code.startswith('5'))
        )
        potential_matches = q.all()
        out[ligne.id] = f"Found {len(potential_matches)} potential matches"
        for m in potential_matches:
            out[f"{ligne.id}_matches"] = m.id
            
    import json
    with open('/app/uploads/debug3.json', 'w') as f:
        json.dump(out, f, indent=2)

if __name__ == '__main__':
    run()
