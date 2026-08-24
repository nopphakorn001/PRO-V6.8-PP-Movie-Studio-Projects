# AI Company OS Auto-Post

This folder is the control layer for two daily publishing channels:

| Channel | Series | Schedule | Timezone |
|---|---|---:|---|
| Kid | Minecraft Adventures, Block Tales | 1 episode/day at 17:00 | Asia/Bangkok |
| History | WWII Untold Stories | 1 episode/day at 20:00 | Asia/Bangkok |

Every job targets YouTube, YouTube Shorts, TikTok, and Facebook Reels. Safe mode is enabled by default, so initial platform visibility is private, self-only, or draft until the account owner approves public publishing.

## Local Assets

Store generated media outside Git using this structure:

```text
LOCAL_OUTPUTS/
  KID/
    minecraft-adventures/
      EP01/
        master.mp4
        short.mp4
        thumbnail.jpg
        subtitle.srt
  HISTORY/
    wwii-untold-stories/
      EP01/
        master.mp4
        short.mp4
        thumbnail.jpg
        subtitle.srt
```

`master.mp4` is used for YouTube. `short.mp4` is used for YouTube Shorts, TikTok, and Facebook Reels. For Kid episodes, the system automatically reuses `master.mp4` as the short asset when `short.mp4` is absent. History should normally provide both versions.

## Readiness Rules

A job becomes `READY` only when:

- `AUTOMATION_NOTES.READY_FOR_AUTO_POST` is `true` in the episode metadata.
- `AUTOMATION_NOTES.CAPTION_REVIEWED` is `true`.
- Every enabled platform has a caption.
- Required local video assets exist.

Missing items are listed in `readiness.blockers`. The queue never uploads a video by itself; a publisher agent must claim the job and report each platform result.

The approval command checks all required videos and captions before setting `READY_FOR_AUTO_POST` to `true`. Successful platform IDs and URLs are written back to the episode `metadata.json`, so durable publishing history can be committed without committing runtime queue state.

## Setup

1. Copy `.env.example` to `.env` and set a long `AICOMPANYOS_API_TOKEN`.
2. Refresh and validate the queue:

```powershell
python automation/autopost.py sync
python automation/autopost.py validate
```

3. Start the local bridge:

```powershell
python automation/os_bridge.py
```

The default address is `http://127.0.0.1:8787`. Keep it on localhost unless network access is protected by a firewall and TLS reverse proxy.

## AI Company OS Flow

1. Call `POST /v1/sync` after a render or metadata change.
2. Call `POST /v1/validate` and stop when `ok` is false.
3. Approve an asset-complete job with `POST /v1/jobs/{job_id}/approve` and `{ "approved_by": "qa-agent-01" }`.
4. Ask `GET /v1/jobs/next?channel=kid` or `channel=history`.
5. Claim with `POST /v1/jobs/{job_id}/claim` and `{ "agent_id": "publisher-01" }`.
6. Read the platform-ready request with `GET /v1/jobs/{job_id}/publish-payload?platform=youtube` (or another target).
7. Set the job to `PUBLISHING`.
8. Upload through each platform's approved API and report every result.
9. The job becomes `PUBLISHED` only after every target is `PUBLISHED` or intentionally `SKIPPED`.

## Google Flow Local Worker

`POST /v1/flow/jobs` queues a bounded browser job for one existing PPMovie job. The recommended full render request is `{"job_id":"kid-block-tales-ep03","action":"FLOW_RUN_TO_EXPORT"}`.

The worker uses a dedicated Chrome profile and imports the episode `STEP6.json` directly, so no Windows file-picker interaction is required. Read progress at `GET /v1/flow/status`. The local `Access_Key.txt` is read only at runtime and is ignored by Git. Google sign-in is a one-time owner action in the dedicated profile; CAPTCHA, account mismatch, credit purchase and YouTube upload remain stop conditions.

Use `AI_COMPANY_OS_CONTRACT.json` as the machine-readable endpoint contract. Runtime queue state is stored at `automation/state/queue.json` and is ignored by Git. Platform credentials belong only in `.env` or the AI Company OS secret store.

## CLI Commands

```powershell
python automation/autopost.py status
python automation/autopost.py next --channel kid --include-future
python automation/autopost.py payload kid-minecraft-adventures-ep01 youtube
python automation/autopost.py approve kid-minecraft-adventures-ep01 --by qa-agent-01
python automation/autopost.py claim kid-minecraft-adventures-ep01 --agent publisher-01
python automation/autopost.py update kid-minecraft-adventures-ep01 PUBLISHING
python automation/autopost.py platform-result kid-minecraft-adventures-ep01 youtube PUBLISHED --remote-id VIDEO_ID --url VIDEO_URL
```

Do not commit `.env`, platform access tokens, generated videos, or runtime queue files.

## Platform Activation

- YouTube publisher agents use the official `videos.insert` upload flow and the `youtube.upload` OAuth scope. New unverified API projects may be limited to private uploads until audited.
- TikTok publisher agents use Content Posting API Direct Post with the `video.publish` scope. The payload marks generated content with `is_aigc`; unaudited clients remain `SELF_ONLY` until TikTok approves the app.
- Facebook publisher agents use Meta's Reels Publishing flow and should keep safe mode as draft until the Page/app permissions are verified.

Official references:

- https://developers.google.com/youtube/v3/docs/videos/insert
- https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post
- https://developers.facebook.com/docs/video-api/guides/reels-publishing/

### YouTube Private Publisher

The local publisher uses the official desktop OAuth loopback flow, verifies the authenticated channel ID, forces `privacyStatus=private`, and uses a resumable upload session. OAuth material is stored under the current Windows user's local application data, outside Git.

```powershell
python automation/youtube_publisher.py status
python automation/youtube_publisher.py oauth --client-secrets C:\path\to\desktop-client.json
python automation/youtube_publisher.py oauth --client-secrets C:\path\to\desktop-client.json --auth-url-file %LOCALAPPDATA%\AICompanyOS\secrets\youtube_auth_url.tmp
python automation/youtube_publisher.py upload-private --job-id kid-block-tales-ep03
```

`--auth-url-file` supports a controlled browser handoff when the normal desktop browser cannot be automated. The file contains only a short-lived authorization URL, is stored outside Git, and is deleted after the OAuth callback completes.

One vertical upload is recorded as both the YouTube video and YouTube Short result with the same remote ID; no duplicate upload is created. Public visibility is not implemented by this command.
