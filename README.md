# Dashboard ตรวจสอบเอกสาร TMH Postpaid

Dashboard ผลตรวจเอกสาร DPS (TMH Postpaid): % สมบูรณ์, ข้อเสนอแนะ, สาเหตุที่ไม่สมบูรณ์, รายภาค และ **ชี้เป้ารายสาขา ราย Staff เทียบเดือนนี้กับเดือนก่อน**

**เปิดดู:** https://dunkkie.github.io/truehdocument/ (หลังเปิด GitHub Pages ตามขั้นตอนด้านล่าง)

## โครงสร้าง

| ไฟล์ | หน้าที่ |
|---|---|
| `docs/index.html` | หน้า Dashboard |
| `docs/dash-runtime.js` | ตัวโหลดข้อมูลและวาดกราฟ |
| `docs/data/*.csv` | ข้อมูลสรุป (ยอดรวมเท่านั้น) |
| `scripts/build_data.py` | แปลงไฟล์ DPS `.xlsb` เป็นไฟล์ใน `docs/data/` |

## เข้าเว็บด้วยรหัสผ่าน

หน้าเว็บเปิดด้วยหน้าใส่รหัสผ่าน ข้อมูลทั้งหมด (รวมชื่อ Staff) อยู่ใน `docs/data/site.enc.json` แบบเข้ารหัส (gzip + AES-256-GCM, คีย์จาก PBKDF2-SHA256 600,000 รอบ) ใส่รหัสถูกแล้วเบราว์เซอร์ถอดรหัสและแสดงข้อมูลทันที ไม่มีไฟล์ข้อมูลแบบอ่านได้บนเว็บ

## อัปเดตข้อมูลรอบใหม่ (ข้อมูลเก่าถูกเก็บไว้)

```bash
pip install pyxlsb pandas cryptography
python scripts/build_data.py "DPS_xxx.xlsb" private/data private/staff_names.csv
TMH_PASSWORD='รหัสผ่าน' python scripts/encrypt_site.py private/data private/staff_names.csv docs/data/site.enc.json
git add docs/data/site.enc.json && git commit -m "อัปเดตข้อมูล DPS รอบ ..." && git push
```

- `private/` เก็บไฟล์ข้อมูลแบบอ่านได้ ไม่ถูก commit (อยู่ใน `.gitignore`) ต้องเก็บโฟลเดอร์นี้ไว้เพื่อให้ข้อมูลเดือนเก่าต่อเนื่อง
- เปลี่ยนรหัสผ่าน: รันคำสั่ง `encrypt_site.py` ด้วยรหัสใหม่ แล้ว push รหัสเก่าจะใช้ไม่ได้ทันที
- แก้ `DATA_NOTE` ใน `docs/index.html` ให้ตรงกับไฟล์รอบใหม่
- อย่า commit ไฟล์ DPS ต้นฉบับ (`.xlsb`)

## เกณฑ์ชี้เป้า

ตั้งค่าได้ที่บรรทัด `const GOAL = 90, URGENT = 80, DROP = 5, MIN_SHOP = 10, MIN_STAFF = 5;` และ `DATA_NOTE` (ชื่อไฟล์ข้อมูลรอบนั้น) ใน `docs/index.html`

| สถานะ | เงื่อนไข (เดือนล่าสุด) |
|---|---|
| เร่งด่วน | % สมบูรณ์ < 80% |
| แย่ลง | ลดลง ≥ 5 จุดจากเดือนก่อน |
| ต่ำกว่าเป้า | % สมบูรณ์ < 90% |
| ดีขึ้น | เพิ่มขึ้น ≥ 5 จุด |
| ผ่านเป้า | ≥ 90% |
| เอกสารน้อย | สาขา < 10 ฉบับ / Staff < 5 ฉบับ |

## ข้อมูลส่วนบุคคล

Repo นี้เป็น Public ข้อมูลบนเว็บจึงเข้ารหัสทั้งหมด และเก็บเฉพาะยอดรวม ไม่มีชื่อ เบอร์ BAN หรือ SIM ของลูกค้า
Staff แสดงเป็น Sales ID Code และผู้ตรวจแสดงเป็นรหัส ไม่มีชื่อพนักงานใน repo

ชื่อ Staff แสดงหลังเข้าสู่ระบบ ใช้รหัสผ่านที่ยาวและเดายาก เพราะใครก็ดาวน์โหลดไฟล์ที่เข้ารหัสไปลองเดาได้
