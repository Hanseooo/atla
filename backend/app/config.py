from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    ENVIRONMENT: str = "development"
    SECRET_KEY: str

    # Database URLs (both required)
    DEV_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/atla_db"
    PROD_DATABASE_URL: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # APIs
    GOOGLE_API_KEY: str
    BRAVE_API_KEY: str

    # Cache
    REDIS_URL: str

    # CORS (comma-separated string, parsed into list)
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    @property
    def ALLOWED_ORIGINS_LIST(self) -> List[str]:
        """Parse comma-separated origins into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def DATABASE_URL(self) -> str:
        """Return the appropriate database URL based on environment"""
        if self.ENVIRONMENT.lower() == "production":
            return self.PROD_DATABASE_URL
        return self.DEV_DATABASE_URL


settings = Settings()
