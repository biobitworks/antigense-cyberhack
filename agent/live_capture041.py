#!/usr/bin/env python3
"""Read-only live-local evidence capture (041); never calls sponsor APIs or POST.

Captures independently requested GET responses, checks predecessor/typed-edge
continuity and independently decomposed MMR, then commits ordered *sanitized*
samples as a separate Merkle manifest. Local clocks are UNSIGNED.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import custody

def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"Cache-Control":"no-cache"}), timeout=6) as r:
        if r.status != 200:
            raise RuntimeError("unexpected HTTP response")
        raw = r.read(2_000_001)
        if len(raw) > 2_000_000:
            raise RuntimeError("response exceeds 2 MB")
        return json.loads(raw), sha(raw)

def verify_bundle(proof, run):
    rows = proof["ledger"]
    objects = proof["objects"]
    prefixes = proof["prefixes"]
    genesis = proof["genesis"]
    if not rows or len(objects) != len(rows) - 1 or len(prefixes) != len(rows):
        raise ValueError("incomplete proof bundle")
    if genesis["project_root"] != run["project_root"] or rows[0]["fco_id"] != genesis["ID"]:
        raise ValueError("genesis identity mismatch")
    g = genesis["graph"]
    gleaves = ([{"type":"initial_classification","value":g["initial_classification"]},
                {"type":"g_star_reference","value":g["g_star_reference"]},
                {"type":"graph_contract","value":g["contract"]}] +
               [{"type":"node","value":v} for v in g["nodes"]] +
               [{"type":"edge","value":v} for v in g["edges"]])
    if custody.merkle(gleaves) != genesis["commitment"]:
        raise ValueError("genesis leaf commitment mismatch")
    if sha(canon(genesis)) != rows[0]["event_hash"]:
        raise ValueError("genesis event bytes mismatch")
    keys = ["project_root","parent_fco_id","previous_mmr_root","observation",
            "classification","diagnostic","relation","SIGNATURE"]
    for i, obj in enumerate(objects, start=1):
        if obj["relation"] != "DEPENDS_ON_RECORDED_PREDECESSOR":
            raise ValueError("undeclared typed predecessor")
        if obj["parent_fco_id"] != rows[i-1]["fco_id"] or obj["fco_id"] != rows[i]["fco_id"]:
            raise ValueError("predecessor mismatch")
        if obj["previous_mmr_root"] != prefixes[i-1]["root"]:
            raise ValueError("MMR predecessor mismatch")
        if custody.merkle([{"type":k,"value":obj[k]} for k in keys]) != obj["commitment"]:
            raise ValueError("object commitment mismatch")
        if obj["fco_id"] != "fco:sha256:" + obj["commitment"]["root"]:
            raise ValueError("FCO address mismatch")
        if sha(canon(obj)) != rows[i]["event_hash"]:
            raise ValueError("object event hash mismatch")
    for i, row in enumerate(rows):
        if row["event_index"] != i+1 or row["project_root"] != run["project_root"]:
            raise ValueError("event index/project mismatch")
        if custody.independent_mmr_root(rows[:i+1]) != prefixes[i]["root"]:
            raise ValueError("prefix independently recomputed differs")
    root = custody.independent_mmr_root(rows)
    if root != run["mmr_root"]:
        raise ValueError("independent MMR mismatch")
    return root


def inspect(base):
    snap, sh = get(base + "/api/snapshot")
    run, rh = get(base + "/data/run.json")
    proof, ph = get(base + "/data/proof.json")
    rows = proof["ledger"]
    objects = proof["objects"]
    if snap["run"]["id"] != run["id"] or snap["run"]["mmr_root"] != run["mmr_root"]:
        raise ValueError("snapshot/public run changed between requests")
    root = verify_bundle(proof, run)
    stages = {s["name"]:s["state"] for s in run["stages"]}
    review = next((s for s in run["stages"] if s["name"] == "08 Local review action"), None)
    return {
      "observed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
      "monotonic_ns": time.monotonic_ns(),
      "endpoint_sha256":{"snapshot":sh,"run":rh,"proof":ph},
      "run_id":run["id"], "phase":run["phase"],"mmr_root":root,
      "project_root":run["project_root"],"leaves":len(rows),
      "independent_mmr_match":True,"typed_predecessors_checked":len(objects),
      "local_review_action": "OBSERVED" if review else "NOT_TESTED",
      "local_review_signature": "NOT_SIGNED" if review else "NOT_TESTED",
      "sponsors_current_run":{
         "Semgrep":run["sponsors"].get("Semgrep","UNKNOWN"),
         "Akash":run["sponsors"].get("Akash","UNKNOWN"),
         "Pi":run["sponsors"].get("Pi","UNKNOWN"),
         "ClickHouse":"NOT_IN_THIS_RUN"
      },
      "telemetry":{"source":snap["source"],"cpu_count":snap["cpu_count"],
         "memory_total_bytes":snap["memory_bytes"],
         "load_1min":snap["load_average"][0],
         "usage":snap.get("usage",{"state":"NOT_AVAILABLE_RUNNING_SERVER_UNPATCHED"})},
      "ceiling":"new read-only host observation and existing local persisted custody; sponsor status refers to this local run only; remote sponsor operation not replayed"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--url",default="http://127.0.0.1:8790")
    p.add_argument("--samples",type=int,default=5)
    p.add_argument("--interval",type=float,default=2)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    if a.url.rstrip("/") != "http://127.0.0.1:8790":
        p.error("only the bounded loopback server is allowed")
    if not 1 <= a.samples <= 30 or not 0.5 <= a.interval <= 10:
        p.error("sample bounds exceeded")
    dest=Path(a.out)
    if dest.exists():
        p.error("output exists: preserving predecessor")
    dest.parent.mkdir(parents=True,exist_ok=True)
    samples=[]
    with dest.open("x") as f:
        for n in range(a.samples):
            s=inspect(a.url)
            s["sample_sequence"]=n+1
            line=canon(s).decode()+"\n"
            f.write(line);f.flush();os.fsync(f.fileno())
            samples.append(s)
            print("PASS sample",n+1,"MMR",s["mmr_root"][:16],
                  "leaves",s["leaves"],"Semgrep",s["sponsors_current_run"]["Semgrep"],flush=True)
            if n+1<a.samples:
                time.sleep(a.interval)
    tree=custody.merkle([{"type":"sanitized_live_readback","value":s} for s in samples])
    manifest={"schema":"antigense.live_observation.041.v1",
       "recording_support":"LOCAL_READONLY_API_POLL; NOT_PROVIDER_SPONSOR_EXECUTION",
       "samples_file":dest.name,"samples_sha256":sha(dest.read_bytes()),
       "sample_count":len(samples),"ordered_commitment":{"construction":tree["algorithm"],
       "leaves":tree["leaf_count"],"root":tree["root"]},
       "independent_mmr":"OBSERVED_FOR_EACH_SAMPLE",
       "signature":"NOT_SIGNED","wall_clock_attestation":"NOT_TESTED",
       "video_frame_binding":"NOT_TESTED; bind separately after recording"}
    manifest_path=dest.with_name(dest.stem + ".manifest.json")
    with manifest_path.open("x") as f:
        f.write(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
        f.flush();os.fsync(f.fileno())
    print(json.dumps(manifest,sort_keys=True))
if __name__=="__main__":
    main()
