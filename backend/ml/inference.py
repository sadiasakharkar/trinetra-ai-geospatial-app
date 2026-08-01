from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

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
            raise RuntimeError("PyTorch or ONNX Runtime must be installed for inference.")
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        if self._torchscript_path and self._torchscript_path.exists():
            self._torch_model = torch.jit.load(self._torchscript_path.as_posix(), map_location=self._device)
            self._torch_model.eval()
            precision = "fp16" if self._device == "cuda" else "fp32"
            self._engine_info = EngineInfo(name="torchscript", device=self._device, precision=precision)
            return
        raise RuntimeError(
            "No exported model weights were found. Provide TorchScript or ONNX weights via the configured cache or TRINETRA_MODEL_URL."
        )

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
            raise RuntimeError("No inference backend is available.")
        with torch.inference_mode():
            tensor = torch.from_numpy(batch).to(self._device)
            if self._device == "cuda":
                tensor = tensor.half()
                if next(self._torch_model.parameters()).dtype != torch.float16:
                    self._torch_model = self._torch_model.half()
            outputs = self._torch_model(tensor)
            return {key: value.float().cpu().numpy() for key, value in outputs.items()}
