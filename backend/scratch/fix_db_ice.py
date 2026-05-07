
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "backend"))
from database import SessionLocal
from models import Societe

db = SessionLocal()
try:
    s = db.query(Societe).first()
    if s:
        old_ice = s.ice
        s.ice = s.ice.strip()
        if len(s.ice) == 14:
            s.ice = "0" + s.ice
        db.commit()
        print(f"ICE updated from '{old_ice}' to '{s.ice}'")
    else:
        print("No society found.")
finally:
    db.close()
