from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# 1. Crear el cliente asíncrono usando la URL definida en el .env
client = AsyncIOMotorClient(settings.MONGODB_URL)

# 2. Conectar a la base de datos específica
database = client[settings.DATABASE_NAME]

# 3. Helpers para obtener colecciones específicas
def get_collection(collection_name: str):
    return database[collection_name]