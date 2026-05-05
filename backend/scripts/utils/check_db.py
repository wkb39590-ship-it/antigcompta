import sys
import os
os.environ["DATABASE_URL"] = "sqlite:///./backend/test.db"
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from database import SessionLocal
    from models import ReleveBancaire, LigneReleve
except ImportError:
    from backend.database import SessionLocal
    from backend.models import ReleveBancaire, LigneReleve

db = SessionLocal()
results = db.query(ReleveBancaire).all()
print(f"Total Relevés: {len(results)}")
for r in results:
    print(f"ID: {r.id}, Banque: {r.banque_nom}, Lignes: {len(r.lignes)}, Societe: {r.societe_id}")
db.close()
