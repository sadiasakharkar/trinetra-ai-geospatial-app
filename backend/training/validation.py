from __future__ import annotations

import torch

from backend.training.metrics import mae, psnr


@torch.no_grad()
def run_validation(model, dataloader, device: str) -> dict[str, float]:
    model.eval()
    psnr_scores = []
    mae_scores = []
    for batch in dataloader:
        inputs = batch["input"].to(device)
        target = batch["target"].to(device)
        outputs = model(inputs)
        prediction = outputs["reconstruction"]
        psnr_scores.append(psnr(prediction, target).item())
        mae_scores.append(mae(prediction, target).item())
    return {
        "psnr": float(sum(psnr_scores) / max(len(psnr_scores), 1)),
        "mae": float(sum(mae_scores) / max(len(mae_scores), 1)),
    }
