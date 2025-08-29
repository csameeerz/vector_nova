from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    APP_NAME: str = "Vector Nova"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    ALLOWED_ORIGINS: List[str] = ["*"]  # In production, specify actual origins
    
    DATABASE_URL: str = "sqlite:///./vector_nova.db"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    VECTOR_DB_URL: str = "http://localhost:6333"  # Qdrant default
    VECTOR_DB_API_KEY: str = ""
    
    LLM_PROVIDER: str = "openai"  # openai, anthropic, local
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-3.5-turbo"
    
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 1536
    
    RATE_LIMIT_PER_MINUTE: int = 60
    
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".txt", ".docx", ".md"]
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/vector_nova.log"
    
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
