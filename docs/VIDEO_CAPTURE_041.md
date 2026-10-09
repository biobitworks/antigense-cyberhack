# Live Local + sponsor-proof video — successor 041

Status: **IMPLEMENTED and TESTED only for read-only local capture and telemetry sampler**. Website integration, a new video, provider read-only requests, click-through improvements, Claude independent comparison, and external publication remain **NOT_TESTED / DEFERRED**. Parent: PR1 / 7433431; predecessor 035 / 039R1 and historical failures are retained.

## Input recording inspected
The user supplied a 162.207771 s, 3024×1964, H.264/AAC Safari recording dated October 9, 2026 (local filename 1.46.27 PM). SHA-256 of these exact uploaded MOV bytes: `203fc26e7476566d0e3be659df1865db01e2d124f29eb4a77a34e22434fe3158`. Sampling showed the dashboard at 127.0.0.1, replayable stages, changing load, static CPU count (8) / installed memory (16 GiB), and a local approval. These are *different observables*: installed inventory should not be presented as CPU usage or memory usage.

## Verified local custody run (separate from PR1's historical sponsor receipts)
Current localhost:8790 readback recorded run `run-20261009T204741Z-5cb3db65`, phase=verified, leaf_count=12, project_root=`9053be5ed053068d50f22e96acec01d52e466a2ddcb6fa66cf1e406274dd599c`, MMR=`02d102de2d19334b582a5a9ebde4e55de184533a607d81cc2b317c000423ddc3`. CLI verifier returned PASS with independent MMR prefix recomputation and artifact checks. Event index 9 is distinct `08 Local review action`, parent FCO at index 8 with typed relationship `DEPENDS_ON_RECORDED_PREDECESSOR`. Actor identity and signature are unverified. No real host policy patch; pinned teaching-fixture selection only.

Read-only sidecar `agent/live_capture041.py` performed five consecutive successful HTTP readback/independent MMR checks on the original running server; sanitized sample Merkle root = `6e623a43cbd15b765c406932815860f40aff1df56ec27ce7a82b648c5c4dadea` (ordered five samples, `fco-ordered-v1`). A strengthened two-sample successor passed with root `336093cf941f927e8c1d6c3cb0f8067d86a46b4ee602f2ee8041acf800d22fb5`. Both are **readback-sample commitments**, not the project's canonical custody root and not authenticating wall-clock time.

## Sponsor truth matrix for the video

| Sponsor | Recorded prior activity | Safe active step during next capture | Claim ceiling |
| --- | --- | --- | --- |
| Semgrep | Before/after local source scans observed; old `exec()` finding retained with successor correction | Run local Semgrep CE scanner once with offline rule and pinned target; show command, hashes, finding counts, receipt and exit code | NEW_LOCAL_SCAN_OBSERVED if executed; not proof the source is free of all vulnerabilities |
| ClickHouse | Historical cloud ingestion, replay and exact 11-checkpoint incident readback observed; distinct 55-row branch recorded | With existing **authorized** client only, run read-only SELECT and exact row/hash comparison. No INSERT/DDL or paid rerun | NEW_READBACK_OBSERVED only after HTTP/query receipt and independent comparison; NOT_NEW_INGEST |
| Akash | Separate GPU/Console inference and close API responses observed (successor 024); earlier 401 and 1010 failures preserved | Do **not** deploy/infer again. Optionally run read-only deployment status query using already authorized credentials; otherwise verify archived receipt bytes | HISTORICAL_EXECUTION_REVERIFIED; final closed-state NOT_TESTED unless actual GET |
| Pi Security | Intake packet prepared | Show packet plus boundary/access explanation | NOT_TESTED as sponsor provider; do not animate this as a Pi API call |

Hardware GPU/TEE attestation, billed amount, final closed-state readback, cross-device bridge delivery: distinct NOT_TESTED/NOT_COMPUTED statuses until their own receipts. Do not infer truth from hashes or status colors.

## Intended chapter sequence for capture (prefer a 3–4 minute recording, with truthful timing)

1. **0–20 s — Local baseline**: show localhost, live CPU utilization (%) and approximate memory used vs static count/installed RAM, load and sample age. Name source=`macOS top` and avoid physical GPU sensors.
2. **20–50 s — Controlled software fault**: replay the signed-status-free historical local fault and select its occurrence with hash and predecessor. Treat existing replay as a replay.
3. **50–85 s — Semgrep active evidence**: open a terminal/verified scan result, show new local scan started/finished and target/rule bytes; click the stage and inspect its new receipt.
4. **85–120 s — Akash historical evidence**: show provider-reported GPU prior receipt, inference request/HTTP 200, closure HTTP 200; optionally show fresh READ-ONLY status request if one actually succeeded, or show NOT_TESTED. Show no new billed execution.
5. **120–155 s — ClickHouse**: show previous ingestion and a new live read-only query + row IDs/latency and exact hash comparison if available. Otherwise label REPLAY_OF_PRIOR_READBACK.
6. **155–175 s — Pi Security**: reveal intake packet, explicitly NOT_TESTED provider access.
7. **175–210 s — Locally persisted action**: on a *new authorized local run only*, approve once; wait for newly appended receipt; show root before/after, typed predecessor, actual disk readback, independently recomputed root.
8. **210–235 s — Reload and falsifiers**: browser reload; retrieve the same run id/12+ leaves/root from disk; demonstrate offline tamper and duplicate/stale approval negative controls *against copies*, not by modifying canonical evidence. Display known remaining gaps.

If the narration is fixed at ~142 s, cut scope instead of compressing real execution or inventing clocks; use sponsor proof chapters in an extended silent technical recording and a ~142 s factual summary.

## What Claude should change (separate worktree)

- **Claude owns `public/index.html`, `public/technical-*.html`, and walkthrough media alignment**. Codex 041 changed none of those.
- Replace misleading telemetry tiles: dynamic CPU % and approximate used memory from `/api/snapshot.usage`; static core count and installed RAM move to an inventory caption. Existing load average remains dynamic. Show unknown/stale sensor state, timestamp and sample age. Poll no faster than sampler (3 s) and announce that GPU telemetry is UNKNOWN.
- Give each stage a large action affordance (e.g. `Inspect receipt ↗`) with source, run/occurrence ID, relation, root, observed time and state. Clarify `RECORDED REPLAY` / `NEW LOCAL ACTION` / `READ-ONLY SPONSOR READBACK` visually; never use `LIVE` to describe sponsor calls unless receipt verifies it.
- Give Semgrep its own first-class before/after code/scan view, ClickHouse exact query/readback pane, Akash historical inference+closure pane, and Pi NOT_TESTED pane.
- Do not change page034 or predecessor manifest in place. Create a 041 successor scene manifest with hashes, wall-clock and monotonic observations, PTS offsets, sampled frames, browser-visible receipts, and separate audio checks. Frame SSIM matching a page is not proof of a sponsor call.
- Reuse existing narration if still accurate; publishing requires Byron's review. No paid sponsor reruns. Do not delete 039 scene timing mismatch or overwrite failed calls.

## Reproduction of implemented scope

```bash
cd /Users/byron/projects/hackathon/antigense-codex-live041
python3 -m unittest discover -s tests -p 'test_*041.py' -v
python3 agent/live_capture041.py --samples 5 --interval 2 \
  --out .runtime/live041-NEW-RUN.jsonl
# snapshots only: HTTP GET localhost; no POST or sponsor APIs
```

`src/host_telemetry041.py` uses a 3-second background sampler and cached response. `src/server.py` adds the `usage` object; **the existing live process remains unmodified** until the patch is integrated and restarted through normal authorized change control.

Current test status: 11/11 PASS after correcting a temporary unit-test naming collision (the first run failed when the test fixture shadowed `unittest.TestCase.run`). Five tamper cases rejected, one valid-chain case admitted. Duplicate-action and browser reload **NOT_TESTED** in this isolated patch.

No encryption key, API credential, private URL or operator identity is required or stored in this successor.
