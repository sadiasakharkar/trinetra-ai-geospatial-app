from __future__ import annotations

import torch


def psnr(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    mse = torch.mean((pred - target) ** 2)
    return 20 * torch.log10(torch.tensor(1.0, device=pred.device) / torch.sqrt(mse + 1e-8))


def mae(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return torch.mean(torch.abs(pred - target))
