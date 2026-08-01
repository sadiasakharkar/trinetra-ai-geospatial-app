from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset


class TrinetraDataset(Dataset):
    def __init__(self, manifest_path: str, augmentations=None) -> None:
        self.records = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        if not isinstance(self.records, list) or not self.records:
            raise ValueError("Training manifest must be a non-empty JSON list.")
        self.augmentations = augmentations

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        record = self.records[index]
        self._validate_record(record)
        cloudy = cv2.cvtColor(cv2.imread(record["cloudy"]), cv2.COLOR_BGR2RGB)
        target = cv2.cvtColor(cv2.imread(record["target"]), cv2.COLOR_BGR2RGB)
        historical = cv2.cvtColor(cv2.imread(record["historical"]), cv2.COLOR_BGR2RGB)
        sar = cv2.imread(record["sar"], cv2.IMREAD_GRAYSCALE)
        dem = cv2.imread(record["dem"], cv2.IMREAD_GRAYSCALE)
        cloud_mask = cv2.imread(record["cloud_mask"], cv2.IMREAD_GRAYSCALE)
        if self.augmentations is not None:
            augmented = self.augmentations(
                image=cloudy,
                target=target,
                sar=sar,
                dem=dem,
                historical=historical,
                cloud_mask=cloud_mask,
            )
            cloudy = augmented["image"]
            target = augmented["target"]
            sar = augmented["sar"]
            dem = augmented["dem"]
            historical = augmented["historical"]
            cloud_mask = augmented["cloud_mask"]
        cloudy = cloudy.astype(np.float32) / 255.0
        target = target.astype(np.float32) / 255.0
        historical = historical.astype(np.float32) / 255.0
        sar = sar.astype(np.float32) / 255.0
        dem = dem.astype(np.float32) / 255.0
        cloud_mask = (cloud_mask.astype(np.float32) / 255.0)[None, ...]
        inputs = np.concatenate(
            [
                np.moveaxis(cloudy, -1, 0),
                sar[None, ...],
                dem[None, ...],
                np.moveaxis(historical, -1, 0),
            ],
            axis=0,
        )
        return {
            "input": torch.from_numpy(inputs),
            "target": torch.from_numpy(np.moveaxis(target, -1, 0)),
            "cloud_mask": torch.from_numpy(cloud_mask),
        }

    @staticmethod
    def _validate_record(record: dict) -> None:
        required = ["cloudy", "target", "historical", "sar", "dem", "cloud_mask"]
        missing = [key for key in required if key not in record]
        if missing:
            raise KeyError(f"Manifest record is missing required keys: {missing}")
