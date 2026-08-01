from __future__ import annotations

import albumentations as A


def build_augmentations(patch_size: int) -> A.Compose:
    return A.Compose(
        [
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.RandomCrop(height=patch_size, width=patch_size, p=1.0),
            A.Resize(height=patch_size, width=patch_size, p=1.0),
            A.RandomBrightnessContrast(p=0.4),
            A.ColorJitter(p=0.3),
            A.GaussNoise(p=0.2),
            A.ElasticTransform(p=0.15),
        ],
        additional_targets={
            "target": "image",
            "sar": "mask",
            "dem": "mask",
            "historical": "image",
            "cloud_mask": "mask",
        },
    )
