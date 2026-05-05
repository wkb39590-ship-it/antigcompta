import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://admin:admin123@db:5432/compta_db")
engine = create_engine(DATABASE_URL)

def fix():
    print("--- Adding facture_id to documents_transmis ---")
    with engine.connect() as conn:
        # 1. Check if column exists
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='documents_transmis' AND column_name='facture_id'")).fetchone()
        if not res:
            print("Adding column facture_id...")
            conn.execute(text("ALTER TABLE documents_transmis ADD COLUMN facture_id INTEGER REFERENCES factures(id)"))
            conn.commit()
            print("✅ Column added.")
        else:
            print("ℹ️ Column already exists.")
            
    print("--- Schema Sync ---")
    from database import Base
    import models
    Base.metadata.create_all(bind=engine)
    print("✅ All tables checked.")

if __name__ == "__main__":
    fix()
