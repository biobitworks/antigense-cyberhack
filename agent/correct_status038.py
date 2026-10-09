#!/usr/bin/env python3
"""Correct public/data/defense-status.json from its own custody receipts.

The file (run run011-ad35173536c3, sha256 7ecbf592...) says Akash was
"NOT_TESTED: no credentials supplied", but receipt step-000070 records FAILED,
HTTP 401. It was also never authorized for publication (step-000074:
publication NOT_TESTED). This keeps the old bytes under evidence/status/ and
writes a corrected file that changes only the wrong field and states why.
Deterministic: same inputs, same output bytes. Usage: python agent/correct_status038.py
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public/data/defense-status.json"
OLD_SHA = "7ecbf592270a2e4a907bab78fbd537ce24da91bddbe2fd2beab8db904ed36ec7"
KEEP = ROOT / f"evidence/status/defense-status-{OLD_SHA[:16]}.json"
sha = lambda b: hashlib.sha256(b).hexdigest()


def main():
    old = KEEP.read_bytes() if KEEP.exists() else PUB.read_bytes()
    if sha(old) != OLD_SHA:
        raise SystemExit("unexpected source bytes; refusing to correct")
    KEEP.parent.mkdir(parents=True, exist_ok=True)
    KEEP.write_bytes(old)
    inf = json.loads((ROOT / "evidence/successor_011/step-000070.json").read_text())["observation"]
    pub = json.loads((ROOT / "evidence/successor_011/step-000074.json").read_text())["observation"]
    assert inf["name"] == "akash_inference" and inf["occurrence"]["run_id"] == "run011-ad35173536c3"
    assert pub["name"] == "publication" and pub["details"]["artifact_sha256"] == OLD_SHA
    d = json.loads(old)
    was = d["akash"]["ceiling"]
    det = inf["details"]
    d["akash"]["ceiling"] = f"{det['state']}: {det['reason']} (HTTP {det['http']})"
    d["correction"] = {
        "supersedes_sha256": OLD_SHA,
        "superseded_copy": str(KEEP.relative_to(ROOT)),
        "corrected_fields": {"akash.ceiling": {"was": was, "now": d["akash"]["ceiling"]}},
        "source_receipt": "evidence/successor_011/step-000070.json",
        "reason": "the original reported every Akash failure as missing credentials; the receipt records a credentialed HTTP 401 (bug fixed in agent011.py, PR #1 d5d032a)",
        "publication_note": "the original was a candidate never authorized for publication (step-000074: NOT_TESTED); it reached the site through a later deploy. This correction is published deliberately.",
        "later_akash_result": "a separate Console API GPU run succeeded later (evidence/successor_024); this file describes run run011-ad35173536c3 only",
    }
    PUB.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n")
    print("old kept", KEEP.relative_to(ROOT), "| corrected", sha(PUB.read_bytes()))


if __name__ == "__main__":
    main()
