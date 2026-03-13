from database import engine
from sqlalchemy import inspect

def check_columns():
    inspector = inspect(engine)
    columns = inspector.get_columns('ecritures_journal')
    print("Colonnes dans 'ecritures_journal':")
    for column in columns:
        print(f"- {column['name']}")

if __name__ == "__main__":
    check_columns()
