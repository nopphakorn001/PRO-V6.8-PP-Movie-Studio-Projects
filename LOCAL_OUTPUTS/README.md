# Local Outputs

Put generated videos, thumbnails, subtitles, and upload-ready exports here while working locally.

Recommended structure:

```text
LOCAL_OUTPUTS/
  KID/
    minecraft-adventures/
      EP01/
        master.mp4
        short.mp4
        thumbnail.jpg
        subtitle.srt
    block-tales/
      EP01/
        master.mp4
  HISTORY/
    wwii-untold-stories/
      EP01/
        master.mp4
        short.mp4
        thumbnail.jpg
        subtitle.srt
```

`master.mp4` is the YouTube version. `short.mp4` is the Shorts, TikTok, and Facebook Reels version. Kid jobs may reuse the master when it is already short-form; History normally needs both full and short versions.

Video files such as `.mp4`, `.mov`, `.mkv`, `.avi`, and `.webm` are ignored by Git. Store only metadata references in each episode `metadata.json`.
