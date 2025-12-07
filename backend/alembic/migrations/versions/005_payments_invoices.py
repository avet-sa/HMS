"""Add payments extended fields and invoices table

Revision ID: 005_payments_invoices
Revises: 004_booking_lifecycle
Create Date: 2025-12-08 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '005_payments_invoices'
down_revision: Union[str, Sequence[str], None] = '004_booking_lifecycle'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # Create new enum type for payment status (v2) to avoid colliding with existing type
    payment_status_v2 = postgresql.ENUM('PENDING', 'PAID', 'FAILED', 'REFUNDED', name='payment_status_v2')
    payment_status_v2.create(bind, checkfirst=True)

    # Add columns to existing payments table
    op.add_column('payments', sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'))
    op.add_column('payments', sa.Column('method', sa.String(length=50), nullable=False, server_default='CASH'))
    op.add_column('payments', sa.Column('status', postgresql.ENUM('PENDING', 'PAID', 'FAILED', 'REFUNDED', name='payment_status_v2', create_type=False), nullable=False, server_default='PENDING'))
    op.add_column('payments', sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('payments', sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('payments', sa.Column('reference', sa.String(length=100), nullable=True))

    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(length=50), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tax', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number')
    )
    op.create_index(op.f('ix_invoices_id'), 'invoices', ['id'], unique=False)
    op.create_index(op.f('ix_invoices_invoice_number'), 'invoices', ['invoice_number'], unique=True)
    op.create_index(op.f('ix_invoices_booking_id'), 'invoices', ['booking_id'], unique=False)


def downgrade() -> None:
    # Drop invoices table
    op.drop_index(op.f('ix_invoices_booking_id'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_invoice_number'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_id'), table_name='invoices')
    op.drop_table('invoices')

    # Drop added columns from payments
    op.drop_column('payments', 'reference')
    op.drop_column('payments', 'refunded_at')
    op.drop_column('payments', 'processed_at')
    op.drop_column('payments', 'status')
    op.drop_column('payments', 'method')
    op.drop_column('payments', 'currency')

    # Drop the enum type
    payment_status_v2 = postgresql.ENUM('PENDING', 'PAID', 'FAILED', 'REFUNDED', name='payment_status_v2')
    payment_status_v2.drop(op.get_bind(), checkfirst=True)
