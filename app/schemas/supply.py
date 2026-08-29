from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field, computed_field
from enum import Enum


class SupplyBase(BaseModel):
    barcode: str = Field(..., max_length=100)
    name: str = Field(..., max_length=150)
    description: Optional[str] = None

    minimum_stock: int = Field(default=5, ge=0)
    unit_of_measure: str = Field(default="Unidad", max_length=30)

class SupplyCreate(SupplyBase):
    pass

class BatchBase(BaseModel):
    batch_number: str = Field(..., max_length=50)
    expiration_date: Optional[datetime] = None
    current_stock: int = Field(default=0, ge=0)

class BatchCreate(BatchBase):
    supply_id: int

class BatchSummary(BatchBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def is_expired(self) -> bool:
        if self.expiration_date is None:
            return False
        return self.expiration_date.date() < date.today()

    @computed_field
    @property
    def is_expiring_soon(self) -> bool:
        if self.expiration_date is None:
            return False
        dias = (self.expiration_date.date() - date.today()).days
        return 0 <= dias <= 30

class SupplyResponse(SupplyBase):
    id: int
    batches: list[BatchSummary] = []
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def current_stock(self) -> int:
        return sum(batch.current_stock for batch in self.batches)

    @computed_field
    @property
    def is_critical_stock(self) -> bool:
        return sum(batch.current_stock for batch in self.batches) <= self.minimum_stock

# -------------------------------------------------------------------
# Inventory Flow Bins
# -------------------------------------------------------------------

class SupplyWithdrawalCreate(BaseModel):
    batch_id: int
    procedure_id: int
    withdrawn_quantity: int
    observations: Optional[str] = None

# -------------------------------------------------------------------
# Supply Returns
# -------------------------------------------------------------------

class SupplyStatus(str, Enum):
    STERILE_INTACT = "Estéril/Intacto"
    DAMAGED = "Dañado"
    OPENED = "Abierto"

class SupplyReturnCreate(BaseModel):
    withdrawal_id: int
    returned_quantity: int = Field(..., gt=0)
    supply_status: SupplyStatus
    observations: Optional[str] = None


# -------------------------------------------------------------------
# Summary schemas for movement history
# -------------------------------------------------------------------

class UserSummary(BaseModel):
    id: int
    full_name: str
    model_config = ConfigDict(from_attributes=True)


class SupplySummary(BaseModel):
    id: int
    name: str
    barcode: str
    unit_of_measure: str
    model_config = ConfigDict(from_attributes=True)


class ProcedureSummary(BaseModel):
    id: int
    description: str
    operating_room: str
    model_config = ConfigDict(from_attributes=True)

class WithdrawalSummary(BaseModel):
    id: int
    withdrawn_quantity: int
    supply: SupplySummary
    model_config = ConfigDict(from_attributes=True)

class SupplyWithdrawalResponse(BaseModel):
    id: int
    supply_id: int
    batch_id: int
    user_id: int
    procedure_id: int
    withdrawn_quantity: int
    withdrawal_date: datetime
    observations: Optional[str] = None
    supply: SupplySummary
    batch: BatchSummary
    user: UserSummary
    procedure: ProcedureSummary
    model_config = ConfigDict(from_attributes=True)


class SupplyReturnResponse(BaseModel):
    id: int
    withdrawal_id: int
    receiving_user_id: int
    returned_quantity: int
    supply_status: SupplyStatus
    return_date: datetime
    observations: Optional[str] = None
    receiving_user: UserSummary
    withdrawal: WithdrawalSummary
    model_config = ConfigDict(from_attributes=True)