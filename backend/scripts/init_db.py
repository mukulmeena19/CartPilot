import os
import sqlalchemy
import subprocess

DB_URL = "postgresql://postgres:romy%40sona190718@db.qzuunubeuirxgysabkge.supabase.co:5432/postgres"

def main():
    print("Enabling vector extension...")
    engine = sqlalchemy.create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    print("Vector extension enabled!")
    
    # Set env var for alembic and seed
    os.environ["DATABASE_URL"] = DB_URL
    os.environ["LLM_PROVIDER"] = "mock"
    
    print("Running seed script...")
    subprocess.run(["uv", "run", "python", "scripts/seed_catalog.py"], check=True)
    
    print("Database initialization complete!")

if __name__ == "__main__":
    main()
