#!/usr/bin/env python3
"""Verify every custody record against the git commit its files were frozen from.

Each record's chain (every Merkle/MMR prefix) is recomputed from its own files.
Frozen source bytes are compared against a clean `git archive` of the pinned
commit, so later working-tree edits (for example to the public site) cannot
mask or fake a result. Prints one line per record and exits non-zero on any FAIL.

Usage: .venv/bin/python agent/verify_all.py [--json]
"""
import importlib.util, json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PINNED = "06bbb103765cc2248ad6d9b3d78bc35bcc96fd60"  # all successor freezes' bytes are committed here
HISTORICAL = "6171b7be3afea219babf215b6a19e7daff231116"  # original 009R2 freeze

# (record, module that owns it, what it shows)
RECORDS = [
    ("final_custody", None, "Original incident, 12 leaves (historical)"),
    ("successor_011", "agent011", "Monitor, Semgrep 1->0, publication + readback"),
    ("successor_012", "telemetry012", "ClickHouse local telemetry"),
    ("successor_015", "ch015", "ClickHouse Cloud, first try (hash-format mismatch kept)"),
    ("successor_016", "ch016", "ClickHouse Cloud exact readback + own-code Semgrep"),
    ("successor_019", "akash019", "AkashML attempt (401, kept)"),
    ("successor_020", "akash020", "AkashML attempt, blocked by a concurrent site edit (kept)"),
    ("successor_021", "akash021", "AkashML diagnosis: Console key used (401, kept)"),
    ("successor_022", "akash_console022", "Akash Console call: Cloudflare 1010 (kept)"),
    ("successor_023", "akash_console023", "Akash Console read-only call (200)"),
    ("successor_024", "akash_gpu024", "Akash GPU deployment + inference + close"),
]


# Records whose frozen file bytes exist in no commit (a concurrent uncommitted
# edit, or a governed file edited after freezing). Their chains still recompute.
CHAIN_ONLY = {
    "successor_019": "froze public/index.html while another session had uncommitted edits; those bytes are in no commit",
    "successor_020": "same index.html issue; also docs/ADDENDUM_020.md was appended to after this freeze (custody mistake, kept visible)",
    "successor_022": "docs/ADDENDUM_022.md was appended to after this freeze (custody mistake, kept visible)",
}


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, check=True).stdout


def snapshot(commit):
    # Copy each tracked file's committed bytes. No archive extraction, and every
    # path must stay inside the snapshot directory.
    d = Path(tempfile.mkdtemp(prefix="kit-")).resolve()
    for rel in git("ls-tree", "-r", "--name-only", "-z", commit).decode().split("\0"):
        if not rel:
            continue
        dest = (d / rel).resolve()
        if not dest.is_relative_to(d):
            raise ValueError(f"path escapes snapshot: {rel!r}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(git("show", f"{commit}:{rel}"))
    return d


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "agent" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "A", mod)  # wrappers expose the base module as A


def main():
    pinned, historical = snapshot(PINNED), snapshot(HISTORICAL)
    custody = load("agent011").C
    rows = []
    for record, module, label in RECORDS:
        base = ROOT / "evidence" / record
        if module is None:
            r = custody.verify(base)
            r["artifact_bytes_match"] = custody.verify_artifacts(base, historical)
            commit = HISTORICAL
        else:
            A = load(module)
            r = A.C.verify(base)  # chain only
            r["artifact_bytes_match"] = A.artifacts_ok(base, pinned)
            commit = PINNED
        chain = bool(r.get("PASS"))
        if chain and r.get("artifact_bytes_match"):
            status = "PASS"
        elif chain and record in CHAIN_ONLY:
            status = "CHAIN_ONLY"  # chain recomputes; some frozen bytes were never committed
        else:
            status = "FAIL"
        rows.append({"record": record, "shows": label, "status": status, "leaves": r.get("leaf_count"),
                     "mmr_root": r.get("mmr_root"), "bytes_checked_against": commit[:7],
                     "note": CHAIN_ONLY.get(record) if status == "CHAIN_ONLY" else None})
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2))
    else:
        for x in rows:
            print(f"{x['status']:<10} {x['record']:<15} {x['leaves']:>3} leaves  {x['mmr_root'][:16]}  {x['shows']}")
            if x["note"]:
                print(f"{'':<10} note: {x['note']}")
    sys.exit(1 if any(x["status"] == "FAIL" for x in rows) else 0)


if __name__ == "__main__":
    main()
