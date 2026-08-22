# PRO V6.8 P&P Movie Studio Projects

Production-content repository for JSON projects created for PRO V6.8 P&P Movie Studio.

## Structure

- `BLOCK-TALES/` — original voxel/block-world short stories.
- `WWII-UNTOLD-STORIES/` — historical documentary projects (to be migrated separately).

## BLOCK TALES standard

- Vertical 9:16
- STEP6 import-ready JSON
- 8 seconds per scene
- 1 scene = 1 shot + 1 main action + 1 camera movement
- EP02 onward: no dialogue, no narrator; music + ambience + SFX only
- Original voxel world and characters; no copied game UI, logos, branded textures, or exact copyrighted characters

## File policy

- `STEP6.json` is the primary import file.
- `STEP6_IMAGE.json` may be stored only as an important checkpoint because embedded Base64 images can make files very large.
- Generated video binaries should normally stay outside Git; store project metadata/references here instead.

The older copies under `AICompanyOS/exports/block-tales` are retained as backup until migration is verified.