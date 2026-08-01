from __future__ import annotations

import argparse

from backend.training.config import TrainConfig
from backend.training.trainer import Trainer


def parse_args() -> TrainConfig:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-manifest", required=True)
    parser.add_argument("--val-manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--resume-from")
    args = parser.parse_args()
    return TrainConfig(
        train_manifest=args.train_manifest,
        val_manifest=args.val_manifest,
        output_dir=args.output_dir,
        resume_from=args.resume_from,
    )


def main() -> None:
    config = parse_args()
    Trainer(config).fit()


if __name__ == "__main__":
    main()
