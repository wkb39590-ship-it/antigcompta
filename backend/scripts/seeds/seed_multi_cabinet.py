"""
seed_multi_cabinet.py - Initialise les donnees de test
Version corrigee avec les identifiants demandés : fati / fati123
"""
from dotenv import load_dotenv
import os
import sys
from sqlalchemy.orm import Session

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database import SessionLocal, engine, Base
from models import Cabinet, Agent, Societe, CompteurFacturation
from routes.auth import hash_password
from datetime import datetime

load_dotenv()

def seed_data():
    db = SessionLocal()
    try:
        print("1. Creation des cabinets...")
        cabinet1 = db.query(Cabinet).filter(Cabinet.nom == "Cabinet Expertise Comptable").first()
        if not cabinet1:
            cabinet1 = Cabinet(nom="Cabinet Expertise Comptable", email="contact@expertise-cpt.ma")
            db.add(cabinet1)
        
        db.flush()

        print("2. Creation des agents...")
        
        # Ton compte specifique : fati
        agent_fati = db.query(Agent).filter(Agent.username == "fati").first()
        if not agent_fati:
            agent_fati = Agent(
                cabinet_id=cabinet1.id,
                username="fati",
                email="fati@expertise-cpt.ma",
                password_hash=hash_password("fati123"),
                nom="Utilisateur",
                prenom="Fati",
                is_admin=False, # Passage en mode Agent simple
                is_super_admin=False
            )
            db.add(agent_fati)
        else:
            # Si le compte existe deja, on met a jour le mot de passe
            agent_fati.password_hash = hash_password("fati123")
            agent_fati.is_admin = True
            print("   -> Mise a jour du mot de passe pour fati")
        
        print("3. Creation des societes...")
        soc1 = db.query(Societe).filter(Societe.raison_sociale == "Entreprise de Test SARL").first()
        if not soc1:
            soc1 = Societe(
                cabinet_id=cabinet1.id,
                raison_sociale="Entreprise de Test SARL",
                ice="001234567890001"
            )
            db.add(soc1)
        
        db.flush()
        
        # Assignation de la societe a fati
        if soc1 not in agent_fati.societes:
            agent_fati.societes.append(soc1)
            
        db.commit()
        print("---")
        print("SUCCES : Base de donnes initialisee.")
        print("LOGIN : fati")
        print("PASSWORD : fati123")
        print("---")

    except Exception as e:
        db.rollback()
        print("ERREUR lors du seed : " + str(e))
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
