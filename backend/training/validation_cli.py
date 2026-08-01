from __future__ import annotations

import argparse

import torch
from torch.utils.data import DataLoader

from backend.ml.model import AttentionResidualUNet
from backend.training.dataset import TrinetraDataset
from backend.training.validation import run_validation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--checkpoint")
    args = parser.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = AttentionResidualUNet().to(device)
    if args.checkpoint:
        checkpoint = torch.load(args.checkpoint, map_location=device)
        model.load_state_dict(checkpoint["model"])
    loader = DataLoader(TrinetraDataset(args.manifest), batch_size=2, shuffle=False)
    print(run_validation(model, loader, device))


if __name__ == "__main__":
    main()
