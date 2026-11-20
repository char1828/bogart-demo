from abc import ABC, abstractmethod
from typing import Optional

class StorageProvider(ABC):
    @abstractmethod
    def upload_file(self, filename: str, data: bytes, content_type: str = "image/jpeg") -> str:
        """Uploads file data and returns the stored path or URI."""
        pass

    @abstractmethod
    def download_file(self, storage_path: str) -> bytes:
        """Retrieves raw bytes from object storage."""
        pass

    @abstractmethod
    def delete_file(self, storage_path: str) -> bool:
        """Removes object from storage."""
        pass

    @abstractmethod
    def exists(self, storage_path: str) -> bool:
        """Checks if file exists in storage."""
        pass
