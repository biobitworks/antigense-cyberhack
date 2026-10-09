#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
base=Path(__file__).resolve().parent
m=json.loads((base/'PACKAGE_MANIFEST_030R1.json').read_text())
def h(b):return hashlib.sha256(b).hexdigest()
def canon(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
level=[];ok=True
for entry in m['files']:
    data=(base/entry['path']).read_bytes()
    ok=ok and len(data)==entry['bytes'] and h(data)==entry['sha256']
    level.append(h(b'\x00'+hashlib.sha256(canon(entry)).digest()))
while len(level)>1:
    level=[h(b'\x01'+bytes.fromhex(level[i])+bytes.fromhex(level[i+1])) if i+1<len(level) else level[i] for i in range(0,len(level),2)]
ok=ok and level[0]==m['package_merkle_root']
print(('PASS' if ok else 'FAIL')+' package declared-byte integrity')
print('Package Merkle root: '+level[0])
print('No signature, truth, safety or causality proof.')
sys.exit(0 if ok else 1)
