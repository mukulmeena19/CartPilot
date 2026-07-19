from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "CartPilot API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: str = "cartpilot"
    POSTGRES_PASSWORD: str = "cartpilot_password"
    POSTGRES_DB: str = "cartpilot_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    SECRET_KEY: str = "a-very-secure-secret-key-for-cartpilot-mvp"  # Should be overridden in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    
    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # or 'models/text-embedding-004' for production
    EMBEDDING_DIMENSION: int = 384  # 384 for MiniLM, 768 for Gemini
    
    # Feature Flags
    FEATURE_GROCERY: bool = True
    FEATURE_RESTAURANT: bool = False
    FEATURE_GRAPH: bool = False
    FEATURE_AI: bool = True
    FEATURE_EXPLAINABILITY: bool = True

    DATABASE_URL: str | None = None

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
