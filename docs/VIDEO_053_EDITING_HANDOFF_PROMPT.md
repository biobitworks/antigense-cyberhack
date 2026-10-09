# Prompt for the media-editing lane — Antigense Daisy 053

Work from the exact prior generated media objects in the ChatGPT Library, or from their verified local copies. **Do not recreate a visually similar movie and call it the same source.**

- 051 edit: `Antigense_Daisy_051_review_draft.mp4` (242.984 s, SHA-256 `6cb42d6df983af8d5254a458188db5aff3ae2e5e9aa063db2df393ff440b813b`).
- 051 judge edit: `Antigense_Judge050_clean_clip.mp4` (22.718 s, SHA-256 `b1c4a25f4db0b6e4da404f0581b761bd4b47046fc6ea84f25897adf82fa4b270`).
- Raw judge screen source: `Screen Recording 2026-10-09 at 3.39.20 PM.mov` (30.656792 s), SHA-256 `2d10743074f28bf287b0f6ed8fb05096d70255b6db4e40b3419fa71eec03fbf3`.
- Raw main screen source: `Screen Recording 2026-10-09 at 1.46.27 PM.mov` (162.207771 s).
- Raw audio: `AWS Builder Loft 2.m4a` (220.309333 s) and `AWS Builder Loft 3.m4a` (22.762667 s), if recoverable.

## Goal

Render an edited, **exactly 3:00 (180.00 ± 0.25 seconds)**, high-legibility 1440×900 H.264/AAC submission video. Voice must be crisp, at a natural cadence; every numerical/capability claim must be synchronized with its actual demonstration/receipt, not with generic stock footage. Keep the **Nimble UI sequence**. **Do not remove Nimble.** The raw judge recording's first ~8 seconds contain a previously visible `NIMBLE_API_KEY`; reintroduce the required opening Nimble footage only after permanently blurring/removing **just the credential value** from the output pixels. Reuse all other safe, meaningful Nimble visuals. Other private capability tokens and reviewer notes must be hidden. Never disclose any secret in a tool log or final exported frame. Recommend revocation/rotation separately; not by removing the Nimble demo.

Use `docs/VIDEO_053_THREE_MINUTE_RELEASE.md` as the **timecoded eight-scene storyboard and proposed narration**, and `evidence/video_053/claim_matrix.json` as the evidence/claim truth table. Preserve strict independence between sponsor historical receipts (Semgrep, Akash, ClickHouse), 042 six-leaf source-bound result, hosted 043 twelve-leaf proof, and 050 local four-leaf manual judge root `47a220fd28956dc77d7baf4299cf6e348c8ebe8736955fbc38c3e43de17deafb`. Nothing here proves new sponsor API calls during 050, named judge identity, hardware attestation, settled wallet payments or ROI. The execution captions must state **LOCAL** or **HISTORICAL** as appropriate. All unverified claims are NOT_TESTED.

## Output files

1. `Antigense_Daisy_053_180s_review.mp4` (3:00, voice present, Nimble kept and credential masked).
2. `Antigense_053_captions.vtt` (aligned to actual audio, not invented words).
3. `Antigense_053_render_manifest.json` with raw input SHA-256, selected in/out frame ranges, output SHA-256, exact duration/codec, masked time ranges with no secret values, observed shortcomings, reviewers and human approval status.
4. `Antigense_053_screenshot_audit.md` with evidence that each shown command, FCO ID, number, claim and screenshot maps to a pinned source receipt.
5. A new separate immutable media breakpoint only if ordered leaves, construction, peaks/root and an independent verification receipt have actually been produced; otherwise mark `MMR: NOT_COMPUTED`. Never claim SIGNED without a verified signature.

## Required execution and QA

1. First recover the actual source bytes. If not accessible, report `SOURCE_BYTES_UNAVAILABLE`; **do not invent a completed MP4** or assert audio clarity.
2. Re-edit the original narration at clause boundaries to fit 180 seconds. The previous 243-second assembly was not word-level synchronized. Do not globally accelerate the video or voice to meet the duration. Record/replace voice lines if needed; normalize to around -16 LUFS integrated, true peak ≤-1 dBTP.
3. Verify with `python3 scripts/verify_video053.py ./Antigense_Daisy_053_180s_review.mp4 --measure-loudness`. This is **mechanical only**.
4. Independently listen start-to-end and frame-review every scene, especially the first source 0–8s containing Nimble, overlays, terminal history, mouse/keyboard actions, transitions, and any hidden secret exposed by reintroduced frames. Do not rely on sampled frames for a comprehensive redaction claim.
5. Only after passing mechanical, semantic, spoken-word alignment and privacy checks may the user approve the edit. Do **not** overwrite the existing public 039R1 video, deploy production, or modify the tokens& form without explicit release authorization.
6. Once approved, publish with an immutable 053 media path under the existing verified Vercel video page, preserving the original 039R1 copy and backup; after public readback verify that the stable submitted page resolves to 053 and has the same SHA-256 bytes.

**State of this handoff:** PROPOSED. Source media receipt recovered. Full video not yet verified, rendered or published by this lane.
