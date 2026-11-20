import os
from typing import Optional
from storage.base import StorageProvider
from config import get_active_profile

class AzureADLSStorageProvider(StorageProvider):
    def __init__(self, connection_string: Optional[str] = None, container_name: Optional[str] = None):
        profile = get_active_profile()
        cfg = profile.storage
        self.conn_str = connection_string or cfg.connection_string or os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = container_name or cfg.container_name or "benchmark-images"
        self.base_path = cfg.base_path or "benchmark_images"
        self._client = None
        self._container_client = None

    def _get_container_client(self):
        if self._container_client is None:
            try:
                from azure.storage.blob import BlobServiceClient
            except ImportError:
                raise ImportError("azure-storage-blob package is required for Azure ADLS/Blob Storage.")
            
            if not self.conn_str:
                raise ValueError("Azure Storage connection string is missing. Please set AZURE_STORAGE_CONNECTION_STRING.")
            
            self._client = BlobServiceClient.from_connection_string(self.conn_str)
            self._container_client = self._client.get_container_client(self.container_name)
            if not self._container_client.exists():
                self._container_client.create_container()
        return self._container_client

    def upload_file(self, filename: str, data: bytes, content_type: str = "image/jpeg") -> str:
        container = self._get_container_client()
        blob_path = f"{self.base_path}/{filename}".replace("//", "/")
        blob_client = container.get_blob_client(blob_path)
        
        from azure.storage.blob import ContentSettings
        blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
        return f"abfss://{self.container_name}/{blob_path}"

    def download_file(self, storage_path: str) -> bytes:
        container = self._get_container_client()
        clean_path = storage_path.replace(f"abfss://{self.container_name}/", "").replace(f"https://", "")
        if "/" in clean_path and self.container_name in clean_path:
            clean_path = clean_path.split(f"{self.container_name}/", 1)[1]
        
        blob_client = container.get_blob_client(clean_path)
        return blob_client.download_blob().readall()

    def delete_file(self, storage_path: str) -> bool:
        try:
            container = self._get_container_client()
            clean_path = storage_path.replace(f"abfss://{self.container_name}/", "")
            blob_client = container.get_blob_client(clean_path)
            blob_client.delete_blob()
            return True
        except Exception:
            return False

    def exists(self, storage_path: str) -> bool:
        try:
            container = self._get_container_client()
            clean_path = storage_path.replace(f"abfss://{self.container_name}/", "")
            blob_client = container.get_blob_client(clean_path)
            return blob_client.exists()
        except Exception:
            return False
