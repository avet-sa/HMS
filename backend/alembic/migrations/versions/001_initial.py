"""Initial migration - Hotel Management System

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-04 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    permission_level = postgresql.ENUM('REGULAR', 'MANAGER', 'ADMIN', name='permission_level')
    permission_level.create(op.get_bind())
    
    booking_status = postgresql.ENUM(
        'pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'no_show',
        name='booking_status'
    )
    booking_status.create(op.get_bind())
    
    room_maintenance_status = postgresql.ENUM(
        'available', 'maintenance', 'out_of_service',
        name='room_maintenance_status'
    )
    room_maintenance_status.create(op.get_bind())
    
    payment_status = postgresql.ENUM(
        'pending', 'paid', 'partially_paid', 'refunded',
        name='payment_status'
    )
    payment_status.create(op.get_bind())
    
    payment_method = postgresql.ENUM(
        'cash', 'credit_card', 'debit_card', 'bank_transfer', 'online',
        name='payment_method'
    )
    payment_method.create(op.get_bind())
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column(
            'permission_level',
            postgresql.ENUM('REGULAR', 'MANAGER', 'ADMIN', name='permission_level', create_type=False),
            nullable=False,
            server_default='REGULAR'
        ),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create guests table
    op.create_table(
        'guests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('surname', sa.String(length=100), nullable=False),
        sa.Column('phone_number', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('nationality', sa.String(length=50), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('document_type', sa.String(length=20), nullable=True),
        sa.Column('document_id', sa.String(length=50), nullable=True),
        sa.Column('loyalty_points', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('vip_tier', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_guests_id'), 'guests', ['id'], unique=False)
    op.create_index(op.f('ix_guests_email'), 'guests', ['email'], unique=True)
    op.create_index(op.f('ix_guests_phone_number'), 'guests', ['phone_number'], unique=False)
    
    # Create room_types table
    op.create_table(
        'room_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_room_types_id'), 'room_types', ['id'], unique=False)
    
    # Create rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(length=10), nullable=False),
        sa.Column('room_type_id', sa.Integer(), nullable=False),
        sa.Column('price_per_night', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('square_meters', sa.Integer(), nullable=True),
        sa.Column('floor', sa.Integer(), nullable=True),
        sa.Column(
            'maintenance_status',
            postgresql.ENUM('available', 'maintenance', 'out_of_service', name='room_maintenance_status', create_type=False),
            nullable=False,
            server_default='available'
        ),
        sa.Column('has_view', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('is_smoking', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['room_type_id'], ['room_types.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('number')
    )
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)
    op.create_index(op.f('ix_rooms_number'), 'rooms', ['number'], unique=True)
    op.create_index(op.f('ix_rooms_room_type_id'), 'rooms', ['room_type_id'], unique=False)
    
    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_number', sa.String(length=20), nullable=False),
        sa.Column('guest_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('check_in', sa.Date(), nullable=False),
        sa.Column('check_out', sa.Date(), nullable=False),
        sa.Column('number_of_guests', sa.Integer(), nullable=False, server_default=sa.text('1')),
        sa.Column('number_of_nights', sa.Integer(), nullable=False),
        sa.Column('price_per_night', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            'status',
            postgresql.ENUM('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'no_show', 
                          name='booking_status', create_type=False),
            nullable=False,
            server_default='pending'
        ),
        sa.Column('special_requests', sa.String(length=500), nullable=True),
        sa.Column('internal_notes', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('check_out > check_in', name='check_dates'),
        sa.CheckConstraint('number_of_guests > 0', name='check_guests_positive'),
        sa.CheckConstraint('number_of_nights > 0', name='check_nights_positive'),
        sa.ForeignKeyConstraint(['guest_id'], ['guests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_number')
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_booking_number'), 'bookings', ['booking_number'], unique=True)
    op.create_index(op.f('ix_bookings_guest_id'), 'bookings', ['guest_id'], unique=False)
    op.create_index(op.f('ix_bookings_room_id'), 'bookings', ['room_id'], unique=False)
    op.create_index(op.f('ix_bookings_check_in'), 'bookings', ['check_in'], unique=False)
    op.create_index(op.f('ix_bookings_check_out'), 'bookings', ['check_out'], unique=False)
    op.create_index(op.f('ix_bookings_status'), 'bookings', ['status'], unique=False)
    op.create_index(op.f('ix_bookings_created_at'), 'bookings', ['created_at'], unique=False)
    # Composite index for availability queries
    op.create_index('ix_bookings_dates', 'bookings', ['check_in', 'check_out'])
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            'payment_method',
            postgresql.ENUM('cash', 'credit_card', 'debit_card', 'bank_transfer', 'online',
                          name='payment_method', create_type=False),
            nullable=False
        ),
        sa.Column(
            'payment_status',
            postgresql.ENUM('pending', 'paid', 'partially_paid', 'refunded',
                          name='payment_status', create_type=False),
            nullable=False,
            server_default='pending'
        ),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('amount > 0', name='check_amount_positive'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_index(op.f('ix_payments_booking_id'), 'payments', ['booking_id'], unique=False)
    
    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create triggers for all tables
    for table in ['users', 'guests', 'room_types', 'rooms', 'bookings', 'payments']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers
    for table in ['users', 'guests', 'room_types', 'rooms', 'bookings', 'payments']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    
    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Drop tables in reverse order
    op.drop_index(op.f('ix_payments_booking_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
    
    op.drop_index('ix_bookings_dates', table_name='bookings')
    op.drop_index(op.f('ix_bookings_created_at'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_status'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_check_out'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_check_in'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_room_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_guest_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_booking_number'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_table('bookings')
    
    op.drop_index(op.f('ix_rooms_room_type_id'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_number'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_table('rooms')
    
    op.drop_index(op.f('ix_room_types_id'), table_name='room_types')
    op.drop_table('room_types')
    
    op.drop_index(op.f('ix_guests_phone_number'), table_name='guests')
    op.drop_index(op.f('ix_guests_email'), table_name='guests')
    op.drop_index(op.f('ix_guests_id'), table_name='guests')
    op.drop_table('guests')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop ENUM types
    postgresql.ENUM(name='payment_method').drop(op.get_bind())
    postgresql.ENUM(name='payment_status').drop(op.get_bind())
    postgresql.ENUM(name='room_maintenance_status').drop(op.get_bind())
    postgresql.ENUM(name='booking_status').drop(op.get_bind())
    postgresql.ENUM(name='permission_level').drop(op.get_bind())