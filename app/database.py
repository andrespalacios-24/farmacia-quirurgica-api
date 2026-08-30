from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# 1. Create the asynchronous engine using the PostgreSQL URL from .env
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True  # Show SQL queries in the console during development
)

# 2. Create the asynchronous session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Base class to define all your models (tables) in app/models
class Base(DeclarativeBase):
    pass
