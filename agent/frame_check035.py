#!/usr/bin/env python3
"""Tie video frames to the committed page + data (frame check, not a watermark).

For each scene in evidence/walkthrough/manifest-035.json (scenes_034), take one
frame from the recorded video near the scene's end and render the same scene
from the committed page in a clean headless Chromium. Compare the content area
with SSIM (header progress bar and footer clock excluded: they differ between
autoplay and manual mode). On the two proof scenes, OCR the computed MMR root
from the video frame and compare it with the recorded root.

What a PASS shows: the video displays the committed page/data at those times.
It does not prove the evidence is true, when the video was made, or that the
narration matches. Usage:
  python3 agent/frame_check035.py <video> <out.json> [--chromium PATH] [--min-ssim 0.97]
"""
import argparse, functools, hashlib, http.server, json, re, subprocess, tempfile, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("out")
ap.add_argument("--chromium", default=str(Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell"))
ap.add_argument("--min-ssim", type=float, default=0.97)
a = ap.parse_args()

manifest = json.loads((ROOT / "evidence/walkthrough/manifest-035.json").read_text())
scenes = manifest["scenes_034"]
video = Path(a.video).resolve()
video_seconds = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], text=True))
roots = {5: manifest["incident"]["mmr_root"], 8: manifest["source_records"][0]["mmr_root"]}
CROP = "crop=1440:740:0:90"  # content area between header bar and footer
tmp = Path(tempfile.mkdtemp(prefix="framecheck-"))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "public"))
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
httpd.RequestHandlerClass.log_message = lambda *x: None
threading.Thread(target=httpd.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{httpd.server_address[1]}/walkthrough-034.html"


def ssim(x, y):
    err = subprocess.run(["ffmpeg", "-v", "info", "-i", str(x), "-i", str(y), "-lavfi",
                          f"[0:v]{CROP},format=gray[a];[1:v]{CROP},format=gray[b];[a][b]ssim", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r"All:([0-9.]+)", err).group(1))


def ocr_root(png):
    # Crop the "computed <root>" line; normalize common hex OCR confusions.
    crop = tmp / (png.stem + "-ocr.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "crop=900:30:60:340,scale=2700:-1,format=gray", str(crop)], check=True)
    txt = subprocess.run(["tesseract", str(crop), "-", "--psm", "7"], capture_output=True, text=True).stdout
    txt = txt.lower().replace("computed", "").translate(str.maketrans({"£": "f", "l": "1", "i": "1", "o": "0", "s": "5"}))
    return re.sub(r"[^0-9a-f]", "", txt)


results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=a.chromium)
    for s in scenes:
        n = s["order"]
        t = min(s["start_s"] + s["seconds"] - 0.8, video_seconds - 0.2)
        frame = tmp / f"video-{n:02d}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(frame)], check=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(url, wait_until="networkidle")
        for _ in range(n - 1):
            page.keyboard.press("ArrowRight")
        page.wait_for_timeout(min(t - s["start_s"], 7.0) * 1000)  # let proof animations finish
        ref = tmp / f"ref-{n:02d}.png"
        page.screenshot(path=str(ref))
        page.close()
        row = {"scene": n, "kicker": s["kicker"], "video_t": round(t, 3), "ssim": round(ssim(frame, ref), 5),
               "video_frame_sha256": sha(frame), "reference_sha256": sha(ref)}
        row["ssim_pass"] = row["ssim"] >= a.min_ssim
        if n in roots:
            got = ocr_root(frame)
            row["ocr_expected_root"] = roots[n]
            row["ocr_root_found"] = roots[n] in got
            row["ocr_prefix16_found"] = roots[n][:16] in got
        results.append(row)
    browser.close()
httpd.shutdown()

ok = all(r["ssim_pass"] for r in results)
report = {"check": "frame_check035", "video": str(video.relative_to(ROOT)) if video.is_relative_to(ROOT) else video.name,
          "video_sha256": sha(video), "video_seconds": video_seconds, "page": "public/walkthrough-034.html",
          "page_sha256": sha(ROOT / "public/walkthrough-034.html"), "manifest_root": manifest["commitment"]["root"],
          "min_ssim": a.min_ssim, "scenes": results, "PASS": ok,
          "ocr_note": "OCR is a secondary, non-gating check; hex OCR can misread characters",
          "claim_ceiling": "frames match committed page/data renders; not proof of truth, timing of creation, or narration alignment; not a watermark"}
Path(a.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
for r in results:
    extra = f"  ocr root {'found' if r.get('ocr_root_found') else ('prefix' if r.get('ocr_prefix16_found') else 'MISS')}" if "ocr_expected_root" in r else ""
    print(f"{'PASS' if r['ssim_pass'] else 'FAIL'} scene {r['scene']:>2} t={r['video_t']:>7} ssim={r['ssim']}{extra}")
print("PASS" if ok else "FAIL", "frame check")
raise SystemExit(0 if ok else 1)
