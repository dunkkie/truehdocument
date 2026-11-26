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

## อัปเดตข้อมูลรอบใหม่ (ข้อมูลเก่าถูกเก็บไว้)

```bash
pip install pyxlsb pandas
python scripts/build_data.py "DPS_xxx.xlsb" docs/data private/staff_names.csv
git add docs/data && git commit -m "อัปเดตข้อมูล DPS รอบ ..." && git push
```

แล้วแก้ `DATA_NOTE` ใน `docs/index.html` ให้ตรงกับไฟล์รอบใหม่

สคริปต์เก็บเดือนเก่าที่มีอยู่แล้วไว้ และแทนที่เฉพาะเดือนที่อยู่ในไฟล์ใหม่ จะเติมไฟล์เดือนก่อนๆ ย้อนหลังก็ได้ ในหน้าเว็บเลือก **เดือน** และ **เทียบกับ** ได้ที่แถบด้านบน และกราฟ **ย้อนหลังรายเดือน** แสดงทุกเดือนที่มีข้อมูล

> อย่า commit ไฟล์ DPS ต้นฉบับ (`.xlsb`) เพราะมีข้อมูลลูกค้า (`.gitignore` กันไว้แล้ว)

## เปิด GitHub Pages

Settings → Pages → Build and deployment → Source: **Deploy from a branch** → Branch: `main` / folder `/docs` → Save

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

Repo นี้เป็น Public จึงเก็บเฉพาะยอดรวม ไม่มีชื่อ เบอร์ BAN หรือ SIM ของลูกค้า
Staff แสดงเป็น Sales ID Code และผู้ตรวจแสดงเป็นรหัส ไม่มีชื่อพนักงานใน repo

**ดูชื่อ Staff:** ชื่อพนักงานเก็บใน `docs/data/staff_names.enc.json` แบบเข้ารหัส (AES-256-GCM, PBKDF2 600,000 รอบ) ในหน้าเว็บส่วน "ราย Staff" ใส่รหัสผ่านเพื่อแสดงชื่อ ถ้าไม่มีรหัสผ่านจะอ่านไฟล์นี้ไม่ได้

เปลี่ยนรหัสผ่านหรืออัปเดตรายชื่อ:

```bash
pip install cryptography
TMH_NAMES_PASSWORD='รหัสผ่านใหม่' python scripts/encrypt_names.py private/staff_names.csv docs/data/staff_names.enc.json
```

ใช้รหัสผ่านยาวและเดายาก เพราะใครก็ดาวน์โหลดไฟล์ที่เข้ารหัสไปลองเดาได้
