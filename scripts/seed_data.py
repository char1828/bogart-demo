import sys
import os
import time
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from config import get_active_profile
from database.connection import db_manager
from database.repository import media_repo
from storage.factory import get_storage_provider
from scripts.generate_sample_images import generate_benchmark_dataset

def seed_database(count: int = 15, clear_first: bool = False):
    profile = get_active_profile()
    print("=" * 70)
    print("CLOUD STORAGE BENCHMARK DATA SEEDING ROUTINE")
    print("=" * 70)
    print(f"Active Profile  : {profile.cloud_provider.upper()}")
    print(f"Database Type   : {profile.database.type}")
    print(f"Storage Provider: {profile.storage.provider}")
    print(f"Dataset Size    : {count} assets")
    print("-" * 70)

    # 1. Initialize schema
    print("Step 1: Initializing database schema...")
    db_manager.initialize_schema()
    print("✓ Schema initialized successfully.")

    if clear_first:
        print("Clearing existing benchmark records...")
        media_repo.clear_all()
        print("✓ Tables cleared.")

    # 2. Get storage provider
    storage_provider = get_storage_provider()

    # 3. Generate synthetic calibrated images
    print(f"Step 2: Generating {count} calibrated sample images of varied dimensions/sizes...")
    dataset = generate_benchmark_dataset(count=count)
    print("✓ Images generated successfully in memory.")

    # 4. Ingest into Option 1 (BLOB) & Option 2 (Object Storage + Path)
    print("Step 3: Ingesting assets into both storage models...")
    start_time = time.time()

    opt1_ids = []
    opt2_ids = []

    for idx, item in enumerate(dataset, 1):
        name = item["name"]
        img_id = item["img_id"]
        size = item["size"]
        img_type = item["img_type"]
        raw_data = item["data"]

        # Option 1: Store inside Relational DB as BLOB
        id_1 = media_repo.insert_record_option1(
            name=name,
            img_id=img_id,
            size=size,
            img_type=img_type,
            img_data=raw_data
        )
        opt1_ids.append(id_1)

        # Option 2: Upload to Object Storage & store path in DB
        storage_path = storage_provider.upload_file(
            filename=name,
            data=raw_data,
            content_type=img_type
        )
        id_2 = media_repo.insert_record_option2(
            name=name,
            img_id=img_id,
            size=size,
            img_type=img_type,
            img_path=storage_path
        )
        opt2_ids.append(id_2)

        print(f"  [{idx:02d}/{count:02d}] {name} ({size/1024:.1f} KB) -> Opt1 ID: {id_1} | Opt2 ID: {id_2} (Path: {storage_path})")

    elapsed = time.time() - start_time
    print("-" * 70)
    print(f"✓ Ingestion complete in {elapsed:.2f} seconds.")
    
    counts = media_repo.get_counts()
    print(f"Verification Check:")
    print(f"  - Option 1 (Database BLOBs)      : {counts['option1_blob_count']} records")
    print(f"  - Option 2 (Object Storage Paths): {counts['option2_meta_count']} records")
    print("=" * 70)

if __name__ == "__main__":
    count_arg = 15
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        count_arg = int(sys.argv[1])
    seed_database(count=count_arg, clear_first=True)
