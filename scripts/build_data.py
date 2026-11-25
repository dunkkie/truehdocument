"""Build aggregated CSVs for the TMH Postpaid document-check dashboard.

Usage:
    pip install pyxlsb pandas
    python scripts/build_data.py "DPS_xxx.xlsb" docs/data [private/staff_names.csv]

The optional third path writes a staff_id -> name list for loading in the
browser. Keep it on your own computer: private/ is in .gitignore.

Reads the 'Detail' sheet of the DPS export and writes only aggregated counts.
No customer data (name, phone, BAN, SIM) and no employee names are written:
staff appear by Sales ID Code. Auditor names are not exported.
"""
import sys, os
import pandas as pd
from pyxlsb import open_workbook

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)

rows = []
with open_workbook(src) as wb:
    with wb.get_sheet('Detail') as sh:
        for r in sh.rows():
            rows.append([c.v for c in r])
df = pd.DataFrame(rows[1:], columns=rows[0])
d = df[df['ผลการตรวจสอบ'].notna()].copy()

d['date'] = (pd.Timestamp('1899-12-30') + pd.to_timedelta(d['Order Date'].astype(float), unit='D')).dt.strftime('%Y-%m-%d')
d['month'] = d['date'].str[:7]
d['result'] = d['ผลการตรวจสอบ'].map({'สมบูรณ์': 'complete', 'ไม่สมบูรณ์': 'incomplete', 'ไม่สมบูรณ์ (X Flag)': 'xflag'})
d['rr'] = d['RR']; d['region'] = d['Region']
d['channel'] = d['Channel']; d['order_type'] = d['Order Type']; d['smartdoc'] = d['Smart Doc Flag']
d['delivery'] = d['ประเภทการนำส่ง']

ver = pd.to_datetime(d['วันที่ตรวจเรียบร้อยแล้ว'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
d['tat'] = (ver.dt.normalize() - pd.to_datetime(d['date'])).dt.days
def bucket(x):
    if pd.isna(x): return 'ไม่ระบุ'
    if x <= 1: return '0-1 วัน'
    if x <= 3: return '2-3 วัน'
    if x <= 7: return '4-7 วัน'
    if x <= 14: return '8-14 วัน'
    return '15+ วัน'
d['tat_bucket'] = d['tat'].map(bucket)
d['tat'] = d['tat'].fillna(0)

d['shop_code'] = d['Parent Code/SIM Owner'].astype(str)
nm = d['Parent Code/SIM Owner Name'].fillna('')
d['shop'] = nm.str.extract(r'\((.*)\)\s*$')[0].fillna(nm).str.strip()
d['staff_id'] = d['Sales ID Code'].astype(str).str.strip()

reason = d['เหตุผลการตรวจสอบ'].fillna('').str.replace(r'^\s*-\s*', '', regex=True) \
    .str.replace('ผลตรวจจากการ Upload Verification Result', '', regex=False).str.strip()
d['reason'] = reason.where(reason.str.match(r'^(เอกสารหลัก|ใบสมัคร)_'), '')
d.loc[(d.result != 'complete') & (d.reason == ''), 'reason'] = 'อื่นๆ'

dims = ['month', 'rr', 'region', 'date', 'channel', 'order_type', 'smartdoc', 'delivery', 'result']
d.groupby(dims).agg(n=('tat', 'size'), tat_sum=('tat', 'sum')).reset_index().to_csv(f'{out}/cube.csv', index=False)

bad = d[d.result != 'complete']
bad.groupby(['month', 'rr', 'region', 'result', 'reason']).size().reset_index(name='n').to_csv(f'{out}/reasons_main.csv', index=False)

it = bad[['month', 'rr', 'region', 'เหตุผลการตรวจสอบ อื่นๆ']].copy()
it['item'] = it['เหตุผลการตรวจสอบ อื่นๆ'].fillna('').str.split(',')
it = it.explode('item'); it['item'] = it['item'].str.strip()
it = it[it.item != '']
it['item'] = it['item'].replace({'ขาด Workpermit': 'ขาด Work Permit'})
top = it.item.value_counts().head(20).index
it['item'] = it.item.where(it.item.isin(top), 'อื่นๆ')
it.groupby(['month', 'rr', 'region', 'item']).size().reset_index(name='n').to_csv(f'{out}/reasons_detail.csv', index=False)

d.groupby(['month', 'rr', 'region', 'shop_code', 'shop', 'result']).size().reset_index(name='n').to_csv(f'{out}/shops.csv', index=False)
d.groupby(['month', 'rr', 'region', 'tat_bucket']).size().reset_index(name='n').to_csv(f'{out}/tat.csv', index=False)
d.groupby(['month', 'rr', 'region', 'shop_code', 'shop', 'staff_id', 'result', 'reason']).size().reset_index(name='n').to_csv(f'{out}/staff.csv', index=False)

if len(sys.argv) > 3:
    names = d[['staff_id', 'Sales Name']].rename(columns={'Sales Name': 'staff'})
    names['staff'] = names['staff'].fillna('').astype(str).str.strip()
    names = names[names.staff != ''].drop_duplicates('staff_id').sort_values('staff_id')
    os.makedirs(os.path.dirname(sys.argv[3]) or '.', exist_ok=True)
    names.to_csv(sys.argv[3], index=False, encoding='utf-8-sig')
    print('staff names:', len(names), '->', sys.argv[3], '(do not commit)')

print('rows checked:', len(d), '->', out)
