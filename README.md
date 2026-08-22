# PRO V6.8 P&P Movie Studio Projects

Production-content repository for JSON projects created for PRO V6.8 P&P Movie Studio.

## Structure

- `BLOCK-TALES/` — original voxel/block-world short stories. EP01–EP06 are migrated and organized here.
- `WWII-UNTOLD-STORIES/` — historical documentary projects, kept separate because they use a different production workflow.

## BLOCK TALES standard

- Vertical 9:16
- STEP6 import-ready JSON
- 8 seconds per scene
- 1 scene = 1 shot + 1 main action + 1 camera movement
- EP02 onward: no dialogue, no narrator; music + ambience + SFX only
- Original voxel world and characters; no copied game UI, logos, branded textures, or exact copyrighted characters

## File policy

- `STEP6.json` is the primary import file for each episode.
- `STEP6_IMAGE.json` is optional and should be stored only as an important checkpoint because embedded Base64 images can make files very large.
- Generated video binaries should normally stay outside Git; keep production metadata/references here instead.

## Migration status

BLOCK TALES EP01–EP06 have been migrated from `AICompanyOS/exports/block-tales` into this repository and the new repository is now the source location for future BLOCK TALES production files.

The older AICompanyOS copies are intentionally left untouched as backup for now; no source files were deleted during migration.