"""Encrypt all dashboard data into one file so the website opens only with a password.

Usage:
    pip install cryptography
    TMH_PASSWORD='your password' python scripts/encrypt_site.py private/data private/staff_names.csv docs/data/site.enc.json

Each CSV is gzip-compressed, then the bundle is encrypted with AES-256-GCM using a key
from PBKDF2-SHA256 (600,000 rounds). The page asks for the password and decrypts in the
browser. Plain CSVs stay in private/ (not committed).
"""
import base64, glob, gzip, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

src_dir, names_csv, dst = sys.argv[1], sys.argv[2], sys.argv[3]
pw = os.environ.get('TMH_PASSWORD')
if not pw:
    sys.exit('Set TMH_PASSWORD')
files = {os.path.basename(p): open(p, encoding='utf-8-sig').read() for p in sorted(glob.glob(os.path.join(src_dir, '*.csv')))}
if os.path.exists(names_csv):
    files['staff_names.csv'] = open(names_csv, encoding='utf-8-sig').read()
plain = gzip.compress(json.dumps(files, ensure_ascii=False).encode('utf-8'), 9)
ITER = 600_000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode('utf-8'))
ct = AESGCM(key).encrypt(iv, plain, None)
b64 = lambda b: base64.b64encode(b).decode()
os.makedirs(os.path.dirname(dst), exist_ok=True)
json.dump({'v': 2, 'kdf': 'PBKDF2-SHA256', 'iter': ITER, 'salt': b64(salt), 'iv': b64(iv), 'gzip': True, 'ct': b64(ct)}, open(dst, 'w'))
print('encrypted', ', '.join(files), '->', dst, f'({len(ct)//1024} KB)')
