#!/usr/bin/env python3
"""Cyberhack custody 008R1. Declared kit graph + per-step Merkle + HYDRALAMP_MMR_V1.
No cryptographic authentication, portfolio canonical promotion, or physical truth claim.
"""
import argparse,datetime,hashlib,json,math,os,sys
from pathlib import Path
KIT_FILES=['README.md', 'src/custody.py', 'src/cascade.py', 'src/server.py', 'public/index.html', 'public/verify.js', 'topology.json', 'policy.json', 'fixtures/before.py', 'fixtures/after.py', 'rules/fallback.yaml', 'PREDECESSOR_008.json', 'CUSTODY_CONTRACT_008.json', 'scripts/setup.sh', 'scripts/demo.sh', 'vercel.json', 'tests/test_custody.py', 'docs/DESIGN_009.md', 'docs/SPONSOR_CHECKLIST.md', 'docs/DATASET_REVIEW.md', 'docs/PI_INTAKE.md']
def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf-8")
def digest(b):return hashlib.sha256(b).hexdigest()
def merkle(leaves):
    texts=[canonical(x) for x in leaves]
    level=[digest(b"\x00"+hashlib.sha256(b).digest()) for b in texts]
    hashes=list(level)
    if not level:raise ValueError("empty declared Merkle tree")
    while len(level)>1:
        level=[digest(b"\x01"+bytes.fromhex(level[i])+bytes.fromhex(level[i+1])) if i+1<len(level) else level[i] for i in range(0,len(level),2)]
    return {"algorithm":"fco-ordered-v1","leaf_count":len(texts),
            "leaves":[{"index":i,"canonical_utf8":b.decode(),"leaf_sha256":h} for i,(b,h) in enumerate(zip(texts,hashes))],
            "root":level[0]}
def mmr(items):
    peaks=[];leaves=[]
    for i,item in enumerate(items):
        body={"event_index":i+1,"event_hash":item["event_hash"],"cfmo_version_id":item["fco_id"]}
        h=digest(canonical(body));leaves.append({"body":body,"leaf_sha256":h})
        size=i+1
        while size%2==0:
            h=digest(bytes.fromhex(peaks.pop())+bytes.fromhex(h));size//=2
        peaks.append(h)
    if not peaks:root=digest(b"HYDRALAMP_MMR_EMPTY")
    else:
        acc=peaks[0]
        for peak in peaks[1:]:acc=digest(bytes.fromhex(acc)+bytes.fromhex(peak))
        root=digest(b"HYDRALAMP_MMR_BAG_V1:"+bytes.fromhex(acc))
    return {"algorithm":"HYDRALAMP_MMR_V1","leaf_count":len(items),"leaves":leaves,"peaks":peaks,"root":root}
def independent_mmr_root(items):
    # Independent decomposition into perfect trees, not append/carry logic.
    hs=[digest(canonical({"event_index":i+1,"event_hash":x["event_hash"],"cfmo_version_id":x["fco_id"]})) for i,x in enumerate(items)]
    pos=0;peaks=[]
    for exponent in range(len(hs).bit_length()-1,-1,-1):
        width=1<<exponent
        if len(hs)&width:
            level=hs[pos:pos+width];pos+=width
            while len(level)>1:level=[digest(bytes.fromhex(level[i])+bytes.fromhex(level[i+1])) for i in range(0,len(level),2)]
            peaks.append(level[0])
    if not peaks:return digest(b"HYDRALAMP_MMR_EMPTY")
    acc=peaks[0]
    for peak in peaks[1:]:acc=digest(bytes.fromhex(acc)+bytes.fromhex(peak))
    return digest(b"HYDRALAMP_MMR_BAG_V1:"+bytes.fromhex(acc))
def diagnostic(admissions,previous="0.000000"):
    # Adapted HydraLamp gateway diagnostic. Frozen custody categories; no hardware meaning.
    denied=admissions.count("REJECTED");quarantined=admissions.count("QUARANTINED")
    promoted=admissions.count("ADMITTED");n=max(len(admissions),1)
    burden=min(1.0,(denied+quarantined)/n)
    counts=[promoted,quarantined,denied,max(0,n-promoted-quarantined-denied)]
    total=sum(counts) or 1
    entropy=-sum((x/total)*math.log2(x/total) for x in counts if x)
    norm=entropy/math.log2(4)
    g=max(0,min(1,burden-0.35*norm))
    rounded=round(g,6)
    return {"algorithm":"CYBERHACK_CUSTODY_GSTAR_V1_ADAPTED_HYDRALAMP",
            "inputs":{"steps":len(admissions),"admitted":promoted,"quarantined":quarantined,"rejected":denied},
            "tau":"0.35","g_star":format(rounded,".6f"),
            "delta_g_star":format(round(rounded-float(previous),6),".6f"),
            "reference_g_star":previous,"normalized_entropy":format(round(norm,6),".6f"),
            "claim_ceiling":"UNVALIDATED_INFORMATION_STATE_DIAGNOSTIC; NOT SAFETY, ACCURACY OR PHYSICAL ENERGY"}
def write_new(path,obj):
    with Path(path).open("x",encoding="utf-8") as f:
        json.dump(obj,f,sort_keys=True,ensure_ascii=False,allow_nan=False,indent=2);f.flush();os.fsync(f.fileno())
def read(path):return json.loads(Path(path).read_text())
def rows(base):
    p=base/"ledger.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines() if x] if p.exists() else []
def derive(observation,prior):
    state=observation.get("state","UNKNOWN")
    checks={"state_declared":state in ["PROPOSED","IMPLEMENTED","EXECUTED","OBSERVED","SUPPORTED","FAILED","NULL","NEGATIVE","DEFERRED","NOT_TESTED","UNKNOWN","NOT_COMPUTED"],
            "name_declared":isinstance(observation.get("name"),str),"observation_available":state=="OBSERVED",
            "runtime_operation_validated":False}
    if observation.get("checks") is not None:
        supplied=observation["checks"]
        if not isinstance(supplied,dict) or any(type(v)!=bool for v in supplied.values()):raise ValueError("supplied checks must be actual booleans")
        checks.update({"provided."+k:v for k,v in supplied.items()})
    policy=observation.get("admission_policy", "LEGACY_V1")
    if policy not in ("LEGACY_V1", "STRICT_V2"):
        raise ValueError("unknown admission policy")
    eligible=checks["state_declared"] and checks["name_declared"] and checks["observation_available"]
    if policy=="STRICT_V2":
        required=observation.get("required_checks")
        if (not isinstance(required,list) or not required
                or len(required)!=len(set(required))
                or any(not isinstance(k,str) or not k for k in required)):
            eligible=False
        else:
            eligible=eligible and all(checks.get("provided."+k) is True for k in required)
    admission="REJECTED" if state in ["FAILED","NEGATIVE"] else ("ADMITTED" if eligible else "QUARANTINED")
    classifications={"state":state,"custody_admission":admission,
        "anticube":{"identity":"UNKNOWN","safety":"UNKNOWN","self_safe":None,
                    "proof_of_possession":"NOT_TESTED","authorization_validation":"NOT_TESTED",
                    "classification_executed":True,"reason":"No identity proof or independent safety oracle supplied; local custody admission is not SELF_SAFE"},
        "checks":checks,"checks_yes_no":{k:"YES" if v else "NO" for k,v in checks.items()}}
    ads=[x["admission"] for x in prior]+[admission]
    prev=prior[-1]["g_star"] if prior else "0.000000"
    return classifications,diagnostic(ads,prev)
def freeze(base,kit):
    base=Path(base);kit=Path(kit)
    if (base/"genesis.json").exists():
        if not verify_artifacts(base,kit):raise ValueError("kit bytes changed; create a successor freeze")
        return read(base/"genesis.json")
    base.mkdir(parents=True,exist_ok=True)
    nodes=[{"id":"project:antigense-009","type":"Project","scope":"Antigense 009 declared source graph; successor of 008R1; NOT entire hardware or portfolio graph","state":"PROPOSED"},
           {"id":"group:governance","type":"Group"},{"id":"group:runtime","type":"Group"}]
    edges=[{"source":"project:antigense-009","target":g,"predicate":"CONTAINS"} for g in ["group:governance","group:runtime"]]
    for name in KIT_FILES:
        b=(kit/name).read_bytes()
        nodes.append({"id":"artifact:"+name,"type":"Artifact","sha256":digest(b),"bytes":len(b),"relative_path":name})
        group="group:runtime" if name.endswith((".py",".sh",".json")) else "group:governance"
        edges.append({"source":group,"target":"artifact:"+name,"predicate":"CONTAINS"})
    contract=read(kit/"CUSTODY_CONTRACT_008.json")
    graph={"schema":"cyberhack.frozen-fractal-graph.v008r1","nodes":nodes,"edges":edges,"contract":contract,"PARENT":"008R1"}
    graph["initial_classification"]={"anticube":{"identity":"UNKNOWN","safety":"UNKNOWN","self_safe":None},"checks":{"artifact_hashes_calculated":True,"edge_endpoints_exist":all(e["source"] in {n["id"] for n in nodes} and e["target"] in {n["id"] for n in nodes} for e in edges)}}
    graph["g_star_reference"]=diagnostic([])
    leaves=[{"type":"initial_classification","value":graph["initial_classification"]},{"type":"g_star_reference","value":graph["g_star_reference"]},{"type":"graph_contract","value":contract}]+[{"type":"node","value":x} for x in nodes]+[{"type":"edge","value":x} for x in edges]
    tree=merkle(leaves)
    g={"graph":graph,"commitment":tree,"project_root":tree["root"],"ID":"fco:sha256:"+tree["root"],
       "SIGNATURE":"NOT_SIGNED","g_star_reference":diagnostic([]),"scope":nodes[0]["scope"]}
    write_new(base/"genesis.json",g)
    row={"event_index":1,"project_root":g["project_root"],"event_hash":digest(canonical(g)),
         "fco_id":g["ID"],"merkle_root":tree["root"],"kind":"PROJECT_FREEZE"}
    m=mmr([row]);assert m["root"]==independent_mmr_root([row])
    write_new(base/"prefix-000001.json",m)
    with (base/"ledger.jsonl").open("x") as f:f.write(json.dumps(row,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
    return g
def append_step(base,observation):
    # New occurrences use STRICT_V2; historical receipts lacking this field are
    # verified through LEGACY_V1 without mutation or false retroactive promotion.
    if observation.get("admission_policy") not in (None,"STRICT_V2"):
        raise ValueError("new observations cannot select legacy admission")
    observation={**observation,"admission_policy":"STRICT_V2"}
    base=Path(base);lock=base/".append-lock"
    lock.mkdir() # Fail closed on concurrent writer or interrupted lock; never overwrite.
    try:
        g=read(base/"genesis.json");ledger=rows(base)
        checked=verify(base)
        if not checked["PASS"]:raise ValueError("prior custody verification failed")
        prior=[]
        for row in ledger[1:]:
            obj=read(base/row["object_file"])
            prior.append({"admission":obj["classification"]["custody_admission"],"g_star":obj["diagnostic"]["g_star"]})
        cl,diag=derive(observation,prior)
        body={"schema":"cyberhack.StepFCO.v008r1","project_root":g["project_root"],
              "parent_fco_id":ledger[-1]["fco_id"],"previous_mmr_root":mmr(ledger)["root"],
              "observation":observation,"classification":cl,"diagnostic":diag,
              "relation":"DEPENDS_ON_RECORDED_PREDECESSOR","SIGNATURE":"NOT_SIGNED"}
        tree=merkle([{"type":k,"value":body[k]} for k in ["project_root","parent_fco_id","previous_mmr_root","observation","classification","diagnostic","relation","SIGNATURE"]])
        obj={**body,"commitment":tree,"fco_id":"fco:sha256:"+tree["root"]}
        index=len(ledger)+1;name="step-%06d.json"%index
        write_new(base/name,obj)
        row={"event_index":index,"project_root":g["project_root"],"event_hash":digest(canonical(obj)),
             "fco_id":obj["fco_id"],"merkle_root":tree["root"],"object_file":name,"kind":"STEP"}
        m=mmr(ledger+[row]);assert m["root"]==independent_mmr_root(ledger+[row])
        write_new(base/("prefix-%06d.json"%index),m)
        with (base/"ledger.jsonl").open("a") as f:f.write(json.dumps(row,sort_keys=True)+"\n");f.flush();os.fsync(f.fileno())
        result=verify(base)
        if not result["PASS"]:raise ValueError("new prefix verification failed")
        return {"step_fco_id":obj["fco_id"],"step_merkle_root":tree["root"],"mmr_root":m["root"],
                "verified":result["PASS"],"g_star":diag,"anticube":cl["anticube"]}
    finally:lock.rmdir()
def verify(base,expected_root=None):
    base=Path(base);checks={}
    try:
        g=read(base/"genesis.json");graph=g["graph"]
        leaves=[{"type":"initial_classification","value":graph["initial_classification"]},{"type":"g_star_reference","value":graph["g_star_reference"]},{"type":"graph_contract","value":graph["contract"]}]+[{"type":"node","value":x} for x in graph["nodes"]]+[{"type":"edge","value":x} for x in graph["edges"]]
        tree=merkle(leaves)
        checks["genesis_bytes_and_root"]=tree==g["commitment"] and tree["root"]==g["project_root"] and g["ID"]=="fco:sha256:"+tree["root"]
        expected_class={"anticube":{"identity":"UNKNOWN","safety":"UNKNOWN","self_safe":None},"checks":{"artifact_hashes_calculated":True,"edge_endpoints_exist":all(e["source"] in {n["id"] for n in graph["nodes"]} and e["target"] in {n["id"] for n in graph["nodes"]} for e in graph["edges"])}}
        checks["initial_classification_calculated"]=graph["initial_classification"]==expected_class and graph["g_star_reference"]==diagnostic([])
        checks["expected_root_matches"]=expected_root is None or g["project_root"]==expected_root
        ledger=rows(base);checks["nonempty_ledger"]=bool(ledger)
        prior=[];checks["all_steps_recomputed"]=True;checks["all_mmr_prefixes_recomputed"]=True
        for i,row in enumerate(ledger):
            valid=row["event_index"]==i+1 and row["project_root"]==g["project_root"]
            if i==0:
                valid=valid and row["event_hash"]==digest(canonical(g)) and row["fco_id"]==g["ID"] and row["merkle_root"]==tree["root"] and row["kind"]=="PROJECT_FREEZE"
            else:
                name="step-%06d.json"%(i+1)
                if row["object_file"]!=name:raise ValueError("invalid object filename")
                obj=read(base/name)
                cl,diag=derive(obj["observation"],prior)
                body={k:v for k,v in obj.items() if k not in ["commitment","fco_id"]}
                step_tree=merkle([{"type":k,"value":body[k]} for k in ["project_root","parent_fco_id","previous_mmr_root","observation","classification","diagnostic","relation","SIGNATURE"]])
                valid=valid and obj["classification"]==cl and obj["diagnostic"]==diag and obj["parent_fco_id"]==ledger[i-1]["fco_id"] and obj["project_root"]==g["project_root"]
                valid=valid and obj["previous_mmr_root"]==mmr(ledger[:i])["root"] and obj["commitment"]==step_tree
                valid=valid and obj["fco_id"]=="fco:sha256:"+step_tree["root"]==row["fco_id"] and row["merkle_root"]==step_tree["root"] and row["event_hash"]==digest(canonical(obj))
                prior.append({"admission":cl["custody_admission"],"g_star":diag["g_star"]})
            checks["all_steps_recomputed"]=checks["all_steps_recomputed"] and valid
            m=mmr(ledger[:i+1])
            checks["all_mmr_prefixes_recomputed"]=checks["all_mmr_prefixes_recomputed"] and read(base/("prefix-%06d.json"%(i+1)))==m and independent_mmr_root(ledger[:i+1])==m["root"]
        return {"PASS":all(checks.values()),"YES_NO":"YES" if all(checks.values()) else "NO",
                "checks":checks,"project_root":g["project_root"],"mmr_root":mmr(ledger)["root"],
                "leaf_count":len(ledger),"trusted_expected_root_supplied":expected_root is not None,
                "SIGNATURE":"NOT_SIGNED","claim_ceiling":"Declared-byte integrity and calculated classification only; no authenticity/safety/causality proof"}
    except (OSError,ValueError,KeyError,TypeError,IndexError) as e:
        return {"PASS":False,"YES_NO":"NO","checks":checks,"error":type(e).__name__}
def verify_artifacts(base,kit):
    try:
        g=read(Path(base)/"genesis.json")
        nodes=[n for n in g["graph"]["nodes"] if n["type"]=="Artifact"]
        return {n["relative_path"] for n in nodes}==set(KIT_FILES) and all(digest((Path(kit)/n["relative_path"]).read_bytes())==n["sha256"] for n in nodes)
    except (OSError,ValueError,KeyError):return False

def main():
    p=argparse.ArgumentParser();p.add_argument("action",choices=["freeze","append","verify"])
    p.add_argument("--directory",required=True);p.add_argument("--kit",default=str(Path(__file__).resolve().parent))
    p.add_argument("--input");p.add_argument("--expected-root")
    a=p.parse_args()
    if a.action=="freeze":r=freeze(a.directory,a.kit)
    elif a.action=="append":
        if not a.input:p.error("--input required for append")
        r=append_step(a.directory,read(a.input))
    else:
        r=verify(a.directory,a.expected_root)
        r["artifact_bytes_match"]=verify_artifacts(a.directory,a.kit)
        r["PASS"]=r["PASS"] and r["artifact_bytes_match"]
        r["YES_NO"]="YES" if r["PASS"] else "NO"
    print(json.dumps(r,indent=2,sort_keys=True))
    if a.action=="verify" and not r["PASS"]:sys.exit(1)
if __name__=="__main__":main()

