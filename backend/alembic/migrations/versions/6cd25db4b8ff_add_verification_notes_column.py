"""add_verification_notes_column

Revision ID: 6cd25db4b8ff
Revises: dbac9e8eca5e
Create Date: 2025-12-12 20:50:07.539731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6cd25db4b8ff'
down_revision: Union[str, Sequence[str], None] = 'dbac9e8eca5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add verification_notes column to housekeeping_tasks
    op.add_column('housekeeping_tasks', sa.Column('verification_notes', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove verification_notes column from housekeeping_tasks
    op.drop_column('housekeeping_tasks', 'verification_notes')
