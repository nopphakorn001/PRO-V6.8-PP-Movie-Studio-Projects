# WWII: Untold Stories

Historical documentary projects produced with PRO V6.8 P&P Movie Studio.

## Season 1

The first season is planned as **10 complete standalone episodes**, each based on one real Second World War event.

See:

- `SERIES.md` — full 10-episode lineup, format and historical guardrails.
- `PROJECT_INDEX.json` — machine-readable episode/folder/status index.
- `EPxx-*/PLAN.md` — production outline for each episode, designed to expand to 75 scenes x 8 seconds (~10 minutes).

## Production workflow

Each episode folder may contain:

- `PLAN.md` — researched production outline.
- `STEP4.json` — 75-scene skeleton when preserved.
- `STEP5.json` — character/location production design when preserved.
- `STEP6.json` — primary import-ready detailed project.
- `STEP6_IMAGE.json` — only important image checkpoints because embedded Base64 can become very large.

## Documentary standard

- Vertical 9:16.
- 75 scenes x 8 seconds target.
- 1 scene = 1 shot + 1 main action + 1 camera movement.
- Narrator-primary storytelling; dialogue only when necessary.
- No invented dialogue presented as a verified historical quote.
- Historically plausible reenactment rather than exact real-person face cloning.
- Verify chronology, uniforms, locations, equipment and disputed claims before final STEP6.
- Avoid myths, graphic violence and glamorous/game-like war imagery.

## Season folders

1. `EP01-Castle-Itter`
2. `EP02-Operation-Postmaster`
3. `EP03-Operation-Mincemeat`
4. `EP04-Operation-Gunnerside`
5. `EP05-Battle-of-Attu`
6. `EP06-Operation-Jaywick`
7. `EP07-Rescue-of-Danish-Jews`
8. `EP08-Battle-of-Kohima-Tennis-Court`
9. `EP09-Operation-Viersen-Ghost-Army`
10. `EP10-Raid-at-Cabanatuan`

Large Base64 image snapshots and final video binaries should not be duplicated unnecessarily in Git.
