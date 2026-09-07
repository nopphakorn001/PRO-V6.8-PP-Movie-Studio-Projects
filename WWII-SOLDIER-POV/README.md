# WWII SOLDIER POV

Immersive first-person historical reenactment shorts for PRO V6.8 P&P Movie Studio.

## Format
- 15 episodes total
- Set 01: EP01–EP05
- Set 02: EP06–EP15
- 15 scenes per episode
- 8 seconds per scene
- 120 seconds target runtime
- Vertical 9:16
- English project language for global distribution
- Fictional composite soldier POV inside real historical events
- No spoken dialogue
- No narrator
- No intelligible human speech
- Human audio is limited to breathing and nonverbal exertion
- Environmental audio and SFX only: wind, rain/snow/surf, footsteps, equipment, vehicles, aircraft, artillery, distant battlefield ambience and scene-appropriate effects
- Non-graphic historical combat depiction
- 1 scene = 1 shot + 1 primary action + 1 camera movement

## Immersion-first directing policy
The objective is not constant action. The objective is to make the viewer feel physically present inside the historical environment.

- Do not fire weapons in every scene.
- Do not place explosions or artillery impacts in every scene.
- Every episode must include quiet or recovery beats where little happens externally.
- Silence, breathing, waiting, looking, drinking water, checking gear, cold hands, mud, dust, sweat, sea spray, snow, wind, fabric, metal, footsteps and distant sounds are part of the story.
- Battlefield sound intensity must rise and fall naturally rather than remain continuously loud.
- Avoid action-movie pacing, heroic posing, game-like movement, constant camera shake and excessive visual effects.
- Camera motion should feel like a real tired human body: weight, hesitation, balance shifts, uneven breathing, natural head movement and brief stillness.
- Preserve physical continuity: wetness, dust, snow, mud, damaged equipment, fatigue and lighting should carry from scene to scene.

## Cinematic realism and shot-variety policy
- The weapon is a tool, not the center of every frame.
- Vary weapon presentation naturally: ready, lowered, slung, one-handed, resting, partial-frame or completely outside frame.
- Avoid repeated FPS-game composition with rifle centered at the bottom.
- Use different body states and viewing heights: standing, walking, crouching, kneeling, sitting, lying low, leaning, climbing, looking through windows/doors, looking down at hands/ground and stopping to listen.
- Do not repeat the same forward-facing eye-level angle in consecutive scenes unless continuity requires it.
- Every episode should include environmental exploration, at least one still/near-still tension scene, at least one short sudden movement beat after quiet, and at least one scale/reveal moment.
- Use near-miss debris sparingly and realistically.
- After intense sound, allow auditory recovery before battlefield volume returns.
- Human behavior matters more than spectacle.

Useful 15-scene pacing balance:
- 4 tension/contact/action
- 3 movement/repositioning
- 3 exploration/observation
- 3 quiet/recovery/human detail
- 2 reveal/climax/aftermath

## Faction-lock policy
Faction continuity is mandatory. One episode = one POV faction.

- POV soldier and nearby friendlies must belong to the same selected friendly force for the full episode.
- Uniforms, helmets, weapons, web gear, vehicles, fortifications and movement direction must match that force and setting.
- Enemy troops may appear only as a clearly opposing force, separated by distance, direction, cover, trench line, ridge, tree line, street frontage, river bank or attack axis.
- Do not place friendly and enemy troops side by side in the same local formation unless a documented story specifically requires it.
- When the scene does not need an enemy, prefer no enemy in frame rather than ambiguous mixed soldiers.
- Canonical per-episode faction definitions are stored in `FACTION_LOCKS.json`.

## Audio policy
The POV experience must be understandable without speech. All `script` fields remain empty and all `dialogues` arrays remain empty. Video prompts must not request spoken orders, shouted commands, narration, radio dialogue or intelligible words. Human presence is conveyed through breathing, movement and nonverbal exertion while the environment carries the story through sound.

## Sensory detail standard
Each `imageDescription` and `videoPrompt` should describe concrete physical details: surface texture, temperature, moisture, wind, smoke density, visibility, light quality, distance of sounds, equipment weight, fabric movement, breath, footsteps and immediate space around the soldier. Audio should use depth: foreground breathing/equipment, mid-ground movement/environment, background battlefield activity.

## Set 01 — EP01 to EP05
1. **D-Day — Omaha Beach, 6 June 1944** — U.S. Army infantry POV
2. **Stalingrad — Operation Uranus / encirclement phase, November 1942** — Soviet Red Army POV
3. **Second Battle of El Alamein, 23 October–4 November 1942** — British Eighth Army / Allied desert POV
4. **Bastogne — Battle of the Bulge, December 1944** — U.S. airborne / defending forces POV
5. **Iwo Jima — landings and early advance, February 1945** — U.S. Marines POV

## Set 02 — EP06 to EP15
6. **Dunkirk — Waiting for the Boats** — British Expeditionary Force POV, May–June 1940
7. **Guadalcanal — Jungle Night** — U.S. Marines POV, 1942
8. **Monte Cassino — Up the Mountain** — Polish II Corps infantry POV, May 1944
9. **Arnhem — Streets to the Bridge** — British 1st Airborne POV, September 1944
10. **Peleliu — Heat and Coral** — U.S. Marines POV, September 1944
11. **Hürtgen Forest — Lost Among the Pines** — U.S. Army infantry POV, late 1944
12. **Kohima — Ridge Under Siege** — British-Indian infantry POV, April 1944
13. **Sicily — From Surf to Olive Groves** — U.S. Army infantry POV, July 1943
14. **Berlin — The Last Streets** — Soviet Red Army infantry POV, April 1945
15. **Crossing the Rhine — Into Germany** — British infantry POV, Operation Plunder, March 1945

Each episode contains `STEP6.json` and `metadata.json` prepared for future automated publishing to YouTube, YouTube Shorts, TikTok and Facebook Reels.

## Publishing policy
Metadata is optimized for global discoverability but does not claim guaranteed virality or trend placement. Titles and descriptions clearly identify the videos as AI-generated cinematic historical reenactments rather than real archival footage.
