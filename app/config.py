from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Variables de PostgreSQL requeridas
    DATABASE_URL: str
    DATABASE_NAME: str = "farmacia_quirurgica_db"

    # Configuración para leer el archivo .env
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instancia global de la configuración
settings = Settings()