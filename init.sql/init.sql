-- Create database if it doesn't exist
SELECT 'CREATE DATABASE ml_ops_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ml_ops_db')\gexec

-- Connect to the database
\c ml_ops_db


-- Create enum types
DO $$ BEGIN
    CREATE TYPE deployment_status AS ENUM ('pending', 'running', 'completed', 'failed', 'preempted');
    CREATE TYPE deployment_priority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create tables
CREATE TABLE IF NOT EXISTS organizations (
    id BIGINT  PRIMARY KEY SERIAL,
    name VARCHAR NOT NULL,
    invite_code VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    organization_id BIGINT REFERENCES organizations(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS clusters (
    id SERIAL PRIMARY KEY ,
    name VARCHAR NOT NULL,
    organization_id BIGINT NOT NULL REFERENCES organizations(id),
    owner_id BIGINT NOT NULL REFERENCES users(id),
    total_ram_gb FLOAT NOT NULL,
    total_cpu_cores INTEGER NOT NULL,
    total_gpu_count INTEGER NOT NULL,
    available_ram_gb FLOAT NOT NULL,
    available_cpu_cores INTEGER NOT NULL,
    available_gpu_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS deployments (
    id SERIAL  PRIMARY KEY ,
    name VARCHAR NOT NULL,
    user_id BIGINT NOT NULL REFERENCES users(id),
    cluster_id BIGINT NOT NULL REFERENCES clusters(id),
    docker_image VARCHAR NOT NULL,
    required_ram_gb FLOAT NOT NULL,
    required_cpu_cores INTEGER NOT NULL,
    required_gpu_count INTEGER NOT NULL,
    priority deployment_priority DEFAULT 'MEDIUM',
    status deployment_status DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    meta_data JSONB
);

-- Create indexes
-- CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization_id);
-- CREATE INDEX IF NOT EXISTS idx_clusters_organization ON clusters(organization_id);
-- CREATE INDEX IF NOT EXISTS idx_clusters_owner ON clusters(owner_id);
-- CREATE INDEX IF NOT EXISTS idx_deployments_user ON deployments(user_id);
-- CREATE INDEX IF NOT EXISTS idx_deployments_cluster ON deployments(cluster_id);
-- CREATE INDEX IF NOT EXISTS idx_deployments_status ON deployments(status); 