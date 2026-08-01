from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class FusionSourceModel(BaseModel):
    id: str
    label: str
    desc: str
    enabled: bool


class ReconConfigModel(BaseModel):
    model: str = "attention-resunet"
    sources: list[FusionSourceModel]
    fidelity: int = Field(ge=0, le=100, default=80)
    tileSize: int = Field(ge=128, le=1024, default=256)
    outputFormat: str = "geotiff"
    preserveNdvi: bool = True


class StartJobRequest(BaseModel):
    datasetId: str
    config: ReconConfigModel


class LogEntryModel(BaseModel):
    time: str
    level: Literal["info", "ok", "warn"]
    text: str


class JobStateModel(BaseModel):
    status: Literal["queued", "running", "complete", "failed", "cancelled"]
    progress: int
    logs: list[LogEntryModel]
    result: dict | None = None
    error: str | None = None
