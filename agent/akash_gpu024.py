#!/usr/bin/env python3
"""Akash GPU 024: Console API deploy -> bid -> lease -> Ollama inference -> close. Usage: freeze | run | verify"""
import importlib.util,json,os,sys,time,urllib.error,urllib.request
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location("agent011",ROOT/"agent/agent011.py");A=importlib.util.module_from_spec(s);s.loader.exec_module(A)
BASE=ROOT/"evidence/successor_024";A.KIT=[k for k in A.KIT if not k.startswith("public/")]+["agent/akash_gpu024.py","docs/ADDENDUM_024.md"];A.BASE=BASE
API="https://console-api.akash.network";UA="antigense-agent/024 (+https://github.com/biobitworks/antigense-cyberhack)"
IMAGE="ollama/ollama:0.6.5";MODEL="qwen2.5:0.5b";MAX_UACT=10000
SDL=f'''version: "2.0"
services:
  llm:
    image: {IMAGE}
    expose:
      - port: 11434
        as: 80
        to:
          - global: true
profiles:
  compute:
    llm:
      resources:
        cpu:
          units: 4
        memory:
          size: 16Gi
        storage:
          size: 30Gi
        gpu:
          units: 1
          attributes:
            vendor:
              nvidia:
  placement:
    dcloud:
      pricing:
        llm:
          denom: uact
          amount: {MAX_UACT}
deployment:
  llm:
    dcloud:
      profile: llm
      count: 1
'''
def http(method,url,key=None,body=None,timeout=60):
    h={"User-Agent":UA,"Accept":"application/json"}
    if key:h["x-api-key"]=key
    data=None
    if body is not None:data=json.dumps(body).encode();h["Content-Type"]="application/json"
    t=time.monotonic()
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({}),A.NoRedirect()).open(urllib.request.Request(url,data=data,headers=h,method=method),timeout=timeout) as r:
            raw=r.read(5_000_000);st=r.status
    except urllib.error.HTTPError as e:raw=e.read(3000);st=e.code
    except Exception as e:return None,b"",{"error":type(e).__name__,"ms":round((time.monotonic()-t)*1000,1)}
    meta={"ms":round((time.monotonic()-t)*1000,1)}
    if st>=400:meta["error_excerpt"]=raw.decode(errors="replace").replace(key or "\x00","<key>")[:300]
    return st,raw,meta
def J(raw):
    try:return json.loads(raw)
    except Exception:return {}
def run():
    if not A.artifacts_ok(BASE):raise SystemExit("governed bytes changed; successor freeze needed")
    R=A.Run(BASE);key=os.environ.get("AKASH_API_KEY") or (os.environ.get("AKASHML_API_KEY","") if os.environ.get("AKASHML_API_KEY","").startswith("ac.sk.") else "")
    if not key:R.step("gpu_preflight","NOT_TESTED",{"reason":"no Console key"},{"key_present":False});return
    R.step("gpu_preflight","OBSERVED",{"image":IMAGE,"model":MODEL,"max_uact_per_block":MAX_UACT,"runtime_limit_hours":1,"sdl_sha256":A.sha(SDL.encode()),"sdl":SDL},{"key_present":True,"image_tag_pinned":":" in IMAGE and not IMAGE.endswith(":latest"),"runtime_limit_set":True})
    dseq=None
    try:
        st,raw,m=http("POST",API+"/v1/deployments",key,{"data":{"sdl":SDL,"runtimeLimitHours":1}})
        d=J(raw).get("data",{});dseq=d.get("dseq");tx=(d.get("signTx") or {})
        R.step("gpu_create_deployment","OBSERVED" if st in(200,201) and dseq else "FAILED",{"status":st,**m,"dseq":dseq,"tx_code":tx.get("code"),"tx_hash":tx.get("transactionHash")},{"created":bool(dseq),"tx_code_zero":tx.get("code")==0})
        if not dseq:return
        bids=[];t0=time.monotonic()
        while time.monotonic()-t0<360:
            st,raw,m=http("GET",API+"/v1/bids?dseq="+dseq,key);bids=J(raw).get("data") or []
            if bids:time.sleep(15);st,raw,m=http("GET",API+"/v1/bids?dseq="+dseq,key);bids=J(raw).get("data") or bids;break
            time.sleep(8)
        summ=[]
        for b in bids:
            bb=b["bid"];gpus=[]
            for ro in bb.get("resources_offer",[]):
                g=(ro.get("resources") or {}).get("gpu") or {};gpus.append(json.dumps(g.get("attributes",g),sort_keys=True)[:200])
            summ.append({"provider":bb["id"]["provider"],"price_uact":bb["price"]["amount"],"denom":bb["price"]["denom"],"gpu":gpus})
        R.step("gpu_bids","OBSERVED" if bids else "FAILED",{"bid_count":len(bids),"waited_s":round(time.monotonic()-t0),"bids":summ[:10]},{"bids_received":bool(bids)})
        if not bids:return
        best=min(bids,key=lambda b:float(b["bid"]["price"]["amount"]))["bid"]["id"]
        st,raw,m=http("POST",API+"/v1/leases",key,{"leases":[{"dseq":dseq,"gseq":best["gseq"],"oseq":best["oseq"],"provider":best["provider"]}]},timeout=120)
        R.step("gpu_lease","OBSERVED" if st==200 else "FAILED",{"status":st,**m,"provider":best["provider"],"gseq":best["gseq"],"oseq":best["oseq"]},{"lease_created":st==200})
        if st!=200:return
        uri=None;t0=time.monotonic()
        while time.monotonic()-t0<480 and not uri:
            st,raw,m=http("GET",API+"/v1/deployments/"+dseq,key)
            for l in J(raw).get("data",{}).get("leases",[]):
                sv=((l.get("status") or {}).get("services") or {}).get("llm") or {}
                if sv.get("uris"):uri=sv["uris"][0]
            if not uri:time.sleep(10)
        R.step("gpu_service_uri","OBSERVED" if uri else "FAILED",{"uri_host_sha256":A.sha((uri or "").encode()),"waited_s":round(time.monotonic()-t0)},{"uri_assigned":bool(uri)})
        if not uri:return
        base="http://"+uri.split("://")[-1].rstrip("/");ready=False;t0=time.monotonic();ver=None
        while time.monotonic()-t0<480:
            st,raw,m=http("GET",base+"/api/version",timeout=15)
            if st==200:ready=True;ver=J(raw).get("version");break
            time.sleep(10)
        R.step("gpu_ollama_ready","OBSERVED" if ready else "FAILED",{"ollama_version":ver,"waited_s":round(time.monotonic()-t0)},{"service_ready":ready})
        if not ready:return
        st,raw,m=http("POST",base+"/api/pull",body={"model":MODEL,"stream":False},timeout=900)
        R.step("gpu_model_pull","OBSERVED" if st==200 else "FAILED",{"status":st,**m,"model":MODEL,"result":J(raw).get("status")},{"pulled":st==200})
        if st!=200:return
        prompt=("You are reviewing a security finding. Semgrep rule:\n"+(ROOT/"rules/fallback.yaml").read_text()+"\nCode:\n"+(ROOT/"fixtures/before.py").read_text()+
                "\nReturn JSON only with string keys summary, root_cause, fix, risk.")
        req={"model":MODEL,"prompt":prompt,"stream":False,"format":"json","options":{"temperature":0,"seed":7}}
        st,raw,m=http("POST",base+"/api/generate",body=req,timeout=300);g=J(raw);txt=g.get("response","")
        valid,why=A.validate_advice(txt) if st==200 else (False,"no response")
        R.step("gpu_inference","OBSERVED" if st==200 and txt else "FAILED",{"status":st,**m,"model":g.get("model"),"request_sha256":A.sha(json.dumps(req,sort_keys=True).encode()),"response_sha256":A.sha(raw),"eval_count":g.get("eval_count"),"prompt_eval_count":g.get("prompt_eval_count"),"total_duration_ns":g.get("total_duration"),"eval_duration_ns":g.get("eval_duration"),"advice_excerpt":txt[:600],"schema_valid":valid,"schema_note":why},
              {"actual_akash_gpu_inference":st==200 and bool(txt),"advice_schema_valid":valid,"advice_applied":False,"attestation_verified":False},raw if st==200 else None)
        st,raw,m=http("GET",base+"/api/ps",timeout=15);ps=J(raw).get("models",[])
        R.step("gpu_provider_reported_vram","OBSERVED" if st==200 else "FAILED",{"models":[{"name":x.get("name"),"size":x.get("size"),"size_vram":x.get("size_vram")} for x in ps]},{"vram_reported_nonzero":any((x.get("size_vram") or 0)>0 for x in ps),"gpu_attested":False})
    finally:
        if dseq:
            st,raw,m=http("DELETE",API+"/v1/deployments/"+dseq,key,timeout=120)
            R.step("gpu_close_deployment","OBSERVED" if st==200 else "FAILED",{"status":st,**m,"dseq":dseq,"response":J(raw).get("data")},{"closed":st==200})
            print("CLOSE status",st,"dseq",dseq,flush=True)
if __name__=="__main__":
    c=sys.argv[1] if len(sys.argv)>1 else ""
    if c=="freeze":print("project_root",A.freeze(BASE)["project_root"])
    elif c=="run":run()
    elif c=="verify":r=A.verify(BASE);print(json.dumps(r,indent=2,sort_keys=True));sys.exit(0 if r["PASS"] else 1)
    else:sys.exit("usage: freeze|run|verify")
