from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models.orm.inventario import Insumo, RetiroInsumo
from app.schemas.insumo import RetiroInsumoCreate

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