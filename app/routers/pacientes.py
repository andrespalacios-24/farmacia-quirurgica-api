from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# Importamos nuestro circulante (la dependencia)
from app.api.deps import get_db

# Importamos los esquemas (filtros estrictos de entrada/salida)
from app.schemas import PacienteCreate, PacienteResponse

# Importamos el modelo de la base de datos (la representación de la tabla)
from app.models import Paciente

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

@router.get("/", response_model=list[PacienteResponse], status_code=status.HTTP_200_OK)
async def obtener_pacientes(db: AsyncSession = Depends(get_db)):
    
    # 1. Preparamos la solicitud al archivo (Armamos el Query)
    query = select(Paciente)
    
    # 2. El circulante ejecuta la búsqueda en los estantes de PostgreSQL
    resultado = await db.execute(query)
    
    # 3. Extraemos los expedientes limpios y los ponemos en la mesa
    pacientes_encontrados = resultado.scalars().all()
    
    # 4. Entregamos la lista de pacientes
    return pacientes_encontrados

@router.get("/{cedula}", response_model=PacienteResponse, status_code=status.HTTP_200_OK)
async def obtener_paciente_por_cedula(cedula: str, db: AsyncSession = Depends(get_db)):
    
    # 1. Armamos el query: "Selecciona el paciente DONDE la cédula coincida"
    query = select(Paciente).where(Paciente.cedula == cedula)
    
    # 2. El circulante ejecuta la búsqueda
    resultado = await db.execute(query)
    
    # 3. Extraemos un ÚNICO expediente (o nada si no existe)
    paciente_encontrado = resultado.scalar_one_or_none()
    
    # 4. Protocolo de contingencia: ¿Qué pasa si el paciente es nuevo y no está en el sistema?
    if not paciente_encontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró historia clínica para la cédula {cedula}"
        )
    
    # 5. Si lo encuentra, entregamos el expediente
    return paciente_encontrado