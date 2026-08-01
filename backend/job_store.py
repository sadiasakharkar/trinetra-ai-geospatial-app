from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class JobRecord:
    status: str = "queued"
    progress: int = 0
    logs: list[dict] = field(default_factory=list)
    result: dict | None = None
    error: str | None = None
    cancelled: bool = False


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def create(self, job_id: str) -> None:
        with self._lock:
            self._jobs[job_id] = JobRecord()

    def exists(self, job_id: str) -> bool:
        with self._lock:
            return job_id in self._jobs

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def snapshot(self, job_id: str) -> dict:
        with self._lock:
            job = self._jobs[job_id]
            return {
                "status": job.status,
                "progress": job.progress,
                "logs": list(job.logs),
                "result": job.result,
                "error": job.error,
            }

    def set_status(self, job_id: str, status: str, error: str | None = None) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = status
            job.error = error

    def set_progress(self, job_id: str, progress: int) -> None:
        with self._lock:
            self._jobs[job_id].progress = max(0, min(100, int(progress)))

    def append_log(self, job_id: str, text: str, level: str = "info") -> None:
        with self._lock:
            self._jobs[job_id].logs.append(
                {
                    "time": time.strftime("%H:%M:%S"),
                    "level": level,
                    "text": text,
                }
            )

    def set_result(self, job_id: str, result: dict) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.result = result
            job.progress = 100
            job.status = "complete"

    def cancel(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.cancelled = True
            job.status = "cancelled"

    def is_cancelled(self, job_id: str) -> bool:
        with self._lock:
            return self._jobs[job_id].cancelled
