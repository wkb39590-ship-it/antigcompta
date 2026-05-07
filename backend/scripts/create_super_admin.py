"""
create_super_admin.py - Crée un super administrateur initial après une perte de données.
"""
import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire racine au path pour les imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database import SessionLocal, engine, Base
from models import Cabinet, Agent
from routes.auth import hash_password

load_dotenv()

def create_super_admin():
    db = SessionLocal()
    try:
        print("Verification des tables...")
        Base.metadata.create_all(bind=engine)
        
        # 2. Création d'un cabinet par défaut
        print("Creation du cabinet par défaut...")
        cabinet = db.query(Cabinet).filter(Cabinet.nom == "Cabinet Principal").first()
        if not cabinet:
            cabinet = Cabinet(
                nom="Cabinet Principal",
                email="admin@cabinet.ma"
            )
            db.add(cabinet)
            db.flush()
            print(f"Cabinet créé (ID: {cabinet.id})")
        else:
            print(f"Cabinet existe déjà (ID: {cabinet.id})")

        # 3. Récupération des infos du .env
        username = os.getenv("SUPER_ADMIN_USERNAME", "wissal")
        password = os.getenv("SUPER_ADMIN_PASSWORD", "password123")
        email = "wissal@expertise-cpt.ma" # Email par défaut si non spécifié

        print(f"Creation du Super Admin '{username}'...")
        agent = db.query(Agent).filter(Agent.username == username).first()
        
        if not agent:
            agent = Agent(
                cabinet_id=cabinet.id,
                username=username,
                email=email,
                password_hash=hash_password(password),
                nom="Bennani",
                prenom="Wissal",
                is_active=True,
                is_admin=True,
                is_super_admin=True
            )
            db.add(agent)
            print(f"Super Admin '{username}' créé avec succès.")
        else:
            # Mise à jour si déjà existant
            agent.password_hash = hash_password(password)
            agent.is_super_admin = True
            agent.is_admin = True
            print(f"L'agent '{username}' existe déjà. Son mot de passe et son statut Super Admin ont été mis à jour.")
        
        db.commit()
        print("Opération terminée avec succès !")
        print(f"Login: {username}")
        print(f"Password: {password}")

    except Exception as e:
        db.rollback()
        print(f"ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_super_admin()
