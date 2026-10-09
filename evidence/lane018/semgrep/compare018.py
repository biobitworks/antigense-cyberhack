#!/usr/bin/env python3
"""Fixture-only controlled comparison. The 'malicious' fixture writes a harmless marker file in a temp dir."""
import importlib.util,json,sys,tempfile,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/"agent"))
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=load(R/"agent/agent011.py","a11");S=load(R/"agent/safe_eval016.py","s16")
T=Path(tempfile.mkdtemp());mark=T/"PWNED"
fx={"healthy_before":R/"fixtures/before.py","healthy_after":R/"fixtures/after.py"}
mal=T/"mal.py";mal.write_text('open(%r,"w").write("x")\ndef authorize(authorized, worker_healthy):\n    return authorized\n'%str(mark))
deny=T/"deny.py";deny.write_text('def authorize(authorized, worker_healthy):\n    return False\n')
def attempt(f,p):
    try:return f(p)
    except Exception as e:return {"error":type(e).__name__}
out={"scope":"FIXTURE_ONLY; no general safety claim","cases":{}}
for k,p in fx.items():out["cases"][k]={"exec_path":attempt(A.regress,p),"safe_path":attempt(S.regress,p)}
out["cases"]["healthy_equivalence"]=out["cases"]["healthy_before"]["exec_path"]==out["cases"]["healthy_before"]["safe_path"] and out["cases"]["healthy_after"]["exec_path"]==out["cases"]["healthy_after"]["safe_path"]
r1=attempt(A.regress,mal);out["cases"]["malicious_exec_path"]={"result":r1,"side_effect_executed":mark.exists()}
ran=mark.exists();mark.unlink(missing_ok=True)
r2=attempt(S.regress,mal);out["cases"]["malicious_safe_path"]={"result":r2,"side_effect_executed":mark.exists()}
# negative control: deny-everything repair
d=S.regress(deny);expect={"healthy_auth":True,"healthy_unauth":False,"unhealthy_auth":False,"unhealthy_unauth":False}  # declared policy: fail closed when worker unhealthy; legitimate work = healthy+authorized
out["negative_control_deny_all"]={"outputs":d,"blocks_unauthorized":not d["healthy_unauth"] and not d["unhealthy_unauth"],"legitimate_work_preserved":d["healthy_auth"],"ACCEPTED":False,"reason":"denies healthy authorized request; rejected as negative control"}
a=S.regress(fx["healthy_after"]);out["pinned_repair_after"]={"outputs":a,"matches_expected":a==expect,"blocks_unauthorized":not a["healthy_unauth"] and not a["unhealthy_unauth"],"legitimate_work_preserved":a["healthy_auth"]}
out["conclusion"]="exec() path runs attacker-controlled fixture code: %s; exec-free path does not execute module-level code (AST-evaluates authorize() only): %s"%(ran,not mark.exists())
json.dump(out,open(Path(__file__).parent/"controlled_comparison.json","w"),indent=1,sort_keys=True);print(json.dumps(out,indent=1,sort_keys=True)[:2500])
