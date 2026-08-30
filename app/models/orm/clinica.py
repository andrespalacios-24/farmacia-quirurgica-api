from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.orm.inventario import SupplyWithdrawal

class Patient(Base):
    __tablename__ = "pacientes"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    national_id: Mapped[str] = mapped_column("cedula", String(20), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column("nombre_completo", String(150), nullable=False)
    
    # 1:N Relationship - A patient can have many procedures
    procedures: Mapped[List["Procedure"]] = relationship("Procedure", back_populates="patient")

class Procedure(Base):
    __tablename__ = "procedimientos"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column("paciente_id", ForeignKey("pacientes.id", ondelete="RESTRICT"), nullable=False)
    description: Mapped[str] = mapped_column("descripcion", String(255), nullable=False) # Ex: "Appendectomy"
    operating_room: Mapped[str] = mapped_column("quirofano", String(50), nullable=False)
    
    procedure_date: Mapped[datetime] = mapped_column("fecha_procedimiento", DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="procedures")
    withdrawals: Mapped[List["SupplyWithdrawal"]] = relationship("SupplyWithdrawal", back_populates="procedure")
