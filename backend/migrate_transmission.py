import os
from database import engine, Base
import models

def migrate():
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    migrate()
