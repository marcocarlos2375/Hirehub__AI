from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    DATABASE_URL: str = "sqlite:////app/data/hirehub.db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
