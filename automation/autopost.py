#!/usr/bin/env python3
"""Queue and validation engine controlled by AI Company OS."""

from __future__ import annotations

import argparse
import json
import os
import sys
from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_DIR = ROOT / "automation"
CHANNELS_FILE = AUTOMATION_DIR / "config" / "channels.json"
PLATFORMS_FILE = AUTOMATION_DIR / "config" / "platforms.json"
QUEUE_FILE = AUTOMATION_DIR / "state" / "queue.json"
REQUIRED_METADATA = {
    "CONTENT_ID",
    "SERIES_ID",
    "EPISODE",
    "TITLE_TH",
    "PLATFORM_CAPTIONS",
    "AUTOMATION_NOTES",
}
TERMINAL_STATUSES = {"PUBLISHED"}
ACTIVE_STATUSES = {"CLAIMED", "PUBLISHING", "PARTIAL", "FAILED", "PAUSED"}


class AutoPostError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise AutoPostError(f"Missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AutoPostError(f"Invalid JSON: {path}: {exc}") from exc


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temp_path, path)


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_config() -> tuple[dict[str, Any], dict[str, Any]]:
    channels = load_json(CHANNELS_FILE)
    platforms = load_json(PLATFORMS_FILE)
    if not channels.get("channels"):
        raise AutoPostError("channels.json has no channels")
    if not platforms.get("platforms"):
        raise AutoPostError("platforms.json has no platforms")
    return channels, platforms


def discover_metadata() -> list[tuple[Path, dict[str, Any]]]:
    found: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(ROOT.glob("*/EP*/metadata.json")):
        metadata = load_json(path)
        missing = sorted(REQUIRED_METADATA - metadata.keys())
        if missing:
            raise AutoPostError(f"{relative(path)} missing: {', '.join(missing)}")
        found.append((path, metadata))
    if not found:
        raise AutoPostError("No episode metadata.json files found")
    return found


def channel_for(series_id: str, channels: dict[str, Any]) -> str:
    matches = [
        channel_id
        for channel_id, config in channels["channels"].items()
        if series_id in config.get("series_ids", [])
    ]
    if len(matches) != 1:
        raise AutoPostError(
            f"Series '{series_id}' must belong to exactly one channel; found {matches}"
        )
    return matches[0]


def output_folder(channel_id: str, metadata: dict[str, Any]) -> Path:
    return (
        ROOT
        / "LOCAL_OUTPUTS"
        / channel_id.upper()
        / metadata["SERIES_ID"]
        / f"EP{int(metadata['EPISODE']):02d}"
    )


def expected_assets(channel_id: str, metadata: dict[str, Any]) -> dict[str, str]:
    folder = output_folder(channel_id, metadata)
    master = folder / "master.mp4"
    short = folder / "short.mp4"
    return {
        "master_video": relative(master),
        "short_video": relative(short),
        "thumbnail": relative(folder / "thumbnail.jpg"),
        "subtitle": relative(folder / "subtitle.srt"),
    }


def assess_readiness(
    metadata: dict[str, Any], assets: dict[str, str], platform_names: list[str], platforms: dict[str, Any]
) -> dict[str, Any]:
    blockers: list[str] = []
    notes = metadata.get("AUTOMATION_NOTES", {})
    if not notes.get("READY_FOR_AUTO_POST", False):
        blockers.append("metadata_not_approved")
    if not notes.get("CAPTION_REVIEWED", False):
        blockers.append("caption_not_reviewed")

    captions = metadata.get("PLATFORM_CAPTIONS", {})
    required_roles: set[str] = set()
    for platform_name in platform_names:
        config = platforms["platforms"].get(platform_name)
        if not config or not config.get("enabled", False):
            blockers.append(f"platform_disabled:{platform_name}")
            continue
        required_roles.add(config["asset_role"])
        if not str(captions.get(config["caption_key"], "")).strip():
            blockers.append(f"missing_caption:{platform_name}")

    for role in sorted(required_roles):
        asset_path = ROOT / assets[role]
        if not asset_path.is_file():
            # Kid shorts may reuse master.mp4 when short.mp4 is not present.
            if role == "short_video" and metadata["SERIES_ID"] in {
                "minecraft-adventures",
                "block-tales",
            }:
                master_path = ROOT / assets["master_video"]
                if master_path.is_file():
                    assets["short_video"] = assets["master_video"]
                    continue
            blockers.append(f"missing_asset:{role}")

    return {
        "ready": not blockers,
        "blockers": blockers,
        "checked_at": iso_now(),
    }


def new_platform_runs(platform_names: list[str]) -> dict[str, Any]:
    return {
        name: {
            "status": "PENDING",
            "remote_id": "",
            "url": "",
            "error": "",
            "updated_at": "",
        }
        for name in platform_names
    }


def build_queue(start_date: str | None = None) -> dict[str, Any]:
    channels, platforms = load_config()
    timezone_name = channels.get("timezone", "Asia/Bangkok")
    tz = ZoneInfo(timezone_name)
    configured_start = start_date or channels.get("default_start_date")
    schedule_start = (
        date.fromisoformat(configured_start)
        if configured_start
        else datetime.now(tz).date() + timedelta(days=1)
    )
    existing = load_json(QUEUE_FILE) if QUEUE_FILE.exists() else {"jobs": []}
    old_jobs = {job["job_id"]: job for job in existing.get("jobs", [])}
    metadata_items = discover_metadata()

    grouped: dict[str, list[tuple[Path, dict[str, Any]]]] = {
        channel_id: [] for channel_id in channels["channels"]
    }
    for path, metadata in metadata_items:
        grouped[channel_for(metadata["SERIES_ID"], channels)].append((path, metadata))

    jobs: list[dict[str, Any]] = []
    for channel_id, items in grouped.items():
        channel = channels["channels"][channel_id]
        priority = {
            series_id: index
            for index, series_id in enumerate(channel.get("series_priority", []))
        }
        items.sort(
            key=lambda item: (
                priority.get(item[1]["SERIES_ID"], 999),
                int(item[1]["EPISODE"]),
                item[1]["CONTENT_ID"],
            )
        )
        hour, minute = map(int, channel["daily_publish_time"].split(":"))
        for day_offset, (path, metadata) in enumerate(items):
            scheduled = datetime.combine(
                schedule_start + timedelta(days=day_offset), time(hour, minute), tzinfo=tz
            )
            job_id = f"{channel_id}-{metadata['CONTENT_ID']}"
            asset_map = expected_assets(channel_id, metadata)
            readiness = assess_readiness(
                metadata, asset_map, channel["platforms"], platforms
            )
            previous = old_jobs.get(job_id)
            if previous:
                job = deepcopy(previous)
                previous_runs = dict(job.get("platform_runs") or {})
                default_runs = new_platform_runs(channel["platforms"])
                job["platform_runs"] = {
                    name: previous_runs.get(name, default_runs[name])
                    for name in channel["platforms"]
                }
                job.update(
                    {
                        "content_id": metadata["CONTENT_ID"],
                        "channel_group": channel_id,
                        "series_id": metadata["SERIES_ID"],
                        "episode": int(metadata["EPISODE"]),
                        "title_th": metadata["TITLE_TH"],
                        "metadata_file": relative(path),
                        "assets": asset_map,
                        "updated_at": iso_now(),
                    }
                )
                if job.get("status") not in ACTIVE_STATUSES | TERMINAL_STATUSES:
                    if start_date:
                        job["scheduled_at"] = scheduled.isoformat()
                        job["priority"] = day_offset + 1
                    job["readiness"] = readiness
                    job["status"] = "READY" if readiness["ready"] else "WAITING_ASSETS"
            else:
                job = {
                    "job_id": job_id,
                    "content_id": metadata["CONTENT_ID"],
                    "channel_group": channel_id,
                    "series_id": metadata["SERIES_ID"],
                    "episode": int(metadata["EPISODE"]),
                    "title_th": metadata["TITLE_TH"],
                    "metadata_file": relative(path),
                    "scheduled_at": scheduled.isoformat(),
                    "status": "READY" if readiness["ready"] else "WAITING_ASSETS",
                    "priority": day_offset + 1,
                    "assets": asset_map,
                    "readiness": readiness,
                    "platform_runs": new_platform_runs(channel["platforms"]),
                    "claimed_by": "",
                    "claimed_at": "",
                    "created_at": iso_now(),
                    "updated_at": iso_now(),
                }
            jobs.append(job)

    queue = {
        "schema_version": "1.0.0",
        "timezone": timezone_name,
        "safe_mode": bool(platforms.get("safe_mode", True)),
        "generated_at": iso_now(),
        "jobs": sorted(jobs, key=lambda job: (job["scheduled_at"], job["channel_group"])),
    }
    write_json_atomic(QUEUE_FILE, queue)
    return queue


def load_queue() -> dict[str, Any]:
    if not QUEUE_FILE.exists():
        return build_queue()
    return load_json(QUEUE_FILE)


def queue_summary(queue: dict[str, Any]) -> dict[str, Any]:
    counts: dict[str, dict[str, int]] = {}
    for job in queue.get("jobs", []):
        channel_counts = counts.setdefault(job["channel_group"], {})
        channel_counts[job["status"]] = channel_counts.get(job["status"], 0) + 1
    return {
        "ok": True,
        "queue_file": relative(QUEUE_FILE),
        "total_jobs": len(queue.get("jobs", [])),
        "counts": counts,
        "safe_mode": queue.get("safe_mode", True),
    }


def find_job(queue: dict[str, Any], job_id: str) -> dict[str, Any]:
    for job in queue.get("jobs", []):
        if job["job_id"] == job_id:
            return job
    raise AutoPostError(f"Unknown job: {job_id}")


def next_job(queue: dict[str, Any], channel: str | None, include_future: bool) -> dict[str, Any] | None:
    now = datetime.now(timezone.utc)
    candidates = []
    for job in queue.get("jobs", []):
        if job.get("status") != "READY":
            continue
        if channel and job.get("channel_group") != channel:
            continue
        scheduled = datetime.fromisoformat(job["scheduled_at"]).astimezone(timezone.utc)
        if include_future or scheduled <= now:
            candidates.append(job)
    return min(candidates, key=lambda job: (job["scheduled_at"], job["priority"])) if candidates else None


def build_publish_payload(job_id: str, platform: str) -> dict[str, Any]:
    queue = load_queue()
    job = find_job(queue, job_id)
    channels, platforms = load_config()
    channel = channels["channels"][job["channel_group"]]
    platform_config = platforms["platforms"].get(platform)
    if platform not in job["platform_runs"] or not platform_config:
        raise AutoPostError(f"Platform '{platform}' is not configured for {job_id}")
    metadata = load_json(ROOT / job["metadata_file"])
    caption_key = platform_config["caption_key"]
    caption = metadata.get("PLATFORM_CAPTIONS", {}).get(caption_key, "")
    asset_role = platform_config["asset_role"]
    asset_relative = job["assets"][asset_role]
    policy = channel.get("publishing_policy", {})
    options: dict[str, Any] = {}
    if platform in {"youtube", "youtube_shorts"}:
        options = {
            "privacy_status": platform_config["initial_visibility"],
            "category_id": policy.get("youtube_category_id", "22"),
            "self_declared_made_for_kids": bool(policy.get("youtube_made_for_kids", False)),
            "contains_synthetic_media": bool(policy.get("contains_synthetic_media", True)),
            "notify_subscribers": False,
        }
    elif platform == "tiktok":
        options = {
            "privacy_level": "SELF_ONLY",
            "disable_duet": False,
            "disable_stitch": False,
            "disable_comment": False,
            "brand_content_toggle": False,
            "brand_organic_toggle": False,
            "is_aigc": bool(policy.get("tiktok_is_aigc", True)),
        }
    elif platform == "facebook_reels":
        options = {"publishing_phase": "draft"}
    return {
        "job_id": job_id,
        "platform": platform,
        "channel_group": job["channel_group"],
        "scheduled_at": job["scheduled_at"],
        "asset_role": asset_role,
        "asset_file": asset_relative,
        "asset_absolute_path": str((ROOT / asset_relative).resolve()),
        "title": metadata["TITLE_TH"],
        "description": caption,
        "caption": caption,
        "tags": metadata.get("TAGS", []),
        "language": metadata.get("LANGUAGE", "th-TH"),
        "content_warning": metadata.get("CONTENT_WARNING", ""),
        "options": options,
    }


def claim_job(job_id: str, agent_id: str) -> dict[str, Any]:
    queue = load_queue()
    job = find_job(queue, job_id)
    if job["status"] != "READY":
        raise AutoPostError(f"Job {job_id} is {job['status']}, not READY")
    job["status"] = "CLAIMED"
    job["claimed_by"] = agent_id
    job["claimed_at"] = iso_now()
    job["updated_at"] = iso_now()
    write_json_atomic(QUEUE_FILE, queue)
    return job


def update_job_status(job_id: str, status: str, message: str = "") -> dict[str, Any]:
    allowed = {"PUBLISHING", "PARTIAL", "PUBLISHED", "FAILED", "PAUSED", "READY"}
    if status not in allowed:
        raise AutoPostError(f"Unsupported status: {status}")
    queue = load_queue()
    job = find_job(queue, job_id)
    job["status"] = status
    job["status_message"] = message
    job["updated_at"] = iso_now()
    write_json_atomic(QUEUE_FILE, queue)
    return job


def approve_job(job_id: str, approved_by: str) -> dict[str, Any]:
    queue = load_queue()
    job = find_job(queue, job_id)
    metadata_path = ROOT / job["metadata_file"]
    metadata = load_json(metadata_path)
    channels, platforms = load_config()
    channel = channels["channels"][job["channel_group"]]
    approval_candidate = deepcopy(metadata)
    approval_candidate.setdefault("AUTOMATION_NOTES", {})["READY_FOR_AUTO_POST"] = True
    assets = deepcopy(job["assets"])
    readiness = assess_readiness(
        approval_candidate, assets, channel["platforms"], platforms
    )
    if not readiness["ready"]:
        raise AutoPostError(
            "Job cannot be approved: " + ", ".join(readiness["blockers"])
        )

    approved_at = iso_now()
    metadata.setdefault("AUTOMATION_NOTES", {}).update(
        {
            "READY_FOR_AUTO_POST": True,
            "AUTO_POST_STATUS": "APPROVED",
            "APPROVED_BY": approved_by,
            "APPROVED_AT": approved_at,
        }
    )
    references = metadata.setdefault("OUTPUT_REFERENCES", {})
    references["VIDEO_FILE"] = assets["master_video"]
    references["SHORT_VIDEO_FILE"] = assets["short_video"]
    thumbnail = ROOT / assets["thumbnail"]
    subtitle = ROOT / assets["subtitle"]
    if thumbnail.is_file():
        references["THUMBNAIL_FILE"] = assets["thumbnail"]
    if subtitle.is_file():
        references["SUBTITLE_FILE"] = assets["subtitle"]
    metadata["UPDATED_AT"] = approved_at
    write_json_atomic(metadata_path, metadata)

    refreshed = build_queue()
    return find_job(refreshed, job_id)


def write_platform_result_to_metadata(
    job: dict[str, Any], platform: str, remote_id: str, url: str, status: str
) -> None:
    metadata_path = ROOT / job["metadata_file"]
    metadata = load_json(metadata_path)
    references = metadata.setdefault("OUTPUT_REFERENCES", {})
    references.setdefault("PUBLISHED_URLS", {})
    id_keys = {
        "youtube": "YOUTUBE_VIDEO_ID",
        "youtube_shorts": "YOUTUBE_SHORTS_ID",
        "tiktok": "TIKTOK_POST_ID",
        "facebook_reels": "FACEBOOK_REEL_ID",
    }
    url_keys = {
        "youtube": "YOUTUBE",
        "youtube_shorts": "YOUTUBE_SHORTS",
        "tiktok": "TIKTOK",
        "facebook_reels": "FACEBOOK_REELS",
    }
    if remote_id:
        references[id_keys[platform]] = remote_id
    if url:
        references["PUBLISHED_URLS"][url_keys[platform]] = url
    notes = metadata.setdefault("AUTOMATION_NOTES", {})
    notes["AUTO_POST_STATUS"] = status
    notes["LAST_AUTO_POST_UPDATE"] = iso_now()
    metadata["UPDATED_AT"] = notes["LAST_AUTO_POST_UPDATE"]
    write_json_atomic(metadata_path, metadata)


def record_platform_result(
    job_id: str, platform: str, status: str, remote_id: str = "", url: str = "", error: str = ""
) -> dict[str, Any]:
    allowed = {"PENDING", "UPLOADING", "SCHEDULED", "PUBLISHED", "FAILED", "SKIPPED"}
    if status not in allowed:
        raise AutoPostError(f"Unsupported platform status: {status}")
    queue = load_queue()
    job = find_job(queue, job_id)
    if platform not in job["platform_runs"]:
        raise AutoPostError(f"Platform '{platform}' is not configured for {job_id}")
    job["platform_runs"][platform].update(
        {
            "status": status,
            "remote_id": remote_id,
            "url": url,
            "error": error,
            "updated_at": iso_now(),
        }
    )
    run_statuses = {run["status"] for run in job["platform_runs"].values()}
    if run_statuses <= {"PUBLISHED", "SKIPPED"}:
        job["status"] = "PUBLISHED"
    elif "FAILED" in run_statuses:
        job["status"] = "PARTIAL" if "PUBLISHED" in run_statuses else "FAILED"
    elif run_statuses & {"UPLOADING", "SCHEDULED", "PUBLISHED"}:
        job["status"] = "PUBLISHING"
    job["updated_at"] = iso_now()
    if status in {"SCHEDULED", "PUBLISHED"} and (remote_id or url):
        write_platform_result_to_metadata(job, platform, remote_id, url, status)
    write_json_atomic(QUEUE_FILE, queue)
    return job


def validate_all() -> dict[str, Any]:
    channels, platforms = load_config()
    metadata_items = discover_metadata()
    content_ids: set[str] = set()
    issues: list[str] = []
    for path, metadata in metadata_items:
        content_id = metadata["CONTENT_ID"]
        if content_id in content_ids:
            issues.append(f"duplicate_content_id:{content_id}")
        content_ids.add(content_id)
        channel_for(metadata["SERIES_ID"], channels)
        channel_id = channel_for(metadata["SERIES_ID"], channels)
        for platform in channels["channels"][channel_id]["platforms"]:
            platform_config = platforms["platforms"].get(platform, {})
            caption_key = platform_config.get("caption_key")
            if not caption_key or not metadata["PLATFORM_CAPTIONS"].get(caption_key):
                issues.append(f"missing_caption:{relative(path)}:{platform}")
    queue = build_queue()
    return {
        "ok": not issues,
        "metadata_files": len(metadata_items),
        "queue_jobs": len(queue["jobs"]),
        "issues": issues,
        "summary": queue_summary(queue),
    }


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="AI Company OS auto-post queue")
    subparsers = parser.add_subparsers(dest="command", required=True)
    sync_parser = subparsers.add_parser("sync", help="Discover metadata and refresh queue")
    sync_parser.add_argument("--start-date", help="First schedule date in YYYY-MM-DD")
    subparsers.add_parser("validate", help="Validate config, metadata and queue")
    subparsers.add_parser("status", help="Show queue summary")
    next_parser = subparsers.add_parser("next", help="Return the next READY job")
    next_parser.add_argument("--channel", choices=["kid", "history"])
    next_parser.add_argument("--include-future", action="store_true")
    payload_parser = subparsers.add_parser("payload", help="Build one platform publish payload")
    payload_parser.add_argument("job_id")
    payload_parser.add_argument("platform")
    claim_parser = subparsers.add_parser("claim", help="Claim one READY job")
    claim_parser.add_argument("job_id")
    claim_parser.add_argument("--agent", required=True)
    approve_parser = subparsers.add_parser("approve", help="Approve a job after asset checks")
    approve_parser.add_argument("job_id")
    approve_parser.add_argument("--by", required=True)
    update_parser = subparsers.add_parser("update", help="Update a job status")
    update_parser.add_argument("job_id")
    update_parser.add_argument("status")
    update_parser.add_argument("--message", default="")
    result_parser = subparsers.add_parser("platform-result", help="Record a platform result")
    result_parser.add_argument("job_id")
    result_parser.add_argument("platform")
    result_parser.add_argument("status")
    result_parser.add_argument("--remote-id", default="")
    result_parser.add_argument("--url", default="")
    result_parser.add_argument("--error", default="")
    args = parser.parse_args()

    try:
        if args.command == "sync":
            print_json(queue_summary(build_queue(args.start_date)))
        elif args.command == "validate":
            result = validate_all()
            print_json(result)
            return 0 if result["ok"] else 1
        elif args.command == "status":
            print_json(queue_summary(load_queue()))
        elif args.command == "next":
            print_json(next_job(load_queue(), args.channel, args.include_future))
        elif args.command == "payload":
            print_json(build_publish_payload(args.job_id, args.platform))
        elif args.command == "claim":
            print_json(claim_job(args.job_id, args.agent))
        elif args.command == "approve":
            print_json(approve_job(args.job_id, args.by))
        elif args.command == "update":
            print_json(update_job_status(args.job_id, args.status, args.message))
        elif args.command == "platform-result":
            print_json(
                record_platform_result(
                    args.job_id,
                    args.platform,
                    args.status,
                    args.remote_id,
                    args.url,
                    args.error,
                )
            )
        return 0
    except (AutoPostError, ValueError) as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
