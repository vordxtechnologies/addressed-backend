from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Addressed API"
    API_V1_STR: str = "/api/v1"
    GOOGLE_APPLICATION_CREDENTIALS: str
    FIREBASE_CREDENTIALS_PATH: str = "addressed-firebase-adminsdk.json"
    SECRET_KEY: str 
    REDIS_URL: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    HUGGINGFACE_API_KEY: str
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()