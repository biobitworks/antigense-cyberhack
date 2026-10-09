# Antigense Daisy — 053R3 three-minute end-to-end REVIEW candidate

**Status:** RENDERED / MECHANICAL_VERIFY_PASS / FULL_VISUAL_SCREENING_NOT_TESTED / FULL_NARRATION_SYNC_NOT_TESTED / PORTAL_UNCHANGED / NOT_SIGNED.

**Output:** `public/video-053-review/antigense-daisy-053-r3-three-minute-review.mp4`

**SHA-256:** `047ce22506c41add4793e7762f212b6365bd679b67bf6e62e16840cdb0b3b7a0`

**Runtime:** 180.000 seconds exactly. **Video:** H.264, 1440 × 900, 30 fps. **Audio:** AAC, 48kHz mono. **Loudness:** integrated -17.2 LUFS; true peak -1.4 dBFS. Mechanical verifier PASS.

**Source/context:**
- 0:00–2:22.1667: byte-identical **visual/audio story** taken from separately published sanitized 039R1 video; the new encoded video is a *different content-addressed occurrence*, not a claim of original raw bytes.
- 2:22.1667–2:30.1667: genuine first eight seconds of original 050 screen capture retained as 1440x900 **full-frame blur** with an overlaid `NIMBLE / LOCAL JUDGE 050` label. Do not treat blurred interface pixels as public evidence of an executed Nimble API call. API token must never be visible.
- 2:30.1667–2:52.8333: source 050 local browser recording starts at original t=8s. First 15s of the local actions are shown; result is then held on screen while the separately recorded 22.76s local narration continues. The held result is not a new live event; independent FCO/MMR custody is documented in local 050 receipts and source.
- 2:52.8333–3:00: static evidence-limits outro.

**Check:** Mechanical proof at `evidence/video_053/mechanical_verify_r3.json` and media lineage at `public/video-053-review/media_receipt_r3.json`. In the final release, run the verifier against the downloaded public MP4 and recompute SHA-256.

**Claim boundaries:** Semgrep CE, Akash GPU inference and ClickHouse Cloud are historical separately executed evidence. The 050 interaction is real **localhost** DENY/ALLOW, not remote judging. This video does not attest the GPU/TEE, identify an authorized human cryptographically, demonstrate Pi Security or Tokens& Build Packet consumption, show settled payments, or establish safety/financial ROI. The 043 published 12-leaf root, 042 6-leaf root, and 050 manual 4-leaf root are separate states. Video's SHA-256 is a content identity, not a Merkle/MMR root or signature.

**Visual review:** representative frame contact sheets were inspected around t=141..180 seconds; they show the full-frame blur at Nimble intro and local judge interface, with the unwanted screenshot/Spotlight OS popups removed by an explicit held result. **Full-frame, frame-by-frame screening NOT_TESTED**.

**Speech review:** acoustic integrated loudness measured, but voice intelligibility and word-level synchronization require a complete human listen. Edited audio for first 142.17s preserves the old narration; separately recorded judge narration appended after the deliberately obscured Nimble intro.

**Publication policy:** Publish this only as a clearly labelled *review candidate*, on the separate backup Vercel project, without changing `antigense-cyberhack.vercel.app/video/` or the existing Tokens& entry until human review passes. Preserve 039R1 archival original.

**Predecessors:** R1 and R2 were generated as local draft outputs and retain individual local receipts/hashes. R3 corrects the observed screenshot/Spotlight intrusions. Historical predecessor states remain preserved locally; only R3 review candidate is part of this public successor.

**Signature:** NOT_SIGNED. **Video Merkle/MMR:** NOT_COMPUTED. **Tokens& edit:** NOT_EXECUTED.
