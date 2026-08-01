from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Settings:
    workspace_root: Path
    public_dir: Path = field(init=False)
    upload_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    cache_dir: Path = field(init=False)
    weights_dir: Path = field(init=False)
    model_url: str | None = field(default_factory=lambda: os.getenv("TRINETRA_MODEL_URL"))
    model_sha256: str | None = field(default_factory=lambda: os.getenv("TRINETRA_MODEL_SHA256"))
    torchscript_name: str = field(default_factory=lambda: os.getenv("TRINETRA_TORCHSCRIPT_NAME", "attention_resunet.ts"))
    onnx_name: str = field(default_factory=lambda: os.getenv("TRINETRA_ONNX_NAME", "attention_resunet.onnx"))
    max_patch_size: int = field(default_factory=lambda: int(os.getenv("TRINETRA_MAX_PATCH", "512")))
    default_tile_size: int = field(default_factory=lambda: int(os.getenv("TRINETRA_DEFAULT_TILE", "256")))
    overlap: int = field(default_factory=lambda: int(os.getenv("TRINETRA_TILE_OVERLAP", "48")))
    batch_size: int = field(default_factory=lambda: int(os.getenv("TRINETRA_BATCH_SIZE", "4")))
    num_workers: int = field(default_factory=lambda: int(os.getenv("TRINETRA_NUM_WORKERS", "2")))
    log_level: str = field(default_factory=lambda: os.getenv("TRINETRA_LOG_LEVEL", "INFO").upper())
    max_upload_size_mb: int = field(default_factory=lambda: int(os.getenv("TRINETRA_MAX_UPLOAD_MB", "1024")))

    def __post_init__(self) -> None:
        self.public_dir = self.workspace_root / "public"
        self.upload_dir = self.public_dir / "uploads"
        self.output_dir = self.public_dir / "output"
        self.cache_dir = self.workspace_root / ".cache" / "trinetra"
        self.weights_dir = self.cache_dir / "weights"
        for path in (self.upload_dir, self.output_dir, self.weights_dir):
            path.mkdir(parents=True, exist_ok=True)

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


def get_settings() -> Settings:
    workspace_root = Path(__file__).resolve().parent.parent
    return Settings(workspace_root=workspace_root)
