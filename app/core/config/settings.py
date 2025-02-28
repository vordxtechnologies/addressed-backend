from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Addressed API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Firebase
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY_ID: str
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_CLIENT_ID: str
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_TIMEOUT: int = 5
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "doc", "docx"]
    
    # Hugging Face
    HUGGINGFACE_API_KEY: str
    HUGGINGFACE_MODEL_CACHE: str = "./model_cache"
    
    # Anthropic Claude
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-opus-20240229"
    CLAUDE_MAX_TOKENS: int = 4096
    CLAUDE_TIMEOUT: int = 30
    
    # Amazon API
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    AMAZON_MARKETPLACE: str = "www.amazon.com"
    AMAZON_PARTNER_TAG: str
    AWS_MAX_RETRIES: int = 3
    
    # ChromaDB
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000
    CHROMADB_API_KEY: Optional[str] = None
    CHROMADB_SSL_ENABLED: bool = False
    CHROMADB_MAX_BATCH_SIZE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 5
    RATE_LIMIT_ENABLED: bool = True
    
    # Feature Flags
    ENABLE_AI_FEATURES: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_METRICS: bool = True
    
    # Performance
    REQUEST_TIMEOUT: int = 30
    MAX_WORKERS: int = 4
    KEEP_ALIVE: int = 5
    
    # Cache Settings
    CACHE_TTL: int = 3600
    CACHE_PREFIX: str = "addressed:"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"
        
    @property
    def firebase_credentials(self) -> Dict[str, Any]:
        """Get Firebase credentials as dictionary"""
        if self.FIREBASE_CREDENTIALS_PATH:
            if not os.path.exists(self.FIREBASE_CREDENTIALS_PATH):
                raise ValueError(f"Firebase credentials file not found: {self.FIREBASE_CREDENTIALS_PATH}")
            return Path(self.FIREBASE_CREDENTIALS_PATH).read_text()
            
        return {
            "type": "service_account",
            "project_id": self.FIREBASE_PROJECT_ID,
            "private_key_id": self.FIREBASE_PRIVATE_KEY_ID,
            "private_key": self.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
            "client_email": self.FIREBASE_CLIENT_EMAIL,
            "client_id": self.FIREBASE_CLIENT_ID
        }
        
    def validate_settings(self) -> None:
        """Validate critical settings"""
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set")
            
        if not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY must be set")
            
        if not self.AWS_ACCESS_KEY_ID or not self.AWS_SECRET_ACCESS_KEY:
            raise ValueError("AWS credentials must be set")
            
        if self.ENVIRONMENT not in ["development", "staging", "production"]:
            raise ValueError("Invalid ENVIRONMENT value")

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_settings()
    return settings

settings = get_settings()