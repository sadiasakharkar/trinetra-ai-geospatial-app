from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from threading import Lock

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

from backend.config import Settings
from backend.logging_utils import get_logger
from backend.ml.inference import InferenceEngine
from backend.ml.weights import WeightManager
from backend.pipeline import CloudRemovalPipeline, PipelineError


class TrinetraService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger(__name__)
        self.weight_manager = WeightManager(settings.weights_dir, settings.model_url, settings.model_sha256)
        self._engine: InferenceEngine | None = None
        self._pipeline: CloudRemovalPipeline | None = None
        self._load_error: str | None = None
        self._runtime_lock = Lock()

    @property
    def engine(self) -> InferenceEngine:
        if self._engine is None:
            self._initialize_runtime()
        return self._engine

    @property
    def pipeline(self) -> CloudRemovalPipeline:
        if self._pipeline is None:
            self._initialize_runtime()
        return self._pipeline

    @property
    def load_error(self) -> str | None:
        return self._load_error

    def _initialize_runtime(self) -> None:
        with self._runtime_lock:
            if self._engine is not None and self._pipeline is not None:
                return
            try:
                torchscript_path = self.weight_manager.ensure(self.settings.torchscript_name)
                onnx_path = self.weight_manager.ensure(self.settings.onnx_name)
                self._engine = InferenceEngine(torchscript_path=torchscript_path, onnx_path=onnx_path)
                self._pipeline = CloudRemovalPipeline(self.settings, self._engine)
                self._load_error = None
                self.logger.info("Inference runtime initialized with engine=%s", self._engine.info.name)
            except Exception as exc:
                self._load_error = str(exc)
                self.logger.exception("Failed to initialize runtime")
                raise

    def check_runtime(self) -> str | None:
        try:
            _ = self.engine
            return None
        except Exception as exc:
            return str(exc)

    def list_datasets(self) -> list[dict]:
        from backend.datasets import SAMPLE_DATASETS, load_uploaded_datasets

        return SAMPLE_DATASETS + load_uploaded_datasets(self.settings.upload_dir)

    def ingest_upload(self, filename: str, content: bytes) -> dict:
        if len(content) > self.settings.max_upload_size_bytes:
            raise PipelineError(
                f"Uploaded file exceeds the configured limit of {self.settings.max_upload_size_mb} MB."
            )
        self.pipeline.validate_upload(filename)
        dataset_id = f"UPLOAD-{uuid.uuid4().hex[:8].upper()}"
        upload_dir = self.settings.upload_dir / dataset_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        raw_path = upload_dir / filename
        raw_path.write_bytes(content)
        if Image is None:
            raise PipelineError("Pillow is required for upload ingestion.")
        raster = self.pipeline.load_raster(raw_path)
        preview_path = upload_dir / "cloudy.png"
        Image.fromarray(self._to_uint8(raster.image[..., :3])).save(preview_path)
        detection = self.pipeline.detect_clouds(self.pipeline.normalize(raster.image[..., :3]))
        if cv2 is None:
            raise PipelineError("OpenCV is required for upload ingestion.")
        mask_path = upload_dir / "cloud_mask.png"
        Image.fromarray((detection["cloud_mask"] * 255).astype("uint8")).save(mask_path)
        metadata = {
            "id": dataset_id,
            "name": f"Custom Upload - {Path(filename).name}",
            "sensor": "User Uploaded Scene",
            "region": "Uploaded AOI",
            "acquired": os.path.getmtime(raw_path),
            "resolution": f"{raster.image.shape[1]} x {raster.image.shape[0]}",
            "area": f"{round((raster.image.shape[0] * raster.image.shape[1]) / 1_000_000, 3)} Mpix",
            "cloudCover": round(float(detection["cloud_mask"].mean() * 100.0), 3),
            "size": f"{round(raw_path.stat().st_size / (1024 * 1024), 3)} MB",
            "coords": str(raster.crs) if raster.crs else "Unreferenced",
            "thumb": f"/uploads/{dataset_id}/cloudy.png",
            "reconstructed": f"/uploads/{dataset_id}/cloudy.png",
            "sar": f"/uploads/{dataset_id}/cloudy.png",
            "dem": f"/uploads/{dataset_id}/cloudy.png",
            "temporal": [{"date": "Uploaded", "img": f"/uploads/{dataset_id}/cloudy.png", "clear": False}],
            "files": {"primary": raw_path.name},
        }
        (upload_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        self.logger.info("Ingested upload %s into dataset %s", filename, dataset_id)
        return metadata

    def run_job(self, dataset_id: str, config: dict) -> dict:
        dataset_dir = self.settings.upload_dir / dataset_id
        if dataset_dir.exists():
            metadata = json.loads((dataset_dir / "metadata.json").read_text(encoding="utf-8"))
            primary_path = dataset_dir / metadata["files"]["primary"]
        else:
            primary_path = self.settings.public_dir / "images" / "liss-iv-cloudy.png"
        if not primary_path.exists():
            raise PipelineError(f"Primary raster was not found for dataset {dataset_id}.")
        raster = self.pipeline.load_raster(primary_path)
        extras = {"sar": None, "dem": None, "historical": None}
        outputs, metrics = self.pipeline.run(raster, extras, tile_size=int(config.get("tileSize", self.settings.default_tile_size)))
        output_dir = self.settings.output_dir / config["job_id"]
        output_paths = self.pipeline.write_outputs(output_dir, raster, outputs, metrics)
        return {
            "job_id": config["job_id"],
            "cloud_cover_pct": metrics["cloud_coverage"],
            "metrics": {
                "psnr": metrics["psnr"],
                "ssim": metrics["ssim"],
                "sam": metrics["sam"],
                "ndvi": metrics["ndvi"],
            },
            "detailed_metrics": metrics,
            "output_paths": output_paths,
        }

    @staticmethod
    def _to_uint8(image: object) -> object:
        import numpy as np

        array = np.asarray(image)
        if array.dtype == np.uint8:
            return array
        array = array.astype(np.float32)
        if array.max() <= 1.0:
            array = array * 255.0
        return np.clip(array, 0, 255).astype(np.uint8)
