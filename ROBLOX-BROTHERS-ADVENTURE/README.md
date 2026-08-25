# Roblox Brothers Adventure — 2 พี่น้องตะลุยโลกเกม

ซีรีส์ Roblox-style adventure สำหรับนำเข้า PRO V6.8 P&P Movie Studio ที่ STEP6 โดยใช้เด็กสองคนจากภาพอ้างอิงเป็นแรงบันดาลใจด้าน visual เท่านั้น และออกแบบเป็น stylized Roblox/game avatars ที่ไม่ระบุตัวตนจริง

## Production Standard

- 10 EP / 1 ด่านต่อ 1 EP / จบในตอน
- 15-18 scenes ต่อ EP; เวอร์ชันนี้ใช้ 16 scenes ทุก EP
- 8 วินาทีต่อ scene; ประมาณ 128 วินาทีต่อ EP
- แนวตั้ง 9:16 เหมาะกับ short-form adventure
- มีบทสนทนาสั้น ๆ เป็นธรรมชาติในทุก scene โดยเรียกชื่อกันว่า C-SHARP และ ARI
- ไม่มีผู้บรรยาย
- เน้น dialogue + music + ambience + SFX + visual storytelling
- โทนสดใส ผจญภัย ครอบครัว ไม่ dark/horror
- Roblox-style เท่านั้น: ไม่มี official logo, ไม่มี copied UI, ไม่มี copied branded map หรือ asset
- ทุก scene มี actionDescription, mainAction, imageDescription, videoPrompt, dialogues และหนึ่ง action หลัก

## Character Continuity

ดู `CHARACTER_SHEETS.json`

- **C-SHARP / ซีชาร์ป** — พี่ชาย ตัวสูงกว่า ชุด cream + light green, ใจกล้า วางแผน และช่วยปกป้องน้อง
- **ARI / อารี** — น้องชาย ตัวเล็กกว่า ชุด white + blue, ช่างสังเกต คล่องตัว และเก่งแก้ปริศนา

ทั้งสองเป็น stylized game avatars อ้างอิงภาพผู้ใช้อัปโหลดในระดับรูปลักษณ์รวมเท่านั้น ไม่ใช่ภาพเหมือนจริงและไม่ระบุตัวตนจริง ต้องคง height relationship, outfit, hair, props และ blocky toy-like style ข้ามทั้ง 10 EP

## Episodes

1. **EP01 — ประตูสู่ Beginner Obby** — Beginner Obby / Portal — 16 scenes
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
