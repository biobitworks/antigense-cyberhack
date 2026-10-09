#!/usr/bin/env python3
"""Derive time-aligned, explicitly provisional captions from on-device Whisper output.

Input is a frozen ASR draft, NOT a canonical verbatim transcript. Edits only
normalize clear entity names or flag ambiguous speech. Never claim signed timing.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence/video044/voice_asr_raw.srt"
OUT = ROOT / "public/video"
OUT.mkdir(parents=True, exist_ok=True)

# 1-based source segment corrections; retain all timings, never invent segments.
EDITS = {
    4: "Which decision changed, which boundary",
    6: "Antigense Daisy starts with a device",
    7: "and keeps that incident inspectable.",
    8: "ChatGPT/OpenAI orchestrates; Claude works",
    11: "[This is a software-injected fault, not a physical hardware failure.]",
    13: "but a teaching fixture reveals an unsafe fallback.",
    14: "Failed worker health allows an unauthorized request.",
    15: "Semgrep identifies that fallback.",
    16: "Our pinned repair rejects unauthorized requests",
    22: "checks, and Merkle commitments.",
    23: "The browser independently recomputes the proof.",
    26: "ClickHouse stored eleven checkpoints",
    30: "The measured readback query took about 161 milliseconds.",
    31: "Akash now runs the analysis workload.",
    33: "selected a lease and loaded Qwen.",
    36: "The model's advice remains untrusted",
    40: "which returned success.",
    43: "[We do not claim] a verified final closed state or measured cost savings.",
    47: "Lower troubleshooting and inference costs",
    48: "are goals we still need to measure.",
    49: "Credentials and proprietary internal state stay private.",
    52: "Antigense makes the path from error to recovery",
}
raw = SOURCE.read_bytes()
segments = []
for item in re.split(r"\r?\n\s*\r?\n", raw.decode("utf-8").strip()):
    ls = item.strip().splitlines()
    if len(ls) < 3:
        continue
    idx = int(ls[0]); span=ls[1]; original=" ".join(ls[2:])
    start, end = [x.strip() for x in span.split("-->")]
    text = EDITS.get(idx, original)
    if idx != len(segments) + 1:
        raise ValueError("ASR segment count/order changed")
    segments.append({"index":idx,"start":start.replace(",","."),"end":end.replace(",","."),"text":text,"asr":original,"editorial_edit":idx in EDITS})
if len(segments) != 53:
    raise ValueError(f"Expected 53 actual ASR segments, got {len(segments)}")
vtt="WEBVTT\n\n" + "\n\n".join(
    f"{s['start']} --> {s['end']}\n{s['text']}" for s in segments
)+"\n"
(OUT / "captions.vtt").write_text(vtt,encoding="utf8")
(OUT / "transcript.json").write_text(json.dumps({
    "source_audio":"Published demo-034.mp4",
    "method":"Whisper base.en on-machine ASR, 53 timed cues; entity normalization, ambiguity marked",
    "status":"ASR_EDITORIAL_DRAFT_NOT_HUMAN_VERBATIM",
    "captions_verified_by_listening":"NOT_TESTED",
    "original_srt_sha256":hashlib.sha256(raw).hexdigest(),
    "duration_seconds":142.166667,
    "segments":segments,
},indent=2,ensure_ascii=False)+"\n",encoding="utf8")
print("BUILT",len(segments),"ASR source sha256",hashlib.sha256(raw).hexdigest())
