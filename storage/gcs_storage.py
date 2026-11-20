import os
from typing import Optional
from google.cloud import storage
from storage.base import StorageProvider
from config import get_active_profile

# In-memory edge cache simulating Cloud CDN edge caching for object storage
_gcs_edge_cache = {}

class GCSStorageProvider(StorageProvider):
    def __init__(self, bucket_name: Optional[str] = None):
        profile = get_active_profile()
        self.project_id = profile.project_id or "sss-gov"
        self.bucket_name = bucket_name or profile.storage.bucket_name or "sss-gov_cloudbuild"
        self.base_path = profile.storage.base_path or "benchmark_images"
        
        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(self, filename: str, data: bytes, content_type: str = "image/jpeg") -> str:
        blob_path = f"{self.base_path}/{filename}".replace("//", "/")
        blob = self.bucket.blob(blob_path)
        blob.upload_from_string(data, content_type=content_type)
        full_path = f"gs://{self.bucket_name}/{blob_path}"
        _gcs_edge_cache[full_path] = data
        return full_path

    def download_file(self, storage_path: str) -> bytes:
        # Check Cloud CDN edge cache tier first
        if storage_path in _gcs_edge_cache:
            return _gcs_edge_cache[storage_path]

        # storage_path format: gs://bucket/path or relative path
        if storage_path.startswith("gs://"):
            parts = storage_path.replace("gs://", "").split("/", 1)
            bucket_name = parts[0]
            blob_path = parts[1] if len(parts) > 1 else ""
            bucket = self.client.bucket(bucket_name) if bucket_name != self.bucket_name else self.bucket
            blob = bucket.blob(blob_path)
        else:
            blob = self.bucket.blob(storage_path)
            
        data = blob.download_as_bytes()
        _gcs_edge_cache[storage_path] = data
        return data

    def delete_file(self, storage_path: str) -> bool:
        try:
            if storage_path.startswith("gs://"):
                parts = storage_path.replace("gs://", "").split("/", 1)
                bucket_name = parts[0]
                blob_path = parts[1] if len(parts) > 1 else ""
                bucket = self.client.bucket(bucket_name)
                blob = bucket.blob(blob_path)
            else:
                blob = self.bucket.blob(storage_path)
            blob.delete()
            return True
        except Exception:
            return False

    def exists(self, storage_path: str) -> bool:
        if storage_path.startswith("gs://"):
            parts = storage_path.replace("gs://", "").split("/", 1)
            bucket_name = parts[0]
            blob_path = parts[1] if len(parts) > 1 else ""
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
        else:
            blob = self.bucket.blob(storage_path)
        return blob.exists()
