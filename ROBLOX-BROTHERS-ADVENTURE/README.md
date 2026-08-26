# Roblox Brothers Adventure — 2 พี่น้องตะลุยโลกเกม

ซีรีส์ Roblox-style adventure สำหรับนำเข้า PRO V6.8 P&P Movie Studio ที่ STEP6 โดยใช้เด็กสองคนจากภาพอ้างอิงเป็นแรงบันดาลใจด้าน visual เท่านั้น และออกแบบเป็น stylized Roblox/game avatars ที่ไม่ระบุตัวตนจริง

## Production Standard

- 10 EP / 1 ด่านต่อ 1 EP / จบในตอน
- 15-18 scenes ต่อ EP; เวอร์ชันปัจจุบันใช้ 16 scenes
- 8 วินาทีต่อ scene; ประมาณ 128 วินาทีต่อ EP
- แนวตั้ง 9:16
- ไม่มีผู้บรรยาย
- dialogue + music + ambience + SFX + visual storytelling
- โทนสดใส ผจญภัย ครอบครัว ไม่ dark/horror
- Roblox-style เท่านั้น: ไม่มี official logo, copied UI หรือ branded map/asset

## Character Identity Lock

ดู `CHARACTER_SHEETS.json`

- **C-SHARP / ซีชาร์ป** — พี่ชาย ตัวสูงกว่า เด็กผู้ชายเอเชีย ผิวขาว/สว่าง ผมสีน้ำตาลเข้ม ชุด cream + light green
- **ARI / อาริ** — น้องชาย ตัวเล็กกว่า เด็กผู้ชายเอเชีย ผิวขาว/สว่าง ผมสีน้ำตาลเข้ม ชุด white + blue
- ใบหน้าต้องเป็น face design เดิมตลอดทั้ง scene และข้าม EP: ห้ามเปลี่ยน eye shape, eyebrows, nose, cheek fullness, face width, age, skin tone หรือ hair silhouette
- C-SHARP ใช้หน้าทรง rounded-square; ARI ใช้หน้ากลมกว่าและตาใหญ่กว่าเล็กน้อย
- ห้ามสลับความสูง ชุด ทรงผม หรือ props

## Critical Prompt Rule: Use Roles, Not Literal Names

เพื่อกัน AI สร้างชื่อบนหัว:

- ใน `imageDescription` และ `videoPrompt` ให้เรียกตัวละครว่า **older brother** และ **younger brother**
- หลีกเลี่ยงการใส่ literal `C-SHARP` หรือ `ARI` ลงใน visual prompt
- `C-SHARP` / `ARI` ใช้ได้ใน metadata, IDs และ `sceneCharacters` เท่านั้น
- badge, charm, checkpoint และ props ต้องไม่มีตัวอักษรหรือชื่อคน

## No Nameplate / No Overhead UI — STRICT

ห้ามสร้างทุกกรณี:

- character name / username / display name
- floating label / overhead tag
- chat bubble
- health bar / score
- subtitle / caption
- readable UI ใกล้ตัวละคร
- ชื่อ `C-SHARP`, `ARI`, `ซีชาร์ป`, `อาริ` เป็นข้อความบนหัวหรือบนเสื้อ

ถ้า scene ไม่จำเป็นต้องมีข้อความ ให้ **ไม่มี readable text ใน frame เลย**

## Dialogue / Voice QA

- 1 scene = 1 speaker
- ตัวละครอีกคนต้องปากปิดและ reaction อย่างเดียว
- ประโยคสั้น พูดจบใน 8 วินาที
- system/display name คง `C-SHARP` และ `ARI`
- spoken name ของพี่ = `ซีชาร์ป`
- spoken name ของน้อง = `อาริ`
- **ห้ามส่งตัวอักษร `ARI` เข้า TTS เป็น spoken text** เพราะอาจอ่านผิด
- `อาริ` อ่าน `Ah-ree` สองพยางค์

## Previous Scene Reference / Smooth Continuity

ตั้งแต่ Scene 2 เป็นต้นไป ถ้า location/time/action ต่อกัน ให้ใช้ **ภาพ generated ของ scene ก่อนหน้าเป็น primary visual reference** ก่อนสร้าง scene ถัดไป

ต้องรักษา:

- exact face design
- fair/light skin tone
- hair silhouette
- outfits / props
- C-SHARP taller than ARI
- screen direction
- ตำแหน่งปลาย scene ก่อนหน้า
- obstacle state
- lighting / environment state

Character identity ห้าม reset ระหว่าง scene

## Camera / Motion QA

- หลีกเลี่ยง camera angle ซ้ำหลาย scene ต่อกัน
- สลับ wide reveal, medium two-shot, low side follow, over-shoulder, rear follow, three-quarter view, gentle arc และ static reaction
- 1 scene = 1 action หลัก + 1 camera movement หลัก
- ห้าม teleport / duplicate ตัวละคร
- jump ต้องเห็นต้นทางและ landing ชัด
- วิ่งหรือกระโดดไม่ควรพูดประโยคยาว

## EP01 Final-Render QA Corrections

EP01 ถูก refactor รอบล่าสุดเพื่อแก้ root cause เพิ่มเติม:

- ล็อก face geometry ของเด็กทั้งสองอย่างละเอียด
- ย้าย literal character names ออกจาก visual prompts และใช้ older brother / younger brother แทน
- บังคับ no readable text / no nameplate ทุก scene
- `ARI` เป็น metadata เท่านั้น; spoken dialogue ใช้ `อาริ` เท่านั้น
- 1 speaker ต่อ 1 scene
- previous scene image เป็น continuity reference ตั้งแต่ Scene 2
- props/badges ไม่มีตัวหนังสือ
- story progression และ camera angle ถูกจัดใหม่ให้ smooth ขึ้น

## Episodes

1. **EP01 — ประตูสู่ Beginner Obby** — 16 scenes — QA REVISED V2
2. **EP02 — รถรางเหมืองสุดป่วน** — 16 scenes
3. **EP03 — เกาะลอยฟ้า** — 16 scenes
4. **EP04 — เมืองน้ำท่วม** — 16 scenes
5. **EP05 — ปราสาทปริศนา** — 16 scenes
6. **EP06 — แข่งรถสุดป่วน** — 16 scenes
7. **EP07 — สวนสัตว์หลุดกรง** — 16 scenes
8. **EP08 — โรงงานหุ่นยนต์วุ่นวาย** — 16 scenes
9. **EP09 — โจรสลัดแห่งเกาะสมบัติ** — 16 scenes
10. **EP10 — Mega Obby Final** — 16 scenes

## Import

เปิดโฟลเดอร์ EP แล้วใช้ `STEP6.json`

`PROJECT_INDEX.json` รวม path ทุก EP และ `metadata.json` สำหรับระบบ auto-post ในอนาคต
