from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

try:
    import onnxruntime as ort
except ImportError:  # pragma: no cover
    ort = None

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None

@dataclass(slots=True)
class EngineInfo:
    name: str
    device: str
    precision: str


class InferenceEngine:
    def __init__(self, torchscript_path: Path | None, onnx_path: Path | None) -> None:
        self._torchscript_path = torchscript_path
        self._onnx_path = onnx_path
        self._engine_info = EngineInfo(name="unavailable", device="cpu", precision="fp32")
        self._torch_model = None
        self._onnx_session = None
        self._device = "cpu"
        self._load()

    @property
    def info(self) -> EngineInfo:
        return self._engine_info

    def _load(self) -> None:
        if ort is not None and self._onnx_path and self._onnx_path.exists():
            providers = ort.get_available_providers()
            self._onnx_session = ort.InferenceSession(
                self._onnx_path.as_posix(),
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
                if "CUDAExecutionProvider" in providers
                else ["CPUExecutionProvider"],
            )
            device = "cuda" if "CUDAExecutionProvider" in self._onnx_session.get_providers() else "cpu"
            self._engine_info = EngineInfo(name="onnxruntime", device=device, precision="fp32")
            return
        if torch is None:
            self._engine_info = EngineInfo(name="opencv-telea-cloud-inpaint", device="cpu", precision="fp32")
            return
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        if self._torchscript_path and self._torchscript_path.exists():
            self._torch_model = torch.jit.load(self._torchscript_path.as_posix(), map_location=self._device)
            self._torch_model.eval()
            precision = "fp16" if self._device == "cuda" else "fp32"
            self._engine_info = EngineInfo(name="torchscript", device=self._device, precision=precision)
            return
        self._engine_info = EngineInfo(name="opencv-telea-cloud-inpaint", device="cpu", precision="fp32")

    def predict(self, batch: np.ndarray) -> dict[str, np.ndarray]:
        if self._onnx_session is not None:
            input_name = self._onnx_session.get_inputs()[0].name
            outputs = self._onnx_session.run(None, {input_name: batch.astype(np.float32)})
            return {
                "reconstruction": outputs[0],
                "confidence": outputs[1],
                "risk": outputs[2],
                "cloud": outputs[3],
            }
        if torch is None or self._torch_model is None:
            return self._predict_cpu_inpaint(batch)
        with torch.inference_mode():
            tensor = torch.from_numpy(batch).to(self._device)
            if self._device == "cuda":
                tensor = tensor.half()
                if next(self._torch_model.parameters()).dtype != torch.float16:
                    self._torch_model = self._torch_model.half()
            outputs = self._torch_model(tensor)
            return {key: value.float().cpu().numpy() for key, value in outputs.items()}

    def _predict_cpu_inpaint(self, batch: np.ndarray) -> dict[str, np.ndarray]:
        """CPU-only open-source cloud removal path using OpenCV Telea inpainting.

        It estimates bright low-saturation cloud regions, inpaints only those
        pixels, then uses the historical channel stack as a conservative prior
        where available. External ONNX/TorchScript Attention U-Net weights still
        take precedence when configured.
        """
        rgb = np.clip(batch[:, :3], 0.0, 1.0)
        historical = np.clip(batch[:, 5:8], 0.0, 1.0) if batch.shape[1] >= 8 else rgb
        reconstruction = np.empty_like(rgb, dtype=np.float32)
        confidence = np.empty((batch.shape[0], 1, batch.shape[2], batch.shape[3]), dtype=np.float32)
        risk = np.empty_like(confidence)
        cloud = np.empty_like(confidence)
        for index in range(batch.shape[0]):
            image = np.moveaxis(rgb[index], 0, -1)
            hist = np.moveaxis(historical[index], 0, -1)
            cloud_mask = self._estimate_cloud_mask(image)
            inpainted = self._inpaint_rgb(image, cloud_mask)
            soft_mask = self._soften_mask(cloud_mask)
            prior_weight = np.clip(soft_mask * 0.35, 0.0, 0.35)[..., None]
            model_weight = soft_mask[..., None]
            candidate = inpainted * (1.0 - prior_weight) + hist * prior_weight
            restored = image * (1.0 - model_weight) + candidate * model_weight
            reconstruction[index] = np.moveaxis(np.clip(restored, 0.0, 1.0), -1, 0)
            cloud[index, 0] = cloud_mask
            confidence[index, 0] = np.clip(1.0 - soft_mask * 0.62, 0.0, 1.0)
            risk[index, 0] = np.clip(soft_mask * (1.0 - confidence[index, 0] * 0.45), 0.0, 1.0)
        return {
            "reconstruction": reconstruction.astype(np.float32),
            "confidence": confidence.astype(np.float32),
            "risk": risk.astype(np.float32),
            "cloud": cloud.astype(np.float32),
        }

    @staticmethod
    def _estimate_cloud_mask(image: np.ndarray) -> np.ndarray:
        rgb_u8 = np.clip(image * 255.0, 0, 255).astype(np.uint8)
        if cv2 is None:
            value = rgb_u8.max(axis=2)
            saturation = rgb_u8.max(axis=2) - rgb_u8.min(axis=2)
            mask = (value > np.percentile(value, 88)) & (saturation < np.percentile(saturation, 45))
            return mask.astype(np.float32)
        hsv = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2HSV)
        value = hsv[..., 2]
        saturation = hsv[..., 1]
        bright = value >= max(150, np.percentile(value, 88))
        low_saturation = saturation <= max(45, np.percentile(saturation, 48))
        mask = (bright & low_saturation).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        return mask.astype(np.float32)

    @staticmethod
    def _soften_mask(mask: np.ndarray) -> np.ndarray:
        if cv2 is None:
            return mask.astype(np.float32)
        return np.clip(cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sigmaX=2.0), 0.0, 1.0)

    @staticmethod
    def _inpaint_rgb(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        if cv2 is None or mask.max() <= 0:
            return image.copy()
        rgb_u8 = np.clip(image * 255.0, 0, 255).astype(np.uint8)
        mask_u8 = (mask > 0.25).astype(np.uint8) * 255
        bgr = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2BGR)
        inpainted_bgr = cv2.inpaint(bgr, mask_u8, 5.0, cv2.INPAINT_TELEA)
        inpainted_rgb = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2RGB)
        return inpainted_rgb.astype(np.float32) / 255.0
