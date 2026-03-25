import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://admin:admin123@db:5432/compta_db")
engine = create_engine(DATABASE_URL)

def check_docs():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, societe_id, file_name, statut FROM documents_transmis")).fetchall()
        print("--- Documents Transmis ---")
        for r in res:
            print(f"ID: {r.id} | SocID: {r.societe_id} | Name: {r.file_name} | Statut: '{r.statut}'")

if __name__ == "__main__":
    check_docs()
