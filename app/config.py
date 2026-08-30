from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Required PostgreSQL variables
    DATABASE_URL: str
    DATABASE_NAME: str = "farmacia_quirurgica_db"

    # Authentication configuration (JWT)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 720

    # Configuration for reading the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Global settings instance
settings = Settings()