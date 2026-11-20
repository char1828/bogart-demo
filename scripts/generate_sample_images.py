import os
import io
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Any, Tuple

def create_synthetic_image(width: int, height: int, label: str, bg_color: Tuple[int, int, int], text_color: Tuple[int, int, int] = (255, 255, 255)) -> bytes:
    """Generates an image of specific dimensions with an informative banner."""
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw simple patterns to increase realistic entropy and file size
    for i in range(0, width, 40):
        draw.line([(i, 0), (i, height)], fill=(max(0, bg_color[0]-25), max(0, bg_color[1]-25), max(0, bg_color[2]-25)), width=2)
    for j in range(0, height, 40):
        draw.line([(0, j), (width, j)], fill=(max(0, bg_color[0]-25), max(0, bg_color[1]-25), max(0, bg_color[2]-25)), width=2)

    # Center box
    box_w, box_h = min(width - 40, 500), min(height - 40, 180)
    box_x = (width - box_w) // 2
    box_y = (height - box_h) // 2
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(20, 25, 40), outline=(255, 255, 255), width=3)

    # Info text
    lines = [
        "Cloud Benchmark Asset",
        f"Label: {label}",
        f"Resolution: {width} x {height}",
        "Storage Option: BLOB vs Object Storage"
    ]
    y_offset = box_y + 25
    for line in lines:
        draw.text((box_x + 30, y_offset), line, fill=text_color)
        y_offset += 32

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()

def generate_benchmark_dataset(count: int = 15) -> List[Dict[str, Any]]:
    """
    Generates a calibrated dataset with a mix of small (few KB), medium (~500KB - 1MB),
    and large (~2MB - 5MB) image files for benchmark differentiation.
    """
    categories = [
        # Small files (~30KB - 100KB)
        {"tier": "Small (Icon/Thumbnail)", "dims": (400, 300), "color": (41, 128, 185)},
        {"tier": "Small (Preview)", "dims": (640, 480), "color": (39, 174, 96)},
        # Medium files (~300KB - 1MB)
        {"tier": "Medium (Web Asset)", "dims": (1280, 720), "color": (142, 68, 173)},
        {"tier": "Medium (HD Graphic)", "dims": (1600, 900), "color": (211, 84, 0)},
        # Large files (~1.5MB - 4MB)
        {"tier": "Large (Full HD 1080p)", "dims": (1920, 1080), "color": (192, 57, 43)},
        {"tier": "Large (2K Ultra HD)", "dims": (2560, 1440), "color": (44, 62, 80)},
        {"tier": "Large (4K UHD Architecture)", "dims": (3840, 2160), "color": (22, 160, 133)}
    ]

    dataset = []
    for i in range(1, count + 1):
        cat = categories[(i - 1) % len(categories)]
        w, h = cat["dims"]
        label = f"Sample_{i:03d}_{cat['tier'].split()[0]}"
        filename = f"asset_{i:03d}_{w}x{h}.jpg"
        img_id = f"img_{uuid.uuid4().hex[:12]}"
        
        data = create_synthetic_image(w, h, label, cat["color"])
        size_bytes = len(data)

        dataset.append({
            "name": filename,
            "img_id": img_id,
            "size": size_bytes,
            "img_type": "image/jpeg",
            "data": data,
            "tier": cat["tier"],
            "dimensions": f"{w}x{h}"
        })
    return dataset
