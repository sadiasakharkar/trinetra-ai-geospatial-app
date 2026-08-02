from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from backend.config import BUNDLED_WEIGHTS_DIR, DEFAULT_BUNDLED_SPAGAN_ONNX, DEFAULT_SPAGAN_ONNX_SHA256, resolve_spagan_onnx_path
from backend.ml.export_spagan import verify_onnx
from backend.ml.inference import InferenceEngine, InferenceUnavailableError


BUNDLED_ONNX = DEFAULT_BUNDLED_SPAGAN_ONNX


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
    with pytest.raises(InferenceUnavailableError, match="bundled default"):
        InferenceEngine(spagan_onnx_path=missing, torchscript_path=None, onnx_path=None)


def test_resolve_spagan_onnx_path_prefers_bundled(tmp_path: Path) -> None:
    weights_dir = tmp_path / "weights"
    weights_dir.mkdir()
    resolved = resolve_spagan_onnx_path(
        env_path=None,
        weights_dir=weights_dir,
        spagan_onnx_name="custom.onnx",
        downloaded=None,
    )
    if BUNDLED_ONNX.exists():
        assert resolved == BUNDLED_ONNX.resolve()
    else:
        assert resolved is None


def test_resolve_spagan_onnx_path_uses_env_override(tmp_path: Path) -> None:
    weights_dir = tmp_path / "weights"
    weights_dir.mkdir()
    env_model = tmp_path / "env.onnx"
    if BUNDLED_ONNX.exists():
        env_model.write_bytes(BUNDLED_ONNX.read_bytes())
    else:
        env_model.write_bytes(b"placeholder")
    resolved = resolve_spagan_onnx_path(
        env_path=env_model,
        weights_dir=weights_dir,
        spagan_onnx_name="custom.onnx",
        downloaded=None,
    )
    assert resolved == env_model.resolve()


@pytest.mark.skipif(not BUNDLED_ONNX.exists(), reason="Bundled SpA-GAN ONNX weights are unavailable.")
def test_service_resolves_bundled_spagan_weights(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TRINETRA_MODEL_URL", raising=False)
    monkeypatch.delenv("TRINETRA_MODEL_SHA256", raising=False)
    monkeypatch.delenv("TRINETRA_SPAGAN_ONNX_PATH", raising=False)
    from backend.config import get_settings
    from backend.service import TrinetraService

    settings = get_settings()
    cached = settings.weights_dir / settings.spagan_onnx_name
    if cached.exists():
        cached.unlink()
    service = TrinetraService(settings)
    resolved = service._resolve_spagan_weights()
    assert resolved == BUNDLED_ONNX.resolve()
    assert service.check_runtime() is None
    assert service.engine.info.model == "SpA-GAN-RICE1"
