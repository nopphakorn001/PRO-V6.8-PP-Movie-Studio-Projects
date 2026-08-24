"""Official YouTube private-upload executor for PPMovieStudio.

OAuth material is stored outside the repository.  The module never prints or
returns access tokens, refresh tokens, client secrets, or resumable session URLs.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import secrets
import socket
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

import autopost


SCOPES = (
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
)
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
UPLOAD_URI = "https://www.googleapis.com/upload/youtube/v3/videos"
CHANNEL_URI = "https://www.googleapis.com/youtube/v3/channels?part=id,snippet&mine=true"
SECRET_FILE = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "AICompanyOS" / "secrets" / "ppmoviestudio_youtube.json"


class YouTubePublisherError(RuntimeError):
    pass


def _read_json_response(response: Any) -> dict[str, Any]:
    value = json.loads(response.read().decode("utf-8"))
    if not isinstance(value, dict):
        raise YouTubePublisherError("YOUTUBE_RESPONSE_INVALID")
    return value


def _save_credentials(value: dict[str, Any], path: Path = SECRET_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")), encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(path)


def load_credentials(path: Path = SECRET_FILE) -> dict[str, Any]:
    if not path.is_file():
        raise YouTubePublisherError("YOUTUBE_OAUTH_NOT_CONFIGURED")
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {"client_id", "client_secret", "refresh_token"}
    if not isinstance(value, dict) or any(not str(value.get(key, "")).strip() for key in required):
        raise YouTubePublisherError("YOUTUBE_OAUTH_INCOMPLETE")
    return value


def credential_status(path: Path = SECRET_FILE) -> dict[str, Any]:
    try:
        value = load_credentials(path)
        return {
            "configured": True,
            "refresh_token_configured": True,
            "scopes": list(value.get("scopes") or SCOPES),
            "secret_location": "WINDOWS_USER_PROFILE",
        }
    except (OSError, ValueError, YouTubePublisherError):
        return {
            "configured": False,
            "refresh_token_configured": False,
            "scopes": list(SCOPES),
            "secret_location": "WINDOWS_USER_PROFILE",
        }


def _post_form(url: str, values: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(values).encode("ascii"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return _read_json_response(response)
    except urllib.error.HTTPError as exc:
        raise YouTubePublisherError(f"YOUTUBE_OAUTH_HTTP_{exc.code}") from exc


def _oauth_client(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    client = value.get("installed") or value.get("web")
    if not isinstance(client, dict):
        raise YouTubePublisherError("YOUTUBE_CLIENT_SECRETS_INVALID")
    client_id = str(client.get("client_id", "")).strip()
    client_secret = str(client.get("client_secret", "")).strip()
    if not client_id or not client_secret:
        raise YouTubePublisherError("YOUTUBE_CLIENT_SECRETS_INCOMPLETE")
    return {"client_id": client_id, "client_secret": client_secret}


def authorize(
    client_secrets: Path,
    *,
    timeout_seconds: int = 300,
    store: Path = SECRET_FILE,
    auth_url_file: Path | None = None,
) -> dict[str, Any]:
    """Run the desktop-app loopback OAuth flow and persist only in the user profile."""
    client = _oauth_client(client_secrets)
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode("ascii")
    result: dict[str, str] = {}
    event = threading.Event()

    class Callback(BaseHTTPRequestHandler):
        def log_message(self, *_args: object) -> None:
            return

        def do_GET(self) -> None:
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result["state"] = query.get("state", [""])[0]
            result["code"] = query.get("code", [""])[0]
            result["error"] = query.get("error", [""])[0]
            body = "Authorization received. You may close this window.".encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            event.set()

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = int(probe.getsockname()[1])
    server = HTTPServer(("127.0.0.1", port), Callback)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    redirect_uri = f"http://127.0.0.1:{port}/oauth2callback"
    query = urllib.parse.urlencode({
        "client_id": client["client_id"], "redirect_uri": redirect_uri,
        "response_type": "code", "scope": " ".join(SCOPES), "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256",
        "access_type": "offline", "prompt": "consent",
    })
    authorization_url = AUTH_URI + "?" + query
    if auth_url_file is None:
        webbrowser.open(authorization_url)
    else:
        auth_url_file.parent.mkdir(parents=True, exist_ok=True)
        auth_url_file.write_text(authorization_url, encoding="utf-8")
    event.wait(max(30, min(timeout_seconds, 600)))
    server.shutdown()
    server.server_close()
    if auth_url_file is not None:
        auth_url_file.unlink(missing_ok=True)
    if result.get("state") != state or not result.get("code") or result.get("error"):
        raise YouTubePublisherError("YOUTUBE_OAUTH_AUTHORIZATION_FAILED")
    token = _post_form(TOKEN_URI, {
        "client_id": client["client_id"], "client_secret": client["client_secret"],
        "code": result["code"], "code_verifier": verifier,
        "grant_type": "authorization_code", "redirect_uri": redirect_uri,
    })
    refresh_token = str(token.get("refresh_token", "")).strip()
    if not refresh_token:
        raise YouTubePublisherError("YOUTUBE_OAUTH_REFRESH_TOKEN_MISSING")
    _save_credentials({**client, "refresh_token": refresh_token, "scopes": list(SCOPES)}, store)
    return credential_status(store)


def refresh_access_token(credentials: dict[str, Any]) -> str:
    token = _post_form(TOKEN_URI, {
        "client_id": str(credentials["client_id"]),
        "client_secret": str(credentials["client_secret"]),
        "refresh_token": str(credentials["refresh_token"]),
        "grant_type": "refresh_token",
    })
    access_token = str(token.get("access_token", "")).strip()
    if not access_token:
        raise YouTubePublisherError("YOUTUBE_ACCESS_TOKEN_MISSING")
    return access_token


def authenticated_channel(access_token: str) -> dict[str, str]:
    request = urllib.request.Request(CHANNEL_URI, headers={"Authorization": "Bearer " + access_token})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            value = _read_json_response(response)
    except urllib.error.HTTPError as exc:
        raise YouTubePublisherError(f"YOUTUBE_CHANNEL_HTTP_{exc.code}") from exc
    items = value.get("items") or []
    if len(items) != 1:
        raise YouTubePublisherError("YOUTUBE_CHANNEL_NOT_UNIQUE")
    return {"id": str(items[0].get("id", "")), "title": str((items[0].get("snippet") or {}).get("title", ""))}


def _upload_resumable(access_token: str, payload: dict[str, Any]) -> dict[str, Any]:
    asset = Path(str(payload["asset_absolute_path"])).resolve()
    root = autopost.ROOT.resolve()
    if root not in asset.parents or not asset.is_file():
        raise YouTubePublisherError("YOUTUBE_ASSET_OUTSIDE_WORKSPACE")
    options = dict(payload.get("options") or {})
    metadata = {
        "snippet": {
            "title": str(payload["title"])[:100],
            "description": str(payload["description"])[:5000],
            "tags": list(payload.get("tags") or [])[:500],
            "categoryId": str(options.get("category_id") or "22"),
            "defaultLanguage": str(payload.get("language") or "th-TH").split("-", 1)[0],
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": bool(options.get("self_declared_made_for_kids")),
            "containsSyntheticMedia": bool(options.get("contains_synthetic_media", True)),
        },
    }
    data = json.dumps(metadata, ensure_ascii=False).encode("utf-8")
    start_url = UPLOAD_URI + "?" + urllib.parse.urlencode({
        "uploadType": "resumable", "part": "snippet,status", "notifySubscribers": "false",
    })
    request = urllib.request.Request(start_url, data=data, method="POST", headers={
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Length": str(asset.stat().st_size),
        "X-Upload-Content-Type": "video/mp4",
    })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            session_url = response.headers.get("Location", "")
        if not session_url.startswith("https://www.googleapis.com/upload/"):
            raise YouTubePublisherError("YOUTUBE_RESUMABLE_SESSION_INVALID")
        upload = urllib.request.Request(session_url, data=asset.read_bytes(), method="PUT", headers={
            "Authorization": "Bearer " + access_token,
            "Content-Type": "video/mp4",
            "Content-Length": str(asset.stat().st_size),
        })
        with urllib.request.urlopen(upload, timeout=600) as response:
            return _read_json_response(response)
    except urllib.error.HTTPError as exc:
        raise YouTubePublisherError(f"YOUTUBE_UPLOAD_HTTP_{exc.code}") from exc


def publish_private(job_id: str, *, store: Path = SECRET_FILE) -> dict[str, Any]:
    queue = autopost.load_queue()
    job = autopost.find_job(queue, job_id)
    if job.get("status") not in {"READY", "CLAIMED"}:
        raise YouTubePublisherError("YOUTUBE_JOB_NOT_READY")
    payload = autopost.build_publish_payload(job_id, "youtube_shorts")
    if str((payload.get("options") or {}).get("privacy_status")) != "private":
        raise YouTubePublisherError("YOUTUBE_PRIVATE_ONLY")
    credentials = load_credentials(store)
    token = refresh_access_token(credentials)
    channel = authenticated_channel(token)
    channels, _platforms = autopost.load_config()
    expected = str(channels["channels"][job["channel_group"]].get("youtube_channel_id", ""))
    if not expected or channel["id"] != expected:
        raise YouTubePublisherError("YOUTUBE_CHANNEL_SCOPE_MISMATCH")
    if job.get("status") == "READY":
        autopost.claim_job(job_id, "ppmovie_publisher")
    autopost.update_job_status(job_id, "PUBLISHING", "YouTube private resumable upload")
    try:
        video = _upload_resumable(token, payload)
        video_id = str(video.get("id", "")).strip()
        if not video_id:
            raise YouTubePublisherError("YOUTUBE_VIDEO_ID_MISSING")
        url = "https://youtu.be/" + video_id
        autopost.record_platform_result(job_id, "youtube", "PUBLISHED", video_id, url)
        completed = autopost.record_platform_result(job_id, "youtube_shorts", "PUBLISHED", video_id, url)
        return {
            "ok": True, "job_id": job_id, "privacy_status": "private",
            "channel_id": expected, "channel_title": channel["title"],
            "video_id": video_id, "url": url, "job_status": completed["status"],
        }
    except Exception as exc:
        error = str(exc)[:300]
        autopost.record_platform_result(job_id, "youtube", "FAILED", error=error)
        autopost.record_platform_result(job_id, "youtube_shorts", "FAILED", error=error)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="PPMovieStudio YouTube private publisher")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    oauth = sub.add_parser("oauth")
    oauth.add_argument("--client-secrets", type=Path, required=True)
    oauth.add_argument("--auth-url-file", type=Path)
    upload = sub.add_parser("upload-private")
    upload.add_argument("--job-id", required=True)
    args = parser.parse_args()
    result = credential_status() if args.command == "status" else (
        authorize(args.client_secrets, auth_url_file=args.auth_url_file)
        if args.command == "oauth" else publish_private(args.job_id)
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
