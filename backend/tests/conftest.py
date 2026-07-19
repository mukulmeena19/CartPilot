import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
# Import all models so Base metadata is populated
from app.db.models.user import User
from app.db.models.product import Product
from app.db.models.restaurant import Restaurant, MenuItem
from app.db.models.knowledge import Recipe, Ingredient
from app.db.models.intelligence import TasteProfile
from app.db.models.analytics import AnalyticsEvent

import os
# Force MockProvider for all unit tests to avoid API key requirements
os.environ["LLM_PROVIDER"] = "mock"

# Use an in-memory SQLite database for fast unit tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    # Setup the database
    Base.metadata.create_all(bind=engine)
    yield engine
    # Teardown the database
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Returns a fresh sqlalchemy session for each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
