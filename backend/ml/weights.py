from __future__ import annotations

import hashlib
import shutil
import urllib.request
from pathlib import Path


class WeightManager:
    def __init__(self, weights_dir: Path, model_url: str | None, model_sha256: str | None) -> None:
        self.weights_dir = weights_dir
        self.model_url = model_url
        self.model_sha256 = model_sha256

    def ensure(self, filename: str) -> Path | None:
        target = self.weights_dir / filename
        if target.exists():
            if self.model_sha256:
                self._validate_checksum(target, self.model_sha256)
            return target
        if not self.model_url:
            return None
        tmp_path = target.with_suffix(".download")
        with urllib.request.urlopen(self.model_url, timeout=120) as response, tmp_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        if self.model_sha256:
            self._validate_checksum(tmp_path, self.model_sha256)
        tmp_path.replace(target)
        return target

    @staticmethod
    def _validate_checksum(path: Path, checksum: str) -> None:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest.lower() != checksum.lower():
            raise ValueError(f"Checksum mismatch for {path.name}")
