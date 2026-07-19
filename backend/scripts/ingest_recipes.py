import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path so we can import app
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.db.models.recipe import Recipe, RecipeIngredient
from app.core.embeddings import embedding_service
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    mock_recipes = [
        {
            "id": "recipe_1",
            "title": "High Protein Greek Yogurt Bowl",
            "instructions": "Mix greek yogurt with protein powder, top with berries.",
            "prep_time_minutes": 5,
            "cook_time_minutes": 0,
            "servings": 1,
            "difficulty": "Easy",
            "cuisine": "Healthy",
            "dietary_tags": ["Vegetarian", "High Protein", "Gluten-Free"],
            "ingredients": [
                {"name": "Greek Yogurt", "quantity": 1, "unit": "cup", "calories": 150, "protein": 15},
                {"name": "Whey Protein", "quantity": 1, "unit": "scoop", "calories": 120, "protein": 24}
            ],
            "total_protein": 39,
            "total_calories": 270,
            "estimated_price": 120.0
        },
        {
            "id": "recipe_2",
            "title": "Vegan Lentil Curry",
            "instructions": "Simmer lentils with spices and coconut milk.",
            "prep_time_minutes": 10,
            "cook_time_minutes": 30,
            "servings": 4,
            "difficulty": "Medium",
            "cuisine": "Indian",
            "dietary_tags": ["Vegan", "High Protein"],
            "ingredients": [
                {"name": "Lentils", "quantity": 1, "unit": "cup", "calories": 230, "protein": 18},
                {"name": "Coconut Milk", "quantity": 0.5, "unit": "cup", "calories": 180, "protein": 2}
            ],
            "total_protein": 20,
            "total_calories": 410,
            "estimated_price": 250.0
        }
    ]
    
    db = SessionLocal()
    try:
        for r_data in mock_recipes:
            # Check if exists
            recipe = db.query(Recipe).filter(Recipe.id == r_data["id"]).first()
            if not recipe:
                recipe = Recipe(id=r_data["id"])
            
            recipe.title = r_data["title"]
            recipe.instructions = r_data["instructions"]
            recipe.prep_time_minutes = r_data["prep_time_minutes"]
            recipe.cook_time_minutes = r_data["cook_time_minutes"]
            recipe.servings = r_data["servings"]
            recipe.difficulty = r_data["difficulty"]
            recipe.cuisine = r_data["cuisine"]
            recipe.dietary_tags = r_data["dietary_tags"]
            
            # Embed
            doc = (
                f"Recipe: {r_data['title']}\n"
                f"Cuisine: {r_data['cuisine']}\n"
                f"Tags: {', '.join(r_data['dietary_tags'])}\n"
                f"Instructions: {r_data['instructions']}\n"
                f"Nutrition: {r_data['total_protein']}g protein, {r_data['total_calories']} calories"
            )
            embedding = embedding_service.embed_documents([doc])[0]
            recipe.embedding = embedding
            
            if not recipe.id in db:
                db.add(recipe)
                
        db.commit()
        logger.info(f"Successfully ingested {len(mock_recipes)} recipes.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
