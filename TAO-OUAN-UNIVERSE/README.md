# ต้าวอ้วน Universe — PPMovieProject

Short-form episodic AI animation project prepared for the PPMovieProject / PRO V6.8 workflow.

## Production Standard

- Format: 9:16 vertical
- Target duration: 80–90 seconds
- Default structure: 15 clips × ~6 seconds (maximum 8 seconds per generated clip)
- Language: Thai dialogue
- Visual style: high-quality stylized 3D family animation, Pixar-inspired, cinematic, colorful, warm Thai countryside atmosphere
- Story rule: each episode has a clear beginning, middle, payoff, and end inside the episode
- Scene rule: 1 scene = 1 primary action + 1 camera movement
- Continuity: previous end frame → same character identity/outfit/props/location state → next action
- Voice lock: ต้าวอ้วน = Thai male child, น้องชาย = younger Thai male child, ยายอ่าง = elderly Thai female
- No overlapping dialogue; only current visible speaker moves lips
- Music always lower than dialogue
- Primary production file: `STEP6.json`
- Original planning source is preserved as `PPMOVIEPROJECT_PROMPT.md`

## Character Hard Lock

### ต้าวอ้วน
Chubby Thai boy, round face, soft cheeks, short messy black hair, big brown eyes, playful innocent expression. Cream/light T-shirt, navy shorts, brown sandals. Never redesign or change outfit inside the Songkran arc.

### น้องชาย
Younger and smaller Thai boy, round cheeks, short neat black hair, big curious eyes. Oversized pale-yellow T-shirt, olive shorts, sandals. Clearly younger voice than ต้าวอ้วน.

### ยายอ่าง
Slightly chubby elderly Thai grandmother, short gray hair, warm expressive face. Indigo floral blouse, dark maroon traditional casual wrap skirt, simple sandals.

### Dogs
บริ้ง and ไบร์ท are family dogs. They may appear at home, but never inside the temple.

## Songkran Arc — EP04 to EP10

| EP | Title | Production Status |
|---|---|---|
| EP04 | สงกรานต์ไปวัด | STEP6 import ready |
| EP05 | สงกรานต์หน้าบ้าน | STEP6 import ready |
| EP06 | ตามหาขันน้ำลายดอกไม้ | STEP6 import ready |
| EP07 | ภารกิจไอติมกลางสงกรานต์ | STEP6 import ready |
| EP08 | ขบวนแห่หมู่บ้าน | STEP6 import ready |
| EP09 | เจดีย์ทรายของสองพี่น้อง | STEP6 import ready |
| EP10 | รดน้ำยายอ่าง | STEP6 import ready |

Each episode folder contains both:

- `PPMOVIEPROJECT_PROMPT.md` — original production/story plan
- `STEP6.json` — structured STEP6 project state for import/testing in the PRO V6.8 workflow

## Generation Safety / Credit Policy

Import and review the project before generating. Do not run Generate All automatically. Validate character references, location continuity, dialogue speaker, voice identity, image prompt, and previous-scene reference before spending generation credits.

CTA Thai text is specified for editing/post-production rather than forcing long Thai lettering during video generation when text rendering is unreliable.
