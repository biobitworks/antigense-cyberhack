#!/usr/bin/env python3
"""Read-only verification of paste-ready field lengths and release boundaries."""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ROOT / "docs/TOKENSAND_SUBMISSION_051_PASTE_READY.md"
VIDEO = ROOT / "docs/VIDEO_051_NARRATION_AND_SHOTLIST.md"
LIMITS = {
    "One-sentence description (max 300 characters)": 300,
    "Project description (max 1,500 characters)": 1500,
    "Technical architecture (max 1,200 characters)": 1200,
    "Setup instructions (max 1,200 characters)": 1200,
    "Lessons learned (max 1,200 characters)": 1200,
}

def blocks(text):
    return {k: v.rstrip() for k, v in
            re.findall(r"(?m)^## (.+)\n\n([\s\S]*?)(?=^## |\Z)", text)}

def main():
    text = FIELDS.read_text()
    video = VIDEO.read_text()
    fields = blocks(text)
    checks = {}
    for label, maximum in LIMITS.items():
        value = fields.get(label, "")
        checks[label] = bool(value) and len(value) <= maximum
        print(f"{label}: {len(value)} / {maximum} — {'PASS' if checks[label] else 'FAIL'}")
    checks["same_canonical_project"] = (
        "https://tokensand.com/p/antigense-daisy" in text
        and fields.get("Project name (keep existing)") == "Antigense Daisy")
    checks["existing_fallback_video"] = "https://youtu.be/hpLH88V6PF0" in text
    checks["separate_local_successor"] = ("NOT PUSHED" in text and
        "NOT remotely hosted" in text and
        "NOT remotely hosted" in text)
    checks["video_unpublished"] = "VIDEO_NOT_RECORDED" in video
    checks["scope_limited"] = all(v in text for v in (
        "Pi", "TEE", "NOT_TESTED", "LOCAL"))
    checks["has_no_new_video_url_fabrication"] = (
        "NEW_VIDEO_URL_UNKNOWN" in video)
    for key, status in checks.items():
        if key not in LIMITS: print(f"{key}: {'PASS' if status else 'FAIL'}")
    if "--check-local" in sys.argv:
        try:
            with urllib.request.urlopen("http://127.0.0.1:8850/api/public",
                                        timeout=4) as r:
                snap = json.load(r)
            checks["local_050_server"] = (snap["chain_pass"] is True
                and snap["runtime_code_bound"] is True
                and snap["frozen_artifacts_bound"] is True)
        except Exception:
            checks["local_050_server"] = False
        print("local_050_server:",
              "PASS" if checks["local_050_server"] else "FAIL_OR_OFFLINE")
    if not all(checks.values()):
        raise SystemExit("SUBMISSION_051_PRECHECK_FAILED")
    print("SUBMISSION_051_PRECHECK_PASS; no Tokens& save or cloud write performed")

if __name__ == "__main__":
    main()
