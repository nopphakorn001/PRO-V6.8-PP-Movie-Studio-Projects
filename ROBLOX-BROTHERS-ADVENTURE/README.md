# Roblox Brothers Adventure — 2 พี่น้องตะลุยโลกเกม

ซีรีส์ Roblox-style adventure สำหรับ PRO V6.8 P&P Movie Studio ปรับเป็น **V3 Character + Story Continuity** แล้ว เพื่อแก้ปัญหา 2 จุดหลัก: ตัวละครเปลี่ยนหน้า/ชุดระหว่าง scene และเนื้อหา/ตำแหน่ง/อุปสรรค reset ระหว่าง scene

## V3 — ใช้ไฟล์นี้เป็นหลัก

- `CHARACTER_SHEETS.json` — Canonical identity source of truth
- `CONTINUITY_LOCK_V3.json` — Hard-lock rules สำหรับตัวละครและ story state
- ในแต่ละ EP ให้ใช้ `STEP6_V3.json`
- `STEP6.json` เดิมเก็บไว้เป็น legacy เท่านั้น
- `PROJECT_INDEX.json` ชี้ไป `STEP6_V3.json` ครบ EP01–EP10 แล้ว

## Production Standard

- 10 EP / 1 ด่านต่อ 1 EP / จบในตอน
- 16 scenes ต่อ EP
- 8 วินาทีต่อ scene; ประมาณ 128 วินาที
- 9:16
- ไม่มี narrator
- dialogue + music + ambience + SFX
- 1 scene = 1 main action + 1 camera move + 1 speaker สูงสุด
- โทนสดใส ผจญภัย ครอบครัว ไม่ dark/horror
- Roblox-inspired stylized game world เท่านั้น: ไม่มี official logo, copied UI หรือ branded map/asset

## Character Hard Lock — V3

### Older Brother / C-SHARP / ซีชาร์ป
- ตัวสูงกว่าเสมอ
- East Asian child, fair/light skin
- rounded-square face
- dark-brown almond-shaped eyes
- short dark-brown neat side-swept hair
- cream hoodie + light-green adventure vest + tan shorts + white sneakers
- green wristband + square backpack

### Younger Brother / ARI / อาริ
- ตัวเล็กกว่าเสมอ
- East Asian child, fair/light skin
- rounder face
- slightly larger dark-brown almond-shaped eyes
- short dark-brown fluffy-front hair
- white shirt + bright-blue hoodie + navy shorts + blue-white sneakers
- blue utility pouch + compass charm

### ห้ามเปลี่ยนเด็ดขาด

- face geometry
- skin tone
- age
- relative height
- hair silhouette
- outfit/colors
- personal props
- ห้ามสลับหน้า/ชุด/กระเป๋า/ความสูงกัน
- ห้าม duplicate ตัวละคร
- ห้ามสร้างพี่น้องคนที่ 3

## Mandatory Reference Order

### Scene 1
ใช้ `CHARACTER_SHEETS.json` เป็น primary identity reference เพื่อสร้าง canonical appearance

### Scene 2 เป็นต้นไป — บังคับทุก Scene
ใช้พร้อมกัน 2 reference:

1. **Character Sheets** → ล็อก identity / face / outfit / height / hair
2. **Previous generated scene image** → ล็อก pose handoff / position / screen direction / props / obstacle state / lighting / location geometry

ไม่ใช่ “ใช้เมื่อสะดวก” อีกต่อไป — **previous scene reference เป็น mandatory ทุก scene ตั้งแต่ Scene 2**

## Story Continuity Contract

ทุก Scene ใน `STEP6_V3.json` มี:

- `continuityStartState`
- `mainAction`
- `continuityEndFrame`

กฎหลัก:

> `Scene N continuityEndFrame` ต้องตรงกับ `Scene N+1 continuityStartState`

ต้องต่อกันในเรื่องต่อไปนี้:

- ตำแหน่งพี่/น้อง
- ใครอยู่ซ้าย/ขวา
- direction การเดินทาง
- prop อยู่กับใคร
- key/token/crystal/coin ถูกเก็บแล้วหรือยัง
- button/lever ถูกกดแล้วหรือยัง
- bridge/door/gate ซ่อม/เปิดแล้วหรือยัง
- vehicle/cart/raft อยู่ตรงไหน
- water level
- animal/robot state
- lighting/location state

## No Reset / No Teleport

- ด่านที่ผ่านแล้วห้ามกลับเป็นค่าเริ่มต้น
- ประตูเปิดแล้วต้องเปิดค้างจนมีเหตุผลให้ปิด
- ปุ่มกดแล้วต้องคงสถานะ
- bridge ซ่อมแล้วห้ามกลับมาพัง
- key/token ที่เก็บแล้วห้ามกลับไปอยู่ pedestal
- สัตว์ช่วยแล้วห้ามกลับมา loose อีก
- รถ/รถราง/แพต้องคันเดิม
- ห้ามย้าย location แบบทันที ต้องมี portal / corridor / doorway / bridge / vehicle / stairs / path transition

## Screen Direction

ถ้า previous scene ไม่ได้บังคับอย่างอื่น:

- older brother เริ่ม screen-left
- younger brother เริ่ม screen-right
- รักษาทิศการเคลื่อนที่ต่อเนื่อง
- ถ้าจะสลับซ้าย/ขวา ต้องเห็น action ที่เดินไขว้/หมุนตัวจริง

## Dialogue / Voice QA

- 1 speaker สูงสุดต่อ scene
- non-speaker ปากปิดและ reaction เท่านั้น
- C-SHARP เป็น metadata; spoken name = `ซีชาร์ป`
- ARI เป็น metadata; spoken name = `อาริ` (Ah-ree)
- ห้ามส่ง `A-R-I` เข้า TTS

## No Nameplate / No UI — STRICT

ห้าม:

- character name / username / display name
- floating labels / overhead tags
- chat bubble
- health bar / score
- subtitle / caption ที่ไม่ได้ตั้งใจ
- readable badges / shirt text
- official Roblox UI/logo

ใน visual prompt ให้เรียกแค่ `older brother` และ `younger brother`

## V3 Episodes

1. EP01 — ประตูสู่ Beginner Obby — `STEP6_V3.json`
2. EP02 — รถรางเหมืองสุดป่วน — `STEP6_V3.json`
3. EP03 — เกาะลอยฟ้า — `STEP6_V3.json`
4. EP04 — เมืองน้ำท่วม — `STEP6_V3.json`
5. EP05 — ปราสาทปริศนา — `STEP6_V3.json`
6. EP06 — แข่งรถสุดป่วน — `STEP6_V3.json`
7. EP07 — สวนสัตว์หลุดกรง — `STEP6_V3.json`
8. EP08 — โรงงานหุ่นยนต์วุ่นวาย — `STEP6_V3.json`
9. EP09 — โจรสลัดแห่งเกาะสมบัติ — `STEP6_V3.json`
10. EP10 — Mega Obby Final — `STEP6_V3.json`

## Generation Workflow

1. Import `STEP6_V3.json`
2. Generate/attach canonical Character Sheets ก่อน
3. Generate Scene 1
4. ตรวจหน้า/ชุด/ความสูง
5. Scene 2 เป็นต้นไป attach **Character Sheet + Previous Scene Image**
6. ก่อน Generate ทุก Scene ตรวจ `continuityStartState`
7. หลัง Generate ตรวจว่าภาพสุดท้ายตรง `continuityEndFrame`
8. ถ้า identity หรือ state ผิด ให้ regenerate scene นั้นทันที — ห้ามปล่อยผิดแล้วสร้าง scene ถัดไป

## Stop Conditions

หยุด generation ทันทีถ้า:

- หน้าพี่หรือน้องเปลี่ยน
- ความสูงสลับกัน
- ชุด/สี/props สลับ
- ตัวละคร duplicate
- obstacle reset
- prop หาย/โผล่เอง
- location teleport
- speaker/lip-sync สลับ

สถานะปัจจุบัน: **QA_REVISED_V3_CHARACTER_STORY_CONTINUITY**
