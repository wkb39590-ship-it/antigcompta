import os
from sqlalchemy import text
from database import engine, SessionLocal
from models import Agent, SupplierMapping, DocumentTransmis, Societe

def diag():
    print(f"DATABASE_URL Env: {os.getenv('DATABASE_URL')}")
    db = SessionLocal()
    try:
        print(f"Agents: {db.query(Agent).count()}")
        print(f"Mappings: {db.query(SupplierMapping).count()}")
        print(f"Docs: {db.query(DocumentTransmis).count()}")
        print(f"Societes: {db.query(Societe).count()}")
        
        # Check first societe
        soc = db.query(Societe).first()
        if soc:
            print(f"First Soc: {soc.raison_sociale} (ID: {soc.id})")
        else:
            print("No societe found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    diag()
