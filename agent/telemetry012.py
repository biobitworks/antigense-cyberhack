#!/usr/bin/env python3
"""Telemetry 012: successor_011 steps -> local ClickHouse -> aggregate queries -> successor_012 MMR. Usage: freeze | run | verify"""
import hashlib,importlib.util,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sp=importlib.util.spec_from_file_location("a011",ROOT/"agent/agent011.py");A=importlib.util.module_from_spec(sp);sp.loader.exec_module(A)
BASE=ROOT/"evidence/successor_012";SRC=ROOT/"evidence/successor_011";DB=ROOT/".runtime/ch"
A.KIT=A.KIT+["agent/telemetry012.py","docs/ADDENDUM_012.md"]
CH=shutil.which("clickhouse")
def ch(q,fmt="JSONEachRow",stdin=None):
    p=subprocess.run([CH,"local","--path",str(DB),"--format",fmt,"--query",q],input=stdin,capture_output=True,text=True,timeout=120)
    if p.returncode:raise RuntimeError(p.stderr[-400:])
    return p.stdout
def rows():
    out=[]
    for f in sorted(SRC.glob("step-*.json")):
        o=json.loads(f.read_text());ob=o["observation"];c=ob["checks"]
        d=ob.get("details",{});sg=d.get("findings")
        out.append({"event_index":int(f.stem.split("-")[1]),"run_id":ob["occurrence"]["run_id"],"seq":ob["occurrence"]["seq"],"name":ob["name"],"state":ob["state"],
          "admission":o["classification"]["custody_admission"],"checks_true":sum(c.values()),"checks_false":len(c)-sum(c.values()),
          "findings":len(sg) if isinstance(sg,list) else -1,"http_status":(d.get("result") or {}).get("status") or 0,"elapsed_ms":float((d.get("result") or {}).get("elapsed_ms") or 0)})
    return out
def run():
    if not CH:raise SystemExit("clickhouse not installed")
    if not (BASE/"genesis.json").exists():raise SystemExit("freeze first")
    if not A.artifacts_ok(BASE):raise SystemExit("governed bytes changed")
    R=rows();payload="\n".join(json.dumps(r) for r in R)
    ver=ch("SELECT version() AS v").strip()
    ch("DROP TABLE IF EXISTS steps");ch("CREATE TABLE steps(event_index UInt32,run_id String,seq UInt16,name String,state String,admission String,checks_true UInt16,checks_false UInt16,findings Int32,http_status UInt16,elapsed_ms Float64) ENGINE=MergeTree ORDER BY event_index")
    t=time.monotonic();ch("INSERT INTO steps FORMAT JSONEachRow",stdin=payload);ins=(time.monotonic()-t)*1000
    Q1="SELECT run_id,count() n,countIf(admission='ADMITTED') admitted,countIf(admission='QUARANTINED') quarantined,countIf(admission='REJECTED') rejected FROM steps GROUP BY run_id ORDER BY min(event_index)"
    Q2="SELECT name,count() n,max(findings) max_findings,countIf(state='NOT_TESTED') not_tested FROM steps WHERE name IN('semgrep_before','semgrep_after','akash_inference','pi_security_review','publication') GROUP BY name ORDER BY name"
    t=time.monotonic();r1=[json.loads(x) for x in ch(Q1).splitlines()];l1=(time.monotonic()-t)*1000
    t=time.monotonic();r2=[json.loads(x) for x in ch(Q2).splitlines()];l2=(time.monotonic()-t)*1000
    total=int(json.loads(ch("SELECT count() c FROM steps"))["c"])
    sg={r["name"]:r for r in r2}
    obs=A.Run(BASE)
    obs.step("clickhouse_local_telemetry","OBSERVED",{"clickhouse_version":ver,"mode":"local open-source binary via clickhouse local; NOT ClickHouse Cloud","source_rows_sha256":hashlib.sha256(payload.encode()).hexdigest(),"rows":len(R),
      "queries":{"q1_sha256":hashlib.sha256(Q1.encode()).hexdigest(),"q1_ms":round(l1,1),"q1_result":r1,"q2_sha256":hashlib.sha256(Q2.encode()).hexdigest(),"q2_ms":round(l2,1),"q2_result":r2},"insert_ms":round(ins,1),
      "ceiling":"tens of rows; no scale/latency-at-scale claim; telemetry derived from our own custody steps"},
      {"row_count_matches_source":total==len(R)==len(list(SRC.glob("step-*.json"))),"semgrep_before_finding_seen":sg.get("semgrep_before",{}).get("max_findings")==1,"semgrep_after_zero_seen":sg.get("semgrep_after",{}).get("max_findings")==0,"akash_not_tested_seen":sg.get("akash_inference",{}).get("not_tested",0)>0,"pi_not_tested_seen":sg.get("pi_security_review",{}).get("not_tested",0)>0,"cloud_used":False})
if __name__=="__main__":
    c=sys.argv[1] if len(sys.argv)>1 else ""
    if c=="freeze":print("project_root",A.freeze(BASE)["project_root"])
    elif c=="run":run()
    elif c=="verify":r=A.verify(BASE);print(json.dumps(r,indent=2,sort_keys=True));sys.exit(0 if r["PASS"] else 1)
    else:sys.exit("usage: freeze|run|verify")
