import sys
sys.path.append(r'c:\Users\asus\Desktop\nv - Copie (antig)\backend')
from database import SessionLocal
from models import LigneReleve
from routes.releves import get_suggestions

db = SessionLocal()
session = {'societe_id': 1}
lignes = db.query(LigneReleve).limit(20).all()

for l in lignes:
    try:
        get_suggestions(l.id, db, session)
        print(f"Line {l.id} OK (desc: {l.description})")
    except Exception as e:
        print(f"Line {l.id} FAILED (desc: {l.description}): {e}")
        import traceback
        traceback.print_exc()

db.close()
