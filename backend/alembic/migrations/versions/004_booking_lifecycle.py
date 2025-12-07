"""Add booking lifecycle state machine columns

Revision ID: 004_booking_lifecycle
Revises: 003_add_booking_created_by
Create Date: 2025-12-08 21:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_booking_lifecycle'
down_revision: Union[str, Sequence[str], None] = '003_add_booking_created_by'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add booking lifecycle tracking columns."""
    op.add_column('bookings', sa.Column('actual_check_in', sa.DateTime(timezone=True), nullable=True))
    op.add_column('bookings', sa.Column('actual_check_out', sa.DateTime(timezone=True), nullable=True))
    op.add_column('bookings', sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('bookings', sa.Column('final_bill', sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    """Remove booking lifecycle tracking columns."""
    op.drop_column('bookings', 'final_bill')
    op.drop_column('bookings', 'cancelled_at')
    op.drop_column('bookings', 'actual_check_out')
    op.drop_column('bookings', 'actual_check_in')
