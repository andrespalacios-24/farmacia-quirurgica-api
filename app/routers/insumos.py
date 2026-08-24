from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.api.deps import get_current_user, get_db, require_permission
from app.models.orm.inventario import Insumo, RetiroInsumo, DevolucionInsumo, Lote
from app.models.orm.rbac import Usuario
from datetime import date
 

from app.schemas.insumo import (
    RetiroInsumoCreate,
    InsumoCreate,
    InsumoResponse,
    DevolucionInsumoCreate,
    DevolucionInsumoResponse,
    EstadoInsumo,
    RetiroInsumoResponse,
    LoteCreate,
    LoteResumen,
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
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_permission("insumos:retirar")),
):
    # 1. Buscar el lote en el estante
    resultado_lote = await db.execute(
        select(Lote).where(Lote.id == vale_farmacia.lote_id)
    )
    lote_db = resultado_lote.scalar_one_or_none()

    if not lote_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error: El lote indicado no existe."
        )

    # 2. Verificar que el lote no esté vencido
    if lote_db.fecha_vencimiento is not None and lote_db.fecha_vencimiento.date() < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El lote está vencido y no se puede retirar.",
        )

    # 3. Verificar la cantidad en ese lote
    if lote_db.stock_actual < vale_farmacia.cantidad_retirada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente en el lote. Solo hay {lote_db.stock_actual} unidades."
        )

    # 4. Descontar del lote
    lote_db.stock_actual -= vale_farmacia.cantidad_retirada

    # 5. Crear el registro inmutable (insumo se deriva del lote)
    nuevo_retiro = RetiroInsumo(
        insumo_id=lote_db.insumo_id,
        lote_id=lote_db.id,
        procedimiento_id=vale_farmacia.procedimiento_id,
        usuario_id=usuario.id,
        cantidad_retirada=vale_farmacia.cantidad_retirada,
        observaciones=vale_farmacia.observaciones
    )

    # 6. Guardar
    db.add(nuevo_retiro)
    await db.commit()
    await db.refresh(nuevo_retiro)

    # 7. Entregar el comprobante
    return nuevo_retiro

# -------------------------------------------------------------------
# GET: Auditar el Kardex (Monitor de Inventario)
# -------------------------------------------------------------------
@router.get("/", response_model=list[InsumoResponse], status_code=status.HTTP_200_OK)
async def listar_kardex(
    bajo_stock: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    # 1. Cargar todos los insumos con sus lotes
    consulta = select(Insumo).options(selectinload(Insumo.lotes))
    resultado = await db.execute(consulta)
    insumos = resultado.scalars().all()

    # 2. Si se pide, filtrar críticos en Python (stock = suma de lotes)
    if bajo_stock:
        insumos = [
            i for i in insumos
            if sum(l.stock_actual for l in i.lotes) <= i.stock_minimo
        ]

    # 3. Paginar en Python (después del filtro)
    return insumos[skip:skip + limit]

# -------------------------------------------------------------------
# POST: Ingresar un insumo nuevo a la CEYE (alta de mercancía)
# -------------------------------------------------------------------
@router.post("/", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED)
async def crear_insumo(
    datos: InsumoCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(require_permission("insumos:crear")),
):
    # 1. Verificar que el código de barras no exista ya
    resultado = await db.execute(
        select(Insumo).where(Insumo.codigo_barras == datos.codigo_barras)
    )
    if resultado.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El código de barras ya está registrado.",
        )

    # 2. Crear el insumo
    nuevo_insumo = Insumo(**datos.model_dump())

    # 3. Guardar
    db.add(nuevo_insumo)
    await db.commit()

    # 4. Re-consultar con lotes cargados (vacío al inicio)
    consulta_completa = (
        select(Insumo)
        .where(Insumo.id == nuevo_insumo.id)
        .options(selectinload(Insumo.lotes))
    )
    resultado_final = await db.execute(consulta_completa)
    insumo_completo = resultado_final.scalar_one()

    return insumo_completo

# -------------------------------------------------------------------
# POST: Ingresar un lote nuevo (alta de mercancía a un insumo)
# -------------------------------------------------------------------
@router.post("/lotes", response_model=LoteResumen, status_code=status.HTTP_201_CREATED)
async def crear_lote(
    datos: LoteCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(require_permission("insumos:crear")),
):
    # 1. Verificar que el insumo (producto) exista
    resultado = await db.execute(
        select(Insumo).where(Insumo.id == datos.insumo_id)
    )
    if not resultado.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El insumo indicado no existe.",
        )

    # 2. Validar que la fecha de vencimiento no sea pasada
    if datos.fecha_vencimiento is not None and datos.fecha_vencimiento.date() < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de vencimiento no puede estar en el pasado.",
        )

    # 3. Crear el lote
    nuevo_lote = Lote(**datos.model_dump())

    # 4. Guardar y devolver
    db.add(nuevo_lote)
    await db.commit()
    await db.refresh(nuevo_lote)

    return nuevo_lote

# -------------------------------------------------------------------
# POST: Registrar una devolución (Reintegrar material al inventario)
# -------------------------------------------------------------------
@router.post("/devoluciones", response_model=DevolucionInsumoResponse, status_code=status.HTTP_201_CREATED)
async def registrar_devolucion(
    vale_devolucion: DevolucionInsumoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(require_permission("insumos:devolver"))
):
    # 1. Buscar el retiro original (con su lote cargado)
    resultado_retiro = await db.execute(
        select(RetiroInsumo)
        .where(RetiroInsumo.id == vale_devolucion.retiro_id)
        .options(selectinload(RetiroInsumo.lote))
    )
    retiro_db = resultado_retiro.scalar_one_or_none()

    if not retiro_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error: El retiro original no existe en el sistema."
        )

    # 2. Sumar las devoluciones previas de este retiro
    resultado_suma = await db.execute(
        select(func.coalesce(func.sum(DevolucionInsumo.cantidad_devuelta), 0)).where(
            DevolucionInsumo.retiro_id == vale_devolucion.retiro_id
        )
    )
    ya_devuelto = resultado_suma.scalar() or 0

    # 3. Verificar que el total no supere lo retirado
    if ya_devuelto + vale_devolucion.cantidad_devuelta > retiro_db.cantidad_retirada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La devolución supera lo retirado. Ya devuelto: {ya_devuelto}, retirado: {retiro_db.cantidad_retirada}."
        )

    # 4. Reintegrar al lote del retiro si está Estéril/Intacto
    if vale_devolucion.estado_insumo == EstadoInsumo.ESTERIL_INTACTO:
        retiro_db.lote.stock_actual += vale_devolucion.cantidad_devuelta

    # 5. Crear el registro inmutable de la devolución
    nueva_devolucion = DevolucionInsumo(
        retiro_id=vale_devolucion.retiro_id,
        usuario_recibe_id=usuario.id,
        cantidad_devuelta=vale_devolucion.cantidad_devuelta,
        estado_insumo=vale_devolucion.estado_insumo,
        observaciones=vale_devolucion.observaciones
    )

    # 6. Guardar
    db.add(nueva_devolucion)
    await db.commit()

    # 7. Re-consultar con carga ansiosa
    consulta_completa = select(DevolucionInsumo).where(
        DevolucionInsumo.id == nueva_devolucion.id
    ).options(
        selectinload(DevolucionInsumo.usuario_recibe),
        selectinload(DevolucionInsumo.retiro).selectinload(RetiroInsumo.insumo),
    )
    resultado_final = await db.execute(consulta_completa)
    devolucion_completa = resultado_final.scalar_one()

    # 8. Entregar el comprobante
    return devolucion_completa

# -------------------------------------------------------------------
# GET: Historial de retiros (Libro de movimientos de salida)
# -------------------------------------------------------------------

@router.get("/retiros", response_model=list[RetiroInsumoResponse], status_code=status.HTTP_200_OK)
async def listar_retiros(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    # 1. Consultar retiros con carga ansiosa y paginación
    consulta = select(RetiroInsumo).options(
        selectinload(RetiroInsumo.insumo),
        selectinload(RetiroInsumo.lote),
        selectinload(RetiroInsumo.usuario),
        selectinload(RetiroInsumo.procedimiento),
    ).offset(skip).limit(limit)

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
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    # 1. Consultar devoluciones con carga ansiosa y paginación
    consulta = select(DevolucionInsumo).options(
        selectinload(DevolucionInsumo.usuario_recibe),
        selectinload(DevolucionInsumo.retiro).selectinload(RetiroInsumo.insumo),
    ).offset(skip).limit(limit)

    # 2. Ejecutar la consulta asíncrona
    resultado = await db.execute(consulta)

    # 3. Extraer los objetos ORM en una lista
    devoluciones = resultado.scalars().all()

    # 4. Retornar la lista (FastAPI la serializa con DevolucionInsumoResponse)
    return devoluciones

# -------------------------------------------------------------------
# GET: Buscar un insumo por su código de barras
# -------------------------------------------------------------------
@router.get("/{codigo_barras}", response_model=InsumoResponse, status_code=status.HTTP_200_OK)
async def buscar_por_codigo(
    codigo_barras: str,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    resultado = await db.execute(
        select(Insumo)
        .where(Insumo.codigo_barras == codigo_barras)
        .options(selectinload(Insumo.lotes))
    )
    insumo = resultado.scalar_one_or_none()

    if not insumo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un insumo con ese código de barras.",
        )

    return insumo