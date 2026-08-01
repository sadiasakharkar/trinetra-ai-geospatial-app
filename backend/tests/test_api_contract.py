from __future__ import annotations

from backend.job_store import JobStore


def test_job_store_lifecycle() -> None:
    store = JobStore()
    store.create("job-1")
    store.set_status("job-1", "running")
    store.set_progress("job-1", 55)
    store.append_log("job-1", "started", "info")
    snapshot = store.snapshot("job-1")
    assert snapshot["status"] == "running"
    assert snapshot["progress"] == 55
    assert snapshot["logs"][0]["text"] == "started"


def test_job_store_completion() -> None:
    store = JobStore()
    store.create("job-2")
    store.set_result("job-2", {"ok": True})
    snapshot = store.snapshot("job-2")
    assert snapshot["status"] == "complete"
    assert snapshot["result"] == {"ok": True}
