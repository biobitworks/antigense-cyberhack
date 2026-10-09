#!/usr/bin/env python3
"""Akash 019: Semgrep fixture finding -> actual AkashML inference -> untrusted-advice receipt. Usage: freeze | run | verify"""
import importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
s=importlib.util.spec_from_file_location("agent011",ROOT/"agent/agent011.py");A=importlib.util.module_from_spec(s);s.loader.exec_module(A)
BASE=ROOT/"evidence/successor_019";A.KIT=A.KIT+["agent/akash019.py","docs/ADDENDUM_019.md"];A.BASE=BASE
def run():
    if not A.artifacts_ok(BASE):raise SystemExit("governed bytes changed; successor freeze needed")
    R=A.Run(BASE);b=A.semgrep(ROOT/"fixtures/before.py");braw=b.pop("raw",b"");a=A.semgrep(ROOT/"fixtures/after.py");a.pop("raw",b"")
    R.step("semgrep_before","OBSERVED",b,{"scanner_executed":b["state"]=="OBSERVED","finding_present":len(b["findings"])>0},braw)
    facts={"task":"Explain the vulnerability and propose a fix. Advice only.","semgrep_findings":b["findings"],"rule":(ROOT/"rules/fallback.yaml").read_text(),"fixture_before_source":(ROOT/"fixtures/before.py").read_text()}
    ak=A.akash(facts);raw=ak.pop("raw",None)
    ok=ak["state"]=="OBSERVED"
    R.step("akash_inference",ak["state"],ak,{"actual_akash_call":ok,"advice_schema_valid":bool(ak.get("schema_valid")),"model_identity_returned":bool(ak.get("model_returned")),"inference_id_returned":bool(ak.get("inference_id")),"usage_returned":bool(ak.get("usage")),"gpu_lease_established":False,"attestation_verified":False,"advice_applied":False},raw)
    if ok:
        try:txt=json.loads(raw)["choices"][0]["message"]["content"]
        except Exception:txt=""
        R.step("advice_review_gate","OBSERVED",{"advice_sha256":A.sha(txt.encode()),"advice_chars":len(txt),"mentions_fail_open":("health" in txt.lower() or "fail" in txt.lower()) ,"human_review":"NOT_PERFORMED"},{"advice_untrusted":True,"patch_applied_by_ai":False,"human_review_done":False})
if __name__=="__main__":
    c=sys.argv[1] if len(sys.argv)>1 else ""
    if c=="freeze":print("project_root",A.freeze(BASE)["project_root"])
    elif c=="run":run()
    elif c=="verify":r=A.verify(BASE);print(json.dumps(r,indent=2,sort_keys=True));sys.exit(0 if r["PASS"] else 1)
    else:sys.exit("usage: freeze|run|verify")
