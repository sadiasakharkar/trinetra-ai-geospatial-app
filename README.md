# TRINETRA-AI

TRINETRA-AI is a satellite cloud-reconstruction application with a completed Next.js workflow and a FastAPI backend. This repository now contains a production-oriented backend structure for multimodal cloud removal with an `AttentionResidualUNet`, exported inference runtimes, upload and job orchestration, training utilities, and downloadable geospatial artifacts.

## Current Architecture

- Frontend: Next.js workflow preserving `Upload -> Configure -> Run -> Validation -> Compare -> Download`
- Backend API: FastAPI endpoints for upload, job start, status, result, metrics, health, model information, cancellation, and downloads
- ML model: `AttentionResidualUNet` in `backend/ml/model.py`
- Inference runtime: TorchScript or ONNX Runtime with CPU fallback in `backend/ml/inference.py`
- Processing pipeline: upload validation, raster loading, normalization, cloud detection, sliding-window inference, post-processing, and artifact writing in `backend/pipeline.py`
- Training stack: dataset, augmentations, losses, validation, checkpointing, resume support, TensorBoard logging, and export scripts under `backend/training`

## Repository Layout

```text
backend/
  main.py
  config.py
  service.py
  pipeline.py
  ml/
  training/
  tests/
components/
app/
lib/
public/
```

## Environment Variables

Copy `.env.example` and configure:

- `TRINETRA_MODEL_URL`
- `TRINETRA_MODEL_SHA256`
- `TRINETRA_TORCHSCRIPT_NAME`
- `TRINETRA_ONNX_NAME`
- `TRINETRA_MAX_PATCH`
- `TRINETRA_DEFAULT_TILE`
- `TRINETRA_TILE_OVERLAP`
- `TRINETRA_BATCH_SIZE`
- `TRINETRA_NUM_WORKERS`
- `TRINETRA_MAX_UPLOAD_MB`
- `TRINETRA_LOG_LEVEL`

## Local Development

### Prerequisites

- Node.js 18+
- pnpm
- Python 3.10 to 3.12

### Install

```bash
pnpm install
pip install -r backend/requirements.txt
```

### Run

```bash
pnpm dev
```

The frontend runs on port `3000` and proxies backend requests to the FastAPI service on port `8000`.

## Training

The training pipeline expects JSON manifests with records containing:

- `cloudy`
- `target`
- `historical`
- `sar`
- `dem`
- `cloud_mask`

Run training:

```bash
python -m backend.training.train --train-manifest path/to/train.json --val-manifest path/to/val.json --output-dir work/checkpoints
```

Resume training:

```bash
python -m backend.training.train --train-manifest path/to/train.json --val-manifest path/to/val.json --output-dir work/checkpoints --resume-from work/checkpoints/last.ckpt
```

Export TorchScript and ONNX weights:

```bash
python -m backend.training.export --checkpoint work/checkpoints/best.ckpt --output-dir work/exports
```

## Inference

On startup, the backend lazily initializes the inference runtime:

1. Reuse cached TorchScript or ONNX weights if present.
2. Download weights from `TRINETRA_MODEL_URL` if configured.
3. Prefer ONNX Runtime when available.
4. Fall back to TorchScript on CPU or GPU.

If exported weights are unavailable, the backend reports a degraded health state instead of silently running an untrained model.

## API Endpoints

- `GET /api/health`
- `GET /api/model-info`
- `GET /api/datasets`
- `POST /api/upload`
- `POST /api/reconstruct/start`
- `GET /api/reconstruct/status/{job_id}`
- `POST /api/reconstruct/cancel/{job_id}`
- `GET /api/reconstruct/result/{job_id}`
- `GET /api/metrics/{job_id}`
- `GET /api/download/{job_id}/{artifact_id}`

## Downloads

Completed jobs generate:

- `reconstructed_scene.tif`
- `confidence_map.tif`
- `cloud_mask.geojson`
- `metrics.json`
- `processing_report.pdf`
- `preview.png`

## Deployment

### Render

The repository includes `render.yaml`. Set the model URL and checksum as environment variables and deploy the backend service.

### Docker

A backend-only `Dockerfile` is included:

```bash
docker build -t trinetra-ai .
docker run -p 8000:8000 --env-file .env trinetra-ai
```

### Vercel

The existing frontend deployment can remain on Vercel as long as `/api` traffic is routed to the backend service.

## Testing

Current automated coverage is minimal and lives in `backend/tests`. Expand this before release with API, integration, and large-raster tests in an environment that has the full ML and geospatial stack installed.

## Important Production Note

This repository structure is much closer to production than the original prototype, but a real deployment still requires:

- exported trained weights
- installed ML and geospatial dependencies
- integration tests executed in a full runtime
- operational validation against real satellite scenes
