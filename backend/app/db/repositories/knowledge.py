from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.repositories.base import BaseRepository
from app.db.models.knowledge import Recipe, Ingredient, Substitution, RecipeIngredient

class KnowledgeRepository(BaseRepository[Recipe]):
    def __init__(self, db: Session):
        super().__init__(Recipe, db)

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        return self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        
    def get_recipes_by_cuisine(self, cuisine: str, limit: int = 5) -> List[Recipe]:
        return self.db.query(Recipe).filter(Recipe.cuisine == cuisine).limit(limit).all()

    def get_recipe_ingredients(self, recipe_id: int) -> List[tuple]:
        return self.db.query(Ingredient, RecipeIngredient.quantity, RecipeIngredient.unit, RecipeIngredient.is_optional)\
            .join(RecipeIngredient, Ingredient.id == RecipeIngredient.ingredient_id)\
            .filter(RecipeIngredient.recipe_id == recipe_id)\
            .all()

    def find_substitutions(self, ingredient_id: int, min_confidence: float = 0.5) -> List[tuple]:
        return self.db.query(Ingredient, Substitution.confidence)\
            .join(Substitution, Ingredient.id == Substitution.substitute_ingredient_id)\
            .filter(Substitution.ingredient_id == ingredient_id)\
            .filter(Substitution.confidence >= min_confidence)\
            .order_by(Substitution.confidence.desc())\
            .all()
