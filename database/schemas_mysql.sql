-- ==============================================================================
-- Schema: MySQL / Google Cloud SQL
-- ==============================================================================

-- Create Database if not exists
CREATE DATABASE IF NOT EXISTS benchmark_db;
USE benchmark_db;

-- ------------------------------------------------------------------------------
-- Option 1: Database BLOB Storage Table
-- Stores both image metadata AND binary BLOB data in the database
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS media_blob_store (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    img_id VARCHAR(64) NOT NULL UNIQUE,
    size BIGINT NOT NULL,
    img_type VARCHAR(64) NOT NULL,
    img_data LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_img_id (img_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------------------------
-- Option 2: Hybrid Object Storage Table
-- Stores metadata AND cloud object storage path in the database (Image in GCS/ADLS/S3)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS media_metadata_store (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    img_id VARCHAR(64) NOT NULL UNIQUE,
    size BIGINT NOT NULL,
    img_type VARCHAR(64) NOT NULL,
    img_Path VARCHAR(1024) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_img_id (img_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
