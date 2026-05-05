import os
os.environ['DATABASE_URL'] = 'postgresql://admin:admin123@localhost:5454/compta_db'
from database import SessionLocal
from sqlalchemy import text

with SessionLocal() as db:
    with open('wissal_data.txt', 'w', encoding='utf-8') as f:
        f.write('BULLETINS:\n')
        q1 = text('SELECT id, employe_id, mois, annee, salaire_brut, statut FROM bulletins_paie;')
        for r in db.execute(q1):
            f.write(f"{dict(r._mapping)}\n")
            
        f.write('\nECRITURES:\n')
        q2 = text("SELECT id, journal_code, reference, description FROM ecritures_journal WHERE journal_code = 'OD';")
        for r in db.execute(q2):
            f.write(f"{dict(r._mapping)}\n")
