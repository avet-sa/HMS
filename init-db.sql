-- PostgreSQL initialization script
-- The postgres superuser is created by default with POSTGRES_PASSWORD
-- This ensures the database and permissions are properly configured

-- Verify the hms database exists (it should be created by POSTGRES_DB)
-- Grant all privileges on hms database to postgres user
GRANT ALL PRIVILEGES ON DATABASE hms TO postgres;

-- Create schema if needed
CREATE SCHEMA IF NOT EXISTS public;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;

