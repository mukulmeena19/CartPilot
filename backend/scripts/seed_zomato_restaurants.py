import os
import sys
import pandas as pd
import structlog
import json
from sqlalchemy.orm import Session

# Add backend to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.models.restaurant import Restaurant, MenuItem

logger = structlog.get_logger(__name__)

RAW_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "zomato_restaurants_in_India.csv")

PLACEHOLDER_IMAGES = {
    "north indian": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?q=80&w=600&auto=format&fit=crop",
    "south indian": "https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?q=80&w=600&auto=format&fit=crop",
    "chinese": "https://images.unsplash.com/photo-1552611052-33e04de081de?q=80&w=600&auto=format&fit=crop",
    "italian": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?q=80&w=600&auto=format&fit=crop",
    "fast food": "https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=600&auto=format&fit=crop",
    "desserts": "https://images.unsplash.com/photo-1551024601-bec78aea704b?q=80&w=600&auto=format&fit=crop",
    "default": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?q=80&w=600&auto=format&fit=crop"
}

def get_image_for_cuisines(cuisines: list[str]) -> str:
    if not cuisines:
        return PLACEHOLDER_IMAGES["default"]
    
    first_cuisine = cuisines[0].lower()
    for key, url in PLACEHOLDER_IMAGES.items():
        if key in first_cuisine:
            return url
    return PLACEHOLDER_IMAGES["default"]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def process_restaurants():
    if not os.path.exists(RAW_DATA_PATH):
        logger.error(f"Path not found: {RAW_DATA_PATH}")
        return

    logger.info("Loading Zomato dataset...")
    df = pd.read_csv(RAW_DATA_PATH)
    
    # Filter to Mumbai, New Delhi, Bangalore
    target_cities = ["Mumbai", "New Delhi", "Bangalore"]
    df = df[df['city'].isin(target_cities)]
    
    logger.info(f"Found {len(df)} restaurants in {target_cities}.")
    
    db = next(get_db())
    inserted = 0
    
    # Clear existing to prevent duplicates if ran multiple times
    logger.info("Clearing existing restaurants and menu items...")
    db.query(MenuItem).delete()
    db.query(Restaurant).delete()
    db.commit()

    for idx, row in df.iterrows():
        cuisines_str = str(row.get('cuisines', ''))
        cuisine_list = [c.strip() for c in cuisines_str.split(',') if c.strip()]
        
        rating = 0.0
        try:
            rating = float(row.get('aggregate_rating', 0.0))
        except:
            pass
            
        votes = 0
        try:
            votes = int(row.get('votes', 0))
        except:
            pass
            
        lat = 0.0
        try:
            lat = float(row.get('latitude', 0.0))
        except:
            pass
            
        lon = 0.0
        try:
            lon = float(row.get('longitude', 0.0))
        except:
            pass
            
        avg_cost = 0.0
        try:
            avg_cost = float(row.get('average_cost_for_two', 0.0))
        except:
            pass

        r = Restaurant(
            name=str(row.get('name', 'Unknown')),
            address=str(row.get('address', '')),
            city=str(row.get('city', '')),
            latitude=lat,
            longitude=lon,
            cuisine_tags=cuisine_list,
            rating=rating,
            total_ratings=votes,
            image_url=get_image_for_cuisines(cuisine_list),
            is_active=True
        )
        
        db.add(r)
        inserted += 1
        
        if inserted % 1000 == 0:
            logger.info(f"Inserted {inserted} restaurants...")
            db.commit()

    db.commit()
    logger.info(f"Finished inserting {inserted} Zomato restaurants!")
    
    # Save a mapping of restaurant names to average cost for two for the menu generator
    mapping = {}
    for idx, row in df.iterrows():
        try:
            cost = float(row.get('average_cost_for_two', 0.0))
            mapping[str(row.get('name', 'Unknown'))] = cost
        except:
            pass
            
    mapping_path = os.path.join(os.path.dirname(RAW_DATA_PATH), "restaurant_costs.json")
    with open(mapping_path, "w") as f:
        json.dump(mapping, f)
    logger.info(f"Saved average cost mapping to {mapping_path}")

if __name__ == "__main__":
    process_restaurants()
