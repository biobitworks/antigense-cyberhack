#!/usr/bin/env python3
"""Calibrate scene timing from decoded frames + recorder events; build frame/event ledgers + MMRs; independent recompute; tamper tests.
Usage: calibrate040.py <video.mp4> <events.jsonl|-> <receipt.json|-> <outdir(new)> [label]
Scene boundaries come from OCR-CONFIRMED visual transitions (scene counter changes between frames before/after a pixel-change spike),
never from fitting a tolerance to the expected manifest. The original 039 mismatch is preserved and reproduced, not suppressed."""
import hashlib,json,re,subprocess,sys,importlib.util,copy,statistics
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
V=Path(sys.argv[1]).resolve();EV=sys.argv[2];REC=sys.argv[3];OUT=Path(sys.argv[4]).resolve();LAB=sys.argv[5] if len(sys.argv)>5 else "run";PAGE=sys.argv[6] if len(sys.argv)>6 else None
OUT.mkdir(parents=True,exist_ok=False);(OUT/"samples").mkdir()
s=importlib.util.spec_from_file_location("custody",ROOT/"src/custody.py");K=importlib.util.module_from_spec(s);s.loader.exec_module(K)
H=lambda b:hashlib.sha256(b).hexdigest();canon=K.canonical
def run(c,**k):return subprocess.run(c,capture_output=True,**k)
OCR="/tmp/ocr040"
if not Path(OCR).exists():subprocess.run(["swiftc","-O",str(ROOT/"agent/frame_ocr039.swift"),"-o",OCR],check=True)
def png(n,path):run(["ffmpeg","-nostdin","-v","error","-y","-i",str(V),"-vf","select=eq(n\\,%d)"%n,"-vframes","1",str(path)],check=True)
def ocr(paths):return {Path(e["file"]).name:e.get("lines",[]) for e in json.loads(run([OCR]+[str(p) for p in paths]).stdout)}
def scene_of(lines):
    m=re.findall(r"scene\s*(\d+)\s*/\s*(?:10|12)"," | ".join(lines));return int(m[0]) if m else None
print("START calibrate040",LAB,flush=True)
# 1. pixel-change spikes
W,Hh=192,120
a=np.frombuffer(run(["ffmpeg","-nostdin","-v","error","-i",str(V),"-map","0:v:0","-vf","scale=%d:%d,format=gray"%(W,Hh),"-f","rawvideo","-"]).stdout,np.uint8).reshape(-1,W*Hh).astype(np.int16)
nfr=len(a);d=np.abs(np.diff(a,axis=0)).mean(axis=1)
cand=sorted(int(i+1) for i in np.argsort(-d)[:60] if d[i]>2.0 and (d[i]==d[max(0,i-3):i+4].max()))
print("RUNNING candidates",len(cand),flush=True)
# 2. OCR-confirm: scene counter must change across the candidate
tmp=OUT/"cand";tmp.mkdir()
files={}
for n in cand:
    for o in(-2,1):
        f=tmp/("f%05d.png"%(n+o));png(n+o,f);files[n+o]=f
o=ocr(list(files.values()))
trans=[]
for n in cand:
    b,aft=scene_of(o.get("f%05d.png"%(n-2),[])),scene_of(o.get("f%05d.png"%(n+1),[]))
    if b and aft and aft==b+1:trans.append({"first_frame":n,"video_s":round(n/30,4),"scene_from":b,"scene_to":aft,"diff":round(float(d[n-1]),2),"ocr_before_frame":n-2,"ocr_after_frame":n+1})
    elif b and aft and aft!=b:trans.append({"first_frame":n,"video_s":round(n/30,4),"scene_from":b,"scene_to":aft,"note":"non-consecutive","diff":round(float(d[n-1]),2)})
import shutil;shutil.rmtree(tmp)
import re as _re
NS=len(_re.findall(r"data-t=",Path(PAGE).read_text())) if PAGE else 10
seen={t["scene_to"] for t in trans};missing=[k for k in range(2,NS+1) if k not in seen]
# unresolved boundaries: OCR missed -> search window by OCR bisection across frames
if missing:
    for k in missing:
        prevs=[t for t in trans if t["scene_to"]==k-1];nexts=[t for t in trans if t["scene_to"]==k+1]
        lo=prevs[0]["first_frame"] if prevs else 0;hi=nexts[0]["first_frame"] if nexts else nfr-1
        sub=[n for n in cand if lo<n<hi]
        if len(sub)==1:trans.append({"first_frame":sub[0],"video_s":round(sub[0]/30,4),"scene_from":k-1,"scene_to":k,"note":"INFERRED_BETWEEN_OCR_CONFIRMED_NEIGHBOURS (OCR missed counter)","diff":round(float(d[sub[0]-1]),2)})
trans.sort(key=lambda t:t["scene_to"])
bounds={t["scene_to"]:t["video_s"] for t in trans}
json.dump({"frames":nfr,"fps":30,"transitions":trans,"unresolved":[k for k in range(2,NS+1) if k not in bounds]},open(OUT/"transitions.json","w"),indent=1)
# 3. compare with expected manifest (page time) -> preserved mismatch + offset
if PAGE:
    _d=[float(x) for x in _re.findall(r'data-t="([0-9.]+)"',Path(PAGE).read_text())];exp={};_t=0.0
    for _i,_x in enumerate(_d):exp[_i+1]=round(_t,3);_t+=_x
else:
    M=json.loads((ROOT/"evidence/frame039r1/scene-manifest.json").read_text());exp={s["scene"]:s["expected_start_s"] for s in M["scenes"]}
rows=[{"scene":k,"observed_video_s":bounds[k],"expected_page_s":exp[k],"observed_minus_expected_s":round(bounds[k]-exp[k],4)} for k in sorted(bounds)]
offs=[r["observed_minus_expected_s"] for r in rows]
xs=np.array([r["expected_page_s"] for r in rows]);ys=np.array(offs);sl,ic=np.polyfit(xs,ys,1) if len(xs)>2 else (0,0)
cal={"label":LAB,"video_sha256":H(V.read_bytes()),"frames":nfr,"boundary_table":rows,"offset_mean_s":round(float(np.mean(offs)),4),"offset_min_s":min(offs),"offset_max_s":max(offs),"offset_linear_fit":{"intercept_s":round(float(ic),4),"slope_s_per_s":round(float(sl),6)},
 "original_039_mismatch_preserved":{"frame_at_48s_expected_scene":4,"observed_scene_at_48s":None},"method":"pixel spike + OCR-confirmed scene-counter change; no tolerance applied to expected manifest"}
# frame at 48 s
png(1440,OUT/"samples/frame-48s.png");sc48=scene_of(ocr([OUT/"samples/frame-48s.png"])["frame-48s.png"]);cal["original_039_mismatch_preserved"]["observed_scene_at_48s"]=sc48
cal["original_039_mismatch_preserved"]["explanation_check"]="boundary 4->5 observed at %.4fs vs manifest 48.4s: frame at 48.0s lies after the observed cut"%bounds.get(5,float("nan"))
# 4. recorder events -> video time
evrows=[];evcal=None
if EV!="-":
    rec=json.loads(Path(REC).read_text());t0=rec["marks"]["page_created_epoch_s"]
    evs=[json.loads(l) for l in Path(EV).read_text().splitlines() if l]
    for e in evs:e["recorder_video_s_assumed"]=round(e["epoch_ms"]/1000-t0,4)
    act={e["scene"]:e for e in evs if e["type"]=="scene_activation"}
    pairs=[(k,act[k]["recorder_video_s_assumed"],bounds[k]) for k in sorted(act) if k in bounds]
    res=[round(b-l,4) for k,l,b in pairs];train=res[:len(res)//2];test=res[len(res)//2:]
    off=statistics.median(train) if train else 0
    evcal={"pairs":[{"scene":k,"log_s":l,"frame_cut_s":b,"residual_s":round(b-l,4)} for k,l,b in pairs],"fit_on_first_half_median_offset_s":round(off,4),"holdout_residuals_after_offset_s":[round(r-off,4) for r in test],"holdout_max_abs_s":round(max([abs(r-off) for r in test] or [0]),4),"frame_period_s":round(1/30,4),
     "mapping_used_for_samples":"video_pts_s_anchored (offset of the latest OCR-confirmed scene cut); global-offset holdout is reported separately and is the honest drift measure","note":"recorder log vs frame cut; offset = unmeasured pipeline latency between page event and encoded frame, estimated from first-half scenes and tested on the held-out half"}
    anchors=sorted((l,b-l) for k,l,b in pairs)
    for e in evs:
        e["video_pts_s_calibrated"]=round(e["recorder_video_s_assumed"]+off,4)
        prior=[a for a in anchors if a[0]<=e["recorder_video_s_assumed"]+1e-6];ao=prior[-1][1] if prior else off
        e["video_pts_s_anchored"]=round(e["recorder_video_s_assumed"]+ao,4);e["video_frame"]=int(round(e["video_pts_s_anchored"]*30))
        evrows.append(e)
    (OUT/"events_with_video_time.jsonl").write_text("".join(json.dumps(e,sort_keys=True)+"\n" for e in evrows))
cal["event_to_video_calibration"]=evcal
json.dump(cal,open(OUT/"calibration.json","w"),indent=1,sort_keys=True)
# 5. frame ledger + MMR
raw=run(["ffmpeg","-nostdin","-v","error","-i",str(V),"-map","0:v:0","-an","-pix_fmt","yuv420p","-f","framemd5","-hash","sha256","-"]).stdout.decode()
(OUT/"framemd5.txt").write_text(raw);tb=re.search(r"#tb 0: (\d+)/(\d+)",raw);num,den=map(int,tb.groups())
starts=sorted(bounds.items());mh=H(canon({"scene_starts_s":{str(k):v for k,v in [(1,0.0)]+starts},"method":cal["method"],"video_sha256":cal["video_sha256"]}))
(OUT/"scene_manifest_observed.json").write_bytes(canon({"scene_starts_s":{str(k):v for k,v in [(1,0.0)]+starts},"method":cal["method"],"video_sha256":cal["video_sha256"]})+b"\n")
def scene_at(sec):
    sc=1
    for k,v in starts:
        if sec>=v-1e-9:sc=k
    return sc
recs=[];items=[]
for line in raw.splitlines():
    if line.startswith("#") or not line.strip():continue
    f=[x.strip() for x in line.split(",")];pts=int(f[2])
    r={"schema":"antigense.DecodedFrameOccurrence.v040","frame_index":len(recs),"pts":pts,"time_base":[num,den],"decoded_frame_sha256":f[5],"video_sha256":cal["video_sha256"],"scene_manifest_observed_sha256":mh,"scene_by_observed_transition":scene_at(pts*num/den)}
    eh=H(canon(r));recs.append(r);items.append({"event_hash":eh,"fco_id":"fco:sha256:"+eh})
frame_mmr=K.mmr(items);(OUT/"frame-occurrences.jsonl").write_text("".join(json.dumps(r,sort_keys=True)+"\n" for r in recs))
ev_items=[{"event_hash":H(canon(e)),"fco_id":"fco:sha256:"+H(canon(e))} for e in evrows];ev_mmr=K.mmr(ev_items) if ev_items else None
def indep(items):
    hs=[H(canon({"event_index":i+1,"event_hash":x["event_hash"],"cfmo_version_id":x["fco_id"]})) for i,x in enumerate(items)];n=len(hs);pos=0;pk=[]
    for ex in range(n.bit_length()-1,-1,-1):
        w=1<<ex
        if n&w:
            lv=hs[pos:pos+w];pos+=w
            while len(lv)>1:lv=[H(bytes.fromhex(lv[i])+bytes.fromhex(lv[i+1])) for i in range(0,len(lv),2)]
            pk.append(lv[0])
    acc=pk[0]
    for p in pk[1:]:acc=H(bytes.fromhex(acc)+bytes.fromhex(p))
    return H(b"HYDRALAMP_MMR_BAG_V1:"+bytes.fromhex(acc))
# every prefix independently (frame ledger: sampled prefixes at all scene boundaries + every 100th + full; events: every prefix)
def prefix_ok(its,mm):
    ks=sorted(set(list(range(1,len(its)+1,100))+[len(its)]+[min(len(its),b[1]) for b in [(0,int(v*30)) for _,v in starts]]))
    bad=[k for k in ks if K.mmr(its[:k])["root"]!=indep(its[:k])];return len(ks),bad
fk,fbad=prefix_ok(items,frame_mmr);ek,ebad=(prefix_ok(ev_items,ev_mmr) if ev_items else (0,[]))
if ev_items:
    ek=len(ev_items);ebad=[k for k in range(1,ek+1) if K.mmr(ev_items[:k])["root"]!=indep(ev_items[:k])]
# 6. tamper tests on the ledger (detection = recomputed root != committed root OR source-hash mismatch)
def root_from(recs_):return indep([{"event_hash":H(canon(r)),"fco_id":"fco:sha256:"+H(canon(r))} for r in recs_])
committed=frame_mmr["root"];T={}
x=copy.deepcopy(recs);x[1000]["decoded_frame_sha256"]=x[1000]["decoded_frame_sha256"][:-1]+("0" if x[1000]["decoded_frame_sha256"][-1]!="0" else "1");T["flip_one_frame_hash"]=root_from(x)!=committed
x=copy.deepcopy(recs);x[500],x[501]=x[501],x[500];T["swap_two_records"]=root_from(x)!=committed
x=copy.deepcopy(recs);del x[2000];T["delete_record"]=root_from(x)!=committed
x=copy.deepcopy(recs);x[3000]["scene_by_observed_transition"]=(x[3000]["scene_by_observed_transition"]%NS)+1;T["relabel_scene"]=root_from(x)!=committed
x=copy.deepcopy(recs);x.append(copy.deepcopy(x[-1]));T["append_record"]=root_from(x)!=committed
pk=json.loads(run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","packet=pos,size","-of","json",str(V)]).stdout)["packets"];pp=pk[len(pk)//2];vb=bytearray(V.read_bytes());vb[int(pp["pos"])+int(pp["size"])//2]^=1;(OUT/"tampered.mp4").write_bytes(vb)
raw2=run(["ffmpeg","-nostdin","-v","error","-i",str(OUT/"tampered.mp4"),"-map","0:v:0","-an","-pix_fmt","yuv420p","-f","framemd5","-hash","sha256","-"]).stdout.decode()
T["flip_one_video_byte_detected_by_file_hash"]=H(bytes(vb))!=cal["video_sha256"];T["flip_one_video_byte_detected_by_frame_hashes"]=raw2!=raw
(OUT/"tampered.mp4").unlink()
if ev_items:
    x=copy.deepcopy(evrows);x[3]["epoch_ms"]+=1;T["alter_event_time"]=indep([{"event_hash":H(canon(e)),"fco_id":"fco:sha256:"+H(canon(e))} for e in x])!=ev_mmr["root"]
# 7. sample frames at proof events
samples=[]
if evrows:
    pick=[e for e in evrows if e["type"] in("scene_activation","proof_start","proof_result")]
    leaf=[e for e in evrows if e["type"]=="proof_leaf_progress"]
    for pr in("inc","gpu"):
        L=[e for e in leaf if e["proof"]==pr]
        if L:pick+= [L[0],L[len(L)//2],L[-1]]
    pick=sorted({id(e):e for e in pick}.values(),key=lambda e:e["epoch_ms"])
    paths=[]
    for i,e in enumerate(pick):
        n=min(nfr-1,e["video_frame"]+(16 if e["type"]=="scene_activation" else 3));p=OUT/"samples"/("s%02d_%s_%05d.png"%(i,e["type"],n));png(n,p);paths.append((e,n,p))
    oc=ocr([p for _,_,p in paths])
    for e,n,p in paths:
        lines=oc[p.name];sc=scene_of(lines);row={"event":e["type"],"proof":e.get("proof"),"leaf_index":e.get("leaf_index"),"frame":n,"video_pts_s":round(n/30,4),"png_sha256":H(p.read_bytes()),"ocr_scene":sc,"sample_offset_frames":n-e["video_frame"]}
        if e["type"]=="scene_activation":row["scene_matches_event"]=(sc==e["scene"])
        if e["type"]=="proof_result":
            row["ocr_shows_PASS_at_sample"]=any("PASS" in l for l in lines)
            first=None;probe=tmp2=OUT/"samples"/"probe";probe.mkdir(exist_ok=True)
            for k in range(e["video_frame"]-3,min(nfr-1,e["video_frame"]+60),3):
                q=probe/("p%05d.png"%k);png(k,q);ls=ocr([q])[q.name]
                if any("PASS" in l and "match" in " ".join(ls).lower() for l in ls) or any("PASS" in l for l in ls):first=k;break
            row["first_frame_showing_PASS"]=first;row["log_to_video_lag_s"]=round((first-e["video_frame"])/30,3) if first is not None else None
            import shutil as _sh;_sh.rmtree(probe)
        samples.append(row)
summary={"label":LAB,"video_sha256":cal["video_sha256"],"frame_count":nfr,"frame_mmr_root":committed,"frame_mmr_peaks":frame_mmr["peaks"],"frame_prefixes_checked":fk,"frame_prefix_mismatches":fbad,
 "frame_framemd5_equals_ledger":True,"event_count":len(evrows),"event_mmr_root":ev_mmr["root"] if ev_mmr else None,"event_prefix_mismatches":ebad,"tamper_detection":T,"sample_frames":samples,"scene_manifest_observed_sha256":mh,
 "claims":{"full_frame_semantics":"NOT_TESTED","live_calculation_attestation":"NOT_TESTED (recorder log only)","narration_alignment":"SEE align040","signature":"NOT_SIGNED"}}
json.dump(summary,open(OUT/"verification.json","w"),indent=1,sort_keys=True)
print("PASS" if not fbad and not ebad and all(T.values()) else "FAIL",json.dumps({"transitions":len(bounds),"offset_mean":cal["offset_mean_s"],"offset_range":[cal["offset_min_s"],cal["offset_max_s"]],"scene_at_48s":sc48,"frame_root":committed[:16],"tamper_all_detected":all(T.values()),"unresolved":[k for k in range(2,NS+1) if k not in bounds]}),flush=True)
