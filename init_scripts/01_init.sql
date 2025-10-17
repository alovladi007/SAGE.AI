-- Initial database setup script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database user if not exists
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'aiplatform') THEN
      CREATE ROLE aiplatform LOGIN PASSWORD 'change_me_in_production';
   END IF;
END
$do$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE academic_integrity TO aiplatform;

-- Create indexes for common queries
-- These will be created by SQLAlchemy models, but included here as backup

-- Set timezone
SET TIME ZONE 'UTC';

-- Create audit log trigger function
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

COMMENT ON DATABASE academic_integrity IS 'Academic Integrity Platform Database';
