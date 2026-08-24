"""Bounded local Google Flow worker orchestration for PPMovieStudio.

The runner persists paths and status only. It never stores the access-key value,
browser cookies, or generated media bytes in the queue database.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from uuid import uuid4

import autopost


STATE_FILE = autopost.ROOT / "automation" / "state" / "flow_jobs.json"
WORKER = autopost.ROOT / "automation" / "flow_worker.mjs"
ACCESS_KEY_FILE = autopost.ROOT / "Access_Key.txt"
FLOW_URL = (
    "https://labs.google/fx/tools/flow/project/7c7bdbb9-b431-4ad8-a2d7-0597f685b5fe/"
    "tool-version/c137fec7-6ff7-41eb-8d93-784d1d54c03c"
)
ALLOWED_ACTIONS = {
    "FLOW_IMPORT_STEP6",
    "FLOW_CREATE_ALL_IMAGES",
    "FLOW_GENERATE_ALL_VIDEOS",
    "FLOW_CREATE_COVER",
    "FLOW_EXPORT_1080P",
    "FLOW_RUN_TO_EXPORT",
}


class FlowRunnerError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_path(value: str) -> Path:
    relative = PurePosixPath(value.replace("\\", "/"))
    if relative.is_absolute() or ".." in relative.parts:
        raise FlowRunnerError("PPMOVIE_FLOW_PATH_OUTSIDE_WORKSPACE")
    root = autopost.ROOT.resolve()
    candidate = root.joinpath(*relative.parts).resolve()
    if root not in candidate.parents:
        raise FlowRunnerError("PPMOVIE_FLOW_PATH_OUTSIDE_WORKSPACE")
    return candidate


def _read_state() -> dict[str, object]:
    if not STATE_FILE.exists():
        return {"schema_version": "1.0.0", "jobs": []}
    value = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("jobs"), list):
        raise FlowRunnerError("PPMOVIE_FLOW_STATE_INVALID")
    return value


def _write_state(state: dict[str, object]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(STATE_FILE)


def _job_contract(job_id: str) -> dict[str, object]:
    queue = autopost.load_queue() if autopost.QUEUE_FILE.exists() else autopost.build_queue()
    job = next((item for item in queue["jobs"] if item["job_id"] == job_id), None)
    if not job:
        raise FlowRunnerError("PPMOVIE_FLOW_JOB_NOT_FOUND")
    metadata_path = _safe_path(str(job["metadata_file"]))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    source_value = str(metadata.get("SOURCE_PROJECT_FILE") or "")
    source_path = _safe_path(source_value)
    if source_path.name.lower() != "step6.json" or not source_path.is_file():
        raise FlowRunnerError("PPMOVIE_FLOW_STEP6_NOT_FOUND")
    output_value = str((job.get("assets") or {}).get("master_video") or "")
    output_path = _safe_path(output_value)
    return {
        "job_id": job_id,
        "content_id": str(job["content_id"]),
        "source_path": str(source_path),
        "output_path": str(output_path),
        "channel_group": str(job["channel_group"]),
    }


def status() -> dict[str, object]:
    state = _read_state()
    changed = False
    for item in state["jobs"]:
        result_path = Path(str(item.get("result_path") or ""))
        if not result_path.is_file():
            continue
        value = json.loads(result_path.read_text(encoding="utf-8"))
        if item.get("status") != value.get("status") or item.get("detail") != value.get("detail"):
            item["status"] = value.get("status", "FAILED")
            item["detail"] = value.get("detail", {})
            item["updated_at"] = value.get("updated_at", _now())
            changed = True
    if changed:
        _write_state(state)
    jobs = list(state["jobs"])[-20:]
    return {
        "ok": True,
        "worker_available": WORKER.is_file(),
        "access_key_configured": ACCESS_KEY_FILE.is_file() and ACCESS_KEY_FILE.stat().st_size > 0,
        "jobs": jobs,
    }


def dispatch(job_id: str, action: str) -> dict[str, object]:
    if action not in ALLOWED_ACTIONS:
        raise FlowRunnerError("PPMOVIE_FLOW_ACTION_NOT_ALLOWLISTED")
    if not WORKER.is_file():
        raise FlowRunnerError("PPMOVIE_FLOW_WORKER_MISSING")
    if not ACCESS_KEY_FILE.is_file() or ACCESS_KEY_FILE.stat().st_size == 0:
        raise FlowRunnerError("PPMOVIE_FLOW_ACCESS_KEY_NOT_CONFIGURED")
    contract = _job_contract(job_id)
    state = _read_state()
    active = next((item for item in reversed(state["jobs"]) if item["job_id"] == job_id and item["status"] in {"QUEUED", "RUNNING"}), None)
    if active:
        return active
    run_id = "flowrun_" + uuid4().hex
    request_path = STATE_FILE.parent / f"{run_id}.request.json"
    result_path = STATE_FILE.parent / f"{run_id}.result.json"
    request = {
        **contract,
        "run_id": run_id,
        "action": action,
        "flow_url": FLOW_URL,
        "access_key_path": str(ACCESS_KEY_FILE),
        "result_path": str(result_path),
        "created_at": _now(),
        "policy": {
            "existing_credits_only": True,
            "purchase_allowed": False,
            "stop_on_captcha": True,
            "stop_on_account_mismatch": True,
            "youtube_upload": False,
        },
    }
    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8")
    record = {
        "run_id": run_id,
        "job_id": job_id,
        "content_id": contract["content_id"],
        "action": action,
        "status": "QUEUED",
        "request_path": str(request_path),
        "result_path": str(result_path),
        "created_at": request["created_at"],
    }
    state["jobs"].append(record)
    _write_state(state)
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(
        ["node", str(WORKER), "--request", str(request_path)],
        cwd=str(autopost.ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )
    return record
