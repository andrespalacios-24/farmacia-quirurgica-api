"""agregar_lotes

Revision ID: 9742bf4129d6
Revises: 9ff937c5de2e
Create Date: 2026-08-23 20:25:23.799252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9742bf4129d6'
down_revision: Union[str, Sequence[str], None] = '9ff937c5de2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear la tabla lotes
    op.create_table(
        'lotes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('insumo_id', sa.Integer(), nullable=False),
        sa.Column('numero_lote', sa.String(length=50), nullable=False),
        sa.Column('fecha_vencimiento', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stock_actual', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['insumo_id'], ['insumos.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 2. Migrar datos: un lote por cada insumo existente
    op.execute("""
        INSERT INTO lotes (insumo_id, numero_lote, fecha_vencimiento, stock_actual)
        SELECT id, COALESCE(lote, 'SIN_LOTE'), fecha_vencimiento, stock_actual
        FROM insumos
    """)

    # 3. Agregar lote_id (nullable) a retiros_insumos
    op.add_column('retiros_insumos', sa.Column('lote_id', sa.Integer(), nullable=True))

    # 4. Rellenar lote_id con el lote del insumo de cada retiro
    op.execute("""
        UPDATE retiros_insumos r
        SET lote_id = l.id
        FROM lotes l
        WHERE l.insumo_id = r.insumo_id
    """)

    # 5. Convertir lote_id en NOT NULL + foreign key
    op.alter_column('retiros_insumos', 'lote_id', nullable=False)
    op.create_foreign_key(None, 'retiros_insumos', 'lotes', ['lote_id'], ['id'], ondelete='RESTRICT')

    # 6. Quitar columnas que se movieron a lotes
    op.drop_column('insumos', 'fecha_vencimiento')
    op.drop_column('insumos', 'lote')
    op.drop_column('insumos', 'stock_actual')


def downgrade() -> None:
    op.add_column('insumos', sa.Column('stock_actual', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('insumos', sa.Column('lote', sa.String(length=50), nullable=True))
    op.add_column('insumos', sa.Column('fecha_vencimiento', sa.DateTime(timezone=True), nullable=True))
    op.drop_constraint(None, 'retiros_insumos', type_='foreignkey')
    op.drop_column('retiros_insumos', 'lote_id')
    op.drop_table('lotes')