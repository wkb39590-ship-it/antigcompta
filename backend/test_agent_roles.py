from database import SessionLocal
from models import Agent

db = SessionLocal()
try:
    agent = db.query(Agent).filter(Agent.id == 1).first()
    if agent:
        print(f"Agent: {agent.username}")
        print(f"is_admin: {agent.is_admin} (type: {type(agent.is_admin)})")
        print(f"is_super_admin: {agent.is_super_admin} (type: {type(agent.is_super_admin)})")
    else:
        print("Agent 1 non trouvé")
finally:
    db.close()
