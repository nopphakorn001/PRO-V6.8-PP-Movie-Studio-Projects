# Auto-Post Metadata README

This repository stores one `metadata.json` file per episode for future automation that publishes or schedules content to YouTube, YouTube Shorts, TikTok, and Facebook Reels.

## Location

Each episode folder contains:

- `STEP6.json` or `PLAN.md` as the production source file.
- `metadata.json` as the publishing metadata source.

Series indexes also include a `metadata` field per episode so automation can discover files without scanning folders.

## Schema

The shared schema lives in `METADATA_SCHEMA.json`. All episode metadata uses uppercase publishing fields for stable automation mapping:

- `TITLE_TH`, `TITLE_EN`
- `SHORT_DESCRIPTION_TH`, `LONG_DESCRIPTION_TH`
- `HOOK`
- `HASHTAGS`
- `KEYWORDS` and `TAGS`
- `PLATFORM_CAPTIONS.YOUTUBE`
- `PLATFORM_CAPTIONS.YOUTUBE_SHORTS`
- `PLATFORM_CAPTIONS.TIKTOK`
- `PLATFORM_CAPTIONS.FACEBOOK_REELS`
- `CTA`
- `CONTENT_WARNING`
- `LANGUAGE`
- `ASPECT_RATIO`
- `DURATION_TARGET`
- `SERIES`, `SERIES_ID`, `EPISODE`
- `STATUS`
- `GITHUB_PATH`, `GITHUB_URL`, `SOURCE_PROJECT_FILE`
- `OUTPUT_REFERENCES` for final video, thumbnail, subtitle, platform IDs, and published URLs

## Automation Notes

`OUTPUT_REFERENCES` values are intentionally blank until render/export/upload steps produce real assets or platform IDs. Automation should write those fields after each successful stage.

`AUTOMATION_NOTES.READY_FOR_AUTO_POST` is currently `false` by default. Set it to `true` only after the rendered video, thumbnail, subtitles, and final caption review are complete.

## Content Policy Notes

- `MINECRAFT-ADVENTURES` is an unofficial fan-made creative project and should keep the fan project notice.
- `BLOCK-TALES` is original voxel/block-world content and should avoid copied game UI, logos, branded textures, or exact copyrighted characters.
- `WWII-UNTOLD-STORIES` is historical documentary content. Verify names, dates, and claims before publication.
