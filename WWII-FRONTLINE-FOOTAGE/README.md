# WWII FRONTLINE FOOTAGE

Historical AI cinematic reenactment series covering 10 major World War II battlefields from 1939–1945.

## Production standard

- Workflow: PRO V6.8 / P&P Movie Studio STEP6
- Format: 9:16 vertical
- Runtime: 15 scenes × 8 seconds ≈ 120 seconds per episode
- Camera language: third-person embedded field-camera / wartime-film reenactment
- This is intentionally separate from the first-person `WWII-SOLDIER-POV` series
- No spoken dialogue
- No narrator
- Human audio: breathing and nonverbal exertion only
- Environmental audio: battlefield ambience, weather, engines, vehicles, footsteps, equipment, distant gunfire and artillery
- Music: restrained, always secondary to environmental sound
- Combat: non-graphic historical depiction
- 1 scene = 1 primary action + 1 dominant camera movement
- Preserve physical continuity across scenes: uniform, mud, snow, dust, wetness, smoke, daylight, equipment and damage state
- Period-correct uniforms, weapons, vehicles and environments
- No modern objects, game UI or action-game framing
- No triumphalist or propaganda staging
- Disclosure: AI-generated cinematic historical reenactment. Not archival footage.

## Detailed STEP6 pattern

EP01 was authored first as the master detailed pattern. EP02–EP10 follow the same production structure:

- episode-specific visual style and historical environment
- unique `mainStoryPrompt` and `storySummary`
- 15 individually directed scenes
- scene-level `actionDescription`
- scene-level `imageDescription`
- scene-level `videoPrompt`
- scene-level audio direction
- continuity-anchor character definition
- episode-specific atmosphere/location assets
- `metadata.json` beside every `STEP6.json`

## Episodes

| EP | Battlefield / Story | Status |
|---|---|---|
| EP01 | Poland 1939 — The War Begins | STEP6_IMPORT_READY |
| EP02 | Dunkirk 1940 — Waiting on the Beach | STEP6_IMPORT_READY |
| EP03 | Eastern Front 1941 — Into the Vast Land | STEP6_IMPORT_READY |
| EP04 | Moscow 1941 — Winter Resistance | STEP6_IMPORT_READY |
| EP05 | El Alamein 1942 — War in the Desert | STEP6_IMPORT_READY |
| EP06 | Stalingrad 1942–43 — City of Fire | STEP6_IMPORT_READY |
| EP07 | Guadalcanal 1942–43 — Jungle Frontline | STEP6_IMPORT_READY |
| EP08 | Normandy 1944 — Omaha Beach Assault | STEP6_IMPORT_READY |
| EP09 | Bastogne 1944 — Surrounded in Snow | STEP6_IMPORT_READY |
| EP10 | Berlin 1945 — The Last Streets | STEP6_IMPORT_READY |

Use `PROJECT_INDEX.json` as the series entry point for future import helpers or automation.
