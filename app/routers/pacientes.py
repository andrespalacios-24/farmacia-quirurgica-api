from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Importamos nuestro circulante (la dependencia)
from app.api.deps import get_db

# Importamos los esquemas (filtros estrictos de entrada/salida)
from app.schemas.paciente import PacienteCreate, PacienteResponse

# Importamos el modelo de la base de datos (la representación de la tabla)
from app.models.orm.clinica import Paciente

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)
@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
async def registrar_paciente(paciente_in: PacienteCreate, db: AsyncSession = Depends(get_db)):
    nuevo_paciente = Paciente(**paciente_in.model_dump())
    db.add(nuevo_paciente)
    await db.commit()
    await db.refresh(nuevo_paciente)
    return nuevo_paciente