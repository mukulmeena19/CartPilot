from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base
from app.core.config import settings

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    brand = Column(String, index=True, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    price = Column(Float, nullable=False)
    unit = Column(String, nullable=False) # e.g., 'kg', 'g', 'liter', 'piece'
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Embedding for semantic search (e.g. text-embedding-3-small -> 1536 dims)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=True)
    
    # Embedding Metadata for Versioning and Explainability
    embedding_model = Column(String, nullable=True)
    embedding_version = Column(String, nullable=True)
    embedding_generated_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
