from typing import List
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Paciente(Base):
    __tablename__ = "pacientes"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cedula: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    
    # Relación 1:N - Un paciente puede tener muchos procedimientos (ej. reintervenciones)
    procedimientos: Mapped[List["Procedimiento"]] = relationship("Procedimiento", back_populates="paciente")

class Procedimiento(Base):
    __tablename__ = "procedimientos"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("pacientes.id", ondelete="RESTRICT"), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False) # Ej: "Apendicectomía", "Lavado Quirúrgico"
    quirofano: Mapped[str] = mapped_column(String(50), nullable=False)
    
    fecha_procedimiento: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relaciones
    paciente: Mapped["Paciente"] = relationship("Paciente", back_populates="procedimientos")
    # Nota: En el próximo paso enlazaremos esta tabla con los retiros de farmacia.