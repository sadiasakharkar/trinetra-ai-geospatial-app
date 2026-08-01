from __future__ import annotations

import time
import uuid

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.config import get_settings
from backend.job_store import JobStore
from backend.logging_utils import configure_logging, get_logger
from backend.schemas import StartJobRequest
from backend.service import PipelineError, TrinetraService


settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)
service = TrinetraService(settings)
jobs = JobStore()
app = FastAPI(title="TRINETRA-AI API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/output", StaticFiles(directory=settings.output_dir), name="output")
app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.mount("/previews", StaticFiles(directory=settings.preview_dir), name="previews")
app.mount("/thumbnails", StaticFiles(directory=settings.thumbnail_dir), name="thumbnails")
app.mount("/datasets", StaticFiles(directory=settings.dataset_dir), name="datasets")
app.mount("/confidence", StaticFiles(directory=settings.confidence_dir), name="confidence")
app.mount("/masks", StaticFiles(directory=settings.mask_dir), name="masks")


@app.get("/api/health")
def health() -> dict:
    engine = None
    error = service.check_runtime()
    if error is None:
        engine = service.engine.info
    return {
        "status": "ok" if error is None else "degraded",
        "time": time.time(),
        "engine": engine.name if engine else None,
        "device": engine.device if engine else None,
        "error": error,
    }


@app.get("/api/model-info")
def model_info() -> dict:
    error = service.check_runtime()
    if error:
        raise HTTPException(status_code=503, detail=error)
    info = service.engine.info
    return {
        "name": "AttentionResidualUNet",
        "engine": info.name,
        "device": info.device,
        "precision": info.precision,
        "weights_dir": str(settings.weights_dir),
    }


@app.get("/api/datasets")
def get_datasets() -> list[dict]:
    return service.list_datasets()


@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)) -> dict:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must include a filename.")
    try:
        return service.ingest_upload(file.filename, content)
    except PipelineError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _run_reconstruction(job_id: str, dataset_id: str, config: dict) -> None:
    jobs.set_status(job_id, "running")
    jobs.append_log(job_id, "Initializing production reconstruction pipeline...", "info")
    jobs.set_progress(job_id, 5)
    try:
        runtime_error = service.check_runtime()
        if runtime_error:
            jobs.append_log(job_id, f"Runtime initialized with CPU cloud-removal engine: {runtime_error}", "warn")
        config = {**config, "job_id": job_id}
        jobs.append_log(job_id, "Loading raster and validating modalities...", "info")
        jobs.set_progress(job_id, 20)
        result = service.run_job(dataset_id, config)
        jobs.append_log(job_id, f"Cloud coverage detected: {result['cloud_cover_pct']}%", "ok")
        jobs.set_progress(job_id, 80)
        jobs.append_log(job_id, "Artifacts generated successfully.", "ok")
        jobs.set_result(job_id, result)
    except Exception as exc:  # pragma: no cover
        logger.exception("Reconstruction failed for job %s", job_id)
        jobs.append_log(job_id, f"Pipeline failed: {exc}", "warn")
        jobs.set_status(job_id, "failed", error=str(exc))


@app.post("/api/reconstruct/start")
def start_reconstruction(req: StartJobRequest, background_tasks: BackgroundTasks) -> dict:
    job_id = f"JOB-{uuid.uuid4().hex[:6].upper()}"
    jobs.create(job_id)
    background_tasks.add_task(_run_reconstruction, job_id, req.datasetId, req.config.model_dump())
    return {"job_id": job_id}


@app.get("/api/reconstruct/status/{job_id}")
def get_job_status(job_id: str) -> dict:
    if not jobs.exists(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs.snapshot(job_id)


@app.post("/api/reconstruct/cancel/{job_id}")
def cancel_job(job_id: str) -> dict:
    if not jobs.exists(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    jobs.cancel(job_id)
    return {"job_id": job_id, "status": "cancelled"}


@app.get("/api/reconstruct/result/{job_id}")
def get_job_result(job_id: str) -> dict:
    if not jobs.exists(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs.snapshot(job_id)
    if job["status"] != "complete" or job["result"] is None:
        raise HTTPException(status_code=400, detail="Job not complete yet")
    return job["result"]


@app.get("/api/metrics/{job_id}")
def get_metrics(job_id: str) -> dict:
    result = get_job_result(job_id)
    return result["detailed_metrics"]


@app.get("/api/download/{job_id}/{artifact_id}")
def download_artifact(job_id: str, artifact_id: str):
    output_dir = settings.output_dir / job_id
    files = {
        "recon-tiff": ("reconstructed_scene.tif", "image/tiff"),
        "confidence": ("confidence_map.tif", "image/tiff"),
        "cloudmask": ("cloud_mask.geojson", "application/geo+json"),
        "metrics": ("metrics.json", "application/json"),
        "report": ("processing_report.pdf", "application/pdf"),
        "preview": ("preview.png", "image/png"),
        "before": ("before.png", "image/png"),
        "difference": ("difference.png", "image/png"),
        "risk": ("risk.png", "image/png"),
    }
    if artifact_id not in files:
        raise HTTPException(status_code=400, detail="Invalid artifact ID")
    filename, media_type = files[artifact_id]
    path = output_dir / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{filename} not found")
    if artifact_id == "metrics":
        return JSONResponse(content=get_metrics(job_id))
    return FileResponse(path, media_type=media_type, filename=filename)
