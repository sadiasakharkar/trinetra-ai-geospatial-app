"""Download SpA-GAN RICE1 weights and export CPU ONNX for deployment."""

from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

import torch

from backend.ml.spagan import DEFAULT_WEIGHTS_URL, SpAGANInference


def download_weights(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DEFAULT_WEIGHTS_URL, timeout=120) as response, target.open("wb") as handle:
        handle.write(response.read())


def export_onnx(weights_path: Path, output_path: Path, patch_size: int = 256) -> str:
    model = SpAGANInference()
    checkpoint = torch.load(weights_path, map_location="cpu", weights_only=False)
    model.generator.load_state_dict(checkpoint)
    model.eval()
    sample = torch.randn(1, 3, patch_size, patch_size)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        sample,
        output_path.as_posix(),
        input_names=["rgb"],
        output_names=["reconstruction", "cloud_attention"],
        dynamic_axes={
            "rgb": {0: "batch", 2: "height", 3: "width"},
            "reconstruction": {0: "batch", 2: "height", 3: "width"},
            "cloud_attention": {0: "batch", 2: "height", 3: "width"},
        },
        opset_version=17,
    )
    return hashlib.sha256(output_path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights-dir", default=".cache/trinetra/weights")
    parser.add_argument("--patch-size", type=int, default=256)
    args = parser.parse_args()
    weights_dir = Path(args.weights_dir)
    weights_path = weights_dir / "spagan_rice1.pth"
    onnx_path = weights_dir / "spagan_rice1.onnx"
    if not weights_path.exists():
        print(f"Downloading SpA-GAN weights to {weights_path}...")
        download_weights(weights_path)
    print(f"Exporting ONNX to {onnx_path}...")
    sha256 = export_onnx(weights_path, onnx_path, patch_size=args.patch_size)
    print(f"SHA256: {sha256}")
    print(f"Size: {onnx_path.stat().st_size / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    main()
