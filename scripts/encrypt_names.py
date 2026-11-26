"""Encrypt the staff-name list so the public dashboard can show names only after a password.

Usage:
    pip install cryptography
    TMH_NAMES_PASSWORD='your password' python scripts/encrypt_names.py private/staff_names.csv docs/data/staff_names.enc.json

AES-256-GCM with a key from PBKDF2-SHA256 (600,000 rounds). The browser decrypts with the
same password (Web Crypto). Without the password the file cannot be read, so use a long
password: anyone can download the encrypted file and try to guess it.
"""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

src, dst = sys.argv[1], sys.argv[2]
pw = os.environ.get('TMH_NAMES_PASSWORD')
if not pw:
    sys.exit('Set TMH_NAMES_PASSWORD')
ITER = 600_000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode('utf-8'))
data = open(src, 'rb').read()
ct = AESGCM(key).encrypt(iv, data, None)
b64 = lambda b: base64.b64encode(b).decode()
json.dump({'v': 1, 'kdf': 'PBKDF2-SHA256', 'iter': ITER, 'salt': b64(salt), 'iv': b64(iv), 'ct': b64(ct)}, open(dst, 'w'))
print('encrypted', len(data), 'bytes ->', dst)
