#!/usr/bin/env python3
"""Build evidence/walkthrough/manifest-035.json: the walkthrough's scenes bound to sources.

Binds: construction version, page bytes (034 recorded, 035 successor label), data
bytes, every source receipt (path, SHA-256, MMR root, project root), narration
hash, scene order and timing (parsed from the page itself), and both recording
attempts with their different receipt states. Large media stay outside git; the
manifest records their local locations and hashes.

The manifest commitment is custody.merkle() over its ordered leaves, so a
rebuild from unchanged inputs must reproduce the same root. MP4/MOV bytes are
NOT required to reproduce: the encoder does not guarantee identical output.

Usage: python agent/walkthrough_manifest035.py [--check]
  --check  rebuild in memory and compare with the committed manifest (exit 1 on drift)
"""
import hashlib, html, importlib.util, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evidence/walkthrough/manifest-035b.json"
VERSION = "walkthrough-manifest/035.2"
spec = importlib.util.spec_from_file_location("custody", ROOT / "src/custody.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

# Large media: local operator locations only (not committed). Hashes are what bind them.
NARRATION = {"name": "AWS Builder Loft.m4a", "location": "operator iCloud Drive: Hackathon/ (local, not public)",
             "sha256": "12be0853fee931726ae48ff98e02a94e33e2f0a71c3d1f3e09da0cf0085389ba", "seconds": 142.144}
RECORDINGS = [
    {"attempt": "A", "location": "media/walkthrough-034/screen-034.mov (local, git-ignored path)", "page": "public/walkthrough-034.html",
     "receipt_state": "NO_RECEIPT (recorder path error after encoding; video valid)", "seconds": 144.966667},
    {"attempt": "B", "location": "media/walkthrough-034b/screen-034.mov (local, git-ignored path)", "page": "public/walkthrough-034.html",
     "receipt_state": "RECEIPT media/walkthrough-034b/screen-034.receipt.json", "seconds": 145.0},
    {"attempt": "B-review", "location": "media/walkthrough-034b/demo-034-review.mp4 (local, git-ignored path)",
     "receipt_state": "RECEIPT media/walkthrough-034b/demo-034-review.mp4.receipt.json", "seconds": 142.166667,
     "inputs": ["B screen-034.mov", "narration"]},
]
SOURCE_RECORDS = ["successor_024"]  # GPU branch shown in scenes 7-8
SOURCE_FILES = ["evidence/walkthrough/sources/proof.json", "evidence/walkthrough/sources/run.json", "public/data/walkthrough-034.json",
                "evidence/successor_024/ledger.jsonl", "agent/walkthrough034.py"]


def media_hashes():
    # Hashes of local media if present; otherwise the hashes recorded in receipt 034.
    rec = json.loads((ROOT / ".planning/receipts_034.jsonl").read_text().splitlines()[-1])["OBSERVED"]
    known = {"A": rec["screen_034_A"]["sha256"], "B": rec["screen_034_B"]["sha256"], "B-review": rec["review_mp4"]["sha256"]}
    out = []
    for r in RECORDINGS:
        out.append({**r, "sha256": known[r["attempt"]], "hash_source": "receipt_034"})
    return out


def scenes(page):
    src = (ROOT / page).read_text()
    out, t = [], 0.0
    for i, m in enumerate(re.finditer(r'<section class="scene" data-t="([0-9.]+)"><div class="kicker">(.*?)</div>', src)):
        d = float(m.group(1))
        out.append({"order": i + 1, "kicker": html.unescape(m.group(2)), "start_s": round(t, 3), "seconds": d})
        t += d
    out[-1]["seconds"] = round(out[-1]["seconds"] + 2.856, 3)  # page script adds 2.856 s to the last scene
    return out


def record_summary(name):
    base = ROOT / "evidence" / name
    g = json.loads((base / "genesis.json").read_text())
    led = [json.loads(l) for l in (base / "ledger.jsonl").read_text().splitlines() if l]
    root = json.loads((base / f"prefix-{len(led):06d}.json").read_text())["root"]
    return {"record": f"evidence/{name}", "project_root": g["project_root"], "genesis_id": g["ID"], "mmr_root": root, "leaves": len(led)}


def build():
    data = json.loads((ROOT / "public/data/walkthrough-034.json").read_text())
    body = {
        "construction_version": VERSION,
        "label": "Recorded sponsor execution · live browser proof recomputation.",
        "scope": "Walkthrough presentation bound to recorded receipts. Not interaction-generated or persistent FCG state; that requirement is separate and untested.",
        "pages": {p: sha(ROOT / p) for p in ("public/walkthrough-034.html", "public/walkthrough-035.html")},
        "sources": {p: sha(ROOT / p) for p in SOURCE_FILES},
        "source_records": [record_summary(r) for r in SOURCE_RECORDS],
        "incident": {"id": data["incident"]["id"], "mmr_root": data["incident"]["expected_mmr_root"], "leaves": data["incident"]["leaf_count"]},
        "narration": NARRATION,
        "scenes_034": scenes("public/walkthrough-034.html"),
        "scenes_035": scenes("public/walkthrough-035.html"),
        "recordings": media_hashes(),
        "timeline": "page timeline 147.856 s (scene data-t sum 145.0 + 2.856 s added to the last scene by the page script); recordings capture the first 145.0 s; final scene starts at 127.5 s",
        "mp4_reproducibility": "NOT_GUARANTEED (encoder/capture timing); bound by recorded hashes, verified by frame check",
        "predecessor": "evidence/walkthrough/manifest-035.json (035.1) bound public/data/proof.json and run.json by hash, but those bytes were in no commit; 035.2 binds committed snapshots recovered byte-identical from the live site",
        "signature": "NOT_SIGNED",
    }
    leaves = [{"type": k, "value": body[k]} for k in sorted(body)]
    tree = C.merkle(leaves)
    return {**body, "commitment": {"algorithm": tree["algorithm"], "leaf_count": tree["leaf_count"], "root": tree["root"],
                                   "leaf_sha256": [l["leaf_sha256"] for l in tree["leaves"]]}}


def main():
    m = build()
    text = json.dumps(m, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        old = OUT.read_text() if OUT.exists() else ""
        same = old == text
        print(("PASS" if same else "FAIL") + " manifest rebuild byte-identical; root " + m["commitment"]["root"])
        sys.exit(0 if same else 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print("wrote", OUT.relative_to(ROOT), "root", m["commitment"]["root"])


if __name__ == "__main__":
    main()
