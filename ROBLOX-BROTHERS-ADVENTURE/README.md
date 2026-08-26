# Roblox Brothers Adventure — 2 พี่น้องตะลุยโลกเกม

ซีรีส์ Roblox-style adventure สำหรับนำเข้า PRO V6.8 P&P Movie Studio ที่ STEP6 โดยใช้เด็กสองคนจากภาพอ้างอิงเป็นแรงบันดาลใจด้าน visual เท่านั้น และออกแบบเป็น stylized Roblox/game avatars ที่ไม่ระบุตัวตนจริง

## Production Standard

- 10 EP / 1 ด่านต่อ 1 EP / จบในตอน
- 15-18 scenes ต่อ EP; เวอร์ชันปัจจุบันใช้ 16 scenes
- 8 วินาทีต่อ scene; ประมาณ 128 วินาทีต่อ EP
- แนวตั้ง 9:16 เหมาะกับ short-form adventure
- ไม่มีผู้บรรยาย
- เน้น dialogue + music + ambience + SFX + visual storytelling
- โทนสดใส ผจญภัย ครอบครัว ไม่ dark/horror
- Roblox-style เท่านั้น: ไม่มี official logo, ไม่มี copied UI, ไม่มี copied branded map หรือ asset
- ทุก scene มี actionDescription, mainAction, imageDescription, videoPrompt, dialogues และหนึ่ง action หลัก

## Character Continuity

ดู `CHARACTER_SHEETS.json`

- **C-SHARP / ซีชาร์ป** — พี่ชาย ตัวสูงกว่า เด็กผู้ชายเอเชีย ผิวขาว/สว่าง ผมสีน้ำตาลเข้ม ชุด cream + light green
- **ARI / อาริ** — น้องชาย ตัวเล็กกว่า เด็กผู้ชายเอเชีย ผิวขาว/สว่าง ผมสีน้ำตาลเข้ม ชุด white + blue
- ต้องคงใบหน้า สีผิว ทรงผม ชุด props และสัดส่วนเดิมตลอดทั้งตอนและทุก EP
- ห้ามเปลี่ยนให้ตัวละครดูเป็นผู้ใหญ่ ห้ามสลับความสูงของพี่กับน้อง

## No Nameplate / No Overhead UI

ห้ามสร้างชื่อบนหัวตัวละครทุกกรณี ไม่ว่าจะเป็น `C-SHARP`, `ARI`, username, display name, label, chat bubble, health bar, score, badge หรือข้อความ UI ลอยเหนือหัว

ใน generated image/video ห้ามมี subtitle, caption หรือ text overlay โดยไม่จำเป็น และห้ามใช้ชื่อ C-SHARP/ARI เป็นข้อความที่มองเห็นในฉาก เว้นแต่มีเหตุผลของเนื้อเรื่องโดยตรง

## Dialogue / Voice QA

เพื่อป้องกันเสียงสลับคน, lip-sync ผิดตัว หรือบทพูดไม่ทัน 8 วินาที:

- ใช้ **หนึ่งคนพูดต่อหนึ่ง scene** เป็นมาตรฐาน
- สลับ scene พูดระหว่าง C-SHARP และ ARI เมื่อเหมาะสม
- ตัวละครที่ไม่ได้พูดต้องเงียบ ปากปิด และแสดง reaction ตามธรรมชาติ
- ประโยคต้องสั้นและพูดจบสบาย ๆ ภายใน 8 วินาที
- ชื่อระบบ/metadata คงเป็น `C-SHARP` และ `ARI`
- เวลาพูดภาษาไทยให้ใช้ `ซีชาร์ป` และ `อาริ`
- `ARI` pronunciation = `อาริ` / `Ah-ree`

EP01 ถูก refactor แล้วให้ C-SHARP และ ARI สลับกันพูดทีละ scene

## Previous Scene Reference / Smooth Continuity

ตั้งแต่ Scene 2 เป็นต้นไป ถ้า scene ต่อเนื่องด้าน location/time/action ให้ใช้ **ภาพ generated ของ scene ก่อนหน้าเป็น primary reference ใน PRO V6.8** ก่อนสร้าง scene ถัดไป

สิ่งที่ต้องรักษาจาก previous scene:

- ใบหน้าและสีผิว
- ทรงผมและชุด
- props
- ความสูง C-SHARP > ARI
- ตำแหน่งตัวละคร ณ ตอนจบ scene ก่อนหน้า
- screen direction / ทิศทางการเดิน
- สถานะของ obstacle เช่น ประตูเปิดแล้วต้องยังเปิด, checkpoint ที่ติดแล้วไม่ควร reset
- lighting และ environment state

ถ้ามีการเปลี่ยน location/time อย่างชัดเจน ให้ใช้ Character Sheet เป็น identity reference หลัก และใช้ previous scene เฉพาะส่วนที่จำเป็นต่อ transition

## Camera / Motion QA

- หลีกเลี่ยงมุมซ้ำและ camera move ซ้ำทุก scene
- สลับ wide reveal, medium two-shot, low side follow, over-shoulder, three-quarter view, gentle arc และ static reaction shot
- 1 scene = 1 action หลัก + 1 camera movement หลัก
- ห้าม teleport ตัวละครระหว่างแท่น
- ห้าม duplicate ตัวละครหรือสร้างพี่/น้องเกินหนึ่งคน
- การกระโดดต้องมีต้นทาง → mid motion → landing ที่เข้าใจได้
- ตัวละครที่กำลังวิ่ง/กระโดดไม่ควรพูดประโยคยาว; ให้พูดก่อนเริ่มหรือหลังลงถึงพื้น

## EP01 Final-Render QA Corrections

EP01 `Beginner Obby Portal` ได้แก้ STEP6 จากปัญหาเชิงโครงสร้างที่มีโอกาสทำให้ final render ผิดปกติ:

- เดิมสองคนพูดใน scene เดียวเกือบทุก scene → เปลี่ยนเป็นหนึ่งคนพูดต่อ scene
- เดิมบทพูดบางประโยคไม่สัมพันธ์กับ action เช่นเตือน “จุดเด้ง” ในฉาก High-five → เขียนบทใหม่ให้ตรง action
- เดิม camera pattern วนซ้ำ push-in / side-track / crane / follow → กระจายมุมใหม่
- เดิมไม่ได้ห้าม nameplate/UI อย่างชัดเจน → เพิ่ม negative instruction ทุก scene
- เดิมไม่ได้กำหนดรูปลักษณ์เอเชียและสีผิวชัด → ล็อก East Asian + fair/light skin ทั้งสองคน
- เดิม scene continuity พึ่ง prompt แต่ไม่กำชับ previous image → เพิ่มคำสั่งให้ใช้ previous generated scene reference ใน scene ต่อเนื่อง
- ปรับ story progression ใหม่ให้ Portal → start → obstacles → checkpoint → final portal → finish → return Lobby ต่อเนื่องกว่าเดิม

## Episodes

1. **EP01 — ประตูสู่ Beginner Obby** — Beginner Obby / Portal — 16 scenes — QA REVISED
2. **EP02 — รถรางเหมืองสุดป่วน** — Minecart Adventure — 16 scenes
3. **EP03 — เกาะลอยฟ้า** — Sky Islands — 16 scenes
4. **EP04 — เมืองน้ำท่วม** — Flood Escape — 16 scenes
5. **EP05 — ปราสาทปริศนา** — Puzzle Castle — 16 scenes
6. **EP06 — แข่งรถสุดป่วน** — Racing World — 16 scenes
7. **EP07 — สวนสัตว์หลุดกรง** — Animal Rescue — 16 scenes
8. **EP08 — โรงงานหุ่นยนต์วุ่นวาย** — Robot Factory — 16 scenes
9. **EP09 — โจรสลัดแห่งเกาะสมบัติ** — Pirate Island — 16 scenes
10. **EP10 — Mega Obby Final** — Mega Obby Final — 16 scenes

## Import

เปิดโฟลเดอร์ของ EP ที่ต้องการแล้วใช้ไฟล์ `STEP6.json`

`PROJECT_INDEX.json` รวม path ของทุก EP และ `metadata.json` ของแต่ละตอนสำหรับระบบ auto-post ในอนาคต
