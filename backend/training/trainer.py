from __future__ import annotations

from pathlib import Path

import torch
from torch.cuda.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from backend.logging_utils import get_logger
from backend.ml.model import AttentionResidualUNet
from backend.training.checkpoint import load_checkpoint
from backend.training.augmentations import build_augmentations
from backend.training.checkpoint import save_checkpoint
from backend.training.dataset import TrinetraDataset
from backend.training.losses import HybridLoss
from backend.training.validation import run_validation


class Trainer:
    def __init__(self, config) -> None:
        self.config = config
        self.logger = get_logger(__name__)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AttentionResidualUNet().to(self.device)
        self.optimizer = AdamW(self.model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
        self.scheduler = ReduceLROnPlateau(self.optimizer, mode="max", factor=0.5, patience=3)
        self.scaler = GradScaler(enabled=config.mixed_precision and self.device == "cuda")
        self.criterion = HybridLoss(config)
        self.writer = SummaryWriter(log_dir=str(Path(config.output_dir) / "tensorboard"))
        self.best_score = float("-inf")
        self.epochs_without_improvement = 0
        self.start_epoch = 0
        if config.resume_from:
            checkpoint = load_checkpoint(config.resume_from, self.model, self.optimizer, self.scaler)
            self.best_score = checkpoint.get("score", self.best_score)
            self.start_epoch = checkpoint.get("epoch", -1) + 1
            self.logger.info("Resumed training from %s at epoch %s", config.resume_from, self.start_epoch)

    def fit(self) -> None:
        train_dataset = TrinetraDataset(self.config.train_manifest, augmentations=build_augmentations(self.config.patch_size))
        val_dataset = TrinetraDataset(self.config.val_manifest)
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True, num_workers=self.config.num_workers)
        val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size, shuffle=False, num_workers=self.config.num_workers)
        for epoch in range(self.start_epoch, self.config.epochs):
            self.model.train()
            running_loss = 0.0
            for batch in train_loader:
                inputs = batch["input"].to(self.device)
                target = batch["target"].to(self.device)
                cloud_mask = batch["cloud_mask"].to(self.device)
                self.optimizer.zero_grad(set_to_none=True)
                with autocast(enabled=self.config.mixed_precision and self.device == "cuda"):
                    outputs = self.model(inputs)
                    loss = self.criterion(outputs, target, cloud_mask)
                self.scaler.scale(loss).backward()
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clip)
                self.scaler.step(self.optimizer)
                self.scaler.update()
                running_loss += loss.item()
            val_metrics = run_validation(self.model, val_loader, self.device)
            score = val_metrics["psnr"]
            self.scheduler.step(score)
            epoch_loss = running_loss / max(len(train_loader), 1)
            self.writer.add_scalar("loss/train", epoch_loss, epoch)
            self.writer.add_scalar("metric/val_psnr", score, epoch)
            self.writer.add_scalar("metric/val_mae", val_metrics["mae"], epoch)
            self.logger.info(
                "Epoch %s complete: train_loss=%.5f val_psnr=%.4f val_mae=%.6f",
                epoch,
                epoch_loss,
                score,
                val_metrics["mae"],
            )
            save_checkpoint(
                str(Path(self.config.output_dir) / "last.ckpt"),
                {
                    "epoch": epoch,
                    "model": self.model.state_dict(),
                    "optimizer": self.optimizer.state_dict(),
                    "scaler": self.scaler.state_dict(),
                    "score": score,
                },
            )
            if score > self.best_score:
                self.best_score = score
                self.epochs_without_improvement = 0
                save_checkpoint(
                    str(Path(self.config.output_dir) / "best.ckpt"),
                    {
                        "epoch": epoch,
                        "model": self.model.state_dict(),
                        "optimizer": self.optimizer.state_dict(),
                        "scaler": self.scaler.state_dict(),
                        "score": score,
                    },
                )
            else:
                self.epochs_without_improvement += 1
                if self.epochs_without_improvement >= self.config.patience:
                    self.logger.info("Early stopping triggered at epoch %s", epoch)
                    break
        self.writer.flush()
        self.writer.close()
