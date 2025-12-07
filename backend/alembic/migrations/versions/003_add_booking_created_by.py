"""Add created_by column to bookings table

Revision ID: 003_add_booking_created_by
Revises: d8e515997d8a
Create Date: 2025-12-08 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_add_booking_created_by'
down_revision: Union[str, Sequence[str], None] = 'd8e515997d8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add created_by column to bookings table."""
    # Add the created_by column with foreign key constraint
    op.add_column('bookings', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_bookings_created_by_users', 'bookings', 'users', ['created_by'], ['id'])
    op.create_index('ix_bookings_created_by', 'bookings', ['created_by'], unique=False)


def downgrade() -> None:
    """Remove created_by column from bookings table."""
    op.drop_index('ix_bookings_created_by', table_name='bookings')
    op.drop_constraint('fk_bookings_created_by_users', 'bookings', type_='foreignkey')
    op.drop_column('bookings', 'created_by')
