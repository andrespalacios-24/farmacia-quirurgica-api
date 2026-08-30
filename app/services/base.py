from typing import TypeVar, Generic, Type, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.domain_exceptions import NotFoundError

# Type variables para modelos SQLAlchemy y esquemas Pydantic
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Clase base para todos los servicios de negocio (La "Central de Esterilización").
    Provee operaciones CRUD comunes que pueden ser extendidas o sobreescritas por servicios específicos.
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
        # Nota: Asume que obj_in es un esquema de Pydantic
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        # El router o manejador de dependencias hace el commit final,
        # pero podemos hacer un flush para obtener el ID si es necesario.
        await self.session.flush()
        return db_obj
