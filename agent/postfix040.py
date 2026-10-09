#!/usr/bin/env python3
"""Post-fix verification: does current agent011.regress still execute attacker-controlled fixture code? Fixture-only, harmless marker.
Also re-checks F2 (cascade.auth) on the same tree. Usage: postfix040.py <out.json>"""
import hashlib,importlib.util,json,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/"src"))
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=load(R/"agent/agent011.py","a11");S=load(R/"agent/safe_eval016.py","s16");CAS=load(R/"src/cascade.py","cas")
T=Path(tempfile.mkdtemp());mark=T/"M";mal=T/"mal.py";mal.write_text('open(%r,"w").write("x")\ndef authorize(authorized, worker_healthy):\n    return authorized\n'%str(mark))
out={"scope":"FIXTURE_ONLY","agent011_sha256":hashlib.sha256((R/"agent/agent011.py").read_bytes()).hexdigest()}
r=A.regress(mal);out["agent011_regress_on_malicious_fixture"]={"result":r,"side_effect_executed":mark.exists()};mark.unlink(missing_ok=True)
out["agent011_regress_matches_safe_eval_on_real_fixtures"]=all(A.regress(R/("fixtures/%s.py"%n))==S.regress(R/("fixtures/%s.py"%n)) for n in("before","after"))
exp={"healthy_auth":True,"healthy_unauth":False,"unhealthy_auth":False,"unhealthy_unauth":False}
out["after_fixture_matches_declared_policy"]=A.regress(R/"fixtures/after.py")==exp
(T/"fixtures").mkdir();(T/"fixtures/before.py").write_text(mal.read_text());real=CAS.ROOT;CAS.ROOT=T;CAS.auth("before",True,True);CAS.ROOT=real
out["cascade_auth_exec_still_runs_fixture_code"]=mark.exists()
out["F2a_resolved"]=not out["agent011_regress_on_malicious_fixture"]["side_effect_executed"] and out["agent011_regress_matches_safe_eval_on_real_fixtures"]
out["F2_resolved"]=not out["cascade_auth_exec_still_runs_fixture_code"]
json.dump(out,open(sys.argv[1],"w"),indent=1,sort_keys=True);print(json.dumps({k:v for k,v in out.items() if k!="agent011_regress_on_malicious_fixture"},indent=1))
