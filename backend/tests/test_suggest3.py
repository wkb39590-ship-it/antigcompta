import sys
sys.path.append(r'c:\Users\asus\Desktop\nv - Copie (antig)\backend')
from database import SessionLocal
from models import LigneReleve, ReleveBancaire, JournalEntry, EntryLine
from routes.releves import get_suggestions
import datetime

db = SessionLocal()
try:
    # 1. Create fake data
    rb = ReleveBancaire(societe_id=1, date_debut=datetime.date(2024, 7, 1))
    db.add(rb)
    db.flush()
    
    lr = LigneReleve(releve_id=rb.id, date_operation=datetime.date(2024, 7, 31), description='TAXE SUR VALEUR AJOUTEE', credit=9.90, debit=0)
    db.add(lr)
    db.flush()
    
    je = JournalEntry(societe_id=1, journal_code='BQ', entry_date=datetime.date(2024, 7, 31), description='TEST JE', reference='123')
    db.add(je)
    db.flush()
    
    el = EntryLine(ecriture_journal_id=je.id, account_code='345520', debit=0, credit=9.90)
    db.add(el)
    db.commit()
    
    # 2. Test
    try:
        session = {'societe_id': 1}
        print("Running suggestions for id:", lr.id)
        res = get_suggestions(lr.id, db, session)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
        
finally:
    db.rollback()
    # clean up
    db.query(LigneReleve).filter(LigneReleve.id == lr.id).delete()
    db.query(ReleveBancaire).filter(ReleveBancaire.id == rb.id).delete()
    db.query(EntryLine).filter(EntryLine.id == el.id).delete()
    db.query(JournalEntry).filter(JournalEntry.id == je.id).delete()
    db.commit()
    db.close()
