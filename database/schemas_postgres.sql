-- ==============================================================================
-- Schema: PostgreSQL / Google Cloud SQL Postgres
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Option 1: Database BLOB Storage Table
-- Stores metadata AND binary BYTEA data directly in Postgres Cloud SQL
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS media_blob_store (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    img_id VARCHAR(64) NOT NULL UNIQUE,
    size BIGINT NOT NULL,
    img_type VARCHAR(64) NOT NULL,
    img_data BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_media_blob_img_id ON media_blob_store (img_id);

-- ------------------------------------------------------------------------------
-- Option 2: Hybrid Object Storage Table
-- Stores metadata AND GCS path in Postgres Cloud SQL
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS media_metadata_store (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    img_id VARCHAR(64) NOT NULL UNIQUE,
    size BIGINT NOT NULL,
    img_type VARCHAR(64) NOT NULL,
    img_Path VARCHAR(1024) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_media_meta_img_id ON media_metadata_store (img_id);
