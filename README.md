# Dashboard ตรวจสอบเอกสาร TMH Postpaid

Dashboard ผลตรวจเอกสาร DPS (TMH Postpaid): % สมบูรณ์, สาเหตุที่ไม่สมบูรณ์, รายภาค, รายสาขา, ราย Staff และข้อเสนอแนะ

**เปิดดู:** https://dunkkie.github.io/truehdocument/ (หลังเปิด GitHub Pages ตามขั้นตอนด้านล่าง)

## โครงสร้าง

| ไฟล์ | หน้าที่ |
|---|---|
| `docs/index.html` | หน้า Dashboard |
| `docs/dash-runtime.js` | ตัวโหลดข้อมูลและวาดกราฟ |
| `docs/data/*.csv` | ข้อมูลสรุป (ยอดรวมเท่านั้น) |
| `scripts/build_data.py` | แปลงไฟล์ DPS `.xlsb` เป็นไฟล์ใน `docs/data/` |

## อัปเดตข้อมูลรอบใหม่

```bash
pip install pyxlsb pandas
python scripts/build_data.py "DPS_xxx.xlsb" docs/data private/staff_names.csv
git add docs/data && git commit -m "อัปเดตข้อมูล DPS รอบ ..." && git push
```

แล้วแก้ช่วงวันที่ในหัวข้อ `docs/index.html` ให้ตรงกับรอบใหม่

> อย่า commit ไฟล์ DPS ต้นฉบับ (`.xlsb`) เพราะมีข้อมูลลูกค้า (`.gitignore` กันไว้แล้ว)

## เปิด GitHub Pages

Settings → Pages → Build and deployment → Source: **Deploy from a branch** → Branch: `main` / folder `/docs` → Save

## ข้อมูลส่วนบุคคล

Repo นี้เป็น Public จึงเก็บเฉพาะยอดรวม ไม่มีชื่อ เบอร์ BAN หรือ SIM ของลูกค้า
Staff แสดงเป็น Sales ID Code และผู้ตรวจแสดงเป็นรหัส ไม่มีชื่อพนักงานใน repo

**ดูชื่อ Staff:** ในส่วน "รายละเอียดรายสาขา ราย Staff" กด "รายชื่อพนักงาน (ไฟล์ในเครื่อง)" แล้วเลือกไฟล์ `staff_names.csv` (คอลัมน์ `staff_id,staff`) ไฟล์จะถูกอ่านในเบราว์เซอร์ของคุณเท่านั้น ไม่ถูกส่งขึ้นเว็บ และเบราว์เซอร์จะจำไว้ครั้งต่อไป สร้างไฟล์นี้ด้วยอาร์กิวเมนต์ที่ 3 ของ `scripts/build_data.py`
