# Handoff 040: Claude -> ChatGPT/OpenAI orchestrator

From: Claude Sonnet 5.5 (Claude Code), 2026-10-09. Branch `agent-011-sponsor-evidence`, PR 1 https://github.com/biobitworks/antigense-cyberhack/pull/1 (open, ready). Repo is PUBLIC.
Machine-readable manifest with hashes and roots: `docs/HANDOFF_040.json`.

**Signature: NOT_SIGNED (cryptographic).** This handoff carries a SHA-256 manifest and is bound by the commit that contains it. Byron can sign it (`git tag -s`, or `ssh-keygen -Y sign`). A written handoff does not prove delivery or review.

Real repo path: `/Users/byron/projects/hackathon/antigense-cyberhack`. The session folder `/Users/byron/projects/active/antigense-cyberhack` is an empty directory.

## Rules still in force
No paid compute, no ClickHouse ingestion, no Akash deploy (`agent/live037.py --akash-deploy` spends money: do not run). Do not edit `public/` or `agent/live037*` while other sessions work. Do not publish or replace demo.mp4 before Byron reviews. Keep NOT_TESTED as NOT_TESTED. Hashes prove integrity; behavior needs controlled healthy/fault comparison.

## Verified (executed by me)
- 48 s mismatch explained: 034b cuts sit 0.60-0.70 s before the page-time manifest (scene 5 starts 47.73 s, so the 48 s frame is scene 5). Untrimmed re-record aligns 0.03-0.27 s; 48 s frame is scene 4. Cause: recorder trim 0.749 s measures goto latency. `agent/frame_check035.py` samples 0.8 s before scene end so it was blind to offsets under 0.8 s. Evidence: `evidence/calib040/orig034b_b/`, `evidence/calib040/run040d/`.
- Recording `media/walkthrough-040/rec2/screen-040.mp4` (204 s, 12 scenes, silent, outside git): 11 OCR-confirmed cuts, 12/12 scene activations match, 6132-frame ledger MMR recomputed, 8/8 tamper tests detected. Log-to-video lag on proof results: 0.0, 0.0, +0.2, -0.1 s, so event mapping is good to about 0.2 s, not one frame.
- Narration: original file hash matches receipt (12be0853...). 7.4% of narrated seconds fall on a non-intended scene (8.6% in 034b); worst is "about 161 milliseconds" (2.4-3.1 s into the Akash scene). Intended-scene mapping is declared by hand; ASR is whisper base.en. `evidence/align040/alignment.json`.
- ClickHouse 015/016: every MMR prefix independently recomputed; Cloud readback 55 rows, 55 unique, identical in both tables. No re-ingest.
- Public-release scans: gitleaks history 0 leaks (23 commits); Semgrep CE repo scan 1 finding in an untracked third-party skill. `evidence/publicscan040/`.

## Code review (by reading) and Semgrep
20 findings in `evidence/review040/reviews_v2.json`; Semgrep CE detected 1 (the exec at agent011.py:89, now fixed by another session: verified, HEAD scan 0 findings). Still OPEN, notable:
- F1 `src/custody.py:derive` admits `OBSERVED` steps with false checks as ADMITTED (demonstrated).
- F2 `src/cascade.py:auth` still executes fixture code (demonstrated in `evidence/review040/head/postfix.json`); Semgrep reports clean, so a clean scan hides it.
- F12 `frame_check035.py` offset blind spot. F7 UA change after Cloudflare 1010 in akash_console023 needs owner review. F3 partial: publication token is the public project_root.
- Semgrep Guardian: authenticated, 0 projects, NOT_TESTED.

## Roots
Review tree reviewed 8ea49f12...5d57; HEAD v2 tree c7f1de02...fb15. FCG review lane: 8 leaves 3f3349e6...; extended append-only to 14 leaves b6aafad9...7bf3c (prefix reproduces the 8-leaf root). Typed edges INPUT_TO / PRODUCED_BY / CHECKED_AGAINST / DERIVED_FROM are declared relations, not causality. Anticube identity/safety UNKNOWN, SELF_SAFE null, G* unvalidated.
Measured, not claimed as speedups: 3 of 27 files changed since the reviewed tree (agent011.py modified, live037.py/.html added); Semgrep wall time full 3.7-6.5 s vs changed-only 3.2-3.8 s; root descent flags 15 positions for 3 true changes (positional tree shifts on insertion: F17). Review-time saving: NOT_TESTED.

## Failures and gaps (do not paper over)
1. `agent/verify040.py` fails `tree_leaf_files_match_working_tree`: tree was built before agent011.py changed. Check against the reviewed commit 7433431 or the v2 tree. It also has checks that cannot fail (hard-coded True; function compared with itself): replace with a second MMR implementation (incremental vs decomposition) over every prefix, and recompute scene labels from `transitions.json`.
2. Page and recording do not yet include the v2 incremental data (`evidence/review040/v2/site_data.json` has a `v2` section; `agent/build_page040.py` reads only the v1 sections). Scene 11 should say: found 1, fixed, rescanned 0, but F2 remains.
3. Scenes 11-12 have no narration: `docs/VOICE_SCRIPT_040_ADDENDUM.md` is a draft for Byron. Do not request re-recording of scenes 1-10.
4. No visible overlay or muxed review video for rec2. Overlay should point to a committed scene manifest (`evidence/calib040/run040d/scene_manifest_observed.json`); it is not authentication.
5. Akash: AkashML call returned 401 because the stored key has the Console `ac.sk.` shape. No AkashML inference claimed. GPU attestation, billing, closed-state, bridge delivery: NOT_TESTED.
6. Seedgraph sentence-diagramming contract and Agent Foundry breakpoints: UNKNOWN (searched, not found). Fault-to-response interval: NOT_COMPUTED.
7. The `form` claim about "12 MMR leaves" live-local FCG evidence (branch `codex/live-observation-041`) was not verified by me.
8. Large superseded ledgers/samples under `evidence/calib040/` are untracked on purpose (regenerable).

## Next actions (in order)
1. Fix verify040 per gap 1 and rerun: `python3 agent/verify040.py media/walkthrough-040/rec2/screen-040.mp4 evidence/calib040/run040d media/walkthrough-040/site3 evidence/review040/run2 media/walkthrough-040/rec2/screen-040.receipt.json`.
2. Extend build_page040 with the v2 section; re-record (`agent/record_walkthrough040.py <newdir> --site-dir <newsite> --page walkthrough-040.html`), then `agent/calibrate040.py ... <page>`.
3. Have Byron record the addendum narration; assemble only after review.
4. Decide F1/F2 fixes with Byron (new freeze needed if governed bytes change).
5. Return an acceptance matrix and a lane-qualified TURN_BREAKPOINT.

TURN_BREAKPOINT lane=claude-040 pred=OFFLOAD_PROMPT_018,PR1:23e9717
VERIFIED_NEW: calibration, rec2 ledger+tamper, narration alignment, review roots, scans.
EXECUTED: whisper, Semgrep CE x many, gitleaks, controlled fixtures, one AkashML call (401).
OBSERVED: F1, F2, F12 demonstrated.
DECISIONS: no re-ingest; repo made public on Byron's instruction; scenes 1-10 and narration unchanged.
PROPOSED: gap list above.
NOT_TESTED: Guardian, Akash inference/attestation, review-time saving, full-frame semantics.
FAILURES: verify040 tree check; 4 subagents model_not_found; Akash 401.
UNRESOLVED: gaps 2-8.
NEXT_ACTION: item 1.
