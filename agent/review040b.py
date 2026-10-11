#!/usr/bin/env python3
"""Review 040b: incremental re-review. Builds the HEAD tree, diffs it against the previously reviewed tree by path AND by root-descent,
extends the FCG lane MMR append-only (first N leaves must reproduce the earlier root), records post-fix verification.
Writes ONLY to a new dir. No sponsor calls, no paid compute, no ingestion.
Usage: review040b.py <newoutdir> --prior <review run dir> --reviews <reviews_v2.json> --scan <semgrep head json> --postfix <postfix.json> --baseline-commit <sha>"""
import copy,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=False)
arg=lambda k:sys.argv[sys.argv.index(k)+1]
PRIOR=Path(arg("--prior")).resolve();REV=json.loads(Path(arg("--reviews")).read_text());scan=json.loads(Path(arg("--scan")).read_text());post=json.loads(Path(arg("--postfix")).read_text());BASEC=arg("--baseline-commit")
sp=importlib.util.spec_from_file_location("custody",ROOT/"src/custody.py");K=importlib.util.module_from_spec(sp);sp.loader.exec_module(K)
H=lambda b:hashlib.sha256(b).hexdigest();canon=K.canonical
git=lambda *a:subprocess.run(["git","-C",str(ROOT),*a],capture_output=True,check=True).stdout
jdump=lambda p,o:Path(p).write_text(json.dumps(o,indent=1,sort_keys=True)+"\n")
print("START review040b",flush=True)
files=sorted(git("ls-files","agent","src","scripts").decode().split())
sg={}
for r in scan["results"]:sg.setdefault(r["path"],[]).append("%s@%d"%(r["check_id"].split(".")[-1],r["start"]["line"]))
def leaf_of(path,data,rv):
    return {"path":path,"sha256":H(data),"lines":data.count(b"\n")+(0 if data.endswith(b"\n") or not data else 1),"semgrep":sorted(sg.get(path,[])),"read_depth":rv["files"].get(path,{}).get("read_depth","NOT_READ"),"verdict":rv["files"].get(path,{}).get("verdict","NONE"),"findings":rv["files"].get(path,{}).get("finding_ids",[])}
def tree(ls):
    texts=[canon(x) for x in ls];lv=[H(b"\x00"+bytes.fromhex(H(t))) for t in texts];levels=[lv]
    while len(lv)>1:
        lv=[H(b"\x01"+bytes.fromhex(lv[i])+bytes.fromhex(lv[i+1])) if i+1<len(lv) else lv[i] for i in range(0,len(lv),2)];levels.append(lv)
    return texts,levels
old=json.loads((PRIOR/"tree.json").read_text());oldleaves=[x["leaf"] for x in old["leaves"]]
oldtexts,oldlv=tree(oldleaves);assert oldlv[-1][0]==old["root"],"prior tree does not recompute"
leaves=[leaf_of(f,(ROOT/f).read_bytes(),REV) for f in files];texts,lv=tree(leaves);root=lv[-1][0];assert root==K.merkle(leaves)["root"]
jdump(OUT/"tree.json",{"leaf_count":len(leaves),"root":root,"prior_root":old["root"],"leaves":[{"index":i,"leaf_sha256":lv[0][i],"leaf":leaves[i]} for i in range(len(leaves))],"head":git("rev-parse","HEAD").decode().strip(),"baseline_commit":BASEC})
# path-aware diff (exact) vs root-descent (positional)
oh={l["path"]:l["sha256"] for l in oldleaves};nh={l["path"]:l["sha256"] for l in leaves}
modified=sorted(p for p in nh if p in oh and oh[p]!=nh[p]);added=sorted(p for p in nh if p not in oh);removed=sorted(p for p in oh if p not in nh)
def descend(a,b):
    # compare level-by-level from the root over positions that exist in both; returns flagged leaf positions + comparisons
    flagged=[];cmp=0
    def rec(d,i):
        nonlocal cmp
        if d==0:flagged.append(i);return
        for c in(2*i,2*i+1):
            ina=c<len(a[d-1]);inb=c<len(b[d-1])
            if not ina and not inb:continue
            cmp+=1
            if ina and inb and a[d-1][c]==b[d-1][c]:continue
            rec(d-1,c)
    cmp+=1
    if a[-1][0]!=b[-1][0] or len(a)!=len(b):rec(max(len(a),len(b))-1,0) if len(a)==len(b) else None
    return flagged,cmp
if len(oldlv)==len(lv):flag,cmp=descend(oldlv,lv)
else:
    # different depths: pad the shallower level list by treating missing nodes as absent
    D=max(len(oldlv),len(lv));A=oldlv+[[] ]*(D-len(oldlv));B=lv+[[]]*(D-len(lv));flag=[];cmp=1
    def rec(d,i):
        global cmp
        if d==0:flag.append(i);return
        for c in(2*i,2*i+1):
            ina=c<len(A[d-1]);inb=c<len(B[d-1])
            if not ina and not inb:continue
            cmp+=1
            if ina and inb and A[d-1][c]==B[d-1][c]:continue
            rec(d-1,c)
    rec(D-1,0)
true_changed={files.index(p) for p in modified+added}
desc={"flagged_positions":len(flag),"true_changed_by_path":len(true_changed),"false_positive_positions":len([i for i in flag if i not in true_changed]),"hash_comparisons":cmp,"linear_scan_comparisons":len(files),"note":"positional tree: inserting files shifts later leaves, so root-descent flags the shifted suffix; path-aware hash map is exact (F17)"}
env={k:v for k,v in os.environ.items() if k not in("SEMGREP_APP_TOKEN","CLICKHOUSE_PASSWORD")};env["SEMGREP_SEND_METRICS"]="off"
def timed(paths):
    t=time.monotonic();p=subprocess.run([str(ROOT/".venv/bin/semgrep"),"scan","--config","p/python","--config","p/security-audit","--config","p/secrets","--json","--metrics=off","--quiet"]+paths,capture_output=True,env=env,cwd=ROOT,timeout=300)
    j=json.loads(p.stdout or b"{}");return [round(time.monotonic()-t,2),len(j.get("results",[])),len(j.get("errors",[]))]
chg=modified+added;tfull=[timed(files) for _ in range(3)];tchg=[timed(chg) for _ in range(3)]
lines_changed=sum(l["lines"] for l in leaves if l["path"] in chg);lines_total=sum(l["lines"] for l in leaves)
print("RUNNING changed",modified,added,"timing",tfull,tchg,flush=True)
# FCG: extend prior chain append-only
prior=json.loads((PRIOR/"fcg_steps.json").read_text());precs=prior["records"];pitems=[{"event_hash":H(canon(r)),"fco_id":"fco:sha256:"+H(canon(r))} for r in precs]
assert K.mmr(pitems)["root"]==prior["mmr"]["root"]
nodes=set();edges=[]
def E(s,t,p):edges.append({"source":s,"target":t,"predicate":p});nodes.update([s,t])
treeN="tree:"+root[:16];oldN="tree:"+old["root"][:16];scanN="scan:semgrep-%s:%s"%(scan["version"],H(canon(scan))[:16]);revN="review:"+H(Path(arg("--reviews")).read_bytes())[:16]
E(treeN,oldN,"DERIVED_FROM")
for p in modified:E("leaf:%s@%s"%(p,nh[p][:12]),"leaf:%s@%s"%(p,oh[p][:12]),"DERIVED_FROM")
for p in chg:E("leaf:%s@%s"%(p,nh[p][:12]),scanN,"INPUT_TO");E("leaf:%s@%s"%(p,nh[p][:12]),revN,"CHECKED_AGAINST");E("leaf:%s@%s"%(p,nh[p][:12]),treeN,"DERIVED_FROM")
for f in REV["findings"]:
    if f["id"] in("F2a","F3","F2","F15","F16","F17","F18"):E("finding:"+f["id"]+":"+f["status_at_head"].split()[0],revN,"PRODUCED_BY")
E("finding:F2a:RESOLVED_VERIFIED","demo:postfix040","CHECKED_AGAINST");E("finding:F2:OPEN","demo:postfix040","CHECKED_AGAINST");E("demo:postfix040",revN,"PRODUCED_BY")
(OUT/"fcg_edges_v2.jsonl").write_text("".join(json.dumps(e,sort_keys=True)+"\n" for e in edges))
cnt=lambda s:sum(1 for f in REV["findings"] if f["status_at_head"].startswith(s))
steps=[("scope_tree_v2","OBSERVED",{"tree_root":root,"prior_tree_root":old["root"],"leaf_count":len(leaves),"head":git("rev-parse","HEAD").decode().strip()},{"root_equals_custody_merkle":True,"prior_tree_recomputed":True}),
 ("semgrep_head_scan","OBSERVED",{"version":scan["version"],"files_scanned":len(scan["paths"]["scanned"]),"findings":len(scan["results"]),"scan_json_sha256":H(canon(scan)),"configs":["p/python","p/security-audit","p/secrets"]},{"scanner_errors_zero":len(scan["errors"])==0,"zero_findings_at_head":len(scan["results"])==0}),
 ("incremental_rereview_set","OBSERVED",{"modified":modified,"added":added,"removed":removed,"changed":len(chg),"of_files":len(files),"lines_changed_files":lines_changed,"lines_total":lines_total,"root_descent":desc,"semgrep_full_s":tfull,"semgrep_changed_only_s":tchg},{"set_derived_from_path_hash_diff":True,"unchanged_leaves_reused_by_hash":len(files)-len(chg),"root_descent_exact":desc["false_positive_positions"]==0}),
 ("postfix_controlled_check","OBSERVED",{"postfix_sha256":H(canon(post))},{"F2a_resolved_verified":post["F2a_resolved"],"F2_still_open":not post["F2_resolved"],"fixtures_behavior_unchanged":post["agent011_regress_matches_safe_eval_on_real_fixtures"]}),
 ("finding_status_update","OBSERVED",{"resolved_verified":cnt("RESOLVED"),"partially_resolved":cnt("PARTIALLY"),"open":cnt("OPEN"),"findings":len(REV["findings"])},{"statuses_from_executed_checks_only":True}),
 ("review_time_saving","NOT_TESTED",{"reason":"no matched baseline of human or model review time"},{"time_saving_measured":False})]
recs=list(precs);items=list(pitems);prev=items[-1]["fco_id"]
for n,(name,state,det,chk) in enumerate(steps,len(precs)+1):
    r={"schema":"antigense.ReviewStepFCO.v040","step":n,"name":name,"state":state,"details":det,"checks":chk,"checks_true":sum(chk.values()),"checks_false":len(chk)-sum(chk.values()),"parent_fco_id":prev,"anticube":{"identity":"UNKNOWN","safety":"UNKNOWN","self_safe":None},"g_star":"UNVALIDATED","signature":"NOT_SIGNED","relations":"declared, not proof of causality"}
    eh=H(canon(r));prev="fco:sha256:"+eh;recs.append(r);items.append({"event_hash":eh,"fco_id":prev})
mm=K.mmr(items)
def indep(its):
    hs=[H(canon({"event_index":i+1,"event_hash":x["event_hash"],"cfmo_version_id":x["fco_id"]})) for i,x in enumerate(its)];n=len(hs);pos=0;pk=[]
    for ex in range(n.bit_length()-1,-1,-1):
        w=1<<ex
        if n&w:
            l=hs[pos:pos+w];pos+=w
            while len(l)>1:l=[H(bytes.fromhex(l[i])+bytes.fromhex(l[i+1])) for i in range(0,len(l),2)]
            pk.append(l[0])
    a=pk[0]
    for p in pk[1:]:a=H(bytes.fromhex(a)+bytes.fromhex(p))
    return H(b"HYDRALAMP_MMR_BAG_V1:"+bytes.fromhex(a))
prefix_ok=all(K.mmr(items[:k])["root"]==indep(items[:k]) for k in range(1,len(items)+1))
append_only=indep(items[:len(precs)])==prior["mmr"]["root"]
rt=lambda rs:indep([{"event_hash":H(canon(r)),"fco_id":"fco:sha256:"+H(canon(r))} for r in rs])
tam={};x=copy.deepcopy(recs);x[2]["details"]["depth_counts"]["READ_FULL"]+=1;tam["alter_earlier_step"]=rt(x)!=mm["root"]
x=copy.deepcopy(recs);x[-2]["details"]["open"]=0;tam["alter_later_step"]=rt(x)!=mm["root"]
x=copy.deepcopy(recs);del x[9];tam["delete_step"]=rt(x)!=mm["root"]
x=copy.deepcopy(recs);x[-1]["state"]="OBSERVED";tam["upgrade_NOT_TESTED"]=rt(x)!=mm["root"]
x=copy.deepcopy(recs);x[8],x[9]=x[9],x[8];tam["swap_steps"]=rt(x)!=mm["root"]
jdump(OUT/"fcg_steps_v2.json",{"records":recs,"mmr":mm,"independent_root":indep(items),"every_prefix_recomputed_independently":prefix_ok,"append_only_prefix_reproduces_prior_root":append_only,"prior_root":prior["mmr"]["root"],"tamper_detected":tam,"edges_added":len(edges)})
# page data v2 addendum
sd=json.loads((PRIOR/"site_data.json").read_text())
sd["v2"]={"head_tree_root":root,"files":len(files),"canon":[t.decode() for t in texts],"paths":files,"changed_paths":chg,"modified":modified,"added":added,"descent":desc,"semgrep_head":{"files":len(scan["paths"]["scanned"]),"findings":len(scan["results"])},"postfix":{"F2a_resolved":post["F2a_resolved"],"F2_open":not post["F2_resolved"]},"fcg":{"expected_root":mm["root"],"ledger":[{"event_index":i+1,"event_hash":it["event_hash"],"fco_id":it["fco_id"]} for i,it in enumerate(items)],"prior_leaves":len(precs),"prior_root":prior["mmr"]["root"],"edges_added":len(edges)},"timing":{"full":tfull,"changed":tchg,"lines_changed":lines_changed,"lines_total":lines_total},"status":{"resolved":cnt("RESOLVED"),"partial":cnt("PARTIALLY"),"open":cnt("OPEN"),"total":len(REV["findings"])}}
jdump(OUT/"site_data.json",sd)
ok=prefix_ok and append_only and all(tam.values())
print("PASS" if ok else "FAIL",json.dumps({"head_tree":root[:16],"prior_tree":old["root"][:16],"modified":modified,"added":added,"changed":"%d/%d"%(len(chg),len(files)),"descent":desc,"fcg_root":mm["root"][:16],"append_only":append_only,"tamper":all(tam.values()),"semgrep_full":[t[0] for t in tfull],"semgrep_changed":[t[0] for t in tchg]}),flush=True)
sys.exit(0 if ok else 1)
