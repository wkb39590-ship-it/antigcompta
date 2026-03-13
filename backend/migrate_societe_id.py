from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE ecritures_journal ADD COLUMN societe_id INTEGER REFERENCES societes(id)"))
            conn.commit()
            print("Colonne societe_id ajoutée avec succès.")
        except Exception as e:
            print(f"Erreur (peut-être déjà existante) : {e}")

if __name__ == "__main__":
    migrate()
