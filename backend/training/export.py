from __future__ import annotations

import argparse
from pathlib import Path

import torch

from backend.ml.model import AttentionResidualUNet


def export_model(checkpoint_path: str, output_dir: str, patch_size: int = 256) -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = AttentionResidualUNet().to(device)
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint["model"])
    model.eval()
    dummy = torch.randn(1, 8, patch_size, patch_size, device=device)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    torchscript_path = output_path / "attention_resunet.ts"
    traced = torch.jit.trace(model, dummy, strict=False)
    traced.save(torchscript_path.as_posix())
    onnx_path = output_path / "attention_resunet.onnx"
    torch.onnx.export(
        model,
        dummy,
        onnx_path.as_posix(),
        input_names=["input"],
        output_names=["reconstruction", "confidence", "risk", "cloud"],
        dynamic_axes={"input": {2: "height", 3: "width"}},
        opset_version=17,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--patch-size", type=int, default=256)
    args = parser.parse_args()
    export_model(args.checkpoint, args.output_dir, patch_size=args.patch_size)


if __name__ == "__main__":
    main()
