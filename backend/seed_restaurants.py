from main import app
from app.db.session import SessionLocal
from app.tasks.etl_restaurant import generate_restaurants
from app.tasks.etl_restaurant import generate_restaurants

if __name__ == "__main__":
    db = SessionLocal()
    try:
        generate_restaurants(db)
        print("Successfully generated synthetic restaurants")
    finally:
        db.close()
