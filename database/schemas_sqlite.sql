-- ==============================================================================
-- Schema: SQLite (Local & Fast Testing)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Option 1: Database BLOB Storage Table
-- Stores both image metadata AND binary BLOB data in SQLite
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS media_blob_store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    img_id TEXT NOT NULL UNIQUE,
    size INTEGER NOT NULL,
    img_type TEXT NOT NULL,
    img_data BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_media_blob_img_id ON media_blob_store (img_id);

-- ------------------------------------------------------------------------------
-- Option 2: Hybrid Object Storage Table
-- Stores metadata AND object storage path (Image stored in bucket or local object dir)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS media_metadata_store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    img_id TEXT NOT NULL UNIQUE,
    size INTEGER NOT NULL,
    img_type TEXT NOT NULL,
    img_Path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_media_meta_img_id ON media_metadata_store (img_id);
