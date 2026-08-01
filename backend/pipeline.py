from __future__ import annotations

import io
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

try:
    import rasterio
    from rasterio import features
    from rasterio.enums import Resampling
    from rasterio.transform import Affine
except ImportError:  # pragma: no cover
    rasterio = None
    features = None
    Resampling = None
    Affine = None

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None

from backend.config import Settings
from backend.logging_utils import get_logger
from backend.media import save_difference, save_gray, save_heatmap, save_rgb, save_thumbnail
from backend.ml.inference import InferenceEngine


SUPPORTED_EXTENSIONS = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".jp2"}


@dataclass(slots=True)
class RasterData:
    image: np.ndarray
    profile: dict
    transform: object | None
    crs: object | None
    nodata: float | int | None


class PipelineError(RuntimeError):
    pass


class CloudRemovalPipeline:
    def __init__(self, settings: Settings, engine: InferenceEngine) -> None:
        self.settings = settings
        self.engine = engine
        self.logger = get_logger(__name__)

    def validate_upload(self, filename: str) -> None:
        suffix = Path(filename).suffix.lower()
        if not filename:
            raise PipelineError("Uploaded file must have a valid filename.")
        if suffix not in SUPPORTED_EXTENSIONS:
            raise PipelineError(f"Unsupported file type: {suffix}")

    def load_raster(self, path: Path) -> RasterData:
        if not path.exists():
            raise PipelineError(f"Raster path does not exist: {path}")
        if rasterio is not None and path.suffix.lower() in {".tif", ".tiff", ".jp2"}:
            with rasterio.open(path) as src:
                image = src.read(out_dtype=np.float32)
                image = np.moveaxis(image, 0, -1)
                return RasterData(
                    image=image,
                    profile=src.profile.copy(),
                    transform=src.transform,
                    crs=src.crs,
                    nodata=src.nodata,
                )
        if Image is None:
            raise PipelineError("Pillow is required to read non-GeoTIFF imagery.")
        with Image.open(path) as image:
            array = np.asarray(image).astype(np.float32)
        if array.ndim == 2:
            array = np.repeat(array[..., None], 3, axis=2)
        return RasterData(
            image=array,
            profile={"driver": "PNG", "height": array.shape[0], "width": array.shape[1], "count": array.shape[2]},
            transform=None,
            crs=None,
            nodata=None,
        )

    def normalize(self, array: np.ndarray) -> np.ndarray:
        array = np.nan_to_num(array, nan=0.0, posinf=0.0, neginf=0.0)
        if array.ndim == 2:
            array = array[..., None]
        if array.shape[-1] < 3:
            array = np.repeat(array, 3, axis=2)
        normalized = np.zeros_like(array, dtype=np.float32)
        for channel in range(array.shape[-1]):
            band = array[..., channel]
            p2, p98 = np.percentile(band, [2, 98])
            if math.isclose(p2, p98):
                normalized[..., channel] = np.clip(band / 255.0, 0.0, 1.0)
                continue
            scaled = (band - p2) / (p98 - p2)
            normalized[..., channel] = np.clip(scaled, 0.0, 1.0)
        return normalized

    def detect_clouds(self, rgb: np.ndarray) -> dict[str, np.ndarray]:
        if cv2 is None:
            raise PipelineError("OpenCV is required for cloud detection.")
        rgb_u8 = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)
        hsv = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2HSV)
        value = hsv[..., 2]
        saturation = hsv[..., 1]
        brightness_threshold = float(np.percentile(value, 92))
        saturation_threshold = float(np.percentile(saturation, 40))
        raw_cloud = (value >= brightness_threshold) & (saturation <= saturation_threshold)
        raw_cloud = raw_cloud.astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        refined_cloud = cv2.morphologyEx(raw_cloud, cv2.MORPH_CLOSE, kernel, iterations=2)
        refined_cloud = cv2.morphologyEx(refined_cloud, cv2.MORPH_OPEN, kernel, iterations=1)
        shadow_threshold = float(np.percentile(value, 15))
        shadow = ((value <= shadow_threshold) & (cv2.dilate(refined_cloud, kernel, iterations=3) > 0)).astype(np.uint8)
        distance = cv2.distanceTransform((1 - refined_cloud).astype(np.uint8), cv2.DIST_L2, 5)
        confidence = 1.0 - np.clip(distance / max(distance.max(), 1.0), 0.0, 1.0)
        probability = cv2.GaussianBlur(refined_cloud.astype(np.float32), (0, 0), sigmaX=3)
        return {
            "cloud_probability": np.clip(probability, 0.0, 1.0),
            "cloud_mask": refined_cloud.astype(np.uint8),
            "shadow_mask": shadow,
            "confidence_mask": confidence.astype(np.float32),
        }

    def build_multimodal_tensor(self, rgb: np.ndarray, extras: dict[str, np.ndarray | None]) -> np.ndarray:
        if cv2 is None:
            raise PipelineError("OpenCV is required to build the multimodal tensor.")
        h, w, _ = rgb.shape
        sar = extras.get("sar")
        dem = extras.get("dem")
        historical = extras.get("historical")
        if sar is None:
            sar = cv2.cvtColor(np.clip(rgb * 255.0, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
        if dem is None:
            dem = np.gradient(rgb[..., 1])[0]
            dem = (dem - dem.min()) / (dem.max() - dem.min() + 1e-6)
        if historical is None:
            historical = rgb
        tensors = [
            np.moveaxis(rgb, -1, 0),
            sar[None, ...] if sar.ndim == 2 else np.moveaxis(sar[..., :1], -1, 0),
            dem[None, ...] if dem.ndim == 2 else np.moveaxis(dem[..., :1], -1, 0),
            np.moveaxis(historical[..., :3], -1, 0),
        ]
        stacked = np.concatenate(tensors, axis=0).astype(np.float32)
        return stacked.reshape(1, 8, h, w)

    def sliding_window_predict(self, tensor: np.ndarray, tile_size: int, overlap: int) -> dict[str, np.ndarray]:
        if tile_size <= overlap:
            raise PipelineError("Tile size must be greater than overlap.")
        _, _, height, width = tensor.shape
        stride = max(32, tile_size - overlap)
        accumulators = {
            "reconstruction": np.zeros((1, 3, height, width), dtype=np.float32),
            "confidence": np.zeros((1, 1, height, width), dtype=np.float32),
            "risk": np.zeros((1, 1, height, width), dtype=np.float32),
            "cloud": np.zeros((1, 1, height, width), dtype=np.float32),
        }
        weights = np.zeros((1, 1, height, width), dtype=np.float32)
        window = np.outer(np.hanning(tile_size), np.hanning(tile_size)).astype(np.float32)
        window = np.maximum(window, 1e-3)
        for top in range(0, height, stride):
            for left in range(0, width, stride):
                bottom = min(top + tile_size, height)
                right = min(left + tile_size, width)
                tile = tensor[:, :, top:bottom, left:right]
                pad_h = tile_size - tile.shape[-2]
                pad_w = tile_size - tile.shape[-1]
                if pad_h or pad_w:
                    tile = np.pad(tile, ((0, 0), (0, 0), (0, pad_h), (0, pad_w)), mode="reflect")
                prediction = self.engine.predict(tile)
                tile_window = window[None, None, : bottom - top, : right - left]
                for key, value in prediction.items():
                    value = value[..., : bottom - top, : right - left]
                    accumulators[key][..., top:bottom, left:right] += value * tile_window
                weights[..., top:bottom, left:right] += tile_window
        for key in accumulators:
            accumulators[key] /= np.maximum(weights, 1e-6)
        return accumulators

    def postprocess(self, rgb_input: np.ndarray, cloud_mask: np.ndarray, prediction: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        if cv2 is None:
            raise PipelineError("OpenCV is required for post-processing.")
        reconstructed = np.moveaxis(prediction["reconstruction"][0], 0, -1)
        confidence = prediction["confidence"][0, 0]
        risk = prediction["risk"][0, 0]
        model_cloud = prediction["cloud"][0, 0]
        mask = np.clip(cloud_mask.astype(np.float32), 0.0, 1.0)
        feathered_mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=2.5)
        feathered_mask = np.clip(feathered_mask, 0.0, 1.0)
        blend_mask = feathered_mask[..., None]
        blended = rgb_input * (1.0 - blend_mask) + reconstructed * blend_mask
        blended = np.where(mask[..., None] > 0, blended, rgb_input)
        blended = np.clip(blended, 0.0, 1.0)
        blended_u8 = np.clip(blended * 255.0, 0, 255).astype(np.uint8)
        enhanced = cv2.addWeighted(blended_u8, 1.08, cv2.GaussianBlur(blended_u8, (0, 0), sigmaX=1.2), -0.08, 0.0)
        sharpened = np.where(mask[..., None] > 0, enhanced, np.clip(rgb_input * 255.0, 0, 255).astype(np.uint8))
        return {
            "reconstructed": sharpened,
            "confidence": np.clip(confidence, 0.0, 1.0),
            "risk": np.clip(risk * 0.7 + model_cloud * 0.3, 0.0, 1.0),
            "cloud_mask": (mask > 0.25).astype(np.uint8),
        }

    def compute_metrics(self, source: np.ndarray, reconstructed: np.ndarray, cloud_mask: np.ndarray, started_at: float) -> dict[str, float]:
        source_f = source.astype(np.float32)
        recon_f = reconstructed.astype(np.float32)
        mse = float(np.mean((source_f - recon_f) ** 2))
        rmse = float(np.sqrt(mse))
        mae = float(np.mean(np.abs(source_f - recon_f)))
        psnr = 99.0 if mse == 0 else float(20.0 * np.log10(255.0 / np.sqrt(mse)))
        mu_x = source_f.mean()
        mu_y = recon_f.mean()
        sigma_x = source_f.var()
        sigma_y = recon_f.var()
        sigma_xy = ((source_f - mu_x) * (recon_f - mu_y)).mean()
        c1 = 6.5025
        c2 = 58.5225
        ssim = float(((2 * mu_x * mu_y + c1) * (2 * sigma_xy + c2)) / ((mu_x**2 + mu_y**2 + c1) * (sigma_x + sigma_y + c2)))
        source_vec = source_f.reshape(-1, 3)
        recon_vec = recon_f.reshape(-1, 3)
        dot = np.sum(source_vec * recon_vec, axis=1)
        denom = np.linalg.norm(source_vec, axis=1) * np.linalg.norm(recon_vec, axis=1) + 1e-6
        sam = float(np.degrees(np.mean(np.arccos(np.clip(dot / denom, -1.0, 1.0)))))
        source_nir = source_f[..., 0]
        source_red = source_f[..., 1]
        recon_nir = recon_f[..., 0]
        recon_red = recon_f[..., 1]
        ndvi_source = (source_nir - source_red) / (source_nir + source_red + 1e-6)
        ndvi_recon = (recon_nir - recon_red) / (recon_nir + recon_red + 1e-6)
        ndvi_preservation = float(100.0 - np.mean(np.abs(ndvi_source - ndvi_recon)) * 100.0)
        confidence_score = float(100.0 - cloud_mask.mean() * 100.0)
        memory_usage = float(source.nbytes + reconstructed.nbytes) / (1024.0 * 1024.0)
        return {
            "psnr": round(psnr, 3),
            "ssim": round(max(0.0, min(1.0, ssim)), 4),
            "sam": round(sam, 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "cloud_coverage": round(float(cloud_mask.mean() * 100.0), 4),
            "confidence_score": round(max(0.0, min(100.0, confidence_score)), 4),
            "inference_time": round(time.time() - started_at, 4),
            "memory_usage": round(memory_usage, 4),
            "ndvi": round(max(0.0, min(100.0, ndvi_preservation)), 4),
        }

    def write_outputs(
        self,
        output_dir: Path,
        raster: RasterData,
        outputs: dict[str, np.ndarray],
        metrics: dict[str, float],
    ) -> dict[str, str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        before_png = output_dir / "before.png"
        reconstructed_png = output_dir / "reconstructed.png"
        confidence_png = output_dir / "confidence.png"
        confidence_heatmap_png = output_dir / "confidence_heatmap.png"
        risk_png = output_dir / "risk.png"
        cloud_mask_png = output_dir / "cloud_mask.png"
        difference_png = output_dir / "difference.png"
        if Image is None:
            raise PipelineError("Pillow is required to write preview outputs.")
        before = self.normalize(raster.image[..., :3])
        before_u8 = np.clip(before * 255.0, 0, 255).astype(np.uint8)
        save_rgb(before_png, before_u8)
        save_rgb(reconstructed_png, outputs["reconstructed"])
        save_gray(confidence_png, outputs["confidence"])
        save_heatmap(confidence_heatmap_png, outputs["confidence"])
        save_gray(risk_png, outputs["risk"])
        save_gray(cloud_mask_png, outputs["cloud_mask"] * 255)
        save_difference(difference_png, before_u8, outputs["reconstructed"])
        metrics_path = output_dir / "metrics.json"
        metrics_path.write_text(json.dumps({"metrics": metrics}, indent=2), encoding="utf-8")
        report_path = output_dir / "processing_report.pdf"
        report_path.write_bytes(self._render_pdf_report(metrics))
        preview_path = output_dir / "preview.png"
        save_rgb(preview_path, outputs["reconstructed"])
        thumbnail_path = output_dir / "thumbnail.png"
        save_thumbnail(preview_path, thumbnail_path)
        public_preview_path = self.settings.preview_dir / output_dir.name / "preview.png"
        public_thumbnail_path = self.settings.thumbnail_dir / output_dir.name / "thumbnail.png"
        public_confidence_path = self.settings.confidence_dir / output_dir.name / "confidence_heatmap.png"
        public_mask_path = self.settings.mask_dir / output_dir.name / "cloud_mask.png"
        save_rgb(public_preview_path, outputs["reconstructed"])
        save_thumbnail(public_preview_path, public_thumbnail_path)
        save_heatmap(public_confidence_path, outputs["confidence"])
        save_gray(public_mask_path, outputs["cloud_mask"] * 255)
        cloud_geojson_path = output_dir / "cloud_mask.geojson"
        cloud_geojson_path.write_text(
            json.dumps(self._mask_to_geojson(outputs["cloud_mask"], raster.transform), indent=2),
            encoding="utf-8",
        )
        recon_tif = output_dir / "reconstructed_scene.tif"
        conf_tif = output_dir / "confidence_map.tif"
        if rasterio is not None and raster.profile and "dtype" in raster.profile:
            profile = raster.profile.copy()
            profile.update(driver="GTiff", dtype="uint8", count=3, compress="deflate")
            with rasterio.open(recon_tif, "w", **profile) as dst:
                dst.write(np.moveaxis(outputs["reconstructed"], -1, 0))
            conf_profile = raster.profile.copy()
            conf_profile.update(driver="GTiff", dtype="uint8", count=1, compress="deflate")
            with rasterio.open(conf_tif, "w", **conf_profile) as dst:
                dst.write((outputs["confidence"] * 255.0).astype(np.uint8), 1)
        else:
            Image.fromarray(outputs["reconstructed"]).save(recon_tif)
            Image.fromarray((outputs["confidence"] * 255.0).astype(np.uint8)).save(conf_tif)
        urls = {
            "before": f"/output/{output_dir.name}/before.png",
            "reconstructed": f"/output/{output_dir.name}/reconstructed.png",
            "reconstructed_image_url": f"/output/{output_dir.name}/reconstructed.png",
            "confidence": f"/confidence/{output_dir.name}/confidence_heatmap.png",
            "confidence_map_url": f"/confidence/{output_dir.name}/confidence_heatmap.png",
            "confidence_raw_url": f"/output/{output_dir.name}/confidence.png",
            "risk": f"/output/{output_dir.name}/risk.png",
            "risk_map_url": f"/output/{output_dir.name}/risk.png",
            "cloud_mask": f"/masks/{output_dir.name}/cloud_mask.png",
            "cloud_mask_url": f"/masks/{output_dir.name}/cloud_mask.png",
            "difference": f"/output/{output_dir.name}/difference.png",
            "difference_map_url": f"/output/{output_dir.name}/difference.png",
            "preview": f"/previews/{output_dir.name}/preview.png",
            "preview_image_url": f"/previews/{output_dir.name}/preview.png",
            "thumbnail_url": f"/thumbnails/{output_dir.name}/thumbnail.png",
            "download_urls": {
                "recon-tiff": f"/api/download/{output_dir.name}/recon-tiff",
                "confidence": f"/api/download/{output_dir.name}/confidence",
                "cloudmask": f"/api/download/{output_dir.name}/cloudmask",
                "metrics": f"/api/download/{output_dir.name}/metrics",
                "report": f"/api/download/{output_dir.name}/report",
                "preview": f"/api/download/{output_dir.name}/preview",
                "before": f"/api/download/{output_dir.name}/before",
                "difference": f"/api/download/{output_dir.name}/difference",
                "risk": f"/api/download/{output_dir.name}/risk",
            },
        }
        return urls

    def _mask_to_geojson(self, mask: np.ndarray, transform: object | None) -> dict:
        if features is None:
            return {"type": "FeatureCollection", "features": []}
        affine = transform if transform is not None else Affine.identity()
        feature_list = []
        for index, (geometry, value) in enumerate(features.shapes(mask.astype(np.uint8), mask=mask.astype(bool), transform=affine)):
            if int(value) != 1:
                continue
            feature_list.append(
                {
                    "type": "Feature",
                    "properties": {"id": index},
                    "geometry": geometry,
                }
            )
        return {"type": "FeatureCollection", "features": feature_list}

    def _render_pdf_report(self, metrics: dict[str, float]) -> bytes:
        lines = [
            "TRINETRA-AI Processing Report",
            "",
            *(f"{key}: {value}" for key, value in metrics.items()),
        ]
        payload = "\n".join(lines).encode("utf-8")
        pdf = io.BytesIO()
        pdf.write(b"%PDF-1.4\n")
        pdf.write(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
        pdf.write(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
        stream = b"BT /F1 12 Tf 40 780 Td (" + payload.replace(b"(", b"[").replace(b")", b"]").replace(b"\n", b") Tj T* (") + b") Tj ET"
        pdf.write(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n")
        pdf.write(f"4 0 obj << /Length {len(stream)} >> stream\n".encode("ascii"))
        pdf.write(stream)
        pdf.write(b"\nendstream endobj\n")
        pdf.write(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
        pdf.write(b"xref\n0 6\n0000000000 65535 f \n")
        pdf.write(b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n0\n%%EOF")
        return pdf.getvalue()

    def run(self, raster: RasterData, extras: dict[str, np.ndarray | None], tile_size: int) -> tuple[dict[str, np.ndarray], dict[str, float]]:
        started_at = time.time()
        self.logger.info("Starting cloud-removal pipeline with tile_size=%s", tile_size)
        rgb = self.normalize(raster.image[..., :3])
        masks = self.detect_clouds(rgb)
        tensor = self.build_multimodal_tensor(rgb, extras)
        prediction = self.sliding_window_predict(tensor, tile_size=tile_size, overlap=self.settings.overlap)
        outputs = self.postprocess(rgb, masks["cloud_mask"], prediction)
        metrics = self.compute_metrics((rgb * 255.0).astype(np.uint8), outputs["reconstructed"], outputs["cloud_mask"], started_at)
        result_metrics = {
            **metrics,
            "engine": self.engine.info.name,
            "device": self.engine.info.device,
            "precision": self.engine.info.precision,
        }
        self.logger.info("Pipeline finished in %.2fs", result_metrics["inference_time"])
        return outputs, result_metrics
