import asyncio
from sqlalchemy import text
from database import SessionLocal

def check_duplicates():
    with SessionLocal() as db:
        query = text("""
            SELECT b.id, b.employe_id, e.nom, e.prenom, b.mois, b.annee, b.salaire_brut, b.salaire_net, b.statut 
            FROM bulletins_paie b 
            JOIN employes e ON b.employe_id = e.id 
            WHERE e.nom ILIKE '%kibali%' 
            ORDER BY b.annee, b.mois, b.id;
        """)
        result = db.execute(query).fetchall()
        for row in result:
            print(dict(row._mapping))

if __name__ == "__main__":
    check_duplicates()
