from typing import Optional, List
from pydantic import BaseModel

class MediaMetadataResponse(BaseModel):
    id: int
    name: str
    img_id: str
    size: int
    img_type: str
    created_at: Optional[str] = None
    img_Path: Optional[str] = None

class SystemConfigResponse(BaseModel):
    active_profile: str
    cloud_provider: str
    database_type: str
    storage_provider: str
    storage_target: str
    database_target: str

class BenchmarkMetric(BaseModel):
    option: int
    record_id: int
    image_name: str
    image_size_bytes: int
    response_time_ms: float
    source: str
