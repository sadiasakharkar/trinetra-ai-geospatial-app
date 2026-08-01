from __future__ import annotations

from pathlib import Path

import numpy as np

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


def public_url(path: Path, root: Path, prefix: str) -> str:
    rel = path.resolve().relative_to(root.resolve()).as_posix()
    return f"{prefix.rstrip('/')}/{rel}"


def to_uint8_image(array: np.ndarray) -> np.ndarray:
    image = np.asarray(array)
    if image.ndim == 2:
        image = np.repeat(image[..., None], 3, axis=2)
    if image.shape[-1] > 3:
        image = image[..., :3]
    if image.dtype == np.uint8:
        return image
    image = image.astype(np.float32)
    if image.max(initial=0.0) <= 1.0:
        image *= 255.0
    return np.clip(image, 0, 255).astype(np.uint8)


def save_rgb(path: Path, array: np.ndarray) -> None:
    if Image is None:
        raise RuntimeError("Pillow is required to write image previews.")
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(to_uint8_image(array)).save(path)


def save_gray(path: Path, array: np.ndarray) -> None:
    if Image is None:
        raise RuntimeError("Pillow is required to write image previews.")
    image = np.asarray(array).astype(np.float32)
    if image.max(initial=0.0) <= 1.0:
        image *= 255.0
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.clip(image, 0, 255).astype(np.uint8)).save(path)


def save_thumbnail(source: Path, target: Path, size: tuple[int, int] = (384, 216)) -> None:
    if Image is None:
        raise RuntimeError("Pillow is required to generate thumbnails.")
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image = image.convert("RGB")
        image.thumbnail(size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", size, (18, 24, 28))
        offset = ((size[0] - image.width) // 2, (size[1] - image.height) // 2)
        canvas.paste(image, offset)
        canvas.save(target)


def save_heatmap(path: Path, array: np.ndarray) -> None:
    values = np.clip(np.asarray(array, dtype=np.float32), 0.0, 1.0)
    red = np.clip(1.6 * values, 0.0, 1.0)
    green = np.clip(1.6 * (1.0 - np.abs(values - 0.5) * 2.0), 0.0, 1.0)
    blue = np.clip(1.4 * (1.0 - values), 0.0, 1.0)
    save_rgb(path, np.dstack([red, green, blue]))


def save_difference(path: Path, before: np.ndarray, after: np.ndarray) -> None:
    before_f = to_uint8_image(before).astype(np.float32)
    after_f = to_uint8_image(after).astype(np.float32)
    diff = np.abs(after_f - before_f)
    if diff.max(initial=0.0) > 0:
        diff = diff / diff.max()
    save_heatmap(path, diff.mean(axis=2))
