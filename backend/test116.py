import sys
sys.path.append(r'c:\Users\asus\Desktop\nv - Copie (antig)\backend')
from routes.releves import get_suggestions
from database import SessionLocal

db = SessionLocal()
session = {'societe_id': 1}
try:
    print("Testing get_suggestions for 116...")
    res = get_suggestions(116, db, session)
    print("SUCCESS: length =", len(res))
except Exception as e:
    print("FAILED:", e)
    import traceback
    traceback.print_exc()
finally:
    db.close()
