from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _with_legacy_fields(dataset: dict[str, Any]) -> dict[str, Any]:
    preview = dataset.get("preview_image_url") or dataset.get("thumbnail_url")
    reconstructed = dataset.get("reconstructed_image_url") or dataset.get("clear_reference_url") or preview
    cloud_mask = dataset.get("cloud_mask_url")
    historical = dataset.get("historical_image_url") or preview
    dataset["thumb"] = dataset.get("thumb") or preview
    dataset["reconstructed"] = dataset.get("reconstructed") or reconstructed
    dataset["sar"] = dataset.get("sar") or cloud_mask or preview
    dataset["dem"] = dataset.get("dem") or historical
    dataset["temporal"] = dataset.get("temporal") or [
        {"date": "Historical", "img": historical, "clear": True},
        {"date": "Current", "img": preview, "clear": False},
    ]
    return dataset


def load_sample_datasets(dataset_root: Path) -> list[dict[str, Any]]:
    datasets: list[dict[str, Any]] = []
    if not dataset_root.exists():
        return datasets
    for directory in sorted(dataset_root.iterdir()):
        dataset_json = directory / "dataset.json"
        if not dataset_json.exists():
            continue
        payload = _read_json(dataset_json)
        payload.setdefault("source", "sample")
        payload.setdefault("dataset_json_url", f"/datasets/{directory.name}/dataset.json")
        datasets.append(_with_legacy_fields(payload))
    return datasets


def find_dataset(dataset_root: Path, dataset_id: str) -> dict[str, Any] | None:
    for dataset in load_sample_datasets(dataset_root):
        if dataset.get("id") == dataset_id:
            return dataset
    return None


def dataset_path_from_url(dataset_root: Path, url: str | None) -> Path | None:
    if not url or not url.startswith("/datasets/"):
        return None
    rel = url.removeprefix("/datasets/")
    path = (dataset_root / rel).resolve()
    try:
        path.relative_to(dataset_root.resolve())
    except ValueError:
        return None
    return path


def load_uploaded_datasets(upload_root: Path) -> list[dict[str, Any]]:
    datasets: list[dict[str, Any]] = []
    if not upload_root.exists():
        return datasets
    for directory in sorted(upload_root.iterdir(), reverse=True):
        metadata_path = directory / "metadata.json"
        if metadata_path.exists():
            datasets.append(_with_legacy_fields(_read_json(metadata_path)))
    return datasets
