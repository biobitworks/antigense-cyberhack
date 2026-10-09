#!/usr/bin/env python3
"""Antigense 053 mechanical video verifier.

NEVER claim that audio is intelligible, credentials are redacted, or
historical claims are visible based on this tool: those need human review.
This tool only checks container bytes, codecs, duration, geometry, and
optionally audio loudness against a declared target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def command(argv: list[str]) -> str:
    out = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         check=False, text=True)
    if out.returncode:
        raise RuntimeError(f"Command {argv[0]} failed with code {out.returncode}; "
                           f"stderr tail: {out.stderr[-400:]}")
    return out.stdout


def file_sha256(path: Path) -> str:
    dig = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(2 * 1024 * 1024), b""):
            dig.update(block)
    return dig.hexdigest()


def inspect(path: Path, expected_hash: str | None = None, measure_loudness: bool = False) -> dict:
    if not path.is_file():
        raise FileNotFoundError(str(path))
    meta = json.loads(command(["ffprobe", "-v", "error", "-show_format",
                               "-show_streams", "-of", "json", str(path)]))
    tracks = meta.get("streams", [])
    video = [x for x in tracks if x.get("codec_type") == "video"]
    audio = [x for x in tracks if x.get("codec_type") == "audio"]
    v = video[0] if video else {}
    a = audio[0] if audio else {}
    duration = float(meta.get("format", {}).get("duration", "0"))
    height, width = int(v.get("height", 0)), int(v.get("width", 0))
    sha = file_sha256(path)
    checks = {
        "duration_180_plusminus_0p25": abs(duration - 180.0) <= .25,
        "video_h264": v.get("codec_name") == "h264",
        "audio_aac": a.get("codec_name") == "aac",
        "raster_min_960x600": width >= 960 and height >= 600,
        "aspect_16_to_10": bool(height) and abs(width / height - 1.6) <= .02,
        "audio_sampling_at_least_44100": int(a.get("sample_rate", "0")) >= 44100,
        "video_frame_rate_at_least_24": bool(v) and (
            (lambda z: float(z[0]) / float(z[1]) if len(z) == 2 and float(z[1]) else 0)(
                v.get("avg_frame_rate", "0/1").split("/")) >= 24),
    }
    if expected_hash:
        checks["expected_sha256_matches"] = sha.lower() == expected_hash.lower()
    loudness = {"status": "NOT_MEASURED"}
    if measure_loudness and audio:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                            "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True, check=False)
        summary = r.stderr.rsplit("Summary:", 1)[-1]
        lu = re.search(r"Integrated loudness:.*?I:\s*(-?\d+(?:\.\d+)?)\s*LUFS", summary, flags=re.S)
        tp = re.search(r"True peak:.*?Peak:\s*(-?\d+(?:\.\d+)?)\s*dBFS", summary, flags=re.S)
        loudness = {"status": "MEASURED" if r.returncode == 0 else "MEASUREMENT_FAILED",
                    "integrated_lufs": float(lu.group(1)) if lu else None,
                    "true_peak_dbfs": float(tp.group(1)) if tp else None}
        checks["loudness_integrated_minus16_plusminus2"] = (
            loudness["integrated_lufs"] is not None and
            -18 <= loudness["integrated_lufs"] <= -14)
        checks["true_peak_at_most_minus1"] = (
            loudness["true_peak_dbfs"] is not None and
            loudness["true_peak_dbfs"] <= -1)
    return {
        "schema": "antigense.video053.mechanical_verification.v1",
        "path_basename": path.name, "bytes": path.stat().st_size,
        "sha256": sha, "seconds": duration, "frame_width": width,
        "frame_height": height, "video_codec": v.get("codec_name"),
        "audio_codec": a.get("codec_name"), "checks": checks,
        "PASS_MECHANICAL": bool(checks) and all(checks.values()),
        "loudness": loudness,
        "semantic_claim_alignment": "NOT_TESTED_NEEDS_HUMAN",
        "voice_intelligibility": "NOT_TESTED_NEEDS_HUMAN",
        "secret_visibility": "NOT_TESTED_NEEDS_FULL_FRAME_REVIEW",
        "nimble_segment_present": "NOT_TESTED_NEEDS_HUMAN",
        "captions_synced": "NOT_TESTED_NEEDS_HUMAN",
        "SIGNATURE": "NOT_SIGNED",
        "MMR": "NOT_COMPUTED",
        "PUBLICATION": "NOT_AUTHORIZED_BY_MECHANICAL_PASS"
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video", type=Path)
    p.add_argument("--expected-sha256")
    p.add_argument("--measure-loudness", action="store_true")
    p.add_argument("--receipt", type=Path,
                   help="Write a new immutable JSON receipt; existing paths rejected.")
    args = p.parse_args()
    outcome = inspect(args.video, args.expected_sha256, args.measure_loudness)
    rendered = json.dumps(outcome, sort_keys=True, indent=2) + "\n"
    print(rendered)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        with args.receipt.open("x", encoding="utf-8") as h:
            h.write(rendered)
    return 0 if outcome["PASS_MECHANICAL"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
