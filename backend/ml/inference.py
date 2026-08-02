from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from backend.config import DEFAULT_BUNDLED_SPAGAN_ONNX
from backend.logging_utils import get_logger

try:
    import onnxruntime as ort
except ImportError:  # pragma: no cover
    ort = None

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None


class InferenceUnavailableError(RuntimeError):
    """Raised when no pretrained inference backend could be loaded."""


@dataclass(slots=True)
class EngineInfo:
    name: str
    device: str
    precision: str
    model: str


class InferenceEngine:
    """Cloud-removal inference using pretrained SpA-GAN (default) or AttentionResidualUNet weights."""

    def __init__(
        self,
        spagan_onnx_path: Path | None,
        torchscript_path: Path | None,
        onnx_path: Path | None,
    ) -> None:
        self.logger = get_logger(__name__)
        self._spagan_onnx_path = spagan_onnx_path
        self._torchscript_path = torchscript_path
        self._onnx_path = onnx_path
        self._engine_info = EngineInfo(name="unavailable", device="cpu", precision="fp32", model="none")
        self._torch_model = None
        self._onnx_session = None
        self._backend: str | None = None
        self._device = "cpu"
        self._load()

    @property
    def info(self) -> EngineInfo:
        return self._engine_info

    def _load(self) -> None:
        spagan_path = self._spagan_onnx_path.resolve() if self._spagan_onnx_path is not None else None
        torchscript_path = self._torchscript_path.resolve() if self._torchscript_path is not None else None
        onnx_path = self._onnx_path.resolve() if self._onnx_path is not None else None
        if ort is not None and self._spagan_onnx_path and self._spagan_onnx_path.exists():
            self.logger.info("Loaded bundled SpA-GAN model: %s", spagan_path)
            self._onnx_session = ort.InferenceSession(
                spagan_path.as_posix(),
                providers=["CPUExecutionProvider"],
            )
            self._backend = "spagan"
            self._engine_info = EngineInfo(
                name="onnxruntime",
                device="cpu",
                precision="fp32",
                model="SpA-GAN-RICE1",
            )
            return
        if ort is not None and self._onnx_path and self._onnx_path.exists():
            self.logger.info("Loaded AttentionResidualUNet ONNX model: %s", onnx_path)
            providers = ort.get_available_providers()
            self._onnx_session = ort.InferenceSession(
                onnx_path.as_posix(),
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
                if "CUDAExecutionProvider" in providers
                else ["CPUExecutionProvider"],
            )
            device = "cuda" if "CUDAExecutionProvider" in self._onnx_session.get_providers() else "cpu"
            self._backend = "attention_resunet"
            self._engine_info = EngineInfo(
                name="onnxruntime",
                device=device,
                precision="fp32",
                model="AttentionResidualUNet",
            )
            return
        if torch is not None and self._torchscript_path and self._torchscript_path.exists():
            self.logger.info("Loaded AttentionResidualUNet torchscript model: %s", torchscript_path)
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._torch_model = torch.jit.load(torchscript_path.as_posix(), map_location=self._device)
            self._torch_model.eval()
            precision = "fp16" if self._device == "cuda" else "fp32"
            self._backend = "attention_resunet"
            self._engine_info = EngineInfo(
                name="torchscript",
                device=self._device,
                precision=precision,
                model="AttentionResidualUNet",
            )
            return
        spagan_hint = spagan_path or DEFAULT_BUNDLED_SPAGAN_ONNX.resolve()
        bundled_status = "found" if DEFAULT_BUNDLED_SPAGAN_ONNX.is_file() else "missing"
        raise InferenceUnavailableError(
            "No pretrained cloud-removal weights found. Expected SpA-GAN ONNX at "
            f"{spagan_hint} (bundled default {bundled_status} at {DEFAULT_BUNDLED_SPAGAN_ONNX}) "
            "or AttentionResidualUNet weights."
        )

    def predict(self, batch: np.ndarray) -> dict[str, np.ndarray]:
        if self._onnx_session is not None and self._backend == "spagan":
            return self._predict_spagan(batch)
        if self._onnx_session is not None:
            input_name = self._onnx_session.get_inputs()[0].name
            outputs = self._onnx_session.run(None, {input_name: batch.astype(np.float32)})
            return {
                "reconstruction": outputs[0],
                "confidence": outputs[1],
                "risk": outputs[2],
                "cloud": outputs[3],
            }
        if self._torch_model is not None:
            with torch.inference_mode():
                tensor = torch.from_numpy(batch).to(self._device)
                if self._device == "cuda":
                    tensor = tensor.half()
                    if next(self._torch_model.parameters()).dtype != torch.float16:
                        self._torch_model = self._torch_model.half()
                outputs = self._torch_model(tensor)
                return {key: value.float().cpu().numpy() for key, value in outputs.items()}
        raise InferenceUnavailableError("Inference backend is not initialized.")

    def _predict_spagan(self, batch: np.ndarray) -> dict[str, np.ndarray]:
        rgb = np.clip(batch[:, :3], 0.0, 1.0).astype(np.float32)
        # RICE1 weights were trained on OpenCV BGR channel order.
        model_input = rgb[:, [2, 1, 0], :, :]
        reconstruction, attention = self._onnx_session.run(None, {"rgb": model_input})
        reconstruction = reconstruction[:, [2, 1, 0], :, :]
        reconstruction = np.clip(reconstruction, 0.0, 1.0).astype(np.float32)
        cloud = np.clip(attention, 0.0, 1.0).astype(np.float32)
        confidence = np.clip(1.0 - cloud * 0.75, 0.0, 1.0).astype(np.float32)
        risk = np.clip(cloud * 0.85, 0.0, 1.0).astype(np.float32)
        return {
            "reconstruction": reconstruction,
            "confidence": confidence,
            "risk": risk,
            "cloud": cloud,
        }
