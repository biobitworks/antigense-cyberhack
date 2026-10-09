#!/usr/bin/env python3
"""Akash Console 022: one read-only authenticated Console API call. Usage: freeze | run | verify"""
import importlib.util,json,os,sys,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location("agent011",ROOT/"agent/agent011.py");A=importlib.util.module_from_spec(s);s.loader.exec_module(A)
BASE=ROOT/"evidence/successor_022";A.KIT=[k for k in A.KIT if not k.startswith("public/")]+["agent/akash_console022.py","docs/ADDENDUM_022.md"];A.BASE=BASE
URL="https://console-api.akash.network/v1/deployments?limit=5"
def run():
    if not A.artifacts_ok(BASE):raise SystemExit("governed bytes changed; successor freeze needed")
    R=A.Run(BASE);k=os.environ.get("AKASH_API_KEY","")
    src="AKASH_API_KEY"
    if not k and os.environ.get("AKASHML_API_KEY","").startswith("ac.sk."):k=os.environ["AKASHML_API_KEY"];src="AKASHML_API_KEY (Console-prefixed)"
    if not k:R.step("akash_console_list","NOT_TESTED",{"reason":"no Console key in env"},{"call_made":False});return
    t=time.monotonic();out={"url":URL,"key_source_var":src,"key_prefix_console":k.startswith("ac.sk.")}
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({}),A.NoRedirect()).open(urllib.request.Request(URL,headers={"x-api-key":k}),timeout=30) as r:
            raw=r.read(500000);out["status"]=r.status
    except urllib.error.HTTPError as e:raw=e.read(1000);out["status"]=e.code;out["error_excerpt"]=raw.decode(errors="replace").replace(k,"<key>")[:300]
    except Exception as e:raw=b"";out.update(status=None,error=type(e).__name__)
    out["elapsed_ms"]=round((time.monotonic()-t)*1000,1);out["response_sha256"]=A.sha(raw)
    ok=out["status"]==200;pg={}
    if ok:
        d=json.loads(raw).get("data",{});pg=d.get("pagination",{});out["deployment_count_returned"]=len(d.get("deployments",[]));out["pagination_total"]=pg.get("total")
    R.step("akash_console_list","OBSERVED" if ok else "FAILED",out,{"http_200":ok,"authenticated_akash_api_call":ok,"deployment_created":False,"lease_created":False,"gpu_inference":False,"spend":False})
if __name__=="__main__":
    c=sys.argv[1] if len(sys.argv)>1 else ""
    if c=="freeze":print("project_root",A.freeze(BASE)["project_root"])
    elif c=="run":run()
    elif c=="verify":r=A.verify(BASE);print(json.dumps(r,indent=2,sort_keys=True));sys.exit(0 if r["PASS"] else 1)
    else:sys.exit("usage: freeze|run|verify")
