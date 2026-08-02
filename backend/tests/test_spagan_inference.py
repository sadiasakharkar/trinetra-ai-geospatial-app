from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from backend.config import BUNDLED_WEIGHTS_DIR, DEFAULT_SPAGAN_ONNX_SHA256
from backend.ml.export_spagan import verify_onnx
from backend.ml.inference import InferenceEngine, InferenceUnavailableError


BUNDLED_ONNX = BUNDLED_WEIGHTS_DIR / "spagan_rice1.onnx"


@pytest.mark.skipif(not BUNDLED_ONNX.exists(), reason="Bundled SpA-GAN ONNX weights are unavailable.")
def test_bundled_onnx_checksum() -> None:
    digest = __import__("hashlib").sha256(BUNDLED_ONNX.read_bytes()).hexdigest()
    assert digest == DEFAULT_SPAGAN_ONNX_SHA256


@pytest.mark.skipif(not BUNDLED_ONNX.exists(), reason="Bundled SpA-GAN ONNX weights are unavailable.")
def test_verify_onnx_contract() -> None:
    verify_onnx(BUNDLED_ONNX)


@pytest.mark.skipif(not BUNDLED_ONNX.exists(), reason="Bundled SpA-GAN ONNX weights are unavailable.")
def test_spagan_inference_engine() -> None:
    engine = InferenceEngine(spagan_onnx_path=BUNDLED_ONNX, torchscript_path=None, onnx_path=None)
    assert engine.info.model == "SpA-GAN-RICE1"
    assert engine.info.name == "onnxruntime"
    batch = np.random.rand(1, 8, 256, 256).astype(np.float32)
    outputs = engine.predict(batch)
    assert set(outputs) == {"reconstruction", "confidence", "risk", "cloud"}
    assert outputs["reconstruction"].shape == (1, 3, 256, 256)
    assert outputs["cloud"].shape == (1, 1, 256, 256)


def test_inference_engine_requires_weights(tmp_path: Path) -> None:
    missing = tmp_path / "missing.onnx"
    with pytest.raises(InferenceUnavailableError):
        InferenceEngine(spagan_onnx_path=missing, torchscript_path=None, onnx_path=None)
