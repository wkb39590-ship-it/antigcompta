





# ── Configuration de la Base de Données ──────────────────────────────────
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Récupération de l'URL de connexion depuis les variables d'environnement (.env ou Docker)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # Valeur par défaut pour le développement local si Postgres n'est pas lancé
    "sqlite:///./test.db"
)

# Création du moteur de base de données (Engine)
# future=True : utilise les fonctionnalités de SQLAlchemy 2.0
engine = create_engine(DATABASE_URL, future=True)

# Création de la fabrique de sessions (SessionLocal)
# On désactive l'autocommit et l'autoflush pour garder le contrôle sur les transactions
SessionLocal = sessionmaker(
    autocommit=False,     #commit pas automatique
    autoflush=False,      #flush pas automatique
    bind=engine,
    future=True,
)

# Classe de base pour tous les modèles ORM (Mappage colonnes -> objets)
Base = declarative_base()


# Fonction utilisée par FastAPI pour fournir une session de base de données
def get_db():

    # Création d'une nouvelle session (connexion temporaire à la base)
    db = SessionLocal()

    try:
        # On "donne" la session à la route FastAPI qui en a besoin
        # Le mot-clé yield permet de faire une pause ici
        # La route va s'exécuter avec cette session
        yield db

    finally:
        # Une fois que la route a fini (même en cas d'erreur),
        # on ferme la session pour libérer la connexion
        db.close()
