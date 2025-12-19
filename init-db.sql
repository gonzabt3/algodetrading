-- Initial database setup
-- This runs automatically when the database is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- Create indexes for performance
-- (Will be managed by Alembic migrations, but good to have)

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE trading_db TO trading_user;
