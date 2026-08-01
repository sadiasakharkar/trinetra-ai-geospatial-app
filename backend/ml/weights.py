from __future__ import annotations

import hashlib
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class WeightSpec:
    url: str
    sha256: str | None = None


class WeightManager:
    def __init__(self, weights_dir: Path, catalog: dict[str, WeightSpec]) -> None:
        self.weights_dir = weights_dir
        self.catalog = catalog

    def ensure(self, filename: str) -> Path | None:
        target = self.weights_dir / filename
        if target.exists():
            spec = self.catalog.get(filename)
            if spec and spec.sha256:
                self._validate_checksum(target, spec.sha256)
            return target
        spec = self.catalog.get(filename)
        if spec is None:
            return None
        tmp_path = target.with_suffix(".download")
        with urllib.request.urlopen(spec.url, timeout=180) as response, tmp_path.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        if spec.sha256:
            self._validate_checksum(tmp_path, spec.sha256)
        tmp_path.replace(target)
        return target

    @staticmethod
    def _validate_checksum(path: Path, checksum: str) -> None:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest.lower() != checksum.lower():
            raise ValueError(f"Checksum mismatch for {path.name}")
