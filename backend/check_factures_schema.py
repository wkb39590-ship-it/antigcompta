from database import engine
from sqlalchemy import inspect

def check_factures_columns():
    inspector = inspect(engine)
    columns = inspector.get_columns('factures')
    print("Colonnes dans 'factures':")
    for column in columns:
        print(f"- {column['name']} ({column['type']})")

if __name__ == "__main__":
    check_factures_columns()
