import os
from pathlib import Path
from typing import Optional
from storage.base import StorageProvider
from config import BASE_DIR, get_active_profile

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: Optional[str] = None):
        cfg = get_active_profile().storage
        target_dir = base_dir or cfg.local_dir
        self.root_dir = BASE_DIR / target_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, filename: str, data: bytes, content_type: str = "image/jpeg") -> str:
        safe_name = Path(filename).name
        target_path = self.root_dir / safe_name
        with open(target_path, "wb") as f:
            f.write(data)
        return f"local://{safe_name}"

    def download_file(self, storage_path: str) -> bytes:
        filename = storage_path.replace("local://", "").strip()
        target_path = self.root_dir / Path(filename).name
        if not target_path.exists():
            raise FileNotFoundError(f"Object not found in local storage: {storage_path}")
        with open(target_path, "rb") as f:
            return f.read()

    def delete_file(self, storage_path: str) -> bool:
        filename = storage_path.replace("local://", "").strip()
        target_path = self.root_dir / Path(filename).name
        if target_path.exists():
            target_path.unlink()
            return True
        return False

    def exists(self, storage_path: str) -> bool:
        filename = storage_path.replace("local://", "").strip()
        target_path = self.root_dir / Path(filename).name
        return target_path.exists()
