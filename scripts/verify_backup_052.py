#!/usr/bin/env python3
"""Independent, offline verification of published static backup 052 bytes.

A successful check establishes repository-byte custody against its manifest,
not historical recording authenticity, uploader identity or MMR commitment.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public"
MANIFEST = ROOT / "evidence/backup_052/asset_manifest.json"


def verify() -> dict:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = {}
    names = []
    for a in m["assets"]:
        rel = Path(a["public_path"])
        names.append(a["public_path"])
        if rel.is_absolute() or ".." in rel.parts or str(rel).startswith("."):
            checks[a["public_path"]] = False
            continue
        target = BASE / rel
        data = target.read_bytes() if target.is_file() and not target.is_symlink() else None
        checks[a["public_path"]] = (data is not None and
                                    len(data) == a["bytes"] and
                                    hashlib.sha256(data).hexdigest() == a["sha256"])
    return {
        "PASS": bool(checks) and all(checks.values()) and len(names) == len(set(names))
                and len(checks) == m["asset_count"],
        "asset_count": len(checks),
        "checks": checks,
        "mmr": "NOT_COMPUTED",
        "signature": "NOT_SIGNED",
        "source_authenticity": "NOT_ATTESTED",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    p.parse_args()
    r = verify()
    print(json.dumps(r, indent=2, sort_keys=True))
    raise SystemExit(0 if r["PASS"] else 1)
