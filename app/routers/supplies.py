from fastapi import APIRouter, Depends, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.api.deps import DbSession, CurrentUser, require_permission
from app.core.domain_exceptions import DomainException
from app.models import Supply, SupplyWithdrawal, SupplyReturn, Batch, User
from datetime import date
 

from app.schemas import (
    SupplyWithdrawalCreate,
    SupplyCreate,
    SupplyResponse,
    SupplyReturnCreate,
    SupplyReturnResponse,
    SupplyStatus,
    SupplyWithdrawalResponse,
    BatchCreate,
    BatchSummary,
)

router = APIRouter(
    prefix="/supplies",
    tags=["Inventory and Pharmacy"]
)

@router.post("/withdrawals", status_code=status.HTTP_201_CREATED)
async def process_withdrawal(
    withdrawal_voucher: SupplyWithdrawalCreate,
    db: DbSession,
    user: User = Depends(require_permission("supplies:withdraw")),
):
    result_batch = await db.execute(
        select(Batch).where(Batch.id == withdrawal_voucher.batch_id)
    )
    batch_db = result_batch.scalar_one_or_none()

    if not batch_db:
        raise DomainException("errors.batch_not_found", status_code=404)

    if batch_db.expiration_date is not None and batch_db.expiration_date.date() < date.today():
        raise DomainException("errors.batch_expired", status_code=400)

    if batch_db.current_stock < withdrawal_voucher.withdrawn_quantity:
        raise DomainException("errors.insufficient_stock", status_code=400, units=batch_db.current_stock)

    batch_db.current_stock -= withdrawal_voucher.withdrawn_quantity

    new_withdrawal = SupplyWithdrawal(
        supply_id=batch_db.supply_id,
        batch_id=batch_db.id,
        procedure_id=withdrawal_voucher.procedure_id,
        user_id=user.id,
        withdrawn_quantity=withdrawal_voucher.withdrawn_quantity,
        observations=withdrawal_voucher.observations
    )

    db.add(new_withdrawal)
    await db.commit()
    await db.refresh(new_withdrawal)

    return new_withdrawal


@router.get("/", response_model=list[SupplyResponse], status_code=status.HTTP_200_OK)
async def list_inventory(
    db: DbSession,
    user: CurrentUser,
    low_stock: bool = False,
    skip: int = 0,
    limit: int = 100,
):
    query = select(Supply).options(selectinload(Supply.batches))
    result = await db.execute(query)
    supplies = result.scalars().all()

    if low_stock:
        supplies = [
            s for s in supplies
            if sum(b.current_stock for b in s.batches) <= s.minimum_stock
        ]

    return supplies[skip:skip + limit]


@router.post("/", response_model=SupplyResponse, status_code=status.HTTP_201_CREATED)
async def create_supply(
    data: SupplyCreate,
    db: DbSession,
    current_user: User = Depends(require_permission("supplies:create")),
):
    result = await db.execute(
        select(Supply).where(Supply.barcode == data.barcode)
    )
    if result.scalar_one_or_none():
        raise DomainException("errors.barcode_already_registered", status_code=409)

    new_supply = Supply(**data.model_dump())

    db.add(new_supply)
    await db.commit()

    complete_query = (
        select(Supply)
        .where(Supply.id == new_supply.id)
        .options(selectinload(Supply.batches))
    )
    final_result = await db.execute(complete_query)
    complete_supply = final_result.scalar_one()

    return complete_supply


@router.post("/batches", response_model=BatchSummary, status_code=status.HTTP_201_CREATED)
async def create_batch(
    data: BatchCreate,
    db: DbSession,
    current_user: User = Depends(require_permission("supplies:create")),
):
    result = await db.execute(
        select(Supply).where(Supply.id == data.supply_id)
    )
    if not result.scalar_one_or_none():
        raise DomainException("errors.supply_not_found", status_code=404)

    if data.expiration_date is not None and data.expiration_date.date() < date.today():
        raise DomainException("errors.expiration_date_in_past", status_code=400)

    new_batch = Batch(**data.model_dump())

    db.add(new_batch)
    await db.commit()
    await db.refresh(new_batch)

    return new_batch


@router.post("/returns", response_model=SupplyReturnResponse, status_code=status.HTTP_201_CREATED)
async def register_return(
    return_voucher: SupplyReturnCreate,
    db: DbSession,
    user: User = Depends(require_permission("supplies:return"))
):
    result_withdrawal = await db.execute(
        select(SupplyWithdrawal)
        .where(SupplyWithdrawal.id == return_voucher.withdrawal_id)
        .options(selectinload(SupplyWithdrawal.batch))
    )
    withdrawal_db = result_withdrawal.scalar_one_or_none()

    if not withdrawal_db:
        raise DomainException("errors.withdrawal_not_found", status_code=404)

    sum_result = await db.execute(
        select(func.coalesce(func.sum(SupplyReturn.returned_quantity), 0)).where(
            SupplyReturn.withdrawal_id == return_voucher.withdrawal_id
        )
    )
    already_returned = sum_result.scalar() or 0

    if already_returned + return_voucher.returned_quantity > withdrawal_db.withdrawn_quantity:
        raise DomainException("errors.return_exceeds_withdrawal", status_code=400, already_returned=already_returned, withdrawn=withdrawal_db.withdrawn_quantity)

    if return_voucher.supply_status == SupplyStatus.STERILE_INTACT:
        withdrawal_db.batch.current_stock += return_voucher.returned_quantity

    new_return = SupplyReturn(
        withdrawal_id=return_voucher.withdrawal_id,
        receiving_user_id=user.id,
        returned_quantity=return_voucher.returned_quantity,
        supply_status=return_voucher.supply_status,
        observations=return_voucher.observations
    )

    db.add(new_return)
    await db.commit()

    complete_query = select(SupplyReturn).where(
        SupplyReturn.id == new_return.id
    ).options(
        selectinload(SupplyReturn.receiving_user),
        selectinload(SupplyReturn.withdrawal).selectinload(SupplyWithdrawal.supply),
    )
    final_result = await db.execute(complete_query)
    complete_return = final_result.scalar_one()

    return complete_return


@router.get("/withdrawals", response_model=list[SupplyWithdrawalResponse], status_code=status.HTTP_200_OK)
async def list_withdrawals(
    db: DbSession,
    user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    query = select(SupplyWithdrawal).options(
        selectinload(SupplyWithdrawal.supply),
        selectinload(SupplyWithdrawal.batch),
        selectinload(SupplyWithdrawal.user),
        selectinload(SupplyWithdrawal.procedure),
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    withdrawals = result.scalars().all()

    return withdrawals


@router.get("/returns", response_model=list[SupplyReturnResponse], status_code=status.HTTP_200_OK)
async def list_returns(
    db: DbSession,
    user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
):
    query = select(SupplyReturn).options(
        selectinload(SupplyReturn.receiving_user),
        selectinload(SupplyReturn.withdrawal).selectinload(SupplyWithdrawal.supply),
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    returns = result.scalars().all()

    return returns


@router.get("/{barcode}", response_model=SupplyResponse, status_code=status.HTTP_200_OK)
async def search_by_barcode(
    barcode: str,
    db: DbSession,
    user: CurrentUser,
):
    result = await db.execute(
        select(Supply)
        .where(Supply.barcode == barcode)
        .options(selectinload(Supply.batches))
    )
    supply = result.scalar_one_or_none()

    if not supply:
        raise DomainException("errors.supply_not_found_by_barcode", status_code=404)

    return supply