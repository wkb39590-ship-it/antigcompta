from database import engine
from sqlalchemy import text

def migrate():
    columns = [
        ('matricule', 'VARCHAR(20)'),
        ('situation_familiale', 'VARCHAR(50)'),
        ('adresse', 'VARCHAR(500)'),
        ('departement', 'VARCHAR(100)'),
        ('numero_mutuelle', 'VARCHAR(30)'),
        ('numero_retraite', 'VARCHAR(30)')
    ]
    
    with engine.connect() as conn:
        for col_name, col_type in columns:
            try:
                # PostgreSQL syntax for adding column if it doesn't exist
                conn.execute(text(f"ALTER TABLE employes ADD COLUMN {col_name} {col_type}"))
                print(f"Colonne {col_name} ajoutée.")
            except Exception as e:
                print(f"Colonne {col_name} existe déjà ou erreur : {e}")
        conn.commit()
    print("Migration terminée !")

if __name__ == "__main__":
    migrate()
