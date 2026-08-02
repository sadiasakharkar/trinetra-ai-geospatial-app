from __future__ import annotations

import json
import os
import time
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

from backend.config import DEFAULT_BUNDLED_SPAGAN_ONNX, Settings, resolve_spagan_onnx_path
from backend.datasets import dataset_path_from_url, find_dataset, load_sample_datasets, load_uploaded_datasets
from backend.logging_utils import get_logger
from backend.media import public_url, save_gray, save_rgb, save_thumbnail
from backend.ml.inference import InferenceEngine
from backend.ml.weights import WeightManager, WeightSpec
from backend.pipeline import CloudRemovalPipeline, PipelineError


class TrinetraService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = get_logger(__name__)
        catalog: dict[str, WeightSpec] = {}
        if settings.model_url:
            catalog[settings.spagan_onnx_name] = WeightSpec(
                url=settings.model_url,
                sha256=settings.model_sha256,
            )
        if settings.attention_onnx_url:
            catalog[settings.onnx_name] = WeightSpec(
                url=settings.attention_onnx_url,
                sha256=settings.attention_onnx_sha256,
            )
        self.weight_manager = WeightManager(settings.weights_dir, catalog)
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
                spagan_path = self._resolve_spagan_weights()
                torchscript_path = self.weight_manager.ensure(self.settings.torchscript_name)
                onnx_path = self.weight_manager.ensure(self.settings.onnx_name)
                self._engine = InferenceEngine(
                    spagan_onnx_path=spagan_path,
                    torchscript_path=torchscript_path,
                    onnx_path=onnx_path,
                )
                self._pipeline = CloudRemovalPipeline(self.settings, self._engine)
                self._load_error = None
                self.logger.info(
                    "Inference runtime initialized with engine=%s model=%s spagan_onnx=%s",
                    self._engine.info.name,
                    self._engine.info.model,
                    spagan_path,
                )
            except Exception as exc:
                self._load_error = str(exc)
                self.logger.exception("Failed to initialize runtime")
                raise

    def _resolve_spagan_weights(self) -> Path | None:
        downloaded = self.weight_manager.ensure(self.settings.spagan_onnx_name)
        return resolve_spagan_onnx_path(
            env_path=self.settings.spagan_onnx_path,
            weights_dir=self.settings.weights_dir,
            spagan_onnx_name=self.settings.spagan_onnx_name,
            downloaded=downloaded,
        )

    def check_runtime(self) -> str | None:
        try:
            _ = self.engine
            return None
        except Exception as exc:
            return str(exc)

    def list_datasets(self) -> list[dict]:
        return load_sample_datasets(self.settings.dataset_dir) + load_uploaded_datasets(self.settings.upload_dir)

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
        save_rgb(preview_path, self._to_uint8(raster.image[..., :3]))
        thumbnail_path = upload_dir / "thumbnail.png"
        save_thumbnail(preview_path, thumbnail_path)
        detection = self.pipeline.detect_clouds(self.pipeline.normalize(raster.image[..., :3]))
        if cv2 is None:
            raise PipelineError("OpenCV is required for upload ingestion.")
        mask_path = upload_dir / "cloud_mask.png"
        save_gray(mask_path, detection["cloud_mask"] * 255)
        historical_path = upload_dir / "historical.png"
        save_rgb(historical_path, self._to_uint8(raster.image[..., :3]))
        public_preview_path = self.settings.preview_dir / dataset_id / "cloudy.png"
        public_thumbnail_path = self.settings.thumbnail_dir / dataset_id / "thumbnail.png"
        public_mask_path = self.settings.mask_dir / dataset_id / "cloud_mask.png"
        save_rgb(public_preview_path, self._to_uint8(raster.image[..., :3]))
        save_thumbnail(public_preview_path, public_thumbnail_path)
        save_gray(public_mask_path, detection["cloud_mask"] * 255)
        cloud_cover = round(float(detection["cloud_mask"].mean() * 100.0), 3)
        image_url = public_url(public_preview_path, self.settings.public_dir, "")
        thumbnail_url = public_url(public_thumbnail_path, self.settings.public_dir, "")
        mask_url = public_url(public_mask_path, self.settings.public_dir, "")
        historical_url = public_url(historical_path, self.settings.public_dir, "")
        metadata = {
            "id": dataset_id,
            "name": f"Custom Upload - {Path(filename).name}",
            "sensor": "User Uploaded Scene",
            "region": "Uploaded AOI",
            "acquired": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(raw_path))),
            "resolution": f"{raster.image.shape[1]} x {raster.image.shape[0]}",
            "area": f"{round((raster.image.shape[0] * raster.image.shape[1]) / 1_000_000, 3)} Mpix",
            "cloudCover": cloud_cover,
            "size": f"{round(raw_path.stat().st_size / (1024 * 1024), 3)} MB",
            "coords": str(raster.crs) if raster.crs else "Unreferenced",
            "preview_image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "cloud_mask_url": mask_url,
            "historical_image_url": historical_url,
            "clear_reference_url": historical_url,
            "reconstructed_image_url": historical_url,
            "dataset_json_url": f"/uploads/{dataset_id}/metadata.json",
            "thumb": thumbnail_url,
            "reconstructed": historical_url,
            "sar": mask_url,
            "dem": historical_url,
            "temporal": [{"date": "Uploaded", "img": historical_url, "clear": True}, {"date": "Current", "img": image_url, "clear": False}],
            "files": {"primary": raw_path.name},
            "geographic_info": {
                "crs": str(raster.crs) if raster.crs else "Unreferenced",
                "bounds": None,
                "transform": str(raster.transform) if raster.transform else None,
            },
            "metadata": {
                "filename": Path(filename).name,
                "width": int(raster.image.shape[1]),
                "height": int(raster.image.shape[0]),
                "bands": int(raster.image.shape[2]),
                "cloud_percentage": cloud_cover,
            },
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
            metadata = find_dataset(self.settings.dataset_dir, dataset_id)
            if metadata is None:
                raise PipelineError(f"Dataset {dataset_id} was not found.")
            primary_path = dataset_path_from_url(self.settings.dataset_dir, metadata.get("preview_image_url"))
            if primary_path is None:
                raise PipelineError(f"Dataset {dataset_id} does not include a valid preview image.")
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
            "preview_image_url": output_paths["preview_image_url"],
            "thumbnail_url": output_paths["thumbnail_url"],
            "cloud_mask_url": output_paths["cloud_mask_url"],
            "confidence_map_url": output_paths["confidence_map_url"],
            "reconstructed_image_url": output_paths["reconstructed_image_url"],
            "download_urls": output_paths["download_urls"],
            "metadata": metadata,
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
