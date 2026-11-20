import time
import io
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form, Response
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import config, get_active_profile, BASE_DIR
from database.connection import db_manager
from database.repository import media_repo
from storage.factory import get_storage_provider
from app.models import MediaMetadataResponse, SystemConfigResponse

# Initialize Database Schema at startup
db_manager.initialize_schema()

app = FastAPI(
    title="Cloud Storage Architecture & Performance Benchmark API",
    description="Performance benchmark comparing Database BLOB storage vs. Hybrid Object Storage across clouds.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Response-Time-MS", "X-Payload-Bytes", "X-Storage-Source"]
)

# Static files for the JavaScript UI
static_dir = BASE_DIR / "app" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def serve_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({"status": "Cloud Storage Benchmark API is running. UI file is loading."})

@app.get("/api/config", response_model=SystemConfigResponse)
def get_system_config():
    profile = get_active_profile()
    db_target = profile.database.database
    if profile.database.host:
        db_target += f" ({profile.database.host})"
        
    st_target = profile.storage.bucket_name or profile.storage.local_dir
    return SystemConfigResponse(
        active_profile=config.active_profile,
        cloud_provider=profile.cloud_provider,
        database_type=profile.database.type,
        storage_provider=profile.storage.provider,
        storage_target=str(st_target),
        database_target=db_target
    )

@app.get("/api/records", response_model=List[MediaMetadataResponse])
def list_records(option: int = Query(..., description="1 for Database BLOB, 2 for Object Storage")):
    """
    CRITICAL ARCHITECTURAL DIRECTIVE (Saroj Rout):
    When loading the table, fetch ONLY metadata, NEVER the image binary!
    """
    if option == 1:
        records = media_repo.get_records_option1()
        return [
            MediaMetadataResponse(
                id=r["id"],
                name=r["name"],
                img_id=r["img_id"],
                size=r["size"],
                img_type=r["img_type"],
                created_at=str(r.get("created_at", ""))
            )
            for r in records
        ]
    elif option == 2:
        records = media_repo.get_records_option2()
        return [
            MediaMetadataResponse(
                id=r["id"],
                name=r["name"],
                img_id=r["img_id"],
                size=r["size"],
                img_type=r["img_type"],
                created_at=str(r.get("created_at", "")),
                img_Path=r.get("img_Path") or r.get("img_path")
            )
            for r in records
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid option. Choose 1 (Database BLOB) or 2 (Object Storage).")

@app.get("/api/image/{record_id}")
def fetch_image(record_id: int, option: int = Query(..., description="1 for Database BLOB, 2 for Object Storage")):
    """
    Fetches the specific image payload upon user click, capturing server-side latency.
    """
    start_time = time.perf_counter()

    if option == 1:
        # Option 1: Retrieve from Database BLOB table
        record = media_repo.get_image_blob_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Image record not found in Database BLOB store.")
        
        raw_data = record["img_data"]
        content_type = record.get("img_type", "image/jpeg")
        filename = record.get("name", f"image_{record_id}.jpg")
        source_label = f"Database BLOB ({get_active_profile().database.type})"

    elif option == 2:
        # Option 2: Retrieve from Cloud Object Storage using path from DB
        record = media_repo.get_image_path_by_id(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Image record not found in Object Storage metadata store.")
        
        storage_path = record.get("img_Path") or record.get("img_path")
        content_type = record.get("img_type", "image/jpeg")
        filename = record.get("name", f"image_{record_id}.jpg")

        storage_provider = get_storage_provider()
        try:
            raw_data = storage_provider.download_file(storage_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch object from storage: {str(e)}")
            
        source_label = f"Object Storage ({get_active_profile().storage.provider.upper()})"

    else:
        raise HTTPException(status_code=400, detail="Invalid option.")

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    headers = {
        "X-Response-Time-MS": str(elapsed_ms),
        "X-Payload-Bytes": str(len(raw_data)),
        "X-Storage-Source": source_label,
        "Content-Disposition": f'inline; filename="{filename}"'
    }

    if option == 2:
        headers["Cache-Control"] = "public, max-age=86400"
    else:
        headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        headers["Pragma"] = "no-cache"

    return StreamingResponse(
        io.BytesIO(raw_data),
        media_type=content_type,
        headers=headers
    )

@app.post("/api/upload")
async def upload_asset(
    file: UploadFile = File(...),
    option: int = Form(..., description="1 for Database BLOB, 2 for Object Storage, 3 for Both")
):
    """
    Allows uploading a local image into the benchmark database/storage.
    """
    raw_data = await file.read()
    file_size = len(raw_data)
    filename = file.filename or f"upload_{uuid.uuid4().hex[:8]}.jpg"
    img_id = f"img_{uuid.uuid4().hex[:12]}"
    content_type = file.content_type or "image/jpeg"

    res = {}
    if option in [1, 3]:
        id1 = media_repo.insert_record_option1(
            name=filename,
            img_id=img_id,
            size=file_size,
            img_type=content_type,
            img_data=raw_data
        )
        res["option1_id"] = id1

    if option in [2, 3]:
        provider = get_storage_provider()
        path = provider.upload_file(filename, raw_data, content_type)
        id2 = media_repo.insert_record_option2(
            name=filename,
            img_id=img_id,
            size=file_size,
            img_type=content_type,
            img_path=path
        )
        res["option2_id"] = id2
        res["storage_path"] = path

    return {"status": "success", "file": filename, "size_bytes": file_size, **res}

@app.post("/api/seed")
def trigger_seed(count: int = Query(15, ge=1, le=100)):
    from scripts.seed_data import seed_database
    seed_database(count=count, clear_first=True)
    counts = media_repo.get_counts()
    return {"status": "success", "seeded_count": count, **counts}

@app.delete("/api/records")
def clear_records():
    media_repo.clear_all()
    return {"status": "success", "message": "All benchmark records cleared."}
