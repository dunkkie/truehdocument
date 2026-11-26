"""Update the dashboard with a new DPS file. Only the data changes; the page design stays the same.

Usage:
    pip install pyxlsb pandas cryptography
    TMH_PASSWORD='<website password>' python scripts/update.py "DPS_xxx.xlsb"

What it does:
1. Opens the current encrypted data (docs/data/site.enc.json) with the password, so the
   months already on the website are kept (each DPS file holds only about 2 months).
2. Builds the months in the new file (scripts/build_data.py). Months in the new file
   replace the same months already stored; older months stay.
3. Merges the staff-name list (names from the new file win).
4. Writes a note about the date range and source file, and encrypts everything again
   into docs/data/site.enc.json. docs/index.html is never touched.
"""
import base64, gzip, json, os, subprocess, sys, tempfile
from io import StringIO
import pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUNDLE = os.path.join(ROOT, 'docs', 'data', 'site.enc.json')
src = sys.argv[1]
pw = os.environ.get('TMH_PASSWORD')
if not pw:
    sys.exit('Set TMH_PASSWORD (the website password)')


def key_for(salt, iters):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iters).derive(pw.encode('utf-8'))


work = tempfile.mkdtemp(prefix='tmh_')
data_dir = os.path.join(work, 'data')
os.makedirs(data_dir)
old_names = None
if os.path.exists(BUNDLE):
    b = json.load(open(BUNDLE))
    try:
        plain = AESGCM(key_for(base64.b64decode(b['salt']), b['iter'])).decrypt(
            base64.b64decode(b['iv']), base64.b64decode(b['ct']), None)
    except Exception:
        sys.exit('Wrong password for the current data: nothing was changed')
    files = json.loads(gzip.decompress(plain).decode('utf-8'))
    for name, text in files.items():
        if name == 'staff_names.csv':
            old_names = text
        elif name.endswith('.csv') and name != 'meta.csv':
            open(os.path.join(data_dir, name), 'w', encoding='utf-8').write(text)
    print('kept history from current website:', ', '.join(sorted(files)))

new_names = os.path.join(work, 'staff_names_new.csv')
subprocess.run([sys.executable, '-I', os.path.join(HERE, 'build_data.py'), src, data_dir, new_names], check=True)

# merge names: names from the new file win
frames = []
if old_names:
    frames.append(pd.read_csv(StringIO(old_names.lstrip('﻿')), dtype=str))
if os.path.exists(new_names):
    frames.append(pd.read_csv(new_names, dtype=str, encoding='utf-8-sig'))
names_path = os.path.join(work, 'staff_names.csv')
if frames:
    pd.concat(frames).drop_duplicates('staff_id', keep='last').sort_values('staff_id').to_csv(names_path, index=False)

# note shown on the page
facts = pd.read_csv(os.path.join(data_dir, 'facts.csv'), dtype=str)
months = sorted(facts.month.unique())
d0, d1 = facts.date.min(), facts.date.max()
TH = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']
fmt = lambda s: f"{int(s[8:10])} {TH[int(s[5:7]) - 1]} {s[2:4]}"
note = f"ข้อมูล {fmt(d0)} – {fmt(d1)} · ไฟล์ล่าสุด {os.path.basename(src)}"
pd.DataFrame([{'key': 'note', 'value': note}, {'key': 'months', 'value': ' '.join(months)}]).to_csv(
    os.path.join(data_dir, 'meta.csv'), index=False)

subprocess.run([sys.executable, '-I', os.path.join(HERE, 'encrypt_site.py'), data_dir, names_path, BUNDLE], check=True)
print('months on website:', ', '.join(months))
print('note:', note)
print('done: commit and push docs/data/site.enc.json')
