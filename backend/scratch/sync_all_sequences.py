from sqlalchemy import create_engine, MetaData, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:admin@127.0.0.1:5432/compta_db")

engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

def sync_all_sequences():
    with engine.begin() as conn:
        for table in metadata.sorted_tables:
            # Check if table has an 'id' column that uses a sequence
            if 'id' in table.columns:
                seq_name = f"{table.name}_id_seq"
                try:
                    # Execute a Postgres specific query to sync sequence
                    conn.execute(text(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX(id) FROM {table.name}), 1), max(id) IS NOT null) FROM {table.name};"))
                    print(f"✅ Séquence synchronisée pour la table : {table.name}")
                except Exception as e:
                    # If sequence doesn't exist or other error, just ignore
                    print(f"ℹ️ Pas de séquence classique pour {table.name} ou erreur ignorée.")

if __name__ == "__main__":
    print("🔄 Démarrage de la synchronisation de toutes les séquences...")
    sync_all_sequences()
    print("✅ Terminé !")
