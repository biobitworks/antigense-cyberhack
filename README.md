# Antigense Daisy — evidence-driven cyberdefense

**Hardware faults must not become security failures.** Antigense Daisy is the single published [tokens& Cyberdefense Hackathon 2026 entry](https://tokensand.com/p/antigense-daisy). It demonstrates a **software-simulated** worker-byte fault, an unsafe fail-open authorization fallback, detection, a gated repair, regression verification, and addressable evidence.

> **Judge-facing status (October 9, 2026):** The official submission and narrated **039R1** video are publicly reachable. **The new 180-second 053R3 end-to-end REVIEW CANDIDATE is [publicly playable on the independent backup Vercel host](https://antigense-daisy-evidence-backup.vercel.app/video-053-review/), but the submitted primary video remains 039R1 until human narration/privacy signoff.** Local Live Judge 050 source is now published on its own branch, but it is not a remotely available judge service. Do not confuse recorded historical sponsor executions with new live cloud calls.

## Start here — public entry and evidence

| Resource | Link | Boundary |
|---|---|---|
| Official Tokens& entry | [Antigense Daisy](https://tokensand.com/p/antigense-daisy) | Single organizer project; platform's actual submission state is authoritative |
| Working project website | [Vercel production](https://antigense-cyberhack.vercel.app/) | Sanitized static recorded replay |
| **Submitted video URL** | [Watch the narrated demonstration](https://antigense-cyberhack.vercel.app/video/) | **Currently 039R1** (earlier narrated video), not the upcoming 051/053 cut |
| Independent redundant media archive | [Public Vercel backup](https://antigense-daisy-evidence-backup.vercel.app/backup/) | Publicly verified archival copy of 039R1, with captions/transcript |
| **New 3:00 review candidate** | [Watch 053R3](https://antigense-daisy-evidence-backup.vercel.app/video-053-review/) · [direct MP4](https://antigense-daisy-evidence-backup.vercel.app/video-053-review/antigense-daisy-053-r3-three-minute-review.mp4) | 180.000 sec; public SHA-256 readback PASS; **human audio-sync/full-frame security QA pending** |
| Judge instructions | [Public judge walkthrough](https://antigense-cyberhack.vercel.app/judges/) | Scope and reproduction guidance |
| Independently recomputable historical proof | [Judge proof 043](https://antigense-cyberhack.vercel.app/judges-043.html) | Historical 12-leaf browser proof, not live Judge 050 |
| Incident walkthrough | [35](https://antigense-cyberhack.vercel.app/walkthrough-035.html) | Recorded sequence |
| Technical explanation | [29](https://antigense-cyberhack.vercel.app/technical-029.html) | Architecture and limitations |

**For the executed code**, GitHub's `main` branch preserves an older standalone local demonstration. The newer work has separately maintained, reviewable source branches. Start with the links below rather than assuming `main` contains every hackathon successor.

## End-to-end flow: what was demonstrated

1. **Inject:** a controlled XOR corruption changes one simulated worker result. No hardware was deliberately damaged.
2. **Reproduce:** a deliberately unsafe teaching fixture fails **open** when an integrity/health check fails.
3. **Detect:** Semgrep Community Edition identified the pinned unsafe fallback; the specific before/after scan went from **1 finding to 0**. Separate self-auditing found a hazardous Python module-execution path, replaced with bounded AST evaluation.
4. **Advise:** a **historical, separately recorded** Akash deployment ran `qwen2.5:0.5b` advisory inference, HTTP 200, 3,466.4 ms; the provider reported a V100 GPU. The response did **not** authorize patch application, and GPU/TEE attestation was **NOT_TESTED**.
5. **Intervene:** a deterministic review oracle applies a pinned fail-closed repair only with exact expected state checks. A local regression matrix tests healthy/unhealthy and authorized/unauthorized combinations.
6. **Reconcile:** **historical** ClickHouse Cloud ingestion/replay recovered 55 records with matching hashes. This does **not** mean the newer local Judge 050 session was ingested into ClickHouse.
7. **Preserve:** addressable FCOs capture content and occurrence identity; typed FCG edges declare provenance/predecessor relationships. Ordered Merkle/MMR leaves, peaks, roots and verification receipts allow deterministic custody checks.

Evidence state has limitations. An exact content hash is not a semantic embedding or proof of truth. A graph relationship is not evidence of causation. A Merkle/MMR root attests to the ordered bytes under its recorded construction, **not** independently to correct attribution or a named reviewer's identity.

## Which source / evidence should judges inspect?

| Source lane | GitHub | What to expect |
|---|---|---|
| Sponsor executions and receipts | [PR #1](https://github.com/biobitworks/antigense-cyberhack/pull/1) | Semgrep CE, historical Akash run, ClickHouse ingestion and readback; historical failures retained |
| Later live observation | [PR #2](https://github.com/biobitworks/antigense-cyberhack/pull/2) | Additional host-local observation context |
| Guarded intervention 042 | [Source branch](https://github.com/biobitworks/antigense-cyberhack/tree/codex/guarded-intervention-042) | Exec-free evaluator, regression tests, a 6-leaf independently recomputable MMR |
| **Live Judge 050** | [Public source branch](https://github.com/biobitworks/antigense-cyberhack/tree/codex/live-judge-050) | Loopback HTTP/SSE public updates; capability-guarded local review; DENY/ALLOW append, private local notes. **Not a hosted judge service** |
| Static public media archive 052 | [Archive branch](https://github.com/biobitworks/antigense-cyberhack/tree/codex/public-backup-052) · [PR #3](https://github.com/biobitworks/antigense-cyberhack/pull/3) | SHA-256-verified earlier 039R1 video, captions/transcript, historic proof; separate public Vercel host |
| Three-minute video successor | [Draft PR #4](https://github.com/biobitworks/antigense-cyberhack/pull/4) | **Rendered and publicly backed up as a 3:00 REVIEW candidate**; mechanical QA PASS, full human editorial/privacy QA outstanding |

The 050 branch was pushed after rerunning **17 local tests (PASS)** and Gitleaks scans (no detected leaks). A separately verified *manual* local 050 session recorded synthetic DENY then ALLOW, with 4 ordered leaves and root `47a220fd28956dc77d7baf4299cf6e348c8ebe8736955fbc38c3e43de17deafb`. The **separate automated** 050 run root `a077e88ac206d5c02e18f47cdde5558af3d4f159573df021615968170d3edd55` must not be conflated with the manually recorded run, the 042 root or historical browser proof 043. The local reviewer credential/private notes are not part of the public website.

## Reproduce a bounded local lane

```sh
# Main branch: older local demonstration, no sponsor credentials required
sh scripts/setup.sh
sh scripts/demo.sh                   # local cockpit http://127.0.0.1:8790

# Inspect the later 050 implementation separately
git fetch origin codex/live-judge-050
git switch --detach origin/codex/live-judge-050
python3 -m unittest discover -s tests -v
# Local-only server; do not expose its capability file
python3 agent/judge_live050.py --port 8850 --output .runtime/new-publication-test-unique
```

For 042, use `python3 agent/intervention042.py verify` on the 042 branch; its verified 6-leaf root is `43522a82b0c2a4428cda56366f65689757d70085031e26997e90b583b846e5a0` (NOT_SIGNED). The older root-level chain verifier can report preserved `CHAIN_ONLY` failure records; this is a known historical gap rather than evidence to silently discard.

## Sponsor and claim boundaries

| Sponsor | Status |
|---|---|
| **Semgrep CE** | EXECUTED, pinned rule/scope. Zero findings after repair does not prove general security |
| **Akash** | EXECUTED in a separately recorded historical inference/close branch; provider-reported GPU, not independently attested |
| **ClickHouse Cloud** | EXECUTED in earlier historical ingestion/replay; exact row-hash readback for 55 records |
| **Pi Security** | **NOT_USED / NOT_TESTED**; no event-time product access |
| **Tokens& Build Packet** | **EXECUTION NOT_ESTABLISHED** by the published sponsor receipts; should not be treated as a fourth verified sponsor |

Cryptographically signed reviewer identity, GPU/TEE attestation, real payments, live wallet settlement, financial return, safety certification and new sponsor calls in the 050 session remain **NOT_TESTED or NOT_COMPUTED**. All relevant FCO/MMR local receipts are **NOT_SIGNED**. Historical failures stay addressable, and corrections require successors, not edits of predecessor checkpoints.

## Video publication policy

The Tokens& entry links to `https://antigense-cyberhack.vercel.app/video/`, which currently serves the 039R1 source. The public 053R3 [review candidate](https://antigense-daisy-evidence-backup.vercel.app/video-053-review/) retains anonymized Nimble source motion behind full-frame blur, shows the later real local 050 judge interaction, and explicitly labels sponsor results as historical. Its SHA-256 is `047ce22506c41add4793e7762f212b6365bd679b67bf6e62e16840cdb0b3b7a0`. Human final review remains pending. Before replacing the video, validate exact duration, audio clarity/screen synchronization, frame privacy, the final media SHA-256 and public browser playback; archive the old MP4 independently. **053 was published only to the secondary backup Vercel project; the original submitted Vercel video and Tokens& portal remain untouched.**

Original explanatory content © 2026 Biobitworks, CC BY-NC-ND 4.0. Software licensing beyond this statement remains unestablished; third-party rights retained.
