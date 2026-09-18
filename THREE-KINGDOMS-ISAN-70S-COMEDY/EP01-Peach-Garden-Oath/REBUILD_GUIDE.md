# EP01 — ใช้ภาพที่ผู้ใช้อนุมัติจาก JSON export จริง

## สถานะที่ต้องแยกให้ชัด

- ตัวประกอบ EP01, บทใหม่ 6 ฉาก, กฎสถานที่เดียว และตัวตรวจ Base64/continuity อยู่ใน Git แล้ว
- commit นี้ **ยังไม่ใช่การอัปโหลดภาพจริงจากไฟล์แนบ** และไม่อ้างว่าได้ประกอบ Base64 ต้นฉบับครบแล้ว
- ตัวประมวลผลไฟล์แนบในเซสชันที่สร้างงานนี้คืน InvalidArgumentError จึงยังแยก/ดูภาพจริงจาก JSON แนบไม่ได้
- ไม่เปลี่ยนหน้าตัวละคร ไม่ใช้โปสเตอร์ ไม่สร้างภาพใหม่ และไม่แทนที่ STEP6.json เดิมด้วยไฟล์ที่แกล้งว่ามีภาพ
- `STEP6.json` เดิมบน Git ยังเป็นเวอร์ชัน text-only จนกว่าจะนำ Master Pack ที่ประกอบจาก export จริงมาแทน

## ใช้งานครั้งเดียวกับไฟล์ที่มีอยู่แล้ว

เปิด `../tools/BUILD_EP01_FROM_EXPORT.html` ด้วย Chrome/Edge จาก local repo แล้วเลือก JSON export เดิม:
`สามก๊กบ้านเฮา EP01 — สาบานสวนท้อแบบคนบ้านๆ.json`

ตัวช่วยอ่านข้อมูลจากเครื่องเท่านั้น ไม่มี upload, fetch, AI generation หรือบริการภายนอก

1. ยืนยันภาพ เล่าปี่ / กวนอู / เตียวหุย ที่ตรงกับตัวอย่างที่อนุมัติ ถ้า STEP5 มีภาพเดิม ใช้ไบต์เดิมตรง ๆ ถ้ามีแต่ภาพฉาก ลากกรอบให้เหลือเฉพาะคนนั้นก่อนยืนยัน ไม่ครอปให้เองโดยเดาว่าเป็นใคร
2. เลือกภาพสถานที่เดิมที่มีโต๊ะใต้ต้นท้อเป็น reference เดียวของทั้งตอน
3. กดประกอบไฟล์ รับ `EP01_STEP6_WITH_MASTERS.json` แล้ว Import ไฟล์นี้เพียงไฟล์เดียว ไม่ต้อง Import STEP5 และ STEP6 สองรอบ

หลัง import: STEP5 ต้องมีภาพทั้งสามคน; STEP6 ต้องมี 6 ฉาก ฉากละ 6 วินาที และสถานที่เดียว ต้องตรวจ/เลือก visual references ใน tool จริงก่อน generation ถ้าภาพไม่ขึ้น หยุดก่อนใช้เครดิตและเก็บ export หลัง import เพื่อเทียบฟิลด์ ไม่แก้ schema ด้วยการเดา wrapper ใหม่

## โครงที่ใช้

โครง native เดิมคือ `projectId`, `settings`, `movie.characters`, `movie.atmosphereAssets`, `movie.scenes`, `currentStep` ไม่ใช่ `step1` ถึง `step6` แยก root

คำอธิบายภาพและรูปแบบโทนถูกคัดลอกจากไฟล์ต้นฉบับโดยตรง ไม่มีการเปลี่ยน visualStyle, customVisualStyle หรือ customCharacterStyle บทเป็นไทยย้อนยุคไม่ทางการ เรียกพี่เล่า / พี่กวน / เจ้าเตียว ใช้ speaker id เดิม

การฝังรูป: คงข้อมูล native character record จาก export, ฝัง data URI ใน imageBase64/imageUrl, และเก็บ native image field ถ้ามี ค่าภาพ/สถานะของ third-party importer ต้องทดสอบจริง; ไม่อ้างว่าการเพิ่ม identityLocked เป็น enforcement หรือรับประกันว่าโมเดลจะไม่เปลี่ยนหน้า

## ตอนใหม่ 36 วินาที: สาบานได้ แต่ใครจ่ายสุรา

ทุกฉากอยู่ที่โต๊ะเดียว ทั้งสามนั่งอยู่แล้ว ไม่ใช้ตลาดแยกต่างหากหรือทางออกใหม่

| ฉาก | ผู้พูด | บท |
|---|---|---|
| 1 | เล่าปี่ | เฮ้อ...รองเท้าข้าขายมิได้สักคู่ |
| 2 | เตียวหุย | พี่เล่า! หน้าหมองอยู่ใย มาซดสุราก่อน! |
| 3 | กวนอู | เจ้าเตียว...ข้าได้ยินคำว่าสุราแต่ไกล |
| 4 | เล่าปี่ | พี่กวน เจ้าเตียว...จากนี้อย่าทิ้งกันยามยาก |
| 5 | เตียวหุย | ร่วมเป็นร่วมตาย! แต่ค่าสุรา...หารสามนะ! |
| 6 | กวนอู | พี่เล่า...ข้ามีแต่ใจ เอาจ่ายแทนได้หรือไม่? |

จบด้วยทั้งสามมองถุงเงินว่างที่โต๊ะเดิม ไม่มี narrator ไม่มีการเพิ่มสาว/เจ้าของร้านที่ไม่มีภาพอนุมัติ ไม่มีดนตรีกลบมุก ทุกซีนพูดเพียงคนเดียว

## เก็บ Master ลง Git และใช้ข้าม EP

ดาวน์โหลด ZIP Master Pack จากตัวช่วย แล้วแตกลง root ของ repo (ตรวจไฟล์ก่อนแทนที่):

- `CHARACTER_MASTER.json` มี record และ Base64 ของสามคน
- `ASSETS/CHARACTERS/` มีไฟล์ภาพจริงที่ decode จาก Base64; ถ้าครอปจะเป็น PNG ใหม่จากพิกเซลเดิมพร้อม provenance
- `STYLE_LOCK.json` คงข้อความ style ต้นฉบับ
- `SERIES_CONTINUITY_LOCK.json` กฎภาพและบท
- `EP01-Peach-Garden-Oath/STEP6.json` ไฟล์ครบสำหรับ import ครั้งเดียว
- `EP01-Peach-Garden-Oath/STEP5.json` snapshot สำหรับเปิดดู character stage เท่านั้น ไม่ใช่ไฟล์ merge รอบสอง
- `LOCATION_MASTER.json`, `metadata.json`, `QA_REPORT.json` อยู่ในโฟลเดอร์ตอน

ภาพเดิมที่ไม่ได้ครอปไม่ถูก re-encode และเก็บ bytes/provenance เดิมไว้ ถ้าครอปจะระบุขอบเขตและ transformation ไม่อ้างว่าเป็นต้นฉบับ byte-for-byte

หลังแตก ZIP ลง repo และตรวจ diff แล้ว:

```powershell
git status --short
git add -- THREE-KINGDOMS-ISAN-70S-COMEDY/CHARACTER_MASTER.json THREE-KINGDOMS-ISAN-70S-COMEDY/SERIES_CONTINUITY_LOCK.json THREE-KINGDOMS-ISAN-70S-COMEDY/STYLE_LOCK.json THREE-KINGDOMS-ISAN-70S-COMEDY/ASSETS THREE-KINGDOMS-ISAN-70S-COMEDY/EP01-Peach-Garden-Oath
git diff --cached --stat
git commit -m "Embed approved original character masters and EP01 single-location import"
git push origin main
```

ตอนต่อไปคัดลอก character records และ hash ชุดเดิมจาก Master Pack ไม่สร้างตัวละครใหม่ ห้ามเปลี่ยน master version ให้ตอนที่ทำเสร็จแล้วโดยไม่ตั้งใจ

## Validation scope

Builder ตรวจ JSON structure, Base64/signature, SHA-256, 3 distinct master images, 1 location, 6 scenes, 36 seconds, speaker references, script/videoPrompt agreement, exact continuity handoff, source style equality, and exclusion of stale scene video/image IDs. Browser preview checks actual image decoding and asks for human identity approval. The JS test uses synthetic image fixtures only; it is not a test against the actual user file or P&P importer. Actual video quality, model identity retention, voice continuity and importer round-trip remain unverified.
