#!/usr/bin/env python3
"""Local HTTP bridge that lets AI Company OS control the auto-post queue."""

from __future__ import annotations

import argparse
import hmac
import json
import os
import re
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import autopost
import flow_runner


MAX_BODY_BYTES = 1024 * 1024
WRITE_LOCK = threading.Lock()
JOB_ROUTE = re.compile(r"^/v1/jobs/([^/]+)/(approve|claim|status|platform-result)$")
PAYLOAD_ROUTE = re.compile(r"^/v1/jobs/([^/]+)/publish-payload$")


def load_dotenv() -> None:
    env_path = autopost.ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "AICompanyOSAutoPost/1.0"

    def log_message(self, message_format: str, *args: object) -> None:
        print(f"{self.address_string()} - {message_format % args}")

    def send_json(self, status: HTTPStatus, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def authorized(self) -> bool:
        token = os.getenv("AICOMPANYOS_API_TOKEN", "").strip()
        if not token:
            return True
        supplied = self.headers.get("Authorization", "")
        if not supplied.startswith("Bearer "):
            return False
        return hmac.compare_digest(supplied[7:], token)

    def require_auth(self) -> bool:
        if self.authorized():
            return True
        self.send_json(HTTPStatus.UNAUTHORIZED, {"ok": False, "error": "unauthorized"})
        return False

    def read_body(self) -> dict[str, object]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > MAX_BODY_BYTES:
            raise autopost.AutoPostError("request_body_too_large")
        if content_length == 0:
            return {}
        try:
            body = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise autopost.AutoPostError("invalid_json_body") from exc
        if not isinstance(body, dict):
            raise autopost.AutoPostError("request_body_must_be_an_object")
        return body

    def do_GET(self) -> None:
        try:
            route = urlparse(self.path)
            if route.path == "/v1/health":
                self.send_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "service": "ai-company-os-autopost",
                        "version": "1.0.0",
                        "queue_exists": autopost.QUEUE_FILE.exists(),
                        "flow_worker": flow_runner.status(),
                    },
                )
                return
            if route.path == "/v1/flow/status":
                self.send_json(HTTPStatus.OK, flow_runner.status())
                return
            if not self.require_auth():
                return
            if route.path == "/v1/channels":
                channels, platforms = autopost.load_config()
                self.send_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "timezone": channels["timezone"],
                        "channels": channels["channels"],
                        "platforms": platforms,
                    },
                )
                return
            if route.path == "/v1/queue":
                query = parse_qs(route.query)
                channel = query.get("channel", [None])[0]
                status = query.get("status", [None])[0]
                queue = autopost.load_queue()
                jobs = [
                    job
                    for job in queue["jobs"]
                    if (not channel or job["channel_group"] == channel)
                    and (not status or job["status"] == status)
                ]
                self.send_json(HTTPStatus.OK, {"ok": True, "jobs": jobs})
                return
            if route.path == "/v1/jobs/next":
                query = parse_qs(route.query)
                channel = query.get("channel", [None])[0]
                include_future = query.get("include_future", ["false"])[0].lower() == "true"
                job = autopost.next_job(autopost.load_queue(), channel, include_future)
                self.send_json(HTTPStatus.OK, {"ok": True, "job": job})
                return
            payload_match = PAYLOAD_ROUTE.match(route.path)
            if payload_match:
                query = parse_qs(route.query)
                platform = query.get("platform", [""])[0]
                if not platform:
                    raise autopost.AutoPostError("platform is required")
                payload = autopost.build_publish_payload(payload_match.group(1), platform)
                self.send_json(HTTPStatus.OK, {"ok": True, "payload": payload})
                return
            self.send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
        except (autopost.AutoPostError, ValueError) as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})

    def do_POST(self) -> None:
        if not self.require_auth():
            return
        try:
            route = urlparse(self.path)
            body = self.read_body()
            with WRITE_LOCK:
                if route.path == "/v1/sync":
                    queue = autopost.build_queue(body.get("start_date"))
                    self.send_json(HTTPStatus.OK, autopost.queue_summary(queue))
                    return
                if route.path == "/v1/validate":
                    result = autopost.validate_all()
                    self.send_json(
                        HTTPStatus.OK if result["ok"] else HTTPStatus.UNPROCESSABLE_ENTITY,
                        result,
                    )
                    return
                if route.path == "/v1/flow/jobs":
                    job_id = str(body.get("job_id", "")).strip()
                    action = str(body.get("action", "")).strip()
                    if not job_id or not action:
                        raise autopost.AutoPostError("job_id and action are required")
                    self.send_json(HTTPStatus.ACCEPTED, {"ok": True, "flow_job": flow_runner.dispatch(job_id, action)})
                    return
                match = JOB_ROUTE.match(route.path)
                if match:
                    job_id, action = match.groups()
                    if action == "approve":
                        approved_by = str(body.get("approved_by", "")).strip()
                        if not approved_by:
                            raise autopost.AutoPostError("approved_by is required")
                        job = autopost.approve_job(job_id, approved_by)
                    elif action == "claim":
                        agent_id = str(body.get("agent_id", "")).strip()
                        if not agent_id:
                            raise autopost.AutoPostError("agent_id is required")
                        job = autopost.claim_job(job_id, agent_id)
                    elif action == "status":
                        job = autopost.update_job_status(
                            job_id,
                            str(body.get("status", "")),
                            str(body.get("message", "")),
                        )
                    else:
                        platform = str(body.get("platform", ""))
                        status = str(body.get("status", ""))
                        if not platform or not status:
                            raise autopost.AutoPostError("platform and status are required")
                        job = autopost.record_platform_result(
                            job_id,
                            platform,
                            status,
                            str(body.get("remote_id", "")),
                            str(body.get("url", "")),
                            str(body.get("error", "")),
                        )
                    self.send_json(HTTPStatus.OK, {"ok": True, "job": job})
                    return
            self.send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "not_found"})
        except (autopost.AutoPostError, ValueError) as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="AI Company OS auto-post HTTP bridge")
    parser.add_argument("--host", default=os.getenv("AUTOPOST_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("AUTOPOST_PORT", "8787")))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), BridgeHandler)
    print(f"AI Company OS auto-post bridge: http://{args.host}:{args.port}/v1/health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAuto-post bridge stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
