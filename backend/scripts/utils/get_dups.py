import os
os.environ['DATABASE_URL'] = 'postgresql://admin:admin123@localhost:5454/compta_db'
from database import SessionLocal
from sqlalchemy import text

with SessionLocal() as db:
    query = text('''
        SELECT id, employe_id, mois, annee, salaire_brut, salaire_net, statut, created_at 
        FROM bulletins_paie 
        WHERE id IN (5, 6);
    ''')
    for row in db.execute(query).fetchall():
        print(dict(row._mapping))
