"""
Application configuration using Pydantic Settings.

Reads configuration from environment variables and .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Create a .env file in the backend directory with required values.
    See .env.example for reference.
    """
    
    # Application
    APP_NAME: str = "ACE Platform"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    
    # Security - JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173, http://localhost:80"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # File Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    # Allowed file extensions
    ALLOWED_AUDIO_EXTENSIONS: str = ".mp3,.wav,.m4a,.ogg"
    ALLOWED_IMAGE_EXTENSIONS: str = ".jpg,.jpeg,.png,.gif,.webp"
    
    @property
    def audio_extensions(self) -> set:
        """Parse audio extensions."""
        return set(ext.strip() for ext in self.ALLOWED_AUDIO_EXTENSIONS.split(","))
    
    @property
    def image_extensions(self) -> set:
        """Parse image extensions."""
        return set(ext.strip() for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(","))
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()


# Validate critical settings on import
def validate_settings():
    """Validate that critical settings are properly configured."""
    errors = []
    
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY must be at least 32 characters long")
    
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL is required")
    
    if errors:
        raise ValueError(
            "Configuration errors:\n" + "\n".join(f"  - {err}" for err in errors)
        )


# Run validation on import
validate_settings()
