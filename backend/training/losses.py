from __future__ import annotations

import torch
from torch import nn


def gradient_map(tensor: torch.Tensor) -> torch.Tensor:
    grad_x = tensor[..., :, 1:] - tensor[..., :, :-1]
    grad_y = tensor[..., 1:, :] - tensor[..., :-1, :]
    grad_x = nn.functional.pad(grad_x, (0, 1, 0, 0))
    grad_y = nn.functional.pad(grad_y, (0, 0, 0, 1))
    return torch.sqrt(grad_x.pow(2) + grad_y.pow(2) + 1e-6)


class SSIMLoss(nn.Module):
    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        mu_x = pred.mean(dim=(-2, -1), keepdim=True)
        mu_y = target.mean(dim=(-2, -1), keepdim=True)
        sigma_x = ((pred - mu_x) ** 2).mean(dim=(-2, -1), keepdim=True)
        sigma_y = ((target - mu_y) ** 2).mean(dim=(-2, -1), keepdim=True)
        sigma_xy = ((pred - mu_x) * (target - mu_y)).mean(dim=(-2, -1), keepdim=True)
        c1 = 0.01**2
        c2 = 0.03**2
        ssim = ((2 * mu_x * mu_y + c1) * (2 * sigma_xy + c2)) / ((mu_x**2 + mu_y**2 + c1) * (sigma_x + sigma_y + c2))
        return 1.0 - ssim.mean()


class HybridLoss(nn.Module):
    def __init__(self, config) -> None:
        super().__init__()
        self.l1 = nn.L1Loss()
        self.bce = nn.BCELoss()
        self.ssim = SSIMLoss()
        self.config = config

    def forward(self, outputs: dict[str, torch.Tensor], target: torch.Tensor, cloud_mask: torch.Tensor) -> torch.Tensor:
        reconstruction = outputs["reconstruction"]
        confidence = outputs["confidence"]
        l1_loss = self.l1(reconstruction, target)
        ssim_loss = self.ssim(reconstruction, target)
        edge_loss = self.l1(gradient_map(reconstruction), gradient_map(target))
        gradient_loss = self.l1(torch.gradient(reconstruction, dim=(-2, -1))[0], torch.gradient(target, dim=(-2, -1))[0])
        spectral_loss = self.l1(reconstruction.mean(dim=1, keepdim=True), target.mean(dim=1, keepdim=True))
        cloud_loss = self.l1(reconstruction * cloud_mask, target * cloud_mask)
        confidence_target = 1.0 - cloud_mask
        confidence_loss = self.bce(confidence, confidence_target)
        return (
            self.config.l1_weight * l1_loss
            + self.config.ssim_weight * ssim_loss
            + self.config.edge_weight * edge_loss
            + self.config.gradient_weight * gradient_loss
            + self.config.spectral_weight * spectral_loss
            + self.config.cloud_reconstruction_weight * cloud_loss
            + self.config.confidence_weight * confidence_loss
        )
