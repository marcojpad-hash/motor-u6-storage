"""U5 común: hashing canónico y utilidades. No decide H. No escribe nada del motor."""
import hashlib, json
from pathlib import Path
U5 = Path(__file__).resolve().parent
PACK = U5.parent
ENGINE_SHA = "665c39a2861e58772522e91272563260d980908b1d4ab9f7092d3413d0c36082"
PAT_SHA = "d827dcc3882634ec2d21b3a480d0fee811b28d8fa1b73bab04f0af2c2d6667a1"

def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def canon(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")

def self_hash(receipt):
    r = {k: v for k, v in receipt.items() if k != "self_sha256"}
    return hashlib.sha256(canon(r)).hexdigest()
