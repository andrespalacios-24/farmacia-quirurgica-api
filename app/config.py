from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Variables requeridas con su tipo de dato
    MONGODB_URL: str
    DATABASE_NAME: str = "farmacia_quirurgica"

    # Configuracion para leer el archivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instancia global de la configuración
settings = Settings()