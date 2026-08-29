# app/models/orm/inventario.py
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.orm.rbac import User

if TYPE_CHECKING:
    from app.models.orm.clinica import Procedure

class Supply(Base):
    """
    Represents the product or supply (its identity), without stock or batch.
    """
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    barcode: Mapped[str] = mapped_column("codigo_barras", String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column("nombre", String(150), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column("descripcion", Text, nullable=True)

    minimum_stock: Mapped[int] = mapped_column("stock_minimo", Integer, default=5, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column("unidad_medida", String(30), default="Unidad", nullable=False)  # Ex: "Box", "Ampoule", "Unit"

    # Relationships
    withdrawals: Mapped[List["SupplyWithdrawal"]] = relationship("SupplyWithdrawal", back_populates="supply")
    batches: Mapped[List["Batch"]] = relationship("Batch", back_populates="supply")

    def __repr__(self) -> str:
        return f"<Supply(name='{self.name}', barcode='{self.barcode}')>"

class Batch(Base):
    """
    Represents a batch/consignment of a supply, with its stock and expiration.
    """
    __tablename__ = "lotes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    supply_id: Mapped[int] = mapped_column("insumo_id", ForeignKey("insumos.id", ondelete="RESTRICT"), nullable=False)
    batch_number: Mapped[str] = mapped_column("numero_lote", String(50), nullable=False)
    expiration_date: Mapped[Optional[datetime]] = mapped_column("fecha_vencimiento", DateTime(timezone=True), nullable=True)
    current_stock: Mapped[int] = mapped_column("stock_actual", Integer, default=0, nullable=False)

    # Relationships
    supply: Mapped["Supply"] = relationship("Supply", back_populates="batches")
    withdrawals: Mapped[List["SupplyWithdrawal"]] = relationship("SupplyWithdrawal", back_populates="batch")

    def __repr__(self) -> str:
        return f"<Batch(id={self.id}, batch_number='{self.batch_number}', stock={self.current_stock})>"

class SupplyWithdrawal(Base):
    """
    Records the physical exit of a supply to a specific operating room.
    """
    __tablename__ = "retiros_insumos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    supply_id: Mapped[int] = mapped_column("insumo_id", ForeignKey("insumos.id", ondelete="RESTRICT"), nullable=False)
    batch_id: Mapped[int] = mapped_column("lote_id", ForeignKey("lotes.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[int] = mapped_column("usuario_id", ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    
    procedure_id: Mapped[int] = mapped_column("procedimiento_id", ForeignKey("procedimientos.id", ondelete="RESTRICT"), nullable=False)
    withdrawn_quantity: Mapped[int] = mapped_column("cantidad_retirada", Integer, nullable=False)
    
    withdrawal_date: Mapped[datetime] = mapped_column(
        "fecha_retiro",
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    observations: Mapped[Optional[str]] = mapped_column("observaciones", Text, nullable=True)

    # ORM Relationships
    supply: Mapped["Supply"] = relationship("Supply", back_populates="withdrawals")
    batch: Mapped["Batch"] = relationship("Batch", back_populates="withdrawals")
    user: Mapped["User"] = relationship("User", back_populates="withdrawals_made")
    returns: Mapped[List["SupplyReturn"]] = relationship("SupplyReturn", back_populates="withdrawal")
    procedure: Mapped["Procedure"] = relationship("Procedure", back_populates="withdrawals")

    def __repr__(self) -> str:
        return f"<SupplyWithdrawal(id={self.id}, supply_id={self.supply_id}, quantity={self.withdrawn_quantity})>"


class SupplyReturn(Base):
    """
    Records the partial or total return of unused or damaged supplies.
    Mandatorily linked to a previous withdrawal.
    """
    __tablename__ = "devoluciones_insumos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    withdrawal_id: Mapped[int] = mapped_column("retiro_id", ForeignKey("retiros_insumos.id", ondelete="RESTRICT"), nullable=False)
    receiving_user_id: Mapped[int] = mapped_column("usuario_recibe_id", ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    
    returned_quantity: Mapped[int] = mapped_column("cantidad_devuelta", Integer, nullable=False)
    supply_status: Mapped[str] = mapped_column("estado_insumo", String(50), nullable=False)  # Ex: "Sterile/Intact", "Damaged", "Opened"
    
    return_date: Mapped[datetime] = mapped_column(
        "fecha_devolucion",
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    observations: Mapped[Optional[str]] = mapped_column("observaciones", Text, nullable=True)

    # ORM Relationships
    withdrawal: Mapped["SupplyWithdrawal"] = relationship("SupplyWithdrawal", back_populates="returns")
    receiving_user: Mapped["User"] = relationship("User", back_populates="returns_received")

    def __repr__(self) -> str:
        return f"<SupplyReturn(id={self.id}, withdrawal_id={self.withdrawal_id}, status='{self.supply_status}')>"