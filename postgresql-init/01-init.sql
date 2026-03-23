-- Migrated from Oracle to PostgreSQL according to SQL check item 1: Use lowercase for identifiers.
-- This script runs automatically when PostgreSQL container starts.
-- It creates the photoalbum schema and grants necessary privileges.
-- Note: The POSTGRES_USER=photoalbum already creates the user via the Docker image environment variables.
-- This script handles any additional setup needed.

-- Grant privileges on the public schema to the photoalbum user
GRANT ALL PRIVILEGES ON SCHEMA public TO photoalbum;

-- Grant default privileges for future objects created in the public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO photoalbum;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO photoalbum;
