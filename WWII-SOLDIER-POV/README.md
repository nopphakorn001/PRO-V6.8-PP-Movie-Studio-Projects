# WWII SOLDIER POV

Immersive first-person historical reenactment shorts for PRO V6.8 P&P Movie Studio.

## Format
- 5 episodes in Set 01
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

- Do **not** fire weapons in every scene.
- Do **not** place explosions or artillery impacts in every scene.
- Every episode must include quiet or recovery beats where little happens externally.
- Silence, breathing, waiting, looking, drinking water, checking gear, cold hands, mud, dust, sweat, sea spray, snow, wind, fabric, metal, footsteps and distant sounds are part of the story.
- Let some scenes breathe. A scene may contain only a slow look, a hand movement, a pause behind cover, a distant horizon or environmental sound.
- Battlefield sound intensity must rise and fall naturally rather than remain continuously loud.
- Close gunfire should appear only when the story requires it. Distant combat can disappear almost completely during rest or observation scenes.
- Avoid action-movie pacing, heroic posing, game-like movement, constant camera shake and excessive visual effects.
- Camera motion should feel like a real tired human body: weight, hesitation, balance shifts, uneven breathing, natural head movement and brief stillness.
- Preserve physical continuity: wetness, dust, snow, mud, damaged equipment, fatigue and lighting should carry from scene to scene.

## Cinematic realism and shot-variety policy
The visual feeling should be cinematic and exciting like a grounded war film, but it must still feel like a real person physically present in a real historical place. Use cinematic language, tension, timing and reveal without copying an identifiable shot from a specific movie.

- The weapon is a tool, **not the center of every frame**. The POV soldier does not need to hold the weapon visibly in every scene.
- Across an episode, vary weapon presentation naturally: carried ready when danger requires it, lowered, slung, held one-handed, resting against cover, partly visible at the edge of frame, or completely outside the frame during observation, rest, exploration, map reading, drinking, climbing, digging or equipment handling.
- Avoid the repeated FPS-game composition of rifle centered at the bottom of every image.
- Use different body states and viewing heights: standing, walking slowly, crouching, kneeling, sitting, lying low, leaning from cover, climbing, looking through a doorway, looking from a trench, looking down at hands or ground, looking upward, looking over the shoulder and stopping to listen.
- Do not repeat the same forward-facing eye-level angle in consecutive scenes unless continuity requires it.
- Every episode should include environmental exploration: move through or inspect historically plausible spaces such as a ruined room, trench, foxhole, beach obstacle, farm lane, desert track, bunker exterior, crater, supply point or battlefield aftermath area.
- Include scale/reveal moments where the camera discovers a larger environment after passing through a confined space or cover.
- Include at least one deliberate still or near-still scene where tension comes from waiting, distant sound or something slowly becoming visible.
- Include at least one sudden movement beat after a quieter scene: a short dash, duck behind cover, quick turn toward a sound, or rapid move across exposed ground. The contrast creates excitement.
- Use near-miss tension sparingly and realistically: dirt, brick dust, snow, sand, water or debris may react to distant impacts, but do not make every scene a close explosion.
- After intense sound, allow realistic auditory recovery: muffled ambience, ringing-like dullness, breath and environmental sound before full battlefield volume returns.
- Human behavior matters more than spectacle: fatigue, hesitation, checking surroundings, gripping cold metal, wiping moisture, adjusting straps, drinking, catching breath and waiting should appear throughout the episode.
- The camera should behave like a human body, while framing and timing remain cinematic: deliberate reveal, foreground depth, layered background action, natural occlusion and meaningful pauses.

A useful pacing balance for a 15-scene episode is approximately:
- 4 scenes tension/contact/action
- 3 scenes movement/repositioning
- 3 scenes exploration/observation
- 3 scenes quiet/recovery/human detail
- 2 scenes reveal/climax/aftermath

This is a directing balance, not a rigid formula. Historical events and location logic take priority.

## Faction-lock policy
Faction continuity is mandatory. **One episode = one POV faction.** The immediate friendly environment must never become a random mixture of Allied and Axis troops.

- The POV soldier and all nearby friendly soldiers must belong to the same selected friendly faction for the full episode.
- Uniforms, helmets, weapons, web gear, vehicles, fortifications and movement direction around the POV must match that friendly force and historical setting.
- Enemy troops may appear, but they must read clearly as the opposing force through distance, direction, cover, trench line, bunker, ridge, tree line, street frontage or attack axis.
- Do not place friendly and enemy troops side by side in the same local formation unless the documented historical story explicitly requires surrender, prisoners or a mixed situation. Set 01 does not require this.
- Do not visually imply that friendly troops are firing from inside the enemy formation or that enemy troops casually occupy the friendly position.
- If an enemy charge or attack enters the frame, the opposing uniform/equipment and approach direction must make the hostile side immediately understandable.
- When the scene does not require a visible enemy, prefer no enemy in frame rather than ambiguous mixed soldiers.
- Quiet and recovery scenes must preserve faction continuity exactly the same as combat scenes.
- Historical plausibility and faction readability take priority over adding extra soldiers, weapons or spectacle.

Canonical per-episode faction definitions are stored in `FACTION_LOCKS.json` and should be applied to all future prompt revisions, generation passes and automation.

## Set 01 faction locks
1. **D-Day — Omaha Beach:** Allied POV / U.S. Army infantry vs German defenders.
2. **Stalingrad:** Allied POV / Soviet Red Army vs German Sixth Army / Axis forces.
3. **Second Battle of El Alamein:** Allied POV / British Eighth Army and historically appropriate Allied desert forces vs German/Italian Axis forces.
4. **Bastogne:** Allied POV / U.S. airborne and U.S. defending forces vs German attacking forces.
5. **Iwo Jima:** Allied POV / U.S. Marines vs Japanese defenders.

## Sensory detail standard
Each `imageDescription` and `videoPrompt` should describe concrete physical details that help the viewer feel present: surface texture, temperature, moisture, wind direction, smoke density, visibility, light quality, distance of sounds, equipment weight, fabric movement, breath, footsteps and the immediate space around the soldier.

Audio should use depth: foreground breathing/equipment, mid-ground footsteps/vehicles/environment, background battlefield activity. Quiet scenes should intentionally leave space between sounds.

## Set 01
1. D-Day — Omaha Beach, 6 June 1944
2. Stalingrad — Operation Uranus / encirclement phase, November 1942
3. Second Battle of El Alamein, 23 October–4 November 1942
4. Bastogne — Battle of the Bulge, December 1944
5. Iwo Jima — landings and early advance, February 1945

Each episode contains `STEP6.json` and an English `metadata.json` prepared for future automated publishing to YouTube, YouTube Shorts, TikTok and Facebook Reels.

## Audio policy
The POV experience must be understandable without speech. All `script` fields remain empty and all `dialogues` arrays remain empty. Video prompts must not request spoken orders, shouted commands, narration, radio dialogue or intelligible words. Human presence is conveyed through breathing, movement and nonverbal exertion while the environment carries the story through sound.

## Publishing policy
Metadata is optimized for global discoverability but does not claim guaranteed virality or trend placement. Titles and descriptions clearly identify the videos as cinematic historical reenactments rather than real archival footage.
