# WWII FRONTLINE FOOTAGE

Historical AI cinematic reenactment series covering 10 major World War II battlefields from 1939–1945.

## Production standard

- Workflow: PRO V6.8 / P&P Movie Studio STEP6
- Format: 9:16 vertical
- Runtime: 15 scenes × 8 seconds ≈ 120 seconds per episode
- Camera language: **physically embedded human wartime cameraman** inside the same battlefield situation as the soldiers
- This is intentionally separate from the first-person `WWII-SOLDIER-POV` series
- No spoken dialogue
- No narrator
- No generated subtitles inside the clip
- **No music**
- Human audio: breathing and nonverbal exertion only
- Environmental audio: battlefield ambience, weather, engines, vehicles, footsteps, equipment, distant gunfire, artillery, surf, rain, snow, debris and terrain-specific sound
- Combat: non-graphic historical depiction
- 1 scene = 1 primary action + 1 dominant camera movement
- Preserve physical continuity across scenes: uniform, mud, snow, dust, wetness, smoke, daylight, equipment and damage state
- Period-correct uniforms, weapons, vehicles and environments
- No modern objects, game UI or action-game framing
- No triumphalist or propaganda staging
- Disclosure: AI-generated historical reenactment with archival-style treatment. Not genuine archival footage.

## Embedded wartime cameraman lock

Every EP01–EP10 `STEP6.json` includes a `cameraPresenceLock` and `archivalLookLock`.

The camera must feel like a real person is physically filming inside the event:

- cameraman stays roughly 1–5 meters from nearby friendly troops
- camera follows behind or among soldiers; it does not teleport ahead of action
- the operator walks, crouches, crawls, climbs, wades, runs short distances and uses the same cover as the troops
- bodies, walls, vehicles, foliage, trenches and terrain are allowed to block part of the frame
- sudden danger may cause late reaction, imperfect framing, horizon errors, momentary soft focus or exposure breathing
- mud, sand, snow, rain, sea spray, dust or smoke may briefly touch the lens edge
- camera movement must carry physical weight and fatigue
- during shell bursts or incoming fire, the cameraman ducks or takes cover too
- the camera must never remain impossibly exposed while everyone else is hiding

Forbidden camera behavior:

- drone shots
- gimbal glide
- crane moves
- omniscient overhead views
- impossible camera placement ahead of incoming attacks
- passing through walls, soldiers or vehicles
- perfectly centered hero framing
- FPS / game weapon framing
- copied identifiable shots from a specific war movie

## Archival image standard

- black-and-white 35mm wartime newsreel aesthetic
- moderate readable film grain
- subtle gate weave and frame jitter
- fine dust and scratches
- light flicker
- soft period-lens focus
- imperfect exposure and occasional focus breathing
- restrained motion blur
- archival defects must never make the action unreadable

## Detailed STEP6 pattern

EP01 was authored first as the master detailed pattern. EP02–EP10 now follow the same camera-presence standard while retaining battlefield-specific movement and terrain behavior.

Each episode includes:

- episode-specific historical environment
- unique `mainStoryPrompt` and `storySummary`
- 15 individually directed scenes
- scene-level `actionDescription`
- scene-level `imageDescription`
- scene-level `videoPrompt`
- human-camera movement appropriate to the environment
- continuity-anchor character definition
- episode-specific atmosphere/location assets
- `cameraPresenceLock`
- `archivalLookLock`
- `metadata.json` beside every `STEP6.json`

## Episodes

| EP | Battlefield / Story | Camera-specific physical behavior | Status |
|---|---|---|---|
| EP01 | Poland 1939 — The War Begins | mud road, hedge crawl, village walls | STEP6_IMPORT_READY |
| EP02 | Dunkirk 1940 — Waiting on the Beach | soft sand, dunes, wind, wet pier, boat sway | STEP6_IMPORT_READY |
| EP03 | Eastern Front 1941 — Into the Vast Land | mud march, trucks, roadside ditch, open field | STEP6_IMPORT_READY |
| EP04 | Moscow 1941 — Winter Resistance | deep snow, icy footing, trench cover, breath haze | STEP6_IMPORT_READY |
| EP05 | El Alamein 1942 — War in the Desert | dust, heat shimmer, low gun pits, tank vibration | STEP6_IMPORT_READY |
| EP06 | Stalingrad 1942–43 — City of Fire | rubble, stairwells, wall breaches, dark interiors | STEP6_IMPORT_READY |
| EP07 | Guadalcanal 1942–43 — Jungle Frontline | foliage occlusion, streams, rain, muddy foxholes | STEP6_IMPORT_READY |
| EP08 | Normandy 1944 — Omaha Beach Assault | landing craft, surf, spray, obstacles, shingle | STEP6_IMPORT_READY |
| EP09 | Bastogne 1944 — Surrounded in Snow | frozen foxholes, fog, snow, cold-hand tremor | STEP6_IMPORT_READY |
| EP10 | Berlin 1945 — The Last Streets | rubble climbing, building interiors, square crossings | STEP6_IMPORT_READY |

Use `PROJECT_INDEX.json` as the series entry point for future import helpers or automation.
