#!/usr/bin/env python3
"""Antigense agent 011: bounded, manually started. Every material step is appended to a successor custody MMR.
Usage: agent011.py freeze|run [--publish <successor project_root>] | verify
No credentials are ever written. Sponsor access missing => NOT_TESTED receipt, never success."""
import argparse,datetime,hashlib,http.server,importlib.util,json,os,subprocess,sys,tempfile,threading,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location("custody",ROOT/"src/custody.py");C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)
BASE=ROOT/"evidence/successor_011";BLOBS=ROOT/"evidence/run_011/blobs"
SITE="antigense-cyberhack.vercel.app";ALLOW={SITE};MAX_REQ=8;TIMEOUT=10;MAX_BYTES=3_000_000
STATUS_PATH=ROOT/"public/data/defense-status.json";STATUS_URL="https://"+SITE+"/data/defense-status.json"
KIT=["agent/agent011.py","CUSTODY_CONTRACT_011.json","CUSTODY_CONTRACT_008.json","RELEASE_009.json","src/custody.py","src/cascade.py","fixtures/before.py","fixtures/after.py","rules/fallback.yaml","public/index.html","public/verify.js","docs/ONBOARDING_REQUESTS_011.md","vercel.json"]
sha=lambda b:hashlib.sha256(b).hexdigest()
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def blob(b):
    BLOBS.mkdir(parents=True,exist_ok=True);p=BLOBS/sha(b)
    if not p.exists():p.write_bytes(b)
    return str(p.relative_to(ROOT))
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k):return None
class Budget:
    def __init__(s,n=MAX_REQ):s.left=n
def fetch(url,budget,allow=ALLOW,timeout=TIMEOUT,method="GET",https_only=True):
    from urllib.parse import urlparse
    u=urlparse(url);t=now()
    out={"url":url,"ts":t,"method":method,"allowlisted":u.hostname in allow and (u.scheme=="https" or not https_only)}
    if not out["allowlisted"]:return {**out,"error":"NOT_ALLOWLISTED","status":None}
    if budget.left<=0:return {**out,"error":"REQUEST_LIMIT","status":None}
    budget.left-=1;t0=time.monotonic()
    try:
        op=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
        with op.open(urllib.request.Request(url,method=method,headers={"User-Agent":"antigense-agent-011"}),timeout=timeout) as r:
            body=r.read(MAX_BYTES+1);out.update(status=r.status,content_type=r.headers.get("content-type"))
    except urllib.error.HTTPError as e:body=b"";out.update(status=e.code,error="HTTP_%d"%e.code)
    except Exception as e:body=b"";out.update(status=None,error=type(e).__name__)
    out.update(bytes=len(body),truncated=len(body)>MAX_BYTES,sha256=sha(body),elapsed_ms=round((time.monotonic()-t0)*1000,1));out["_body"]=body
    return out
def pub(f):return {k:v for k,v in f.items() if k!="_body"}
class Run:
    def __init__(s,base):s.base=Path(base);s.id="run011-"+sha(now().encode())[:12];s.seq=0;s.facts={};s.results=[]
    def step(s,name,state,details,checks,body=None):
        s.seq+=1
        o={"name":name,"state":state,"checks":{k:bool(v) for k,v in checks.items()},"details":details,
           "occurrence":{"run_id":s.id,"seq":s.seq,"ts":now()}}
        if body is not None:o["source"]={"sha256":sha(body),"bytes":len(body),"blob":blob(body)}
        r=C.append_step(s.base,o);s.results.append({"name":name,"state":state,"admission":None,"mmr_root":r["mmr_root"],"verified":r["verified"]})
        print("%02d %-34s %-10s mmr=%s verified=%s"%(s.seq,name,state,r["mmr_root"][:12],r["verified"]),flush=True);return r
def freeze(base=BASE,kit=ROOT):
    base=Path(base)
    if (base/"genesis.json").exists():
        if not artifacts_ok(base,kit):raise SystemExit("governed bytes changed; create a successor freeze (new directory)")
        return C.read(base/"genesis.json")
    base.mkdir(parents=True,exist_ok=True)
    nodes=[{"id":"project:antigense-011","type":"Project","scope":"Antigense 011 agent run; successor of 009R2; NOT hardware or portfolio","state":"PROPOSED"},{"id":"group:governed","type":"Group"}]
    edges=[{"source":"project:antigense-011","target":"group:governed","predicate":"CONTAINS"}]
    for n in KIT:
        b=(Path(kit)/n).read_bytes();nodes.append({"id":"artifact:"+n,"type":"Artifact","sha256":sha(b),"bytes":len(b),"relative_path":n})
        edges.append({"source":"group:governed","target":"artifact:"+n,"predicate":"CONTAINS"})
    contract=C.read(Path(kit)/"CUSTODY_CONTRACT_011.json")
    ic={"anticube":{"identity":"UNKNOWN","safety":"UNKNOWN","self_safe":None},"checks":{"artifact_hashes_calculated":True,"edge_endpoints_exist":all(e["source"] in {n["id"] for n in nodes} and e["target"] in {n["id"] for n in nodes} for e in edges)}}
    graph={"schema":"cyberhack.frozen-fractal-graph.v011","nodes":nodes,"edges":edges,"contract":contract,"PARENT":"009R2","initial_classification":ic,"g_star_reference":C.diagnostic([])}
    leaves=[{"type":"initial_classification","value":ic},{"type":"g_star_reference","value":graph["g_star_reference"]},{"type":"graph_contract","value":contract}]+[{"type":"node","value":x} for x in nodes]+[{"type":"edge","value":x} for x in edges]
    tree=C.merkle(leaves)
    g={"graph":graph,"commitment":tree,"project_root":tree["root"],"ID":"fco:sha256:"+tree["root"],"SIGNATURE":"NOT_SIGNED","g_star_reference":C.diagnostic([]),"scope":nodes[0]["scope"]}
    C.write_new(base/"genesis.json",g)
    row={"event_index":1,"project_root":g["project_root"],"event_hash":C.digest(C.canonical(g)),"fco_id":g["ID"],"merkle_root":tree["root"],"kind":"PROJECT_FREEZE"}
    m=C.mmr([row]);assert m["root"]==C.independent_mmr_root([row])
    C.write_new(base/"prefix-000001.json",m)
    with (base/"ledger.jsonl").open("x") as f:f.write(json.dumps(row,sort_keys=True)+"\n")
    return g
def artifacts_ok(base,kit=ROOT):
    g=C.read(Path(base)/"genesis.json");ns=[n for n in g["graph"]["nodes"] if n["type"]=="Artifact"]
    return {n["relative_path"] for n in ns}==set(KIT) and all(sha((Path(kit)/n["relative_path"]).read_bytes())==n["sha256"] for n in ns)
def verify(base=BASE,kit=ROOT,expected=None):
    r=C.verify(base,expected);r["artifact_bytes_match"]=artifacts_ok(base,kit) if r.get("project_root") else False
    r["PASS"]=r["PASS"] and r["artifact_bytes_match"];r["YES_NO"]="YES" if r["PASS"] else "NO";return r
# ---- sponsor/local operations
def semgrep(target,rules=ROOT/"rules/fallback.yaml"):
    exe=ROOT/".venv/bin/semgrep"
    if not exe.exists():return {"state":"NOT_TESTED","reason":"semgrep executable missing"}
    env={k:v for k,v in os.environ.items() if k not in("SEMGREP_APP_TOKEN",)};env.update(SEMGREP_SEND_METRICS="off",SEMGREP_ENABLE_VERSION_CHECK="0")
    cmd=[str(exe),"scan","--config",str(rules),"--json","--metrics=off","--disable-version-check","--quiet",str(target)]
    ver=subprocess.run([str(exe),"--version"],capture_output=True,text=True,env=env,timeout=60).stdout.strip()
    p=subprocess.run(cmd,capture_output=True,env=env,timeout=180);j=json.loads(p.stdout or b"{}")
    return {"state":"OBSERVED","cmd":[Path(c).name if i in(0,) else str(Path(c).relative_to(ROOT)) if str(c).startswith(str(ROOT)) else c for i,c in enumerate(cmd)],"version":ver,"exit":p.returncode,
            "findings":[{"check_id":x["check_id"],"line":x["start"]["line"]} for x in j.get("results",[])],"errors":len(j.get("errors",[])),
            "rule_sha256":sha(Path(rules).read_bytes()),"target_sha256":sha(Path(target).read_bytes()),"raw":p.stdout}
def regress(path):
    ns={};exec(compile(Path(path).read_text(),str(path),"exec"),ns);f=ns["authorize"]
    return {"healthy_auth":f(True,True),"healthy_unauth":f(False,True),"unhealthy_auth":f(True,False),"unhealthy_unauth":f(False,False)}
ADVICE_KEYS={"summary","root_cause","fix","risk"}
def validate_advice(text):
    try:j=json.loads(text)
    except Exception:return False,"not JSON"
    if not isinstance(j,dict) or not ADVICE_KEYS<=set(j) or not all(isinstance(j[k],str) and j[k] for k in ADVICE_KEYS):return False,"schema"
    return True,"ok"
def akash(facts):
    key=os.environ.get("AKASHML_API_KEY");model=os.environ.get("AKASHML_MODEL");base=os.environ.get("AKASHML_BASE_URL","https://api.akashml.com/v1")
    if not key or not model:return {"state":"NOT_TESTED","reason":"AKASHML_API_KEY/AKASHML_MODEL not set","credential_present":bool(key),"model_set":bool(model)}
    if not base.startswith("https://api.akashml.com/"):return {"state":"NOT_TESTED","reason":"base URL not the documented AkashML host"}
    body={"model":model,"messages":[{"role":"system","content":"Return JSON only with string keys summary,root_cause,fix,risk."},{"role":"user","content":json.dumps(facts,sort_keys=True)}],"temperature":0,"max_tokens":600}
    rb=json.dumps(body,sort_keys=True).encode();t=time.monotonic()
    req=urllib.request.Request(base.rstrip("/")+"/chat/completions",data=rb,headers={"Content-Type":"application/json","Authorization":"Bearer "+key})
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect()).open(req,timeout=60) as r:raw=r.read();hdr=r.headers.get("Inference-Id");code=r.status
    except Exception as e:return {"state":"FAILED","reason":type(e).__name__,"http":getattr(e,"code",None)}
    j=json.loads(raw);text=j["choices"][0]["message"]["content"];ok,why=validate_advice(text)
    return {"state":"OBSERVED","http":code,"inference_id":hdr,"model_returned":j.get("model"),"usage":j.get("usage"),"elapsed_ms":round((time.monotonic()-t)*1000,1),
            "request_sha256":sha(rb),"response_sha256":sha(raw),"schema_valid":ok,"schema_note":why,"raw":raw,
            "ceiling":"managed AkashML inference only; no GPU lease, attestation, confidentiality or private deployment established"}
def pi():
    cfg=os.environ.get("PI_SECURITY_API_URL");tok=os.environ.get("PI_SECURITY_API_TOKEN")
    return {"state":"NOT_TESTED","reason":"no sponsor-supported public API/CLI/sandbox identified (pi.security exposes demo request only); no credentials/interface supplied","interface_configured":bool(cfg),"token_present":bool(tok),"substitutes_rejected":["pi.dev","Pi cryptocurrency tooling","human gate","prepared packet"]}
def status_artifact(run,facts):
    return {"schema":"antigense.defense-status.v011","run_id":run.id,"generated_utc":now(),
      "scope":"Software-injected byte fault in a disposable demo worker; sanitized teaching fixture; no physical hardware fault.",
      "monitor":facts["monitor"],"semgrep":facts["semgrep"],"akash":facts["akash"],"pi":facts["pi"],
      "custody":{"successor_project_root":facts["root"],"mmr_root_before_publication":facts["mmr"],"leaf_count_before_publication":facts["leaves"],"signature":"NOT_SIGNED","predecessor_mmr_root":"26bdf817ac6a91e8b700ac57a447f2054b0bd633e134ccb8c50d5891ae6557f1"},
      "claim_ceiling":"Hash integrity is not truth, safety or causality. Zero findings means only this scan found none. G*/delta-G* unvalidated.","human_review":"Codex-delegated rehearsal approval in 009; identity UNVERIFIED"}
def deploy():
    p=subprocess.run(["vercel","deploy","--prod","--yes"],cwd=ROOT,capture_output=True,text=True,timeout=300)
    return p.returncode,(p.stdout+p.stderr)[-1500:]
def selftests(run):
    # failure-mode checks against the real fetch/validator/custody code
    b=Budget(3);f=fetch("https://example.invalid/",b)
    run.step("neg_non_allowlisted_url","OBSERVED",{"result":pub(f)},{"refused_not_allowlisted":f["error"]=="NOT_ALLOWLISTED","no_request_made":b.left==3})
    f=fetch("http://127.0.0.1:9/",Budget(2),allow={"127.0.0.1"},https_only=False,timeout=2)
    run.step("neg_unreachable_source","OBSERVED",{"result":pub(f)},{"error_recorded":f["status"] is None and bool(f.get("error")),"no_false_success":f["status"]!=200})
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(s):time.sleep(3)
        def log_message(*a):pass
    srv=http.server.HTTPServer(("127.0.0.1",0),H);threading.Thread(target=srv.serve_forever,daemon=True).start()
    f=fetch("http://127.0.0.1:%d/"%srv.server_port,Budget(2),allow={"127.0.0.1"},https_only=False,timeout=0.5);srv.shutdown()
    run.step("neg_timeout","OBSERVED",{"result":pub(f)},{"timeout_recorded":f["status"] is None and f.get("error") in("TimeoutError","timeout","URLError"),"bounded":f["elapsed_ms"]<2500})
    b=Budget(1);fetch("http://127.0.0.1:9/",b,allow={"127.0.0.1"},https_only=False,timeout=1);g=fetch("http://127.0.0.1:9/",b,allow={"127.0.0.1"},https_only=False)
    run.step("neg_request_limit","OBSERVED",{"second":pub(g)},{"limit_enforced":g.get("error")=="REQUEST_LIMIT"})
    saved={k:os.environ.pop(k,None) for k in("AKASHML_API_KEY","AKASHML_MODEL")}
    a=akash({"x":1});[os.environ.__setitem__(k,v) for k,v in saved.items() if v]
    run.step("neg_missing_akash_credentials","OBSERVED",{"result":a},{"not_tested_not_success":a["state"]=="NOT_TESTED"})
    bad=[validate_advice(x)[0] for x in("not json","[]",'{"summary":"a"}','{"summary":"a","root_cause":"b","fix":"","risk":"c"}')]
    good=validate_advice('{"summary":"a","root_cause":"b","fix":"c","risk":"d"}')[0]
    run.step("neg_malformed_ai_advice","OBSERVED",{"synthetic_inputs":4,"note":"synthetic validator inputs, not Akash output"},{"all_malformed_rejected":not any(bad),"wellformed_accepted":good})
def tamper_tests(run):
    import shutil;res={}
    tmp=Path(tempfile.mkdtemp());d=tmp/"c";shutil.copytree(BASE,d)
    def v():return verify(d)["PASS"]
    base_ok=v()
    p=sorted(d.glob("step-*.json"))[0];o=json.loads(p.read_text());o["classification"]["anticube"]["safety"]="SAFE";p.write_text(json.dumps(o,sort_keys=True,indent=2));res["classification"]=not v();shutil.rmtree(d);shutil.copytree(BASE,d)
    L=(d/"ledger.jsonl").read_text().splitlines();L[1],L[2]=L[2],L[1];(d/"ledger.jsonl").write_text("\n".join(L)+"\n");res["leaf_order"]=not v();shutil.rmtree(d);shutil.copytree(BASE,d)
    g=json.loads((d/"genesis.json").read_text());g["graph"]["nodes"][2]["sha256"]="0"*64;(d/"genesis.json").write_text(json.dumps(g,sort_keys=True,indent=2));res["artifact_record"]=not v();shutil.rmtree(d);shutil.copytree(BASE,d)
    pj=sorted(d.glob("prefix-*.json"))[-1];m=json.loads(pj.read_text());m["root"]="f"*64;pj.write_text(json.dumps(m,sort_keys=True,indent=2));res["root"]=not v();shutil.rmtree(d);shutil.copytree(BASE,d)
    shutil.rmtree(tmp)
    run.step("neg_tamper_detection","OBSERVED",{"pristine_copy_verified":base_ok,"note":"tampering applied to a temp copy, never the real directory"},{"pristine_copy_passes":base_ok,**{"detected_"+k:v for k,v in res.items()}})
def do_run(publish):
    if not (BASE/"genesis.json").exists():raise SystemExit("run freeze first")
    if not artifacts_ok(BASE):raise SystemExit("governed artifacts changed since freeze; make a successor freeze")
    run=Run(BASE);facts={};print("START",run.id)
    g=C.read(BASE/"genesis.json")
    run.step("preflight","OBSERVED",{"allowlist":sorted(ALLOW),"max_requests":MAX_REQ,"timeout_s":TIMEOUT,"max_bytes":MAX_BYTES,"credentials_present":{"AKASHML_API_KEY":bool(os.environ.get("AKASHML_API_KEY")),"PI_SECURITY_API_TOKEN":bool(os.environ.get("PI_SECURITY_API_TOKEN")),"publish_authorization_supplied":bool(publish)},"fault":"SOFTWARE_INJECTED_ONLY"},{"allowlist_nonempty":True,"frozen_artifacts_match":artifacts_ok(BASE),"credential_values_recorded":False})
    selftests(run)
    bud=Budget();mon=[]
    for path in("/","/demo.mp4","/data/run.json"):
        f=fetch("https://"+SITE+path,bud);mon.append(pub(f))
        run.step("monitor"+path.replace("/","_"),"OBSERVED" if f["status"]==200 else "FAILED",{"result":pub(f)},{"http_200":f["status"]==200,"not_truncated":not f["truncated"],"video_hash_matches_release":(f["sha256"]=="c2f18156deecc4c8b51591b28667f5e62dbd492d27aa70dd38040bdfe3deb02c") if path=="/demo.mp4" else True},f["_body"] if f["status"]==200 and path!="/demo.mp4" else None)
    facts["monitor"]=[{k:m.get(k) for k in("url","ts","status","bytes","sha256")} for m in mon]
    sc={}
    for name in("before","after"):
        s=semgrep(ROOT/("fixtures/%s.py"%name));rg=regress(ROOT/("fixtures/%s.py"%name));sc[name]=(s,rg)
        raw=s.pop("raw",b"")
        run.step("semgrep_"+name,s["state"],{**s,"regression":rg},{"scanner_executed":s["state"]=="OBSERVED","no_scanner_errors":s.get("errors")==0,"exit_recorded":s.get("exit") is not None,"finding_present":len(s.get("findings",[]))>0},raw)
    b,a=sc["before"],sc["after"]
    run.step("semgrep_regression_matrix","OBSERVED",{"before":b[1],"after":a[1]},{"before_fails_open":b[1]["unhealthy_unauth"] is True,"after_denies_unauthorized":a[1]["unhealthy_unauth"] is False and a[1]["healthy_unauth"] is False,"after_preserves_healthy_authorized":a[1]["healthy_auth"] is True,"before_findings_1":len(b[0]["findings"])==1,"after_findings_0":len(a[0]["findings"])==0})
    facts["semgrep"]={"version":b[0]["version"],"before_findings":len(b[0]["findings"]),"after_findings":len(a[0]["findings"]),"rule_sha256":b[0]["rule_sha256"],"note":"custom teaching rule; zero findings = this scan only"}
    ak=akash({"finding":b[0]["findings"],"fixture_before_sha256":b[0]["target_sha256"],"fixture_after_sha256":a[0]["target_sha256"]});raw=ak.pop("raw",None)
    run.step("akash_inference",ak["state"],ak,{"actual_akash_call":ak["state"]=="OBSERVED","gpu_lease_established":False,"attestation_verified":False,"advice_schema_valid":bool(ak.get("schema_valid"))},raw)
    facts["akash"]={"state":ak["state"],"model":ak.get("model_returned"),"inference_id":ak.get("inference_id"),"ceiling":"managed inference only" if ak["state"]=="OBSERVED" else "NOT_TESTED: no credentials supplied"}
    pr=pi();run.step("pi_security_review",pr["state"],pr,{"actual_pi_job":False,"substitute_used":False})
    facts["pi"]={"state":pr["state"],"reason":"no sponsor interface/credentials"}
    tamper_tests(run)
    cur=verify(BASE);facts.update(root=g["project_root"],mmr=cur["mmr_root"],leaves=cur["leaf_count"])
    art=json.dumps(status_artifact(run,facts),sort_keys=True,indent=2).encode()+b"\n";h=sha(art)
    # publication authorization tests
    def authorized(token):return token is not None and token==g["project_root"]
    run.step("neg_publication_authorization","OBSERVED",{"artifact_sha256":h,"binding":"successor project_root"},{"missing_authorization_refused":not authorized(None),"stale_binding_refused":not authorized("0"*64),"exact_binding_accepted":authorized(g["project_root"])})
    if not publish:
        run.step("publication","NOT_TESTED",{"reason":"no --publish authorization supplied","artifact_sha256":h},{"published":False});print("ARTIFACT_SHA256",h);STATUS_PATH.write_bytes(art);return
    if not authorized(publish):
        run.step("publication","FAILED",{"reason":"stale/mismatched review binding","expected_binding":"successor project_root","supplied_matches":False},{"published":False,"binding_matches":False});sys.exit("stale binding")
    STATUS_PATH.write_bytes(art);code,log=deploy()
    run.step("publication","OBSERVED" if code==0 else "FAILED",{"deploy_exit":code,"deploy_log_tail":log,"path":str(STATUS_PATH.relative_to(ROOT)),"url":STATUS_URL,"artifact_sha256":h,"bytes":len(art)},{"deploy_ok":code==0,"authorization_bound_to_bytes":True},art)
    ok=False
    for i in range(6):
        f=fetch(STATUS_URL,Budget(1));time.sleep(0 if f["status"]==200 and f["sha256"]==h else 5)
        if f["status"]==200 and f["sha256"]==h:ok=True;break
    declared=json.loads(f["_body"]) if f["status"]==200 else {}
    run.step("publication_readback","OBSERVED" if ok else "FAILED",{"result":pub(f),"expected_sha256":h,"attempts":i+1},{"bytes_match":f["sha256"]==h,"declared_run_matches":declared.get("run_id")==run.id,"declared_state_matches":declared.get("custody",{}).get("mmr_root_before_publication")==facts["mmr"],"http_200":f["status"]==200},f["_body"] if f["status"]==200 else None)
    print("PUBLISHED",STATUS_URL,h)
def main():
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["freeze","run","verify"]);p.add_argument("--publish");p.add_argument("--directory",default=str(BASE));a=p.parse_args()
    if a.cmd=="freeze":g=freeze(Path(a.directory));print("project_root",g["project_root"])
    elif a.cmd=="run":do_run(a.publish)
    else:
        r=verify(Path(a.directory));print(json.dumps(r,indent=2,sort_keys=True));sys.exit(0 if r["PASS"] else 1)
if __name__=="__main__":main()
