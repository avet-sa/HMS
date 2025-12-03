-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS room_types CASCADE;
DROP TABLE IF EXISTS guests CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop existing types if they exist
DROP TYPE IF EXISTS permission_level CASCADE;
DROP TYPE IF EXISTS booking_status CASCADE;
DROP TYPE IF EXISTS room_maintenance_status CASCADE;
DROP TYPE IF EXISTS payment_status CASCADE;
DROP TYPE IF EXISTS payment_method CASCADE;

-- Create ENUM types
CREATE TYPE permission_level AS ENUM ('REGULAR', 'MANAGER', 'ADMIN');
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'no_show');
CREATE TYPE room_maintenance_status AS ENUM ('available', 'maintenance', 'out_of_service');
CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'partially_paid', 'refunded');
CREATE TYPE payment_method AS ENUM ('cash', 'credit_card', 'debit_card', 'bank_transfer', 'online');

-- -----------------------------
-- Users Table
-- -----------------------------
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    permission_level permission_level DEFAULT 'REGULAR' NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_username ON users(username);

-- -----------------------------
-- Guests Table
-- -----------------------------
CREATE TABLE guests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    phone_number VARCHAR(30),
    email VARCHAR(100) UNIQUE,
    nationality VARCHAR(50),
    gender VARCHAR(10),
    birth_date DATE,
    document_type VARCHAR(20),
    document_id VARCHAR(50),
    loyalty_points INTEGER DEFAULT 0,
    vip_tier INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_guests_email ON guests(email);
CREATE INDEX idx_guests_phone_number ON guests(phone_number);

-- -----------------------------
-- Room Types Table
-- -----------------------------
CREATE TABLE room_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    base_price NUMERIC(10, 2) NOT NULL,
    capacity INTEGER NOT NULL,
    description VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- -----------------------------
-- Rooms Table
-- -----------------------------
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    number VARCHAR(10) UNIQUE NOT NULL,
    room_type_id INTEGER NOT NULL REFERENCES room_types(id),
    price_per_night NUMERIC(10, 2) NOT NULL,
    square_meters INTEGER,
    floor INTEGER,
    maintenance_status room_maintenance_status DEFAULT 'available' NOT NULL,
    has_view BOOLEAN DEFAULT FALSE,
    is_smoking BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_rooms_number ON rooms(number);
CREATE INDEX idx_rooms_room_type_id ON rooms(room_type_id);

-- -----------------------------
-- Bookings Table
-- -----------------------------
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    booking_number VARCHAR(20) UNIQUE NOT NULL,
    guest_id INTEGER NOT NULL REFERENCES guests(id) ON DELETE CASCADE,
    room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    number_of_guests INTEGER NOT NULL DEFAULT 1,
    number_of_nights INTEGER NOT NULL,
    price_per_night NUMERIC(10, 2) NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL,
    status booking_status DEFAULT 'pending' NOT NULL,
    special_requests VARCHAR(500),
    internal_notes VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT check_dates CHECK (check_out > check_in),
    CONSTRAINT check_guests_positive CHECK (number_of_guests > 0),
    CONSTRAINT check_nights_positive CHECK (number_of_nights > 0)
);

CREATE INDEX idx_bookings_booking_number ON bookings(booking_number);
CREATE INDEX idx_bookings_guest_id ON bookings(guest_id);
CREATE INDEX idx_bookings_room_id ON bookings(room_id);
CREATE INDEX idx_bookings_check_in ON bookings(check_in);
CREATE INDEX idx_bookings_check_out ON bookings(check_out);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_created_at ON bookings(created_at);

-- Composite index for availability queries
CREATE INDEX idx_bookings_dates ON bookings(check_in, check_out);

-- -----------------------------
-- Payments Table
-- -----------------------------
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL,
    payment_method payment_method NOT NULL,
    payment_status payment_status DEFAULT 'pending' NOT NULL,
    transaction_id VARCHAR(100),
    payment_date TIMESTAMP WITH TIME ZONE,
    notes VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT check_amount_positive CHECK (amount > 0)
);

CREATE INDEX idx_payments_booking_id ON payments(booking_id);

-- -----------------------------
-- Triggers for updated_at
-- -----------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_guests_updated_at
    BEFORE UPDATE ON guests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_room_types_updated_at
    BEFORE UPDATE ON room_types
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rooms_updated_at
    BEFORE UPDATE ON rooms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at
    BEFORE UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- -----------------------------
-- Sample Data (Optional)
-- -----------------------------
-- Insert sample room types
INSERT INTO room_types (name, base_price, capacity, description) VALUES
    ('Single', 100.00, 1, 'Comfortable single room with one bed'),
    ('Double', 150.00, 2, 'Spacious double room with queen bed'),
    ('Suite', 300.00, 4, 'Luxurious suite with separate living area'),
    ('Deluxe', 200.00, 2, 'Premium room with city view');

-- Insert sample rooms
INSERT INTO rooms (number, room_type_id, price_per_night, square_meters, floor, has_view) VALUES
    ('101', 1, 100.00, 20, 1, false),
    ('102', 1, 100.00, 20, 1, false),
    ('201', 2, 150.00, 30, 2, true),
    ('202', 2, 150.00, 30, 2, true),
    ('301', 3, 300.00, 60, 3, true),
    ('401', 4, 200.00, 35, 4, true);

-- Insert sample user
INSERT INTO users (username, password_hash, permission_level) VALUES
    ('admin', 'hashed_password_here', 'ADMIN'),
    ('manager', 'hashed_password_here', 'MANAGER'),
    ('receptionist', 'hashed_password_here', 'REGULAR');

COMMENT ON TABLE users IS 'System users with different permission levels';
COMMENT ON TABLE guests IS 'Hotel guests information';
COMMENT ON TABLE room_types IS 'Different types of rooms available';
COMMENT ON TABLE rooms IS 'Individual room inventory';
COMMENT ON TABLE bookings IS 'Room reservations and check-ins';
COMMENT ON TABLE payments IS 'Payment transactions for bookings';

SELECT * FROM users ;

DO $$
DECLARE
    row RECORD;
BEGIN
    FOR row IN SELECT table_name
               FROM information_schema.tables
               WHERE table_type = 'BASE TABLE'
                 AND table_schema = 'public' -- Adjust schema if needed
                 AND table_name NOT LIKE 'pg_%' -- Exclude system tables
                 AND table_name NOT LIKE 'sql_%' -- Exclude system tables
    LOOP
        EXECUTE format('TRUNCATE TABLE %I CASCADE;', row.table_name);
    END LOOP;
END;
$$;