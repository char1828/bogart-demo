import os
from typing import Optional
from storage.base import StorageProvider
from config import get_active_profile

class S3StorageProvider(StorageProvider):
    def __init__(self, bucket_name: Optional[str] = None, region: Optional[str] = None):
        profile = get_active_profile()
        cfg = profile.storage
        self.bucket_name = bucket_name or cfg.bucket_name or "benchmark-images"
        self.region = region or cfg.region or "us-east-1"
        self.base_path = cfg.base_path or "benchmark_images"
        self._s3_client = None

    def _get_client(self):
        if self._s3_client is None:
            try:
                import boto3
            except ImportError:
                raise ImportError("boto3 package is required for AWS S3 Storage.")
            self._s3_client = boto3.client("s3", region_name=self.region)
        return self._s3_client

    def upload_file(self, filename: str, data: bytes, content_type: str = "image/jpeg") -> str:
        s3 = self._get_client()
        s3_key = f"{self.base_path}/{filename}".replace("//", "/")
        s3.put_object(Bucket=self.bucket_name, Key=s3_key, Body=data, ContentType=content_type)
        return f"s3://{self.bucket_name}/{s3_key}"

    def download_file(self, storage_path: str) -> bytes:
        s3 = self._get_client()
        key = storage_path.replace(f"s3://{self.bucket_name}/", "").lstrip("/")
        response = s3.get_object(Bucket=self.bucket_name, Key=key)
        return response["Body"].read()

    def delete_file(self, storage_path: str) -> bool:
        try:
            s3 = self._get_client()
            key = storage_path.replace(f"s3://{self.bucket_name}/", "").lstrip("/")
            s3.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def exists(self, storage_path: str) -> bool:
        try:
            s3 = self._get_client()
            key = storage_path.replace(f"s3://{self.bucket_name}/", "").lstrip("/")
            s3.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False
