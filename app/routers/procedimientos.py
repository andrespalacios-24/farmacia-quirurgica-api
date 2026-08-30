from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
# Importamos nuestro circulante (la dependencia)
from app.api.deps import DbSession
# Importamos la anatomía (Modelos DB)
from app.models import Procedimiento, Paciente
# Importamos el instrumental (Esquemas Pydantic)
from app.schemas import ProcedimientoCreate, ProcedimientoResponse
from sqlalchemy.orm import selectinload

# Definimos el router (Nuestra nueva sala)
router = APIRouter(
    prefix="/procedimientos",
    tags=["Procedimientos"]
)

@router.post("/", response_model=ProcedimientoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_procedimiento(
    procedimiento_in: ProcedimientoCreate, 
    db: DbSession
):
    # 1. Pausa de Seguridad (Time Out): Verificar que el paciente realmente existe
    resultado = await db.execute(select(Paciente).where(Paciente.id == procedimiento_in.paciente_id))
    paciente_db = resultado.scalar_one_or_none()
    
    if not paciente_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Error: El paciente indicado no se encuentra en el sistema."
        )

    # 2. Preparar el registro (Montar el bisturí)
    nuevo_procedimiento = Procedimiento(**procedimiento_in.model_dump())
    
    # 3. Ejecutar la acción y guardar (Incisión y sutura)
    db.add(nuevo_procedimiento)
    await db.commit()
    
    # --- EL CAMBIO OCURRE AQUÍ ---
    # En lugar del refresh, solicitamos el expediente completo con selectinload
    consulta_post_operatoria = select(Procedimiento).where(Procedimiento.id == nuevo_procedimiento.id).options(selectinload(Procedimiento.paciente))
    resultado_final = await db.execute(consulta_post_operatoria)
    procedimiento_completo = resultado_final.scalar_one()
    
    # 4. Entregar el reporte final
    return procedimiento_completo

# -------------------------------------------------------------------
# GET: Listar todos los procedimientos (La Pizarra del Quirófano)
# -------------------------------------------------------------------
@router.get("/", response_model=list[ProcedimientoResponse], status_code=status.HTTP_200_OK)
async def obtener_procedimientos(db: DbSession):
    
    # 1. Preparar la solicitud de búsqueda
    consulta = select(Procedimiento).options(selectinload(Procedimiento.paciente))
    
    # 2. Enviar al auxiliar al archivo y esperar los expedientes
    resultado = await db.execute(consulta)
    
    # 3. Extraer los registros limpios de la caja
    procedimientos = resultado.scalars().all()
    
    # 4. Mostrar la cartelera
    return procedimientos
