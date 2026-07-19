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
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
