 # app/models/orm/inventario.py
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.orm.rbac import Usuario


class Insumo(Base):
    """
    Representa el inventario de insumos o medicamentos quirúrgicos.
    """
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_barras: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    stock_actual: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock_minimo: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    unidad_medida: Mapped[str] = mapped_column(String(30), default="Unidad", nullable=False)  # Ej: "Caja", "Ampolla", "Unidad"
    lote: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fecha_vencimiento: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relación 1:N con Retiros
    retiros: Mapped[List["RetiroInsumo"]] = relationship("RetiroInsumo", back_populates="insumo")

    def __repr__(self) -> str:
        return f"<Insumo(nombre='{self.nombre}', stock={self.stock_actual})>"


class RetiroInsumo(Base):
    """
    Registra la salida física de un insumo hacia un quirófano determinado.
    """
    __tablename__ = "retiros_insumos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    insumo_id: Mapped[int] = mapped_column(ForeignKey("insumos.id", ondelete="RESTRICT"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    
    id_quirofano: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # Ej: "Quirófano 3" o UUID
    cantidad_retirada: Mapped[int] = mapped_column(Integer, nullable=False)
    
    fecha_retiro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones ORM
    insumo: Mapped["Insumo"] = relationship("Insumo", back_populates="retiros")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="retiros_realizados")
    devoluciones: Mapped[List["DevolucionInsumo"]] = relationship("DevolucionInsumo", back_populates="retiro")

    def __repr__(self) -> str:
        return f"<RetiroInsumo(id={self.id}, insumo_id={self.insumo_id}, cantidad={self.cantidad_retirada})>"


class DevolucionInsumo(Base):
    """
    Registra el retorno parcial o total de insumos no utilizados o dañados.
    Vinculado obligatoriamente a un retiro previo.
    """
    __tablename__ = "devoluciones_insumos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    retiro_id: Mapped[int] = mapped_column(ForeignKey("retiros_insumos.id", ondelete="RESTRICT"), nullable=False)
    usuario_recibe_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    
    cantidad_devuelta: Mapped[int] = mapped_column(Integer, nullable=False)
    estado_insumo: Mapped[str] = mapped_column(String(50), nullable=False)  # Ej: "Estéril/Intacto", "Dañado", "Abierto"
    
    fecha_devolucion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relaciones ORM
    retiro: Mapped["RetiroInsumo"] = relationship("RetiroInsumo", back_populates="devoluciones")
    usuario_recibe: Mapped["Usuario"] = relationship("Usuario", back_populates="devoluciones_recibidas")

    def __repr__(self) -> str:
        return f"<DevolucionInsumo(id={self.id}, retiro_id={self.retiro_id}, estado='{self.estado_insumo}')>"