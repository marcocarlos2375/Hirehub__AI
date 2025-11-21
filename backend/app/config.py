from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600  # 1 hour in seconds
    DATABASE_URL: str = "sqlite:////app/data/hirehub.db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    GEMINI_TIMEOUT: int = 20  # 20 seconds timeout for Gemini API calls
    GEMINI_MAX_RETRIES: int = 0  # No retries - fail fast (Gemini API is highly reliable)

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
