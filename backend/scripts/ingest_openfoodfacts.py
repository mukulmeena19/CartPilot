import sys
import os
import json
import logging
from pathlib import Path

# Add backend to path so we can import app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.ingestion.services import OpenFoodFactsIngestionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # For a real run, this would be a large JSON file downloaded from Open Food Facts
    # e.g., 'data/openfoodfacts_dump.json'
    # We will use a mock structure here to demonstrate the pipeline
    
    mock_data = {
        "products": [
            {
                "_id": "1234567890",
                "product_name": "Greek Yogurt",
                "brands": "Amul",
                "categories": "Dairy, Yogurts",
                "image_url": "https://example.com/yogurt.jpg",
                "nutriments": {
                    "proteins_100g": 18.0,
                    "energy-kcal_100g": 120.0,
                    "carbohydrates_100g": 5.0,
                    "fat_100g": 2.0
                },
                "quantity": "200g"
            },
            {
                "_id": "0987654321",
                "product_name": "Protein Bar",
                "brands": "MuscleBlaze",
                "categories": "Snacks, Supplements",
                "image_url": "https://example.com/protein_bar.jpg",
                "nutriments": {
                    "proteins_100g": 20.0,
                    "energy-kcal_100g": 250.0,
                    "carbohydrates_100g": 30.0,
                    "fat_100g": 8.0
                },
                "quantity": "50g"
            },
            {
                # Invalid product (missing image and category)
                "_id": "111111111",
                "product_name": "Mysterious item",
            }
        ]
    }
    
    # Alternatively, load from file if provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                logger.info(f"Loading data from {file_path}")
                mock_data = json.load(f)
                
    db = SessionLocal()
    try:
        service = OpenFoodFactsIngestionService(db)
        service.run(mock_data)
    finally:
        db.close()

if __name__ == "__main__":
    main()
