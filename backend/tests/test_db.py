from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg://admin:admin123@127.0.0.1:5433/compta_db"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1")).scalar()
    print("DB connection OK:", result)
