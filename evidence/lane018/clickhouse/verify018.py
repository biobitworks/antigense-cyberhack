#!/usr/bin/env python3
"""Lane 3 independent verifier (own code; does not import src/custody.py). Usage: verify018.py [--cloud]"""
import json,hashlib,sys,os,glob,base64,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
H=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def root_of(led):
    hs=[H(canon({"event_index":i+1,"event_hash":e["event_hash"],"cfmo_version_id":e["fco_id"]})) for i,e in enumerate(led)]
    n=len(hs);pos=0;peaks=[]
    for ex in range(n.bit_length()-1,-1,-1):
        w=1<<ex
        if n&w:
            lv=hs[pos:pos+w];pos+=w
            while len(lv)>1:lv=[H(bytes.fromhex(lv[i])+bytes.fromhex(lv[i+1])) for i in range(0,len(lv),2)]
            peaks.append(lv[0])
    acc=peaks[0]
    for p in peaks[1:]:acc=H(bytes.fromhex(acc)+bytes.fromhex(p))
    return peaks,H(b"HYDRALAMP_MMR_BAG_V1:"+bytes.fromhex(acc)),hs
def check(name):
    b=ROOT/"evidence"/name;led=[json.loads(l) for l in (b/"ledger.jsonl").read_text().splitlines() if l]
    out={"base":name,"leaf_count":len(led),"prefixes":[],"ok":True}
    for k in range(1,len(led)+1):
        pk,rt,_=root_of(led[:k]);st=json.loads((b/("prefix-%06d.json"%k)).read_text())
        good=st["root"]==rt and st["peaks"]==pk and st["leaf_count"]==k
        out["prefixes"].append({"k":k,"root":rt,"peaks":len(pk),"match":good});out["ok"]&=good
    # event_hash vs canonical step bytes (probe both raw file and canonical JSON)
    eh=[]
    for e in led:
        i=e["event_index"];f=b/("step-%06d.json"%i)
        if not f.exists():eh.append(None);continue
        raw=f.read_bytes();o=json.loads(raw)
        eh.append("canonical" if H(canon(o))==e["event_hash"] else "rawfile" if H(raw)==e["event_hash"] else "NO_MATCH")
    out["event_hash_binding"]=sorted(set(map(str,eh)));out["final_root"]=out["prefixes"][-1]["root"]
    out["leaf_order"]=[e["fco_id"][-12:] for e in led]
    return out
res={n:check(n) for n in("successor_015","successor_016")}
if "--cloud" in sys.argv:
    env={}
    for l in (ROOT/".env").read_text().splitlines():
        if "=" in l:k,v=l.split("=",1);env[k.strip()]=v.strip().strip('"\'')
    def q(sql):
        u="https://%s:8443/?default_format=JSONEachRow&query=%s"%(env["CLICKHOUSE_HOST"],urllib.parse.quote(sql))
        r=urllib.request.Request(u,headers={"Authorization":"Basic "+base64.b64encode((env.get("CLICKHOUSE_USER","default")+":"+env["CLICKHOUSE_PASSWORD"]).encode()).decode()})
        class NR(urllib.request.HTTPRedirectHandler):
            def redirect_request(*a,**k):return None
        with urllib.request.build_opener(urllib.request.ProxyHandler({}),NR).open(r,timeout=30) as x:return x.status,x.read(5_000_000).decode()
    cl={}
    for t in("antigense_events_015","antigense_events_016"):
        try:
            s,a=q("SELECT count() AS n,uniqExact(occurrence_id) AS u FROM %s FINAL"%t);s2,rows=q("SELECT * FROM %s FINAL ORDER BY occurrence_id"%t)
            cl[t]={"http":s,"count":json.loads(a),"rows_sha256":H(rows.encode()),"rows":len(rows.splitlines())}
        except Exception as e:cl[t]={"state":"FAILED","error":type(e).__name__,"code":getattr(e,"code",None)}
    res["cloud_readback"]=cl
json.dump(res,open(Path(__file__).parent/"verification.json","w"),indent=1,sort_keys=True)
for n in("successor_015","successor_016"):r=res[n];print(n,r["leaf_count"],"ok" if r["ok"] else "FAIL",r["final_root"][:16],r["event_hash_binding"])
print(json.dumps(res.get("cloud_readback"),indent=1)[:900])
