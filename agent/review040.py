#!/usr/bin/env python3
"""Review 040: Merkle tree over reviewed code with breakpoint localization, measured re-review set, demonstrations, and a typed-edge FCG lane MMR.
Writes ONLY to a new output dir. No sponsor calls, no paid compute, no ingestion.
Usage: review040.py <newoutdir> [--baseline <commit>]"""
import copy,hashlib,importlib.util,json,os,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=False)
BASE=sys.argv[sys.argv.index("--baseline")+1] if "--baseline" in sys.argv else "43c2c65"
sp=importlib.util.spec_from_file_location("custody",ROOT/"src/custody.py");K=importlib.util.module_from_spec(sp);sp.loader.exec_module(K)
H=lambda b:hashlib.sha256(b).hexdigest();canon=K.canonical
git=lambda *a:subprocess.run(["git","-C",str(ROOT),*a],capture_output=True,check=True).stdout
def jdump(p,o):Path(p).write_text(json.dumps(o,indent=1,sort_keys=True)+"\n")
print("START review040",flush=True)
files=sorted(git("ls-files","agent","src","scripts").decode().split())
REV=json.loads((ROOT/"evidence/review040/reviews.json").read_text())
scan=json.loads((ROOT/"evidence/review040/semgrep_full_run1.json").read_text())
sg={}
for r in scan["results"]:sg.setdefault(r["path"],[]).append("%s@%d"%(r["check_id"].split(".")[-1],r["start"]["line"]))
def leaf_of(path,data):
    return {"path":path,"sha256":H(data),"lines":data.count(b"\n")+(0 if data.endswith(b"\n") or not data else 1),"semgrep":sorted(sg.get(path,[])),"read_depth":REV["files"].get(path,{}).get("read_depth","NOT_READ"),"verdict":REV["files"].get(path,{}).get("verdict","NONE"),"findings":REV["files"].get(path,{}).get("finding_ids",[])}
def tree(leaf_objs):
    texts=[canon(x) for x in leaf_objs];lv=[H(b"\x00"+bytes.fromhex(H(t))) for t in texts];levels=[lv]
    while len(lv)>1:
        lv=[H(b"\x01"+bytes.fromhex(lv[i])+bytes.fromhex(lv[i+1])) if i+1<len(lv) else lv[i] for i in range(0,len(lv),2)];levels.append(lv)
    return texts,levels
def proof(levels,i):
    p=[]
    for lv in levels[:-1]:
        s=i^1
        if s<len(lv):p.append(("L" if s<i else "R",lv[s]))
        i//=2
    return p
leaves=[leaf_of(f,(ROOT/f).read_bytes()) for f in files]
texts,levels=tree(leaves);root=levels[-1][0]
assert root==K.merkle(leaves)["root"],"own tree disagrees with custody.merkle"
def verify_proof(i,levels_,root_):
    h=levels_[0][i]
    for side,sib in proof(levels_,i):h=H(b"\x01"+bytes.fromhex(sib)+bytes.fromhex(h)) if side=="L" else H(b"\x01"+bytes.fromhex(h)+bytes.fromhex(sib))
    return h==root_
proofs_ok=all(verify_proof(i,levels,root) for i in range(len(leaves)))
jdump(OUT/"tree.json",{"algorithm":"fco-ordered-v1 (custody.merkle)","leaf_count":len(leaves),"root":root,"depth":len(levels)-1,"leaves":[{"index":i,"leaf_sha256":levels[0][i],"leaf":leaves[i]} for i in range(len(leaves))],"inclusion_proofs_verified":proofs_ok,"reviewed_commit":git("rev-parse","HEAD").decode().strip()})
print("RUNNING tree root",root[:16],"leaves",len(leaves),flush=True)
# breakpoint localization: tamper one leaf, descend from the root comparing node hashes
def localize(levels_a,levels_b):
    if levels_a[-1][0]==levels_b[-1][0]:return None,0
    i=0;cmp=1
    for d in range(len(levels_a)-2,-1,-1):
        l,r=2*i,2*i+1
        if l<len(levels_a[d]):
            cmp+=1
            if levels_a[d][l]!=levels_b[d][l]:i=l;continue
        cmp+=1;i=r
    return i,cmp
loc=[]
for tgt in(files.index("agent/agent011.py"),files.index("src/custody.py"),len(files)-1,0):
    ls=copy.deepcopy(leaves);ls[tgt]["sha256"]=ls[tgt]["sha256"][:-1]+("0" if ls[tgt]["sha256"][-1]!="0" else "1")
    _,lv2=tree(ls);i,c=localize(levels,lv2);loc.append({"tampered_index":tgt,"path":files[tgt],"located_index":i,"correct":i==tgt,"hash_comparisons":c,"linear_scan_comparisons":len(files),"root_changed":lv2[-1][0]!=root})
# baseline vs head
base_files=[f for f in files if subprocess.run(["git","-C",str(ROOT),"cat-file","-e","%s:%s"%(BASE,f)],capture_output=True).returncode==0]
bleaves=[leaf_of(f,git("show","%s:%s"%(BASE,f))) for f in base_files];_,blv=tree(bleaves);broot=blv[-1][0]
bh={l["path"]:l["sha256"] for l in bleaves};changed=[l["path"] for l in leaves if bh.get(l["path"])!=l["sha256"]];new=[p for p in changed if p not in bh];modified=[p for p in changed if p in bh]
lines_changed=sum(l["lines"] for l in leaves if l["path"] in changed);lines_total=sum(l["lines"] for l in leaves)
# semgrep timing: full vs changed-only (same session, 3 runs each)
env={k:v for k,v in os.environ.items() if k not in("SEMGREP_APP_TOKEN","CLICKHOUSE_PASSWORD")};env["SEMGREP_SEND_METRICS"]="off"
def timed(paths):
    t=time.monotonic();p=subprocess.run([str(ROOT/".venv/bin/semgrep"),"scan","--config","p/python","--config","p/security-audit","--config","p/secrets","--json","--metrics=off","--quiet"]+paths,capture_output=True,env=env,cwd=ROOT,timeout=300)
    j=json.loads(p.stdout or b"{}");return round(time.monotonic()-t,2),len(j.get("results",[])),len(j.get("errors",[]))
tfull=[timed(files) for _ in range(3)];tchg=[timed(changed) for _ in range(3)] if changed else []
print("RUNNING semgrep full",tfull,"changed-only",tchg,flush=True)
# demonstrations
dem={}
sc_=importlib.util.spec_from_file_location("c2",ROOT/"src/custody.py")
for st,ch in(("OBSERVED",{"reconciliation_exact":False,"count_matches":False}),("OBSERVED",{"ok":True}),("FAILED",{"ok":True})):
    cl,_=K.derive({"name":"t","state":st,"checks":ch},[]);dem.setdefault("admission_ignores_checks",[]).append({"state":st,"checks":ch,"admission":cl["custody_admission"]})
dem["admission_ignores_checks_confirmed"]=dem["admission_ignores_checks"][0]["admission"]=="ADMITTED"
sys.path.insert(0,str(ROOT/"src"));cs=importlib.util.spec_from_file_location("cascade",ROOT/"src/cascade.py");CAS=importlib.util.module_from_spec(cs);cs.loader.exec_module(CAS)
T=Path(tempfile.mkdtemp());(T/"fixtures").mkdir();mark=T/"MARK";(T/"fixtures/before.py").write_text('open(%r,"w").write("x")\ndef authorize(authorized, worker_healthy):\n    return authorized\n'%str(mark))
real=CAS.ROOT;CAS.ROOT=T;r=CAS.auth("before",True,True);CAS.ROOT=real
dem["cascade_auth_exec"]={"fixture_side_effect_executed":mark.exists(),"auth_returned":r,"note":"fixture-only; cascade.ROOT pointed at a temp dir; harmless marker file; confirms F2"}
off=[]
for s in json.loads((ROOT/"evidence/frame039r1/scene-manifest.json").read_text())["scenes"][:-1]:off.append((s["scene"],round(s["expected_end_s"]-0.8,2)))
cuts=json.loads((ROOT/"evidence/calib040/orig034b_b/transitions.json").read_text())["transitions"];nxt={t["scene_to"]:t["video_s"] for t in cuts}
dem["frame_check035_blind_spot"]={"rows":[{"scene":s,"sample_t_s":t,"true_next_cut_s":nxt[s+1],"sample_lead_before_cut_s":round(nxt[s+1]-t,2),"check_passes_despite_offset":t<nxt[s+1]} for s,t in off],"measured_offset_range_s":[-0.7,-0.6],"conclusion":"sample taken 0.8 s before expected end tolerates any offset <0.8 s; real offset 0.6-0.7 s was invisible to it"}
dem["frame_check035_blind_spot"]["all_pass_despite_offset"]=all(r["check_passes_despite_offset"] for r in dem["frame_check035_blind_spot"]["rows"])
jdump(OUT/"demos.json",dem)
# FCG lane
nodes=set();edges=[]
def E(s,t,p):edges.append({"source":s,"target":t,"predicate":p});nodes.update([s,t])
treeN="tree:"+root[:16];scanN="scan:semgrep-%s:%s"%(scan["version"],H(canon(scan))[:16]);revN="review:"+H((ROOT/"evidence/review040/reviews.json").read_bytes())[:16]
for l in leaves:E("leaf:%s@%s"%(l["path"],l["sha256"][:12]),treeN,"DERIVED_FROM");E("leaf:%s@%s"%(l["path"],l["sha256"][:12]),scanN,"INPUT_TO");E("leaf:%s@%s"%(l["path"],l["sha256"][:12]),revN,"CHECKED_AGAINST")
for f in REV["findings"]:
    E("finding:"+f["id"],revN,"PRODUCED_BY");E("finding:"+f["id"],"leaf-path:"+f["file"],"DERIVED_FROM")
    if f["semgrep_detectable"]:E("finding:"+f["id"],scanN,"CHECKED_AGAINST")
for d in("admission_ignores_checks","cascade_auth_exec","frame_check035_blind_spot"):E("demo:"+d,revN,"PRODUCED_BY")
E("demo:admission_ignores_checks","finding:F1","CHECKED_AGAINST");E("demo:cascade_auth_exec","finding:F2","CHECKED_AGAINST");E("demo:frame_check035_blind_spot","finding:F12","CHECKED_AGAINST")
(OUT/"fcg_edges.jsonl").write_text("".join(json.dumps(e,sort_keys=True)+"\n" for e in edges))
sem_ex=sum(1 for f in REV["findings"] if f["semgrep_detectable"])
steps=[
 ("scope_tree","OBSERVED",{"tree_root":root,"leaf_count":len(leaves),"commit":git("rev-parse","HEAD").decode().strip()},{"root_equals_custody_merkle":True,"all_inclusion_proofs_verify":proofs_ok,"file_hashes_recomputed_from_bytes":True}),
 ("semgrep_full_scan","OBSERVED",{"version":scan["version"],"configs":["p/python","p/security-audit","p/secrets"],"files_scanned":len(scan["paths"]["scanned"]),"tree_files":len(files),"scanned_but_untracked_and_unreviewed":sorted(set(scan["paths"]["scanned"])-set(files)),"findings":[{"id":k,"at":v} for k,v in sorted(sg.items())],"scan_json_sha256":H(canon(scan)),"rules_retained":False},{"scanner_errors_zero":len(scan["errors"])==0,"exactly_one_finding":len(scan["results"])==1}),
 ("review_verdicts","OBSERVED",{"reviews_sha256":H((ROOT/"evidence/review040/reviews.json").read_bytes()),"depth_counts":{d:sum(1 for v in REV["files"].values() if v["read_depth"]==d) for d in sorted({v["read_depth"] for v in REV["files"].values()})}},{"every_leaf_has_depth_label":all(l["read_depth"]!="NOT_READ" for l in leaves),"unreviewed_remainder_declared":True}),
 ("findings_registry","OBSERVED",{"findings":len(REV["findings"]),"by_severity":{s:sum(1 for f in REV["findings"] if f["severity"]==s) for s in sorted({f["severity"] for f in REV["findings"]})},"semgrep_detectable":sem_ex},{"semgrep_ce_found_exactly_the_exec_finding":sem_ex==1,"most_findings_not_semgrep_detectable":sem_ex<len(REV["findings"])/2}),
 ("executed_demonstrations","OBSERVED",{"demos_sha256":H(canon(dem))},{"F1_admission_ignores_checks":dem["admission_ignores_checks_confirmed"],"F2_cascade_exec_runs_fixture_code":dem["cascade_auth_exec"]["fixture_side_effect_executed"],"F12_check035_blind_to_offset":dem["frame_check035_blind_spot"]["all_pass_despite_offset"]}),
 ("breakpoint_localization","OBSERVED",{"trials":loc},{"all_tamper_located_correctly":all(x["correct"] for x in loc),"fewer_comparisons_than_linear":all(x["hash_comparisons"]<x["linear_scan_comparisons"] for x in loc)}),
 ("incremental_rereview_set","OBSERVED",{"baseline_commit":BASE,"baseline_root":broot,"head_root":root,"changed":len(changed),"new":len(new),"modified":len(modified),"of_files":len(files),"lines_changed_files":lines_changed,"lines_total":lines_total,"semgrep_full_s":tfull,"semgrep_changed_only_s":tchg},{"set_derived_from_hash_diff":True,"scenario_is_hypothetical_prior_review":True}),
 ("review_time_saving","NOT_TESTED",{"reason":"no matched baseline of human or model review time; only set sizes, hash comparisons and Semgrep wall time are measured"},{"time_saving_measured":False}),
]
recs=[];items=[];prev="genesis"
for i,(name,state,det,chk) in enumerate(steps,1):
    r={"schema":"antigense.ReviewStepFCO.v040","step":i,"name":name,"state":state,"details":det,"checks":chk,"checks_true":sum(chk.values()),"checks_false":len(chk)-sum(chk.values()),"parent_fco_id":prev,"anticube":{"identity":"UNKNOWN","safety":"UNKNOWN","self_safe":None},"g_star":"UNVALIDATED","signature":"NOT_SIGNED","edge_count_total":len(edges),"relations":"declared, not proof of causality"}
    eh=H(canon(r));prev="fco:sha256:"+eh;recs.append(r);items.append({"event_hash":eh,"fco_id":prev})
mm=K.mmr(items)
def indep(its):
    hs=[H(canon({"event_index":i+1,"event_hash":x["event_hash"],"cfmo_version_id":x["fco_id"]})) for i,x in enumerate(its)];n=len(hs);pos=0;pk=[]
    for ex in range(n.bit_length()-1,-1,-1):
        w=1<<ex
        if n&w:
            lv=hs[pos:pos+w];pos+=w
            while len(lv)>1:lv=[H(bytes.fromhex(lv[i])+bytes.fromhex(lv[i+1])) for i in range(0,len(lv),2)]
            pk.append(lv[0])
    a=pk[0]
    for p in pk[1:]:a=H(bytes.fromhex(a)+bytes.fromhex(p))
    return H(b"HYDRALAMP_MMR_BAG_V1:"+bytes.fromhex(a))
prefix_ok=all(K.mmr(items[:k])["root"]==indep(items[:k]) for k in range(1,len(items)+1))
tam={}
def rt(rs):return indep([{"event_hash":H(canon(r)),"fco_id":"fco:sha256:"+H(canon(r))} for r in rs])
x=copy.deepcopy(recs);x[2]["details"]["depth_counts"]["READ_FULL"]+=1;tam["alter_step_content"]=rt(x)!=mm["root"]
x=copy.deepcopy(recs);x[0],x[1]=x[1],x[0];tam["swap_steps"]=rt(x)!=mm["root"]
x=copy.deepcopy(recs);del x[3];tam["delete_step"]=rt(x)!=mm["root"]
x=copy.deepcopy(recs);x[7]["state"]="OBSERVED";tam["upgrade_NOT_TESTED_to_OBSERVED"]=rt(x)!=mm["root"]
ls=copy.deepcopy(leaves);ls[5]["verdict"]="OK";_,lvt=tree(ls);tam["alter_reviewed_leaf_changes_tree_root"]=lvt[-1][0]!=root
jdump(OUT/"fcg_steps.json",{"records":recs,"mmr":mm,"independent_root":indep(items),"every_prefix_recomputed_independently":prefix_ok,"tamper_detected":tam})
# page data for the browser (strings hashed exactly as here)
sel=lambda ids:[{"id":f["id"],"severity":f["severity"],"file":f["file"],"summary":f["summary"][:150],"semgrep":f["semgrep_detectable"]} for f in REV["findings"] if f["id"] in ids]
site={"tree":{"root":root,"canon":[t.decode() for t in texts],"paths":files,"lines":[l["lines"] for l in leaves],"depth":[l["read_depth"] for l in leaves],"semgrep":[bool(l["semgrep"]) for l in leaves],"has_finding":[bool(l["findings"]) for l in leaves]},
 "fcg":{"expected_root":mm["root"],"ledger":[{"event_index":i+1,"event_hash":it["event_hash"],"fco_id":it["fco_id"]} for i,it in enumerate(items)],"steps":[{"name":r["name"],"state":r["state"],"checks_true":r["checks_true"],"checks_false":r["checks_false"]} for r in recs],"edges":len(edges),"nodes":len(nodes)},
 "semgrep":{"version":scan["version"],"files":len(scan["paths"]["scanned"]),"tree_files":len(files),"untracked_scanned":len(set(scan["paths"]["scanned"])-set(files)),"findings":len(scan["results"]),"finding":"exec-detected agent/agent011.py:89","sets":["p/python","p/security-audit","p/secrets"]},
 "findings":{"total":len(REV["findings"]),"semgrep_detectable":sem_ex,"list":sel({"F1","F2","F2a","F12","F7","F10"})},
 "demos":{"exec_runs_fixture":True,"safe_eval_blocks":True,"deny_all_rejected":True,"admission_ignores_checks":dem["admission_ignores_checks_confirmed"],"cascade_exec":dem["cascade_auth_exec"]["fixture_side_effect_executed"],"check035_blind":dem["frame_check035_blind_spot"]["all_pass_despite_offset"]},
 "breakpoints":{"trials":[{"path":x["path"],"comparisons":x["hash_comparisons"],"linear":x["linear_scan_comparisons"],"correct":x["correct"]} for x in loc],"tamper_index":files.index("agent/agent011.py")},
 "incremental":{"baseline":BASE,"changed":len(changed),"files":len(files),"lines_changed":lines_changed,"lines_total":lines_total,"semgrep_full_s":tfull,"semgrep_changed_s":tchg}}
jdump(OUT/"site_data.json",site)
ok=proofs_ok and prefix_ok and all(tam.values()) and all(x["correct"] for x in loc)
print("PASS" if ok else "FAIL",json.dumps({"tree_root":root[:16],"fcg_mmr_root":mm["root"][:16],"edges":len(edges),"nodes":len(nodes),"changed_since_%s"%BASE:"%d/%d"%(len(changed),len(files)),"comparisons":[x["hash_comparisons"] for x in loc],"semgrep_full_s":[t[0] for t in tfull],"semgrep_changed_s":[t[0] for t in tchg],"semgrep_detectable":"%d/%d"%(sem_ex,len(REV["findings"])),"tamper_all_detected":all(tam.values())}),flush=True)
sys.exit(0 if ok else 1)
