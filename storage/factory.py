from typing import Optional
from storage.base import StorageProvider
from storage.local_storage import LocalStorageProvider
from storage.gcs_storage import GCSStorageProvider
from storage.azure_storage import AzureADLSStorageProvider
from storage.s3_storage import S3StorageProvider
from config import get_active_profile

_cached_providers = {}

def get_storage_provider() -> StorageProvider:
    profile = get_active_profile()
    provider_type = profile.storage.provider.lower()

    if provider_type not in _cached_providers:
        if provider_type == "gcs":
            _cached_providers[provider_type] = GCSStorageProvider()
        elif provider_type in ["adls", "azure", "azure_blob"]:
            _cached_providers[provider_type] = AzureADLSStorageProvider()
        elif provider_type in ["s3", "aws"]:
            _cached_providers[provider_type] = S3StorageProvider()
        elif provider_type == "local":
            _cached_providers[provider_type] = LocalStorageProvider()
        else:
            raise ValueError(f"Unknown storage provider: {provider_type}")

    return _cached_providers[provider_type]
