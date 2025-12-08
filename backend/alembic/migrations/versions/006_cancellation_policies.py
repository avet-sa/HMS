backend/alembic/migrations/versions/006_cancellation_policies.py"""Add cancellation policies table

Revision ID: 006_cancellation_policies
Revises: 005_payments_invoices
Create Date: 2025-12-08 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_cancellation_policies'
down_revision: Union[str, Sequence[str], None] = '005_payments_invoices'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create cancellation_policies table."""
    op.create_table(
        'cancellation_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('full_refund_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('partial_refund_days', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('partial_refund_percentage', sa.Numeric(precision=5, scale=2), nullable=False, server_default='50'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_cancellation_policies_id'), 'cancellation_policies', ['id'], unique=False)


def downgrade() -> None:
    """Drop cancellation_policies table."""
    op.drop_index(op.f('ix_cancellation_policies_id'), table_name='cancellation_policies')
    op.drop_table('cancellation_policies')
