from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import structlog
from app.db.repositories.knowledge import KnowledgeRepository

logger = structlog.get_logger(__name__)

class KnowledgeService:
    def __init__(self, db: Session):
        self.repo = KnowledgeRepository(db)

    def get_recipe(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a recipe node and its core properties.
        """
        try:
            recipe = self.repo.get_recipe_by_id(recipe_id)
            if not recipe:
                return None
            return {
                "id": recipe.id,
                "name": recipe.name,
                "cuisine": recipe.cuisine,
                "dietary_tags": recipe.dietary_tags if hasattr(recipe, 'dietary_tags') else [],
                "difficulty": recipe.difficulty if hasattr(recipe, 'difficulty') else "medium"
            }
        except Exception as e:
            logger.error("Failed to retrieve recipe", error=str(e), recipe_id=recipe_id)
            return None

    def get_recipe_ingredients(self, recipe_id: int) -> List[Dict[str, Any]]:
        """
        Traverses from Recipe -> RecipeIngredient -> Ingredient to get the required components.
        """
        try:
            results = self.repo.get_recipe_ingredients(recipe_id)
            
            ingredients = []
            for ingredient, qty, unit, is_opt in results:
                ingredients.append({
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "quantity": qty,
                    "unit": unit,
                    "is_optional": is_opt
                })
            return ingredients
        except Exception as e:
            logger.error("Failed to retrieve recipe ingredients", error=str(e), recipe_id=recipe_id)
            return []

    def find_substitutions(self, original_ingredient_id: int, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """
        Traverses Ingredient -> Substitution -> Ingredient to find valid replacements.
        """
        try:
            results = self.repo.find_substitutions(original_ingredient_id, min_confidence)
            
            subs = []
            for substitute, confidence in results:
                subs.append({
                    "id": substitute.id,
                    "name": substitute.name,
                    "confidence": confidence
                })
            return subs
        except Exception as e:
            logger.error("Failed to find substitutions", error=str(e), ingredient_id=original_ingredient_id)
            return []

    def expand_ingredients(self, ingredient_ids: List[int]) -> List[int]:
        """
        Given a list of ingredient IDs, returns a broader list including common substitutions.
        Used by the Workflow Engine to maximize retrieval hit rate.
        """
        expanded = set(ingredient_ids)
        for i_id in ingredient_ids:
            # Add substitutions with high confidence
            subs = self.find_substitutions(i_id, min_confidence=0.7)
            for sub in subs:
                expanded.add(sub["id"])
        return list(expanded)
