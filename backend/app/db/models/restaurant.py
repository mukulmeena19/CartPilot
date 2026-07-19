"""
Restaurant and MenuItem models.
Supports the Food Ordering domain.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Location
    address = Column(String, nullable=True)
    city = Column(String, nullable=True, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Operations
    is_active = Column(Boolean, default=True, nullable=False)
    is_open = Column(Boolean, default=True, nullable=False)
    delivery_time_estimate = Column(Integer, nullable=True)   # minutes
    minimum_order = Column(Float, nullable=True)
    delivery_fee = Column(Float, default=0.0)

    # Quality signals
    rating = Column(Float, nullable=True)
    total_ratings = Column(Integer, default=0)

    # Tags for fast filtering
    cuisine_tags = Column(JSON, default=list)   # ["Indian", "North Indian"]
    dietary_tags = Column(JSON, default=list)   # ["Vegetarian", "Vegan"]

    # Semantic search
    embedding = Column(Vector(1536), nullable=True)

    image_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)

    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    # Classification
    category = Column(String, nullable=True, index=True)   # "Main Course", "Beverages"
    cuisine = Column(String, nullable=True, index=True)

    # Dietary signals
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    spice_level = Column(Integer, nullable=True)            # 0-5

    # Nutrition (optional, populated by Data Platform)
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)

    # Tags & discounts
    tags = Column(JSON, default=list)
    discount_percent = Column(Float, default=0.0)

    # Semantic search
    embedding = Column(Vector(1536), nullable=True)

    image_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    restaurant = relationship("Restaurant", back_populates="menu_items")
