from __future__ import annotations

import json
from pathlib import Path


SAMPLE_DATASETS = [
    {
        "id": "LISS4-2026-0618-DT04",
        "name": "Ganga Delta - Kolkata Sector",
        "sensor": "LISS-IV (Resourcesat-2A)",
        "region": "West Bengal, India",
        "acquired": "2026-06-18 10:42 IST",
        "resolution": "5.8 m / pixel",
        "area": "1204 km^2",
        "cloudCover": 42.7,
        "size": "486 MB",
        "coords": "22.5726N / 88.3639E",
        "thumb": "/images/liss-iv-cloudy.png",
        "reconstructed": "/images/liss-iv-reconstructed.png",
        "sar": "/images/sentinel-sar.png",
        "dem": "/images/dem-terrain.png",
        "temporal": [
            {"date": "Mar 2026", "img": "/images/temporal-1.png", "clear": True},
            {"date": "Apr 2026", "img": "/images/temporal-2.png", "clear": True},
            {"date": "May 2026", "img": "/images/liss-iv-reconstructed.png", "clear": True},
            {"date": "Jun 2026", "img": "/images/liss-iv-cloudy.png", "clear": False},
        ],
    }
]


def load_uploaded_datasets(upload_root: Path) -> list[dict]:
    datasets: list[dict] = []
    if not upload_root.exists():
        return datasets
    for directory in upload_root.iterdir():
        metadata_path = directory / "metadata.json"
        if metadata_path.exists():
            datasets.append(json.loads(metadata_path.read_text(encoding="utf-8")))
    return datasets
