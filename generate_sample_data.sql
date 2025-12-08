-- Generate Sample Data for HMS - Full Year 2025
-- This script creates realistic test bookings, payments, and invoices across all months

-- Clear existing data (careful with this in production!)
DELETE FROM invoices;
DELETE FROM payments;
DELETE FROM bookings;
DELETE FROM cancellation_policies;
DELETE FROM rooms;
DELETE FROM room_types;
DELETE FROM guests;
DELETE FROM users;

-- Reset sequences so IDs start from 1 (keeps FK references valid)
ALTER SEQUENCE IF EXISTS room_types_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS rooms_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS guests_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS cancellation_policies_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS bookings_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS payments_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS invoices_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS users_id_seq RESTART WITH 1;

-- Create Room Types if not exists
-- Create Sample Users
INSERT INTO users (username, password_hash, permission_level, is_active) VALUES
('admin', '$2b$12$YPbsCWqVWIpV7WgvKRfPm.xPkL5OLy8LNqfVzjLqZJPWQEYALPlvS', 'ADMIN', true)
ON CONFLICT DO NOTHING;

-- Create Room Types if not exists
INSERT INTO room_types (name, base_price, capacity, description) VALUES
('Single Room', 50.00, 1, 'Single occupancy room'),
('Double Room', 75.00, 2, 'Double bed room'),
('Suite', 120.00, 3, 'Luxury suite with separate living area'),
('Deluxe Suite', 180.00, 4, 'Premium deluxe suite with amenities');

-- Create Rooms if not exists
INSERT INTO rooms (number, room_type_id, price_per_night, square_meters, floor) VALUES
  ('101', (SELECT id FROM room_types WHERE name='Single Room'), 50.00, 25, 1),
  ('102', (SELECT id FROM room_types WHERE name='Single Room'), 50.00, 25, 1),
  ('103', (SELECT id FROM room_types WHERE name='Double Room'), 75.00, 35, 1),
  ('104', (SELECT id FROM room_types WHERE name='Double Room'), 75.00, 35, 1),
  ('201', (SELECT id FROM room_types WHERE name='Single Room'), 50.00, 25, 2),
  ('202', (SELECT id FROM room_types WHERE name='Single Room'), 50.00, 25, 2),
  ('203', (SELECT id FROM room_types WHERE name='Suite'), 120.00, 50, 2),
  ('204', (SELECT id FROM room_types WHERE name='Suite'), 120.00, 50, 2),
  ('301', (SELECT id FROM room_types WHERE name='Double Room'), 75.00, 35, 3),
  ('302', (SELECT id FROM room_types WHERE name='Double Room'), 75.00, 35, 3),
  ('303', (SELECT id FROM room_types WHERE name='Deluxe Suite'), 180.00, 70, 3),
  ('304', (SELECT id FROM room_types WHERE name='Deluxe Suite'), 180.00, 70, 3);

-- Create Sample Guests
INSERT INTO guests (name, surname, email) VALUES
('John', 'Smith', 'john.smith@email.com'),
('Jane', 'Doe', 'jane.doe@email.com'),
('Michael', 'Johnson', 'michael.j@email.com'),
('Sarah', 'Williams', 'sarah.w@email.com'),
('Robert', 'Brown', 'robert.brown@email.com'),
('Emily', 'Davis', 'emily.davis@email.com'),
('David', 'Miller', 'david.miller@email.com'),
('Jessica', 'Wilson', 'jessica.w@email.com'),
('James', 'Moore', 'james.moore@email.com'),
('Patricia', 'Taylor', 'patricia.t@email.com'),
('Christopher', 'Anderson', 'chris.anderson@email.com'),
('Linda', 'Thomas', 'linda.thomas@email.com'),
('Mark', 'Jackson', 'mark.jackson@email.com'),
('Barbara', 'White', 'barbara.white@email.com'),
('Donald', 'Harris', 'donald.harris@email.com'),
('Nancy', 'Martin', 'nancy.martin@email.com'),
('Joseph', 'Lee', 'joseph.lee@email.com'),
('Karen', 'Martinez', 'karen.martinez@email.com'),
('Paul', 'Garcia', 'paul.garcia@email.com'),
('Lisa', 'Rodriguez', 'lisa.rodriguez@email.com')
ON CONFLICT DO NOTHING;

-- Create Cancellation Policies
INSERT INTO cancellation_policies (name, full_refund_days, partial_refund_days, partial_refund_percentage) VALUES
('Standard', 7, 2, 50),
('Flexible', 1, 0, 0),
('Non-refundable', 0, 0, 0),
('Moderate', 3, 1, 50)
ON CONFLICT DO NOTHING;

-- Create Bookings across entire 2025 with diverse statuses
-- January (Past bookings - checked_out/no_show/cancelled)
INSERT INTO bookings (booking_number, guest_id, room_id, check_in, check_out, number_of_guests, price_per_night, total_price, status, created_at, created_by, actual_check_in, actual_check_out, cancelled_at) VALUES
('BK-2025-00001', 1, 1, '2025-01-02', '2025-01-06', 1, 50.00, 200.00, 'checked_out', '2024-12-15', 1, '2025-01-02', '2025-01-06', NULL),
('BK-2025-00002', 2, 3, '2025-01-05', '2025-01-09', 1, 75.00, 300.00, 'checked_out', '2024-12-16', 1, '2025-01-05', '2025-01-09', NULL),
('BK-2025-00003', 3, 5, '2025-01-08', '2025-01-13', 1, 50.00, 250.00, 'checked_out', '2024-12-20', 1, '2025-01-08', '2025-01-13', NULL),
('BK-2025-00004', 4, 7, '2025-01-10', '2025-01-16', 1, 120.00, 720.00, 'checked_out', '2024-12-22', 1, '2025-01-10', '2025-01-16', NULL),
('BK-2025-00005', 5, 2, '2025-01-15', '2025-01-20', 1, 75.00, 375.00, 'no_show', '2024-12-28', 1, NULL, NULL, NULL),
('BK-2025-00006', 6, 4, '2025-01-18', '2025-01-24', 1, 75.00, 450.00, 'checked_out', '2024-12-29', 1, '2025-01-18', '2025-01-24', NULL),
('BK-2025-00007', 7, 9, '2025-01-22', '2025-01-27', 1, 75.00, 375.00, 'cancelled', '2025-01-05', 1, NULL, NULL, '2025-01-12'),
('BK-2025-00008', 8, 11, '2025-01-25', '2025-01-31', 1, 180.00, 1080.00, 'checked_out', '2025-01-08', 1, '2025-01-25', '2025-01-31', NULL),

-- February (Past bookings)
('BK-2025-00009', 1, 3, '2025-02-01', '2025-02-05', 1, 75.00, 300.00, 'checked_out', '2025-01-10', 1, '2025-02-01', '2025-02-05', NULL),
('BK-2025-00010', 2, 5, '2025-02-05', '2025-02-10', 1, 50.00, 250.00, 'checked_out', '2025-01-18', 1, '2025-02-05', '2025-02-10', NULL),
('BK-2025-00011', 3, 7, '2025-02-08', '2025-02-14', 1, 120.00, 720.00, 'checked_out', '2025-01-20', 1, '2025-02-08', '2025-02-14', NULL),
('BK-2025-00012', 4, 1, '2025-02-12', '2025-02-18', 1, 50.00, 300.00, 'checked_out', '2025-01-28', 1, '2025-02-12', '2025-02-18', NULL),
('BK-2025-00013', 5, 9, '2025-02-15', '2025-02-22', 1, 75.00, 525.00, 'checked_out', '2025-02-01', 1, '2025-02-15', '2025-02-22', NULL),
('BK-2025-00014', 6, 11, '2025-02-20', '2025-02-28', 1, 180.00, 1440.00, 'cancelled', '2025-02-05', 1, NULL, NULL, '2025-02-15'),

-- March (Past bookings)
('BK-2025-00015', 7, 2, '2025-03-01', '2025-03-05', 1, 75.00, 300.00, 'checked_out', '2025-02-10', 1, '2025-03-01', '2025-03-05', NULL),
('BK-2025-00016', 8, 4, '2025-03-05', '2025-03-11', 1, 75.00, 450.00, 'checked_out', '2025-02-18', 1, '2025-03-05', '2025-03-11', NULL),
('BK-2025-00017', 9, 6, '2025-03-10', '2025-03-16', 1, 75.00, 450.00, 'no_show', '2025-02-25', 1, NULL, NULL, NULL),
('BK-2025-00018', 10, 8, '2025-03-15', '2025-03-22', 1, 120.00, 840.00, 'checked_out', '2025-03-01', 1, '2025-03-15', '2025-03-22', NULL),
('BK-2025-00019', 11, 10, '2025-03-20', '2025-03-27', 1, 75.00, 525.00, 'checked_out', '2025-03-05', 1, '2025-03-20', '2025-03-27', NULL),
('BK-2025-00020', 12, 12, '2025-03-25', '2025-03-31', 1, 180.00, 1080.00, 'checked_out', '2025-03-10', 1, '2025-03-25', '2025-03-31', NULL),

-- April (Spring - mostly checked_out, some pending)
('BK-2025-00021', 1, 1, '2025-04-02', '2025-04-08', 1, 50.00, 300.00, 'checked_out', '2025-03-15', 1, '2025-04-02', '2025-04-08', NULL),
('BK-2025-00022', 2, 3, '2025-04-05', '2025-04-12', 1, 75.00, 525.00, 'checked_out', '2025-03-18', 1, '2025-04-05', '2025-04-12', NULL),
('BK-2025-00023', 3, 5, '2025-04-08', '2025-04-15', 1, 50.00, 350.00, 'checked_out', '2025-03-20', 1, '2025-04-08', '2025-04-15', NULL),
('BK-2025-00024', 4, 7, '2025-04-12', '2025-04-19', 1, 120.00, 840.00, 'cancelled', '2025-03-28', 1, NULL, NULL, '2025-04-05'),
('BK-2025-00025', 5, 9, '2025-04-15', '2025-04-22', 1, 75.00, 525.00, 'checked_out', '2025-04-01', 1, '2025-04-15', '2025-04-22', NULL),
('BK-2025-00026', 6, 11, '2025-04-20', '2025-04-27', 1, 180.00, 1260.00, 'checked_out', '2025-04-05', 1, '2025-04-20', '2025-04-27', NULL),
('BK-2025-00027', 7, 2, '2025-04-22', '2025-04-29', 1, 75.00, 525.00, 'checked_out', '2025-04-08', 1, '2025-04-22', '2025-04-29', NULL),
('BK-2025-00028', 8, 4, '2025-04-25', '2025-05-02', 1, 75.00, 525.00, 'pending', '2025-04-10', 1, NULL, NULL, NULL),

-- May (More spring bookings)
('BK-2025-00029', 9, 6, '2025-05-01', '2025-05-08', 1, 75.00, 525.00, 'checked_out', '2025-04-15', 1, '2025-05-01', '2025-05-08', NULL),
('BK-2025-00030', 10, 8, '2025-05-05', '2025-05-13', 1, 120.00, 960.00, 'checked_out', '2025-04-20', 1, '2025-05-05', '2025-05-13', NULL),
('BK-2025-00031', 11, 10, '2025-05-10', '2025-05-18', 1, 75.00, 600.00, 'no_show', '2025-04-25', 1, NULL, NULL, NULL),
('BK-2025-00032', 12, 12, '2025-05-15', '2025-05-23', 1, 180.00, 1440.00, 'checked_out', '2025-05-01', 1, '2025-05-15', '2025-05-23', NULL),
('BK-2025-00033', 13, 1, '2025-05-20', '2025-05-28', 1, 50.00, 400.00, 'checked_out', '2025-05-05', 1, '2025-05-20', '2025-05-28', NULL),
('BK-2025-00034', 14, 3, '2025-05-22', '2025-05-31', 1, 75.00, 675.00, 'cancelled', '2025-05-08', 1, NULL, NULL, '2025-05-20'),

-- June (Summer starts - mix of statuses)
('BK-2025-00035', 15, 5, '2025-06-01', '2025-06-10', 1, 50.00, 450.00, 'checked_out', '2025-05-15', 1, '2025-06-01', '2025-06-10', NULL),
('BK-2025-00036', 16, 7, '2025-06-05', '2025-06-15', 1, 120.00, 1200.00, 'checked_out', '2025-05-18', 1, '2025-06-05', '2025-06-15', NULL),
('BK-2025-00037', 17, 9, '2025-06-08', '2025-06-18', 1, 75.00, 750.00, 'checked_out', '2025-05-22', 1, '2025-06-08', '2025-06-18', NULL),
('BK-2025-00038', 18, 11, '2025-06-12', '2025-06-22', 1, 180.00, 1800.00, 'checked_out', '2025-05-28', 1, '2025-06-12', '2025-06-22', NULL),
('BK-2025-00039', 1, 2, '2025-06-15', '2025-06-25', 1, 75.00, 750.00, 'checked_out', '2025-06-01', 1, '2025-06-15', '2025-06-25', NULL),
('BK-2025-00040', 2, 4, '2025-06-20', '2025-06-30', 1, 75.00, 750.00, 'checked_out', '2025-06-05', 1, '2025-06-20', '2025-06-30', NULL),
('BK-2025-00041', 3, 6, '2025-06-22', '2025-07-02', 1, 75.00, 750.00, 'pending', '2025-06-08', 1, NULL, NULL, NULL),

-- July (Peak summer)
('BK-2025-00042', 4, 8, '2025-07-01', '2025-07-12', 1, 120.00, 1320.00, 'checked_out', '2025-06-10', 1, '2025-07-01', '2025-07-12', NULL),
('BK-2025-00043', 5, 10, '2025-07-05', '2025-07-16', 1, 75.00, 825.00, 'checked_out', '2025-06-15', 1, '2025-07-05', '2025-07-16', NULL),
('BK-2025-00044', 6, 12, '2025-07-08', '2025-07-20', 1, 180.00, 2160.00, 'checked_out', '2025-06-20', 1, '2025-07-08', '2025-07-20', NULL),
('BK-2025-00045', 7, 1, '2025-07-10', '2025-07-22', 1, 50.00, 600.00, 'no_show', '2025-06-25', 1, NULL, NULL, NULL),
('BK-2025-00046', 8, 3, '2025-07-15', '2025-07-27', 1, 75.00, 900.00, 'checked_out', '2025-07-01', 1, '2025-07-15', '2025-07-27', NULL),
('BK-2025-00047', 9, 5, '2025-07-18', '2025-07-30', 1, 50.00, 600.00, 'checked_out', '2025-07-05', 1, '2025-07-18', '2025-07-30', NULL),
('BK-2025-00048', 10, 7, '2025-07-22', '2025-08-03', 1, 120.00, 1320.00, 'cancelled', '2025-07-10', 1, NULL, NULL, '2025-07-18'),
('BK-2025-00049', 11, 9, '2025-07-25', '2025-08-05', 1, 75.00, 825.00, 'checked_out', '2025-07-12', 1, '2025-07-25', '2025-08-05', NULL),

-- August (Late summer)
('BK-2025-00050', 12, 11, '2025-08-01', '2025-08-12', 1, 180.00, 1980.00, 'checked_out', '2025-07-15', 1, '2025-08-01', '2025-08-12', NULL),
('BK-2025-00051', 13, 2, '2025-08-05', '2025-08-17', 1, 75.00, 900.00, 'checked_out', '2025-07-20', 1, '2025-08-05', '2025-08-17', NULL),
('BK-2025-00052', 14, 4, '2025-08-08', '2025-08-20', 1, 75.00, 900.00, 'checked_out', '2025-07-25', 1, '2025-08-08', '2025-08-20', NULL),
('BK-2025-00053', 15, 6, '2025-08-12', '2025-08-24', 1, 75.00, 900.00, 'pending', '2025-08-01', 1, NULL, NULL, NULL),
('BK-2025-00054', 16, 8, '2025-08-15', '2025-08-27', 1, 120.00, 1440.00, 'checked_out', '2025-08-05', 1, '2025-08-15', '2025-08-27', NULL),
('BK-2025-00055', 17, 10, '2025-08-20', '2025-09-01', 1, 75.00, 900.00, 'checked_out', '2025-08-10', 1, '2025-08-20', '2025-09-01', NULL),
('BK-2025-00056', 18, 12, '2025-08-25', '2025-09-05', 1, 180.00, 1980.00, 'no_show', '2025-08-15', 1, NULL, NULL, NULL),

-- September (Fall begins)
('BK-2025-00057', 19, 1, '2025-09-01', '2025-09-10', 1, 50.00, 450.00, 'checked_out', '2025-08-20', 1, '2025-09-01', '2025-09-10', NULL),
('BK-2025-00058', 20, 3, '2025-09-05', '2025-09-14', 1, 75.00, 675.00, 'checked_out', '2025-08-25', 1, '2025-09-05', '2025-09-14', NULL),
('BK-2025-00059', 1, 5, '2025-09-08', '2025-09-17', 1, 50.00, 450.00, 'pending', '2025-08-30', 1, NULL, NULL, NULL),
('BK-2025-00060', 2, 7, '2025-09-12', '2025-09-21', 1, 120.00, 1080.00, 'checked_out', '2025-09-01', 1, '2025-09-12', '2025-09-21', NULL),
('BK-2025-00061', 3, 9, '2025-09-15', '2025-09-24', 1, 75.00, 675.00, 'cancelled', '2025-09-05', 1, NULL, NULL, '2025-09-10'),
('BK-2025-00062', 4, 11, '2025-09-20', '2025-09-29', 1, 180.00, 1620.00, 'checked_out', '2025-09-10', 1, '2025-09-20', '2025-09-29', NULL),

-- October (Fall - transition to winter)
('BK-2025-00063', 5, 2, '2025-10-01', '2025-10-09', 1, 75.00, 600.00, 'checked_out', '2025-09-15', 1, '2025-10-01', '2025-10-09', NULL),
('BK-2025-00064', 6, 4, '2025-10-05', '2025-10-13', 1, 75.00, 600.00, 'checked_out', '2025-09-20', 1, '2025-10-05', '2025-10-13', NULL),
('BK-2025-00065', 7, 6, '2025-10-08', '2025-10-16', 1, 75.00, 600.00, 'pending', '2025-09-25', 1, NULL, NULL, NULL),
('BK-2025-00066', 8, 8, '2025-10-12', '2025-10-20', 1, 120.00, 960.00, 'checked_out', '2025-10-01', 1, '2025-10-12', '2025-10-20', NULL),
('BK-2025-00067', 9, 10, '2025-10-15', '2025-10-23', 1, 75.00, 600.00, 'checked_out', '2025-10-05', 1, '2025-10-15', '2025-10-23', NULL),
('BK-2025-00068', 10, 12, '2025-10-20', '2025-10-28', 1, 180.00, 1440.00, 'no_show', '2025-10-10', 1, NULL, NULL, NULL),

-- November (Pre-winter)
('BK-2025-00069', 11, 1, '2025-11-01', '2025-11-05', 1, 50.00, 200.00, 'checked_out', '2025-10-15', 1, '2025-11-01', '2025-11-05', NULL),
('BK-2025-00070', 12, 3, '2025-11-03', '2025-11-07', 1, 75.00, 300.00, 'checked_out', '2025-10-18', 1, '2025-11-03', '2025-11-07', NULL),
('BK-2025-00071', 13, 5, '2025-11-08', '2025-11-12', 1, 50.00, 200.00, 'pending', '2025-10-22', 1, NULL, NULL, NULL),
('BK-2025-00072', 14, 7, '2025-11-10', '2025-11-15', 1, 120.00, 600.00, 'checked_out', '2025-10-25', 1, '2025-11-10', '2025-11-15', NULL),
('BK-2025-00073', 15, 9, '2025-11-12', '2025-11-17', 1, 75.00, 375.00, 'checked_out', '2025-10-28', 1, '2025-11-12', '2025-11-17', NULL),
('BK-2025-00074', 16, 11, '2025-11-15', '2025-11-20', 1, 180.00, 900.00, 'checked_out', '2025-11-01', 1, '2025-11-15', '2025-11-20', NULL),
('BK-2025-00075', 17, 2, '2025-11-18', '2025-11-22', 1, 75.00, 300.00, 'cancelled', '2025-11-05', 1, NULL, NULL, '2025-11-10'),
('BK-2025-00076', 18, 4, '2025-11-20', '2025-11-25', 1, 75.00, 375.00, 'checked_out', '2025-11-08', 1, '2025-11-20', '2025-11-25', NULL),
('BK-2025-00077', 19, 6, '2025-11-22', '2025-11-27', 1, 75.00, 375.00, 'checked_out', '2025-11-10', 1, '2025-11-22', '2025-11-27', NULL),
('BK-2025-00078', 20, 8, '2025-11-25', '2025-11-29', 1, 120.00, 480.00, 'checked_in', '2025-11-15', 1, '2025-11-25', NULL, NULL),

-- December (Winter season - mix of past and current)
('BK-2025-00079', 1, 10, '2025-12-01', '2025-12-05', 1, 75.00, 300.00, 'checked_out', '2025-11-10', 1, '2025-12-01', '2025-12-05', NULL),
('BK-2025-00080', 2, 12, '2025-12-02', '2025-12-08', 1, 180.00, 1080.00, 'checked_in', '2025-11-15', 1, '2025-12-02', NULL, NULL),
('BK-2025-00081', 3, 1, '2025-12-05', '2025-12-10', 1, 50.00, 250.00, 'confirmed', '2025-11-20', 1, NULL, NULL, NULL),
('BK-2025-00082', 4, 3, '2025-12-07', '2025-12-12', 1, 75.00, 375.00, 'confirmed', '2025-11-25', 1, NULL, NULL, NULL),
('BK-2025-00083', 5, 5, '2025-12-08', '2025-12-15', 1, 50.00, 350.00, 'confirmed', '2025-11-27', 1, NULL, NULL, NULL),
('BK-2025-00084', 6, 7, '2025-12-10', '2025-12-14', 1, 120.00, 480.00, 'pending', '2025-11-28', 1, NULL, NULL, NULL),
('BK-2025-00085', 7, 9, '2025-12-12', '2025-12-17', 1, 75.00, 375.00, 'confirmed', '2025-11-29', 1, NULL, NULL, NULL),
('BK-2025-00086', 8, 11, '2025-12-14', '2025-12-20', 1, 180.00, 1080.00, 'confirmed', '2025-12-01', 1, NULL, NULL, NULL),
('BK-2025-00087', 9, 2, '2025-12-16', '2025-12-21', 1, 75.00, 375.00, 'pending', '2025-12-02', 1, NULL, NULL, NULL),
('BK-2025-00088', 10, 4, '2025-12-18', '2025-12-25', 1, 75.00, 525.00, 'pending', '2025-12-05', 1, NULL, NULL, NULL),
('BK-2025-00089', 11, 6, '2025-12-20', '2025-12-27', 1, 75.00, 525.00, 'confirmed', '2025-12-08', 1, NULL, NULL, NULL),
('BK-2025-00090', 12, 8, '2025-12-22', '2025-12-29', 1, 120.00, 840.00, 'confirmed', '2025-12-10', 1, NULL, NULL, NULL),
('BK-2025-00091', 13, 10, '2025-12-24', '2025-12-31', 1, 75.00, 525.00, 'pending', '2025-12-12', 1, NULL, NULL, NULL);

-- Create Payments (one per booking, some pending, most paid)
INSERT INTO payments (booking_id, amount, currency, payment_method, method, payment_status, status, processed_at) 
SELECT 
  b.id,
  b.total_price,
  'USD',
  (CASE WHEN (b.id % 3 = 0) THEN 'bank_transfer' WHEN (b.id % 3 = 1) THEN 'credit_card' ELSE 'cash' END)::payment_method,
  CASE WHEN (b.id % 3 = 0) THEN 'BANK_TRANSFER' WHEN (b.id % 3 = 1) THEN 'CREDIT_CARD' ELSE 'CASH' END,
  CASE 
    WHEN b.status = 'cancelled' THEN 'refunded'::payment_status
    WHEN b.check_in <= CURRENT_DATE THEN 'paid'::payment_status
    ELSE 'pending'::payment_status
  END,
  CASE 
    WHEN b.status = 'cancelled' THEN 'REFUNDED'::payment_status_v2
    WHEN b.check_in <= CURRENT_DATE THEN 'PAID'::payment_status_v2
    ELSE 'PENDING'::payment_status_v2
  END,
  CASE 
    WHEN b.status = 'cancelled' THEN b.created_at + INTERVAL '2 days'
    WHEN b.check_in <= CURRENT_DATE THEN b.created_at + INTERVAL '1 day'
    ELSE NULL
  END
FROM bookings b
WHERE NOT EXISTS (SELECT 1 FROM payments WHERE booking_id = b.id);

-- Create Invoices (one per booking)
INSERT INTO invoices (booking_id, invoice_number, subtotal, tax, total)
SELECT 
  b.id,
  'INV-' || TO_CHAR(b.created_at, 'YYYY') || '-' || LPAD(b.id::TEXT, 5, '0'),
  b.total_price,
  (b.total_price * 0.1)::DECIMAL(10, 2),
  (b.total_price * 1.1)::DECIMAL(10, 2)
FROM bookings b
WHERE NOT EXISTS (SELECT 1 FROM invoices WHERE booking_id = b.id);

-- Summary
SELECT 'Sample data generation complete!' AS status;
SELECT COUNT(*) as total_guests FROM guests;
SELECT COUNT(*) as total_rooms FROM rooms;
SELECT COUNT(*) as total_bookings FROM bookings;
SELECT COUNT(*) as total_payments FROM payments;
SELECT COUNT(*) as total_invoices FROM invoices;
SELECT SUM(amount) as total_revenue FROM payments WHERE status = 'PAID';
SELECT COUNT(*) as confirmed_bookings FROM bookings WHERE status = 'confirmed';
SELECT COUNT(*) as cancelled_bookings FROM bookings WHERE status = 'cancelled';
