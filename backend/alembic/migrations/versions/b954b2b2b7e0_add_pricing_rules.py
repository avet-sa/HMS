"""add_pricing_rules

Revision ID: b954b2b2b7e0
Revises: 881741c5e475
Create Date: 2025-12-12 19:21:31.717528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b954b2b2b7e0'
down_revision: Union[str, Sequence[str], None] = '881741c5e475'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create pricing_rules table (using VARCHAR for rule_type for simplicity)
    op.create_table(
        'pricing_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('rule_type', sa.String(length=20), nullable=False),  # seasonal, weekend, etc.
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('adjustment_type', sa.String(length=20), nullable=False),
        sa.Column('adjustment_value', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('room_type_id', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('applicable_days', sa.String(length=50), nullable=True),
        sa.Column('min_nights', sa.Integer(), nullable=True),
        sa.Column('min_advance_days', sa.Integer(), nullable=True),
        sa.Column('max_advance_days', sa.Integer(), nullable=True),
        sa.Column('min_loyalty_tier', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['room_type_id'], ['room_types.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_pricing_rules_rule_type', 'pricing_rules', ['rule_type'])
    op.create_index('ix_pricing_rules_priority', 'pricing_rules', ['priority'])
    op.create_index('ix_pricing_rules_room_type_id', 'pricing_rules', ['room_type_id'])
    op.create_index('ix_pricing_rules_start_date', 'pricing_rules', ['start_date'])
    op.create_index('ix_pricing_rules_end_date', 'pricing_rules', ['end_date'])
    op.create_index('ix_pricing_rules_is_active', 'pricing_rules', ['is_active'])
    
    # Insert default pricing rules
    op.execute("""
        INSERT INTO pricing_rules (name, description, rule_type, priority, adjustment_type, adjustment_value, is_active)
        VALUES 
        ('Weekend Premium', 'Higher rates for Friday and Saturday nights', 'weekend', 10, 'percentage', 20.00, true),
        ('Early Bird Discount', 'Discount for bookings made 30+ days in advance', 'early_bird', 5, 'percentage', -15.00, true),
        ('Long Stay Discount', 'Discount for stays of 7+ nights', 'long_stay', 8, 'percentage', -10.00, true)
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_pricing_rules_is_active', 'pricing_rules')
    op.drop_index('ix_pricing_rules_end_date', 'pricing_rules')
    op.drop_index('ix_pricing_rules_start_date', 'pricing_rules')
    op.drop_index('ix_pricing_rules_room_type_id', 'pricing_rules')
    op.drop_index('ix_pricing_rules_priority', 'pricing_rules')
    op.drop_index('ix_pricing_rules_rule_type', 'pricing_rules')
    
    # Drop table
    op.drop_table('pricing_rules')
