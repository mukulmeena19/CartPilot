"""
Knowledge Layer models.
Forms the core of the Recipe -> Ingredient -> Product graph.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.config import settings
from app.db.base import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    cuisine = Column(String, nullable=True, index=True)
    
    prep_time = Column(Integer, nullable=True) # minutes
    cook_time = Column(Integer, nullable=True) # minutes
    servings = Column(Integer, nullable=True)
    
    # Nutritional info
    calories = Column(Float, nullable=True)
    
    # Semantic search
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    image_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    normalized_name = Column(String, nullable=False, index=True)  # e.g. "tomatoes, diced" -> "tomato"
    
    # Semantic search
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)

    # Relationships
    recipes = relationship("RecipeIngredient", back_populates="ingredient")
    substitutions_out = relationship("Substitution", foreign_keys="Substitution.ingredient_id", back_populates="ingredient")
    substitutions_in = relationship("Substitution", foreign_keys="Substitution.substitute_ingredient_id", back_populates="substitute")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    
    quantity = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    is_optional = Column(Boolean, default=False)
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="recipes")


class Substitution(Base):
    __tablename__ = "substitutions"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False, index=True)
    substitute_ingredient_id = Column(Integer, ForeignKey("ingredients.id"), nullable=False, index=True)
    
    confidence = Column(Float, default=1.0) # 0.0 to 1.0 scale
    notes = Column(Text, nullable=True)     # "Add 1tsp sugar to offset acidity"
    
    # Relationships
    ingredient = relationship("Ingredient", foreign_keys=[ingredient_id], back_populates="substitutions_out")
    substitute = relationship("Ingredient", foreign_keys=[substitute_ingredient_id], back_populates="substitutions_in")
