#!/usr/bin/env python3
"""Akash 020: diagnose and execute AkashML inference with custody receipts. Usage: freeze | run | verify"""
import json,os,sys,time,urllib.error,urllib.request
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location("agent011",ROOT/"agent/agent011.py");A=importlib.util.module_from_spec(s);s.loader.exec_module(A)
BASE=ROOT/"evidence/successor_020";A.KIT=A.KIT+["agent/akash020.py","docs/ADDENDUM_020.md"];A.BASE=BASE
API="https://api.akashml.com/v1"
def call(method,path,key,body=None,ua=None):
    h={"Authorization":"Bearer "+key}
    if body is not None:h["Content-Type"]="application/json"
    if ua:h["User-Agent"]=ua
    req=urllib.request.Request(API+path,data=body,headers=h,method=method);t=time.monotonic();out={"method":method,"path":path,"ua":ua or "python-urllib default"}
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({}),A.NoRedirect()).open(req,timeout=60) as r:
            raw=r.read(200000);out.update(status=r.status,inference_id=r.headers.get("Inference-Id"),content_type=r.headers.get("content-type"))
    except urllib.error.HTTPError as e:
        raw=e.read(2000);out.update(status=e.code,inference_id=e.headers.get("Inference-Id"),content_type=e.headers.get("content-type"),retry_after=e.headers.get("Retry-After"))
    except Exception as e:raw=b"";out.update(status=None,error=type(e).__name__)
    out["elapsed_ms"]=round((time.monotonic()-t)*1000,1);txt=raw.decode(errors="replace")
    if key:txt=txt.replace(key,"<key>")
    out["body_excerpt"]=txt[:400];out["body_sha256"]=A.sha(raw);return out,raw
def run():
    if not A.artifacts_ok(BASE):raise SystemExit("governed bytes changed; successor freeze needed")
    R=A.Run(BASE);key=os.environ.get("AKASHML_API_KEY","");model=os.environ.get("AKASHML_MODEL","")
    R.step("akash_key_shape","OBSERVED",{"key_set":bool(key),"length":len(key),"starts_akml":key.startswith("akml-"),"starts_console_ac_sk":key.startswith("ac.sk."),"has_whitespace_or_quote":any(c in key for c in " \t\n\r\"'"),"model_set":bool(model),"model":model},{"key_present":bool(key),"model_present":bool(model),"looks_like_akashml_key":key.startswith("akml-"),"is_console_key":key.startswith("ac.sk.")})
    if not key or not model:return
    m,raw=call("GET","/models",key);ids=[]
    try:ids=[x["id"] for x in json.loads(raw).get("data",[])]
    except Exception:pass
    R.step("akash_models_list","OBSERVED" if m.get("status")==200 else "FAILED",{**m,"model_ids":ids[:40]},{"http_200":m.get("status")==200,"configured_model_listed":model in ids})
    facts={"task":"Explain the vulnerability and propose a fix. Advice only.","rule":(ROOT/"rules/fallback.yaml").read_text(),"fixture_before_source":(ROOT/"fixtures/before.py").read_text()}
    body=json.dumps({"model":model,"messages":[{"role":"system","content":"Return JSON only with string keys summary,root_cause,fix,risk."},{"role":"user","content":json.dumps(facts,sort_keys=True)}],"temperature":0,"max_tokens":600}).encode()
    ok=False
    for n,ua in enumerate([None,"antigense-agent/020"],1):
        c,raw=call("POST","/chat/completions",key,body,ua);ok=c.get("status")==200
        det={**c,"request_sha256":A.sha(body)}
        if ok:
            j=json.loads(raw);txt=j["choices"][0]["message"]["content"];valid,why=A.validate_advice(txt);det.update(model_returned=j.get("model"),usage=j.get("usage"),schema_valid=valid,schema_note=why,ceiling="managed AkashML inference only; no GPU lease, attestation or confidentiality")
        R.step("akash_chat_attempt_%d"%n,"OBSERVED" if ok else "FAILED",det,{"actual_akash_call":ok,"http_200":ok,"model_identity_returned":ok and bool(det.get("model_returned")),"usage_returned":ok and bool(det.get("usage")),"advice_schema_valid":ok and bool(det.get("schema_valid")),"gpu_lease_established":False,"attestation_verified":False,"advice_applied":False},raw if ok else None)
        if ok:break
if __name__=="__main__":
    c=sys.argv[1] if len(sys.argv)>1 else ""
    if c=="freeze":print("project_root",A.freeze(BASE)["project_root"])
    elif c=="run":run()
    elif c=="verify":r=A.verify(BASE);print(json.dumps(r,indent=2,sort_keys=True));sys.exit(0 if r["PASS"] else 1)
    else:sys.exit("usage: freeze|run|verify")
