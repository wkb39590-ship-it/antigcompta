import sqlalchemy
from sqlalchemy import create_engine

passwords = ["admin", "admin123", "postgres", "root", "password", "fati", "fati123", "123456", "adminadmin"]
users = ["postgres", "admin"]
port = 5432
db_name = "compta_db"

print("Démarrage du test des mots de passe...")

for user in users:
    for pwd in passwords:
        url = f"postgresql+psycopg2://{user}:{pwd}@127.0.0.1:{port}/{db_name}"
        try:
            engine = create_engine(url, connect_args={'connect_timeout': 2})
            with engine.connect() as conn:
                print(f"SUCCÈS ! L'utilisateur est '{user}' et le mot de passe est '{pwd}'")
                exit(0)
        except Exception:
            continue

print("Aucun mot de passe trouvé dans la liste standard.")
