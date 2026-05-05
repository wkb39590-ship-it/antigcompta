import sys
sys.path.append(r'c:\Users\asus\Desktop\nv - Copie (antig)\backend')
from routes.releves import get_suggestions
from database import SessionLocal

def test():
    db = SessionLocal()
    session = {'societe_id': 1}
    try:
        print("Calling get_suggestions(101)....")
        res = get_suggestions(101, db, session)
        print("SUCCESS:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    test()
