from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Use connection pooling for production readiness
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    pool_pre_ping=True,      # Verify connections before usage
    pool_size=20,            # Max number of persistent connections
    max_overflow=10,         # Allow up to 10 extra temporary connections
    pool_recycle=1800        # Recycle connections after 30 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
