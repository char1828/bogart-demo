-- ==============================================================================
-- Schema: Microsoft SQL Server / Azure SQL Database
-- ==============================================================================

IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'benchmark_db')
BEGIN
    CREATE DATABASE benchmark_db;
END
GO

USE benchmark_db;
GO

-- ------------------------------------------------------------------------------
-- Option 1: Database BLOB Storage Table
-- Stores both image metadata AND binary VARBINARY(MAX) data in MSSQL
-- ------------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'media_blob_store')
BEGIN
    CREATE TABLE media_blob_store (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        img_id NVARCHAR(64) NOT NULL UNIQUE,
        size BIGINT NOT NULL,
        img_type NVARCHAR(64) NOT NULL,
        img_data VARBINARY(MAX) NOT NULL,
        created_at DATETIME2 DEFAULT GETUTCDATE()
    );
    CREATE INDEX idx_media_blob_img_id ON media_blob_store (img_id);
END
GO

-- ------------------------------------------------------------------------------
-- Option 2: Hybrid Object Storage Table
-- Stores metadata AND ADLS/Azure Blob path in MSSQL
-- ------------------------------------------------------------------------------
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'media_metadata_store')
BEGIN
    CREATE TABLE media_metadata_store (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        img_id NVARCHAR(64) NOT NULL UNIQUE,
        size BIGINT NOT NULL,
        img_type NVARCHAR(64) NOT NULL,
        img_Path NVARCHAR(1024) NOT NULL,
        created_at DATETIME2 DEFAULT GETUTCDATE()
    );
    CREATE INDEX idx_media_meta_img_id ON media_metadata_store (img_id);
END
GO
