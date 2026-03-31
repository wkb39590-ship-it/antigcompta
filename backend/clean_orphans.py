import sys
sys.path.append(r'c:\Users\asus\Desktop\nv - Copie (antig)\backend')
from database import SessionLocal
from models import JournalEntry, LigneReleve, EntryLine

db = SessionLocal()
try:
    entries = db.query(JournalEntry).filter(
        JournalEntry.journal_code == 'BQ',
        JournalEntry.description.like('Rapprochement :%')
    ).all()
    
    orphans = 0
    for e in entries:
        linked = False
        for el in e.entry_lines:
            lr = db.query(LigneReleve).filter(LigneReleve.entry_line_id == el.id).first()
            if lr:
                linked = True
                break
        if not linked:
            db.delete(e)
            orphans += 1
            
    db.commit()
    print(f'CLEANUP DONE: {orphans} orphaned entries removed from journal.')
finally:
    db.close()
