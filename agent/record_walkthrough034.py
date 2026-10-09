#!/usr/bin/env python3
"""Record public/walkthrough-034.html (served on localhost) to a silent screen video.

A fresh headless Chromium with no profile records only the page viewport, so
no desktop, tabs, notifications or files can appear. The page makes no sponsor
requests. Output: <outdir>/screen-034.mov (H.264) plus a receipt with hashes.
Usage: python3 agent/record_walkthrough034.py <outdir> [--url URL] [--chromium PATH]
"""
import argparse, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("outdir")
ap.add_argument("--url", default="http://127.0.0.1:8834/walkthrough-034.html?autoplay=1")
ap.add_argument("--chromium", default=str(Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell"))
ap.add_argument("--seconds", type=float, default=146.0)
a = ap.parse_args()

out = Path(a.outdir).resolve()
out.mkdir(parents=True, exist_ok=False)  # new folder only; never overwrite earlier media
raw = out / "raw"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=a.chromium)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900}, record_video_dir=str(raw),
                              record_video_size={"width": 1440, "height": 900})
    t0 = time.monotonic()
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(a.url, wait_until="networkidle")
    lead = time.monotonic() - t0  # video time before the timeline started
    page.wait_for_timeout(a.seconds * 1000)
    done = page.title().endswith("done")
    results = {k: page.inner_text(k) for k in ("#inc-res", "#gpu-res")}
    ctx.close()
    browser.close()

webm = next(raw.glob("*.webm"))
mov = out / "screen-034.mov"
subprocess.run(["ffmpeg", "-nostdin", "-n", "-v", "error", "-ss", f"{lead:.3f}", "-i", str(webm), "-an",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", "-t", "145", str(mov)], check=True)
probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration:stream=codec_type,width,height", "-of", "json", str(mov)], text=True))
receipt = {
    "id": "screen-034", "page": a.url, "page_sha256": sha(Path(__file__).resolve().parent.parent / "public/walkthrough-034.html"),
    "data_sha256": sha(Path(__file__).resolve().parent.parent / "public/data/walkthrough-034.json"),
    "raw_webm_sha256": sha(webm), "mov_sha256": sha(mov), "mov_seconds": float(probe["format"]["duration"]),
    "streams": probe["streams"], "trimmed_lead_seconds": round(lead, 3), "timeline_finished": done,
    "in_browser_recompute": results, "page_errors": errors, "audio": "none (narration assembled separately)",
    "capture": "headless Chromium viewport only; no desktop, profile or credentials", "publication": "NOT_EXECUTED",
}
(out / "screen-034.receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
print(json.dumps({k: receipt[k] for k in ("mov_seconds", "timeline_finished", "in_browser_recompute", "page_errors")}))
sys.exit(0 if done and not errors else 1)
