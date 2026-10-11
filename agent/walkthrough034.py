#!/usr/bin/env python3
"""Build public/data/walkthrough-034.json from existing receipts (read-only inputs).

Inputs: public/data/proof.json + run.json (incident run-20261009T191354Z-a98b5c03)
and evidence/successor_024 (separate Akash GPU branch). Every input file's
SHA-256 is recorded so the walkthrough page shows exactly what it replays.
No network, no sponsor calls. Usage: python agent/walkthrough034.py
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public/data/walkthrough-034.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    # Pinned snapshots (recovered byte-identical from the live site); the working-tree
    # copies under public/data are edited by another session and are not stable inputs.
    snap = ROOT / "evidence/walkthrough/sources"
    proof_p, run_p = snap / "proof.json", snap / "run.json"
    proof, run = json.loads(proof_p.read_text()), json.loads(run_p.read_text())
    steps = {o["observation"]["name"][:2]: o["observation"] for o in proof["objects"]}
    pick = lambda n, keys: {k: steps[n]["value"].get(k) for k in keys}
    ch = steps["12"]["value"]

    gpu_dir = ROOT / "evidence/successor_024"
    gpu_ledger = [json.loads(l) for l in (gpu_dir / "ledger.jsonl").read_text().splitlines() if l]
    gpu_steps = {}
    for f in sorted(gpu_dir.glob("step-*.json")):
        o = json.loads(f.read_text())["observation"]
        gpu_steps[o["name"]] = o["details"]
    inf, vram, close = gpu_steps["gpu_inference"], gpu_steps["gpu_provider_reported_vram"], gpu_steps["gpu_close_deployment"]
    last_prefix = json.loads((gpu_dir / f"prefix-{len(gpu_ledger):06d}.json").read_text())

    data = {
        "id": "walkthrough-034",
        "label": "RECORDED REPLAY - walkthrough 034. No sponsor requests are made by this page.",
        "roles": "ChatGPT/OpenAI orchestrates; Claude executes an independent lane. No Ollarma bridge delivery is claimed.",
        "sources": {
            "public/data/proof.json": sha(proof_p),
            "public/data/run.json": sha(run_p),
            "evidence/successor_024/ledger.jsonl": sha(gpu_dir / "ledger.jsonl"),
        },
        "incident": {
            "id": run["id"], "expected_mmr_root": run["mmr_root"], "leaf_count": run["leaf_count"],
            "ledger": [{k: r[k] for k in ("event_index", "event_hash", "fco_id")} for r in proof["ledger"]],
            "fault": pick("02", ["fault", "xor_mask", "original_sha256", "corrupted_sha256", "hardware_fault_observed"]),
            "fallback": steps["03"]["value"],
            "semgrep_before": pick("04", ["count", "findings", "version", "rule_sha256", "target", "target_sha256"]),
            "semgrep_after": pick("11", ["count", "version", "rule_sha256", "target", "target_sha256"]),
            "matrix": steps["10"]["value"]["cases"],
            "clickhouse": {k: ch.get(k) for k in ("http", "rows_sent", "replay_rows_sent", "readback_rows", "readback_sha256", "query_ms", "insert_ms", "replay_ms",
                           "occurrence_count_preserved", "exact_values_match", "query")},
            "clickhouse_checks": steps["12"]["checks"],
        },
        "gpu": {
            "record": "evidence/successor_024", "expected_mmr_root": last_prefix["root"], "leaf_count": len(gpu_ledger),
            "ledger": [{k: r[k] for k in ("event_index", "event_hash", "fco_id")} for r in gpu_ledger],
            "inference": {k: inf.get(k) for k in ("status", "model", "ms", "schema_valid", "eval_count",
                          "prompt_eval_count", "advice_excerpt")},
            "vram": vram.get("models"),
            "close": {k: close.get(k) for k in ("status", "response")},
            "separate_from_incident": True,
            "not_claimed": ["hardware attestation", "verified final closed state", "measured billing", "cost savings"],
        },
    }
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print("wrote", OUT.relative_to(ROOT), sha(OUT)[:16])


if __name__ == "__main__":
    main()
