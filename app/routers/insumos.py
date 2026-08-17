from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.models.orm.inventario import Insumo, RetiroInsumo, DevolucionInsumo
from app.schemas.insumo import (
    RetiroInsumoCreate,
    InsumoResponse,
    DevolucionInsumoCreate,
    DevolucionInsumoResponse,
    EstadoInsumo,
    RetiroInsumoResponse,
)

# Definimos el router (Nuestra ventanilla de farmacia)
router = APIRouter(
    prefix="/insumos",
    tags=["Inventario y Farmacia"]
)

# -------------------------------------------------------------------
# POST: Registrar un retiro (Procesar el vale de farmacia)
# -------------------------------------------------------------------
@router.post("/retiros", status_code=status.HTTP_201_CREATED)
async def procesar_retiro(
    vale_farmacia: RetiroInsumoCreate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Primer 'Time Out': Buscar el insumo en el estante
    resultado_insumo = await db.execute(select(Insumo).where(Insumo.id == vale_farmacia.insumo_id))
    insumo_db = resultado_insumo.scalar_one_or_none()

    if not insumo_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error: El insumo solicitado no existe en la central."
        )
    
    # 2. Segundo 'Time Out': Verificar la cantidad (¿Hay suficiente material?)
    if insumo_db.stock_actual < vale_farmacia.cantidad_retirada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente. Solo hay {insumo_db.stock_actual} unidades disponibles."
        )
        
    # 3. La incisión (Descontar el inventario físico de la caja)
    insumo_db.stock_actual -= vale_farmacia.cantidad_retirada
    
    # 4. El registro oficial (Crear el movimiento inmutable)
    nuevo_retiro = RetiroInsumo(
        insumo_id=vale_farmacia.insumo_id,
        procedimiento_id=vale_farmacia.procedimiento_id,
        usuario_id=vale_farmacia.usuario_id,
        cantidad_retirada=vale_farmacia.cantidad_retirada,
        observaciones=vale_farmacia.observaciones
    )
    
    # 5. Suturar y cerrar (Guardar ambos cambios en la base de datos)
    db.add(nuevo_retiro)
    await db.commit()
    await db.refresh(nuevo_retiro)
    
    # 6. Entregar el comprobante al usuario
    return nuevo_retiro

# -------------------------------------------------------------------
# GET: Auditar el Kardex (Monitor de Inventario)
# -------------------------------------------------------------------
@router.get("/", response_model=list[InsumoResponse], status_code=status.HTTP_200_OK)
async def listar_kardex(
    db: AsyncSession = Depends(get_db)
):
    # 1. Consultar todos los insumos disponibles en la base de datos
    resultado = await db.execute(select(Insumo))
    
    # 2. Desempaquetar los resultados ORM en una lista de objetos
    insumos = resultado.scalars().all()
    
    # 3. Retornar la lista para ser serializada por FastAPI
    return insumos

# -------------------------------------------------------------------
# POST: Registrar una devolución (Reintegrar material al inventario)
# -------------------------------------------------------------------
@router.post("/devoluciones", response_model=DevolucionInsumoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_devolucion(
    vale_devolucion: DevolucionInsumoCreate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Primer 'Time Out': Buscar el retiro original en el libro de movimientos
    resultado_retiro = await db.execute(
        select(RetiroInsumo).where(RetiroInsumo.id == vale_devolucion.retiro_id)
    )
    retiro_db = resultado_retiro.scalar_one_or_none()

    if not retiro_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error: El retiro original no existe en el sistema."
        )

    # 2. Verificar que no se devuelva más material del que se retiró
    if vale_devolucion.cantidad_devuelta > retiro_db.cantidad_retirada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error: No puedes devolver más de lo retirado ({retiro_db.cantidad_retirada})."
        )
    # 3. Buscar el insumo asociado al retiro para reintegrar el stock
    resultado_insumo = await db.execute(
        select(Insumo).where(Insumo.id == retiro_db.insumo_id)
    )
    insumo_db = resultado_insumo.scalar_one_or_none()

    if not insumo_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error: El insumo asociado al retiro no existe."
        )

    # 4. Reintegrar el stock solo si el material está Estéril/Intacto
    if vale_devolucion.estado_insumo == EstadoInsumo.ESTERIL_INTACTO:
        insumo_db.stock_actual += vale_devolucion.cantidad_devuelta

    # 5. Crear el registro inmutable de la devolución
    nueva_devolucion = DevolucionInsumo(
        retiro_id=vale_devolucion.retiro_id,
        usuario_recibe_id=vale_devolucion.usuario_recibe_id,
        cantidad_devuelta=vale_devolucion.cantidad_devuelta,
        estado_insumo=vale_devolucion.estado_insumo,
        observaciones=vale_devolucion.observaciones
    )

    # 6. Suturar y cerrar (guardar cambios en la base de datos)
    db.add(nueva_devolucion)
    await db.commit()

    # 7. Re-consultar con carga ansiosa para armar el comprobante completo
    consulta_completa = select(DevolucionInsumo).where(
        DevolucionInsumo.id == nueva_devolucion.id
    ).options(
        selectinload(DevolucionInsumo.usuario_recibe),
        selectinload(DevolucionInsumo.retiro).selectinload(RetiroInsumo.insumo),
    )
    resultado_final = await db.execute(consulta_completa)
    devolucion_completa = resultado_final.scalar_one()

    # 8. Entregar el comprobante al usuario
    return devolucion_completa

# -------------------------------------------------------------------
# GET: Historial de retiros (Libro de movimientos de salida)
# -------------------------------------------------------------------
@router.get("/retiros", response_model=list[RetiroInsumoResponse], status_code=status.HTTP_200_OK)
async def listar_retiros(
    db: AsyncSession = Depends(get_db)
):
    # 1. Consultar retiros con carga ansiosa de sus relaciones
    consulta = select(RetiroInsumo).options(
        selectinload(RetiroInsumo.insumo),
        selectinload(RetiroInsumo.usuario),
        selectinload(RetiroInsumo.procedimiento),
    )

    # 2. Ejecutar la consulta asíncrona
    resultado = await db.execute(consulta)

    # 3. Extraer los objetos ORM en una lista
    retiros = resultado.scalars().all()

    # 4. Retornar la lista (FastAPI la serializa con RetiroInsumoResponse)
    return retiros

# -------------------------------------------------------------------
# GET: Historial de devoluciones (Libro de movimientos de retorno)
# -------------------------------------------------------------------
@router.get("/devoluciones", response_model=list[DevolucionInsumoResponse], status_code=status.HTTP_200_OK)
async def listar_devoluciones(
    db: AsyncSession = Depends(get_db)
):
    # 1. Consultar devoluciones con carga ansiosa en cadena
    consulta = select(DevolucionInsumo).options(
        selectinload(DevolucionInsumo.usuario_recibe),
        selectinload(DevolucionInsumo.retiro).selectinload(RetiroInsumo.insumo),
    )

    # 2. Ejecutar la consulta asíncrona
    resultado = await db.execute(consulta)

    # 3. Extraer los objetos ORM en una lista
    devoluciones = resultado.scalars().all()

    # 4. Retornar la lista (FastAPI la serializa con DevolucionInsumoResponse)
    return devoluciones