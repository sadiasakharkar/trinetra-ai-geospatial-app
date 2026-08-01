from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TrainConfig:
    train_manifest: str
    val_manifest: str
    output_dir: str
    epochs: int = 100
    batch_size: int = 4
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    num_workers: int = 4
    patch_size: int = 256
    patience: int = 10
    gradient_clip: float = 1.0
    mixed_precision: bool = True
    resume_from: str | None = None
    l1_weight: float = 1.0
    ssim_weight: float = 0.3
    edge_weight: float = 0.2
    gradient_weight: float = 0.2
    spectral_weight: float = 0.2
    cloud_reconstruction_weight: float = 0.4
    confidence_weight: float = 0.2
