from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# 1. Crear el motor asíncrono usando la URL de PostgreSQL del .env
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True  # Muestra los queries SQL en la consola durante desarrollo
)

# 2. Crear la fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Clase Base para definir todos tus modelos (tablas) en app/models
class Base(DeclarativeBase):
    pass

