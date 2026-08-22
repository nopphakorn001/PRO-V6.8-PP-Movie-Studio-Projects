# BLOCK TALES

Original voxel/block-world cinematic shorts for PRO V6.8 P&P Movie Studio.

## Production standard

- Aspect ratio: 9:16
- Scene duration: 8 seconds
- EP02 onward: 10 scenes / about 80 seconds
- No dialogue
- No narrator
- Audio storytelling: music + ambience + SFX
- 1 scene = 1 shot + 1 main action + 1 camera movement
- Keep Nox character identity consistent across episodes
- Each episode is a complete standalone story with a final visual/audio twist
- No branded game UI, logos, copied textures, or exact recreation of copyrighted game characters

## Episodes

| EP | Title | Mode | Import file |
|---|---|---|---|
| 01 | อย่าขุดบล็อกสุดท้ายนั้น | Pilot, minimal dialogue | `EP01-Dont-Mine-The-Last-Block/STEP6.json` |
| 02 | หีบที่ขยับเอง | Silent | `EP02-The-Chest-That-Moved/STEP6.json` |
| 03 | คบเพลิงอันสุดท้าย | Silent | `EP03-One-Torch-Left/STEP6.json` |
| 04 | สะพานที่หายไปทีละบล็อก | Silent | `EP04-The-Disappearing-Bridge/STEP6.json` |
| 05 | หมู่บ้านที่ไม่มีใครตื่น | Silent | `EP05-The-Silent-Village/STEP6.json` |
| 06 | ประตูที่ไม่มีอยู่เมื่อครู่ | Silent | `EP06-The-Door-That-Wasnt-There/STEP6.json` |

## Workflow

1. Import `STEP6.json` into PRO V6.8.
2. Generate character/location reference assets first when needed.
3. Generate images in small batches rather than all scenes at once.
4. Export `STEP6_IMAGE.json` as a checkpoint after image generation.
5. QC image continuity before generating videos.
6. Generate video in small batches and regenerate only failed scenes.

`STEP6.json` is the source-of-truth project file for each episode.