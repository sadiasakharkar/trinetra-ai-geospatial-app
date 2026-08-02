from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Bundled SpA-GAN RICE1 ONNX (exported from Penn000/SpA-GAN_for_cloud_removal weights).
DEFAULT_SPAGAN_ONNX_SHA256 = "5e8b662c72064318e92c9f2ace817cbb68821515dcca3b8083ece6c0d78ee015"
BACKEND_ROOT = Path(__file__).resolve().parent
BUNDLED_WEIGHTS_DIR = BACKEND_ROOT / "ml" / "weights"
DEFAULT_BUNDLED_SPAGAN_ONNX = BUNDLED_WEIGHTS_DIR / "spagan_rice1.onnx"


def _optional_path(value: str | None) -> Path | None:
    if not value or not value.strip():
        return None
    return Path(value.strip()).expanduser()


def resolve_spagan_onnx_path(
    *,
    env_path: Path | None,
    weights_dir: Path,
    spagan_onnx_name: str,
    downloaded: Path | None,
) -> Path | None:
    """Resolve SpA-GAN ONNX weights: env override, cache/download, then bundled default."""
    candidates: tuple[Path, ...] = (
        *(path for path in (env_path, downloaded) if path is not None),
        weights_dir / spagan_onnx_name,
        DEFAULT_BUNDLED_SPAGAN_ONNX,
    )
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_file():
            return resolved
    return None


@dataclass(slots=True)
class Settings:
    workspace_root: Path
    public_dir: Path = field(init=False)
    dataset_dir: Path = field(init=False)
    upload_dir: Path = field(init=False)
    output_dir: Path = field(init=False)
    preview_dir: Path = field(init=False)
    thumbnail_dir: Path = field(init=False)
    confidence_dir: Path = field(init=False)
    mask_dir: Path = field(init=False)
    cache_dir: Path = field(init=False)
    weights_dir: Path = field(init=False)
    model_url: str | None = field(default_factory=lambda: os.getenv("TRINETRA_MODEL_URL") or None)
    model_sha256: str | None = field(
        default_factory=lambda: os.getenv("TRINETRA_MODEL_SHA256") or DEFAULT_SPAGAN_ONNX_SHA256 or None
    )
    attention_onnx_url: str | None = field(default_factory=lambda: os.getenv("TRINETRA_ATTENTION_ONNX_URL"))
    attention_onnx_sha256: str | None = field(default_factory=lambda: os.getenv("TRINETRA_ATTENTION_ONNX_SHA256"))
    spagan_onnx_name: str = field(default_factory=lambda: os.getenv("TRINETRA_SPAGAN_ONNX_NAME", "spagan_rice1.onnx"))
    spagan_onnx_path: Path | None = field(
        default_factory=lambda: _optional_path(os.getenv("TRINETRA_SPAGAN_ONNX_PATH"))
    )
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
        self.dataset_dir = self.workspace_root / "datasets"
        self.upload_dir = self.public_dir / "uploads"
        self.output_dir = self.public_dir / "output"
        self.preview_dir = self.public_dir / "previews"
        self.thumbnail_dir = self.public_dir / "thumbnails"
        self.confidence_dir = self.public_dir / "confidence"
        self.mask_dir = self.public_dir / "masks"
        self.cache_dir = self.workspace_root / ".cache" / "trinetra"
        self.weights_dir = self.cache_dir / "weights"
        for path in (
            self.dataset_dir,
            self.upload_dir,
            self.output_dir,
            self.preview_dir,
            self.thumbnail_dir,
            self.confidence_dir,
            self.mask_dir,
            self.weights_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


def get_settings() -> Settings:
    workspace_root = Path(__file__).resolve().parent.parent
    return Settings(workspace_root=workspace_root)
