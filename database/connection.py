import os
import sqlite3
import pymysql
import pymssql
import pg8000.dbapi
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from config import get_active_profile, BASE_DIR

class DatabaseManager:
    def __init__(self):
        self.profile = get_active_profile()
        self.db_cfg = self.profile.database

    def get_connection(self):
        # Always reload active profile config
        self.profile = get_active_profile()
        self.db_cfg = self.profile.database
        db_type = self.db_cfg.type.lower()
        
        if db_type == "sqlite":
            db_path = BASE_DIR / self.db_cfg.sqlite_path
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn

        elif "postgres" in db_type or "pgsql" in db_type:
            # Cloud SQL PostgreSQL via pg8000
            conn = pg8000.dbapi.connect(
                host=self.db_cfg.host or "127.0.0.1",
                port=self.db_cfg.port or 5432,
                user=self.db_cfg.user or "postgres",
                password=self.db_cfg.password or "",
                database=self.db_cfg.database or "benchmark_db",
                ssl_context=True
            )
            return conn

        elif "mysql" in db_type:
            conn = pymysql.connect(
                host=self.db_cfg.host or "127.0.0.1",
                port=self.db_cfg.port or 3306,
                user=self.db_cfg.user or "root",
                password=self.db_cfg.password or "",
                database=self.db_cfg.database or "benchmark_db",
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return conn

        elif "mssql" in db_type or "azure" in db_type:
            conn = pymssql.connect(
                server=self.db_cfg.host,
                port=self.db_cfg.port or 1433,
                user=self.db_cfg.user,
                password=self.db_cfg.password,
                database=self.db_cfg.database,
                as_dict=True
            )
            return conn

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def initialize_schema(self):
        """Initializes tables if they do not exist based on active profile."""
        self.profile = get_active_profile()
        self.db_cfg = self.profile.database
        db_type = self.db_cfg.type.lower()
        conn = self.get_connection()

        if db_type == "sqlite":
            schema_file = BASE_DIR / "database" / "schemas_sqlite.sql"
            with open(schema_file, "r", encoding="utf-8") as f:
                sql = f.read()
            with conn:
                conn.executescript(sql)
            conn.close()

        elif "postgres" in db_type or "pgsql" in db_type:
            schema_file = BASE_DIR / "database" / "schemas_postgres.sql"
            with open(schema_file, "r", encoding="utf-8") as f:
                sql = f.read()
            cursor = conn.cursor()
            for statement in sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)
            conn.commit()
            conn.close()

        elif "mysql" in db_type:
            schema_file = BASE_DIR / "database" / "schemas_mysql.sql"
            with open(schema_file, "r", encoding="utf-8") as f:
                commands = f.read().split(";")
            with conn.cursor() as cursor:
                for cmd in commands:
                    cmd_clean = cmd.strip()
                    if cmd_clean and not cmd_clean.startswith("--") and not cmd_clean.upper().startswith("CREATE DATABASE") and not cmd_clean.upper().startswith("USE "):
                        cursor.execute(cmd_clean)
            conn.close()

        elif "mssql" in db_type or "azure" in db_type:
            schema_file = BASE_DIR / "database" / "schemas_mssql.sql"
            with open(schema_file, "r", encoding="utf-8") as f:
                commands = f.read().split("GO")
            cursor = conn.cursor()
            for cmd in commands:
                cmd_clean = cmd.strip()
                if cmd_clean and not cmd_clean.startswith("--"):
                    cursor.execute(cmd_clean)
            conn.commit()
            conn.close()

db_manager = DatabaseManager()
