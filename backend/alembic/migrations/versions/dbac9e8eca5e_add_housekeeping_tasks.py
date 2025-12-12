"""add_housekeeping_tasks

Revision ID: dbac9e8eca5e
Revises: b954b2b2b7e0
Create Date: 2025-12-12 20:12:32.340448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbac9e8eca5e'
down_revision: Union[str, Sequence[str], None] = 'b954b2b2b7e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create housekeeping_tasks table
    op.create_table(
        'housekeeping_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('booking_id', sa.Integer(), nullable=True),
        sa.Column('task_type', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=10), nullable=False, server_default='normal'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('scheduled_time', sa.String(length=10), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.String(length=500), nullable=True),
        sa.Column('completion_notes', sa.String(length=500), nullable=True),
        sa.Column('estimated_duration_minutes', sa.Integer(), server_default='30'),
        sa.Column('actual_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('is_checkout_cleaning', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_housekeeping_tasks_room_id', 'housekeeping_tasks', ['room_id'])
    op.create_index('ix_housekeeping_tasks_assigned_to', 'housekeeping_tasks', ['assigned_to'])
    op.create_index('ix_housekeeping_tasks_booking_id', 'housekeeping_tasks', ['booking_id'])
    op.create_index('ix_housekeeping_tasks_task_type', 'housekeeping_tasks', ['task_type'])
    op.create_index('ix_housekeeping_tasks_priority', 'housekeeping_tasks', ['priority'])
    op.create_index('ix_housekeeping_tasks_status', 'housekeeping_tasks', ['status'])
    op.create_index('ix_housekeeping_tasks_scheduled_date', 'housekeeping_tasks', ['scheduled_date'])
    op.create_index('ix_housekeeping_tasks_is_checkout_cleaning', 'housekeeping_tasks', ['is_checkout_cleaning'])
    
    # Create composite indexes for common queries
    op.create_index('ix_housekeeping_tasks_room_status', 'housekeeping_tasks', ['room_id', 'status', 'scheduled_date'])
    op.create_index('ix_housekeeping_tasks_assigned_status', 'housekeeping_tasks', ['assigned_to', 'status', 'priority'])
    op.create_index('ix_housekeeping_tasks_status_priority_date', 'housekeeping_tasks', ['status', 'priority', 'scheduled_date'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop composite indexes
    op.drop_index('ix_housekeeping_tasks_status_priority_date', 'housekeeping_tasks')
    op.drop_index('ix_housekeeping_tasks_assigned_status', 'housekeeping_tasks')
    op.drop_index('ix_housekeeping_tasks_room_status', 'housekeeping_tasks')
    
    # Drop single column indexes
    op.drop_index('ix_housekeeping_tasks_is_checkout_cleaning', 'housekeeping_tasks')
    op.drop_index('ix_housekeeping_tasks_scheduled_date', 'housekeeping_tasks')
    op.drop_index('ix_housekeeping_tasks_status', 'housekeeping_tasks')
    op.drop_index('ix_housekeeping_tasks_priority', 'housekeeping_tasks')
    op.drop_index('ix_housekeeping_tasks_task_type', 'housekeeping_tasks')
    op.drop_index('ix_housekeeping_tasks_booking_id', 'housekeeping_tasks')
    op.drop_index('ix_housekeeping_tasks_assigned_to', 'housekeeping_tasks')
    op.drop_index('ix_housekeeping_tasks_room_id', 'housekeeping_tasks')
    
    # Drop table
    op.drop_table('housekeeping_tasks')
