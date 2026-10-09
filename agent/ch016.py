#!/usr/bin/env python3
"""ClickHouse projection 016 (015 + .env + normalized hashing + own-code Semgrep). Usage: freeze | run | verify  (env CH015_TRANSPORT=local and CH015_BASE are for dry-runs only)"""
import sys as _s;_s.path.insert(0,str(__import__("pathlib").Path(__file__).resolve().parent))
import base64,getpass,hashlib,importlib.util,json,os,subprocess,sys,tempfile,time,urllib.parse,urllib.request,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location("agent011",ROOT/"agent/agent011.py");A=importlib.util.module_from_spec(s);s.loader.exec_module(A)
C=A.C;SRC=ROOT/"evidence/successor_011";BASE=Path(os.environ.get("CH015_BASE",ROOT/"evidence/successor_016"));TABLE="antigense_events_016"
A.KIT=A.KIT+["agent/ch016.py","agent/safe_eval016.py","docs/ADDENDUM_016.md"];A.BASE=BASE
sha=A.sha;LOCAL=os.environ.get("CH015_TRANSPORT")=="local"
COLS=[("occurrence_id","String"),("run_id","String"),("seq","UInt16"),("event_index","UInt32"),("fco_id","String"),("name","String"),("state","String"),("admission","String"),("ts","String"),("source_sha256","Nullable(String)"),("step_merkle_root","String"),("mmr_prefix_root","String"),("checks_true","UInt16"),("checks_false","UInt16"),("http_status","Nullable(UInt16)"),("elapsed_ms","Nullable(Float64)")]
DDL="CREATE TABLE IF NOT EXISTS %s(%s) ENGINE=ReplacingMergeTree ORDER BY occurrence_id"%(TABLE,",".join("%s %s"%c for c in COLS))
def load_env():
    p=ROOT/".env"
    if p.exists():
        for l in p.read_text().splitlines():
            k,_,v=l.partition("=")
            if k.strip() in("CLICKHOUSE_HOST","CLICKHOUSE_USER","CLICKHOUSE_PASSWORD") and v.strip() and not os.environ.get(k.strip()):os.environ[k.strip()]=v.strip()
def nf(x):
    if isinstance(x,float) and x==int(x):return int(x)
    return x
def normed(rows):return [{k:nf(v) for k,v in r.items()} for r in rows]
def canonical_rows():
    out=[]
    for f in sorted(SRC.glob("step-*.json")):
        o=json.loads(f.read_text());ob=o["observation"];i=int(f.stem.split("-")[1]);d=ob.get("details") or {};res=d.get("result") or {}
        c=ob["checks"];oc=ob["occurrence"]
        out.append({"occurrence_id":"%s:%d"%(oc["run_id"],oc["seq"]),"run_id":oc["run_id"],"seq":oc["seq"],"event_index":i,"fco_id":o["fco_id"],"name":ob["name"],"state":ob["state"],"admission":o["classification"]["custody_admission"],"ts":oc["ts"],
          "source_sha256":(ob.get("source") or {}).get("sha256"),"step_merkle_root":o["commitment"]["root"],"mmr_prefix_root":json.loads((SRC/("prefix-%06d.json"%i)).read_text())["root"],
          "checks_true":sum(c.values()),"checks_false":len(c)-sum(c.values()),"http_status":res.get("status"),"elapsed_ms":res.get("elapsed_ms")})
    return out
class CH:
    def __init__(s):
        s.host=os.environ.get("CLICKHOUSE_HOST","");s.user=os.environ.get("CLICKHOUSE_USER","default");s.pw=os.environ.get("CLICKHOUSE_PASSWORD","")
        s.tmp=tempfile.mkdtemp() if LOCAL else None
    def ready(s):return LOCAL or bool(s.host and s.pw)
    def q(s,sql,data=b""):
        qid="ag015-"+uuid.uuid4().hex[:16];t=time.monotonic()
        if LOCAL:
            p=subprocess.run(["clickhouse","local","--path",s.tmp,"--format","JSONEachRow","--query",sql],input=data.decode() if data else None,capture_output=True,text=True,timeout=120)
            if p.returncode:raise RuntimeError("local:"+p.stderr[-200:])
            return p.stdout,{"query_id":qid,"ms":round((time.monotonic()-t)*1000,1),"http":None}
        url="https://%s:8443/?query_id=%s&%s"%(s.host,qid,urllib.parse.urlencode({"default_format":"JSONEachRow"}))
        if data:url="https://%s:8443/?query_id=%s&query=%s"%(s.host,qid,urllib.parse.quote(sql));body=data
        else:body=sql.encode()
        req=urllib.request.Request(url,data=body,headers={"Authorization":"Basic "+base64.b64encode((s.user+":"+s.pw).encode()).decode()})
        with urllib.request.build_opener(urllib.request.ProxyHandler({}),A.NoRedirect()).open(req,timeout=30) as r:
            raw=r.read(5_000_000).decode();return raw,{"query_id":r.headers.get("X-ClickHouse-Query-Id") or qid,"ms":round((time.monotonic()-t)*1000,1),"http":r.status}
def jl(raw):return [json.loads(x) for x in raw.splitlines() if x]
def own_code_steps(R):
    import safe_eval016 as S
    def scan(files):
        exe=ROOT/".venv/bin/semgrep";env={k:v for k,v in os.environ.items() if k not in("SEMGREP_APP_TOKEN","CLICKHOUSE_PASSWORD")};env.update(SEMGREP_SEND_METRICS="off")
        cmd=[str(exe),"scan","--config","p/python","--config","p/security-audit","--metrics=off","--disable-version-check","--json","--quiet"]+[str(ROOT/f) for f in files]
        ver=subprocess.run([str(exe),"--version"],capture_output=True,text=True,env=env,timeout=60).stdout.strip()
        t=time.monotonic();p=subprocess.run(cmd,capture_output=True,env=env,timeout=300);j=json.loads(p.stdout or b"{}")
        return {"version":ver,"configs":["p/python","p/security-audit"],"rules_retained":False,"files":{f:sha((ROOT/f).read_bytes()) for f in files},"exit":p.returncode,"elapsed_s":round(time.monotonic()-t,1),
          "findings":[{"check_id":x["check_id"],"path":str(Path(x["path"]).relative_to(ROOT)),"line":x["start"]["line"],"severity":x["extra"]["severity"]} for x in j.get("results",[])],"errors":len(j.get("errors",[]))},p.stdout
    d,raw=scan(["agent/agent011.py","agent/ch015.py"])
    R.step("own_code_scan_before","OBSERVED",d,{"scanner_executed":d["errors"]==0,"finding_present":len(d["findings"])>0,"exec_detected_in_agent011":any(f["check_id"].endswith("exec-detected") and f["path"]=="agent/agent011.py" for f in d["findings"])},raw)
    old={n:A.regress(ROOT/("fixtures/%s.py"%n)) for n in("before","after")};new={n:S.regress(ROOT/("fixtures/%s.py"%n)) for n in("before","after")}
    R.step("safe_eval_equivalence","OBSERVED",{"exec_based":old,"ast_based":new},{"behavior_identical_on_both_fixtures":old==new,"before_fails_open":new["before"]["unhealthy_unauth"] is True,"after_fails_closed":new["after"]["unhealthy_unauth"] is False and new["after"]["healthy_auth"] is True})
    d2,raw2=scan(["agent/safe_eval016.py","agent/ch016.py"])
    R.step("own_code_scan_after","OBSERVED",d2,{"scanner_executed":d2["errors"]==0,"zero_findings_in_new_code":len(d2["findings"])==0,"scope_note_this_scan_only":True},raw2)
def run():
    load_env()
    if not (BASE/"genesis.json").exists():raise SystemExit("freeze first")
    if not A.artifacts_ok(BASE):raise SystemExit("governed bytes changed; successor freeze needed")
    R=A.Run(BASE);db=CH()
    if not LOCAL and not db.pw and sys.stdin.isatty():
        db.host=db.host or input("ClickHouse host: ").strip();db.pw=getpass.getpass("ClickHouse password (hidden): ")
    rows=normed(canonical_rows())
    own_code_steps(R)
    R.step("ch015_preflight","OBSERVED" if db.ready() else "NOT_TESTED",{"canonical_rows":len(rows),"canonical_rows_sha256":sha("\n".join(json.dumps(r,sort_keys=True) for r in rows).encode()),"transport":"local-dryrun" if LOCAL else "https:8443 TLS-verified","host_sha256":sha(db.host.encode()) if db.host else None,"credentials_present":db.ready(),"distinct_occurrences":len({r["occurrence_id"] for r in rows})},{"credentials_present":db.ready(),"occurrence_ids_unique":len({r["occurrence_id"] for r in rows})==len(rows),"tls_verification_disabled":False})
    if not db.ready():return
    def attempt(name,sql,data=b""):
        try:raw,m=db.q(sql,data);return raw,m,None
        except Exception as e:
            R.step(name,"FAILED",{"sql":sql[:400],"error_type":type(e).__name__,"http_code":getattr(e,"code",None),"note":"server body not retained"},{"succeeded":False});return None,None,e
    raw,m,e=attempt("ch015_version","SELECT version() AS v")
    if e:return
    ver=jl(raw)[0]["v"];R.step("ch015_version","OBSERVED",{"version":ver,"sql":"SELECT version() AS v",**m},{"ok":True})
    raw,m,e=attempt("ch015_schema",DDL)
    if e:return
    R.step("ch015_schema","OBSERVED",{"sql":DDL,"ddl_sha256":sha(DDL.encode()),**m},{"table_ready":True})
    BATCH=25
    def ingest(label):
        tot=0;ms=0;ids=[]
        for i in range(0,len(rows),BATCH):
            b=rows[i:i+BATCH];data=("\n".join(json.dumps(r,sort_keys=True) for r in b)).encode()
            raw,m,e=attempt("ch015_ingest_"+label,"INSERT INTO %s FORMAT JSONEachRow"%TABLE,data)
            if e:return None
            tot+=len(b);ms+=m["ms"];ids.append(m["query_id"])
        R.step("ch015_ingest_"+label,"OBSERVED",{"rows_sent":tot,"batches":len(ids),"batch_size":BATCH,"total_ms":round(ms,1),"query_ids":ids},{"all_batches_ok":True,"rows_sent_matches_canonical":tot==len(rows)});return True
    if not ingest("initial"):return
    if not ingest("replay"):return
    Q={"timeline":"SELECT seq,name,state,admission,ts,http_status,elapsed_ms FROM %s FINAL WHERE run_id=(SELECT run_id FROM %s FINAL WHERE name='publication_readback' AND state='OBSERVED' ORDER BY event_index DESC LIMIT 1) ORDER BY seq"%(TABLE,TABLE),
       "state_counts":"SELECT state,count() AS n FROM %s FINAL GROUP BY state ORDER BY state"%TABLE,
       "sponsor_status":"SELECT name,count() AS n,countIf(state='NOT_TESTED') AS not_tested,countIf(state='OBSERVED') AS observed FROM %s FINAL WHERE name IN('semgrep_before','semgrep_after','akash_inference','pi_security_review') GROUP BY name ORDER BY name"%TABLE,
       "monitor_latency":"SELECT name,count() AS n,min(elapsed_ms) AS min_ms,max(elapsed_ms) AS max_ms FROM %s FINAL WHERE name LIKE 'monitor_%%' AND elapsed_ms IS NOT NULL GROUP BY name ORDER BY name"%TABLE}
    res={}
    for k,sql in Q.items():
        raw,m,e=attempt("ch015_query_"+k,sql)
        if e:return
        rr=jl(raw);res[k]=rr
        R.step("ch015_query_"+k,"OBSERVED",{"sql":sql,"rows":len(rr),"result_sha256":sha(json.dumps(rr,sort_keys=True).encode()),"result":rr if len(rr)<=60 else "see readback",**m},{"returned_rows":len(rr)>0})
    R.step("ch015_fault_to_response","NOT_TESTED",{"reason":"no fault-event timestamp in canonical 011 records; interval NOT_COMPUTED"},{"interval_computed":False})
    cols=",".join(c for c,_ in COLS);sql="SELECT %s FROM %s FINAL ORDER BY occurrence_id FORMAT JSONEachRow"%(cols,TABLE)
    raw,m,e=attempt("ch015_readback",sql.replace(" FORMAT JSONEachRow",""))
    if e:return
    back=normed(jl(raw));cmap={r["occurrence_id"]:r for r in rows};bmap={r["occurrence_id"]:r for r in back}
    diff=[k for k in cmap if k in bmap and {c:bmap[k][c] for c,_ in COLS}!=cmap[k]];missing=[k for k in cmap if k not in bmap];extra=[k for k in bmap if k not in cmap]
    cnt=jl(db.q("SELECT count() AS n, uniqExact(occurrence_id) AS u FROM %s FINAL"%TABLE)[0])[0]
    ok=not diff and not missing and not extra
    R.step("ch015_reconciliation","OBSERVED" if ok else "FAILED",{"sql":sql,"canonical_rows":len(rows),"readback_rows":len(back),"final_count":cnt,"mismatched":diff[:10],"missing":missing[:10],"extra":extra[:10],"readback_sha256":sha(json.dumps(back,sort_keys=True).encode()),"canonical_sha256":sha(json.dumps(sorted(rows,key=lambda r:r["occurrence_id"]),sort_keys=True).encode()),**m},
      {"ids_and_values_exact":ok,"result_hashes_equal":sha(json.dumps(sorted(back,key=lambda r:r["occurrence_id"]),sort_keys=True).encode())==sha(json.dumps(sorted(rows,key=lambda r:r["occurrence_id"]),sort_keys=True).encode()),"count_matches":len(back)==len(rows),"replay_preserved_occurrence_count":int(cnt["n"])==len(rows)==int(cnt["u"]),"canonical_records_unmodified":A.artifacts_ok(BASE)})
if __name__=="__main__":
    c=sys.argv[1] if len(sys.argv)>1 else ""
    if c=="freeze":print("project_root",A.freeze(BASE)["project_root"])
    elif c=="run":run()
    elif c=="verify":r=A.verify(BASE);print(json.dumps(r,indent=2,sort_keys=True));sys.exit(0 if r["PASS"] else 1)
    else:sys.exit("usage: freeze|run|verify")
