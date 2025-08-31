-- Initialize Aetheria database
-- This script sets up basic extensions and configurations

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone to UTC for all connections
ALTER DATABASE aetheria_db SET timezone TO 'UTC';

-- Basic indexes and configurations will be added here
-- when we implement the actual database schema

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Aetheria database initialized successfully';
END
$$;
