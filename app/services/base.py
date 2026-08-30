from typing import TypeVar, Generic, Type, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.domain_exceptions import NotFoundError

# Type variables for SQLAlchemy models and Pydantic schemas
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for all business services (the "Central Sterilization").
    Provides common CRUD operations that can be extended or overridden by specific services.
    """

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
        
    async def get(self, id: Any) -> Optional[ModelType]:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_or_404(self, id: Any) -> ModelType:
        obj = await self.get(id)
        if not obj:
            raise NotFoundError(entity_name=self.model.__name__, entity_id=id)
        return obj

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        # Note: Assumes obj_in is a Pydantic schema
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        # The router or dependency handler performs the final commit,
        # but we can flush to get the ID if needed.
        await self.session.flush()
        return db_obj
