import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

class DatabaseConfig(BaseModel):
    type: str = "sqlite"
    database: str = "benchmark.db"
    sqlite_path: str = "benchmark.db"
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    instance_connection_name: Optional[str] = None
    driver: Optional[str] = None

class StorageConfig(BaseModel):
    provider: str = "local"
    local_dir: str = "data/object_store"
    bucket_name: Optional[str] = None
    base_path: str = "benchmark_images"
    account_name: Optional[str] = None
    container_name: Optional[str] = None
    connection_string: Optional[str] = None
    region: Optional[str] = None

class ProfileConfig(BaseModel):
    cloud_provider: str
    project_id: Optional[str] = None
    database: DatabaseConfig
    storage: StorageConfig

class AppConfig(BaseModel):
    active_profile: str = "local"
    profiles: Dict[str, ProfileConfig]
    server_host: str = "127.0.0.1"
    server_port: int = 8000

def load_config(config_file: Optional[str] = None) -> AppConfig:
    if not config_file:
        config_file = str(BASE_DIR / "config.yaml")

    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    active_profile = os.getenv("APP_PROFILE", data.get("active_profile", "local"))
    
    server_data = data.get("server", {})
    server_host = os.getenv("APP_SERVER_HOST", server_data.get("host", "127.0.0.1"))
    server_port = int(os.getenv("APP_SERVER_PORT", server_data.get("port", 8000)))

    profiles: Dict[str, ProfileConfig] = {}
    for profile_name, p_data in data.get("profiles", {}).items():
        db_data = p_data.get("database", {})
        st_data = p_data.get("storage", {})

        # Environment variable overrides
        if profile_name == active_profile:
            if "DB_TYPE" in os.environ:
                db_data["type"] = os.environ["DB_TYPE"]
            if "DB_HOST" in os.environ:
                db_data["host"] = os.environ["DB_HOST"]
            if "DB_PORT" in os.environ:
                db_data["port"] = int(os.environ["DB_PORT"])
            if "DB_USER" in os.environ:
                db_data["user"] = os.environ["DB_USER"]
            if "DB_PASSWORD" in os.environ:
                db_data["password"] = os.environ["DB_PASSWORD"]
            if "DB_NAME" in os.environ:
                db_data["database"] = os.environ["DB_NAME"]
            if "STORAGE_PROVIDER" in os.environ:
                st_data["provider"] = os.environ["STORAGE_PROVIDER"]
            if "STORAGE_BUCKET" in os.environ:
                st_data["bucket_name"] = os.environ["STORAGE_BUCKET"]

        profiles[profile_name] = ProfileConfig(
            cloud_provider=p_data.get("cloud_provider", profile_name),
            project_id=p_data.get("project_id"),
            database=DatabaseConfig(**db_data),
            storage=StorageConfig(**st_data)
        )

    return AppConfig(
        active_profile=active_profile,
        profiles=profiles,
        server_host=server_host,
        server_port=server_port
    )

config = load_config()

def get_active_profile() -> ProfileConfig:
    return config.profiles[config.active_profile]
