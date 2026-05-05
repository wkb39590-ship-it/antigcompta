import sys
import secrets
import hashlib
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Agent

def hash_password(password: str) -> str:
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"

def reset_agent_password(username: str, new_password: str):
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.username == username).first()
        if not agent:
            print(f"❌ Erreur: Agent '{username}' introuvable.")
            return

        agent.password_hash = hash_password(new_password)
        db.commit()
        print(f"✅ Succès: Le mot de passe de '{username}' a été mis à jour.")
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python reset_password.py <username> <nouveau_mot_de_passe>")
    else:
        reset_agent_password(sys.argv[1], sys.argv[2])
