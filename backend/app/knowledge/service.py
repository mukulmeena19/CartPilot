"""
Knowledge Graph Service.
Provides APIs for traversing Recipes, Ingredients, and Substitutions.
"""
from __future__ import annotations

import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.db.models.knowledge import Recipe, Ingredient, RecipeIngredient, Substitution

logger = logging.getLogger(__name__)


class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        return self.db.query(Recipe).filter(Recipe.id == recipe_id).first()

    def search_recipes(self, query: str, limit: int = 10) -> List[Recipe]:
        """Basic keyword search. Real implementation will use pgvector hybrid search."""
        search_pattern = f"%{query}%"
        return (
            self.db.query(Recipe)
            .filter(or_(
                Recipe.name.ilike(search_pattern),
                Recipe.cuisine.ilike(search_pattern)
            ))
            .limit(limit)
            .all()
        )

    def get_recipe_ingredients(self, recipe_id: int) -> List[Tuple[Ingredient, RecipeIngredient]]:
        """Returns the list of ingredients and their required quantities for a recipe."""
        results = (
            self.db.query(Ingredient, RecipeIngredient)
            .join(RecipeIngredient, Ingredient.id == RecipeIngredient.ingredient_id)
            .filter(RecipeIngredient.recipe_id == recipe_id)
            .all()
        )
        return results

    def get_substitutions(self, ingredient_id: int, min_confidence: float = 0.5) -> List[Tuple[Ingredient, Substitution]]:
        """Finds valid substitutions for a given ingredient."""
        results = (
            self.db.query(Ingredient, Substitution)
            .join(Substitution, Ingredient.id == Substitution.substitute_ingredient_id)
            .filter(Substitution.ingredient_id == ingredient_id)
            .filter(Substitution.confidence >= min_confidence)
            .order_by(Substitution.confidence.desc())
            .all()
        )
        return results

    def expand_ingredients(self, ingredient_ids: List[int]) -> List[int]:
        """
        Given a list of ingredient IDs, returns a broader list including common substitutions.
        Used by the Workflow Engine to maximize retrieval hit rate.
        """
        expanded = set(ingredient_ids)
        for i_id in ingredient_ids:
            subs = self.get_substitutions(i_id, min_confidence=0.7)
            for sub_ingredient, _ in subs:
                expanded.add(sub_ingredient.id)
        return list(expanded)
