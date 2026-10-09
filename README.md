# Antigense Daisy — verifiable cyberdefense evidence

**Hardware faults must not become security failures.** Antigense Daisy is a bounded, local-first cyberdefense prototype created for the [tokens& Cyberdefense Hackathon](https://tokensand.com/p/antigense-daisy) on October 9, 2026. It records source/evidence, event occurrences, declared FCG relationships, verification outcomes, and Merkle/MMR commitments rather than relying on an agent's narration.

**Canonical submission:** [Antigense Daisy on tokens&](https://tokensand.com/p/antigense-daisy) · **Production website:** [antigense-cyberhack.vercel.app](https://antigense-cyberhack.vercel.app/) · **Video and transcript:** [hosted 039R1 recording](https://antigense-cyberhack.vercel.app/video/) · **Judge guide:** [public walkthrough](https://antigense-cyberhack.vercel.app/judges/) · **Archived-media backup in this branch:** [backup index](public/backup/index.html).

> **Scope:** The deployed Vercel pages are sanitized, static **recorded evidence**, not a hosted agent, multi-user review service, or live Semgrep/Akash/ClickHouse session. The separate live local judge 050 server uses a localhost-only bearer capability; it is **not deployed to Vercel**. Its capability and private notes must never be copied to this repository.

## Start here

| Need | Address | Evidence boundary |
|---|---|---|
| Official entry | [tokens& Antigense Daisy](https://tokensand.com/p/antigense-daisy) | Submission authority; acceptance and uploaded files require platform readback |
| Working hosted explanation | [Vercel production](https://antigense-cyberhack.vercel.app/) | Static demonstration |
| Narrated video, captions, transcript | [Video](https://antigense-cyberhack.vercel.app/video/) | Prior 039R1 recording, **not** footage of new live 050 |
| Judge instructions | [Judges](https://antigense-cyberhack.vercel.app/judges/) | Public walkthrough and evidence limits |
| Browser proof | [Judge proof 043](https://antigense-cyberhack.vercel.app/judges-043.html) | **Separate 12-leaf** historical proof |
| Alternative public recording | [YouTube](https://youtu.be/hpLH88V6PF0) | Existing fallback; not the new combined video |
| Archival Vercel copy | [Backup landing page](public/backup/index.html) | Branch includes the 039R1 MP4 and source-hash manifest; deployment URL in [release record](docs/RELEASE_BACKUP_052.md) after verification |

## Actual end-to-end evidence

1. A **simulated byte fault** causes an integrity failure in a controlled fixture. No physical GPU fault is claimed.
2. An intentionally fail-open authorization path makes unauthorized work possible under failed health checks.
3. **Semgrep CE** detects the pinned unsafe pattern (one before, zero after); a separate own-code audit caught Python module execution, subsequently replaced with a constrained AST interpreter.
4. **Akash** provided a separately recorded GPU deployment and one bounded `qwen2.5:0.5b` advisory inference, HTTP 200 in 3,466.4 ms; the advice was not automatically applied. Hardware identity/TEE attestation was not verified.
5. A **deterministic four-case security oracle** checks authorized × healthy combinations and rejects a deliberately ineffective alternative fix.
6. **ClickHouse Cloud** separately ingested and replayed 55 historical records, with hash-exact readback; this is not a new 050 cloud run.
7. Immutable occurrence FCOs, typed FCG relationships, and ordered Merkle/MMR checkpoints preserve both successes and failed/unknown controls.

Sponsor evidence is in [docs/EVIDENCE.md](docs/EVIDENCE.md), [evidence/INDEX.json](evidence/INDEX.json), [docs/INTERVENTION_042.md](docs/INTERVENTION_042.md), and dated successor reports. **Pi was not used.** Semgrep Pro, live wallet settlement, measured ROI, GPU attestation and cryptographically verified judge identities are NOT_TESTED/NOT_COMPUTED.

## Successors and verification boundaries

| Lineage | Execution | Verification or limits |
|---|---|---|
| Sponsor runs 011–040 | Semgrep CE; historical Akash inference; ClickHouse Cloud exact readback; historical 12-leaf browser proof published later | Preserved gaps and failed cases; read [evidence notes](docs/EVIDENCE.md) |
| Guarded intervention **042** | AST-based fixture evaluator replacing arbitrary module execution; strict admission for caller-declared checks | 11/11 local tests; 6 ordered leaves; root `43522a82b0c2a4428cda56366f65689757d70085031e26997e90b583b846e5a0`; NOT_SIGNED. Caller-declared check omission is an unresolved risk |
| Live judge **050** (separate **local-only** worktree) | Real local HTTP/SSE DENY then ALLOW, private notes redacted publicly | 17/17 local tests reported; independent local verification rechecked a **different** four-leaf manual run with root `47a220fd28956dc77d7baf4299cf6e348c8ebe8736955fbc38c3e43de17deafb`. This is **not** the published proof 043 |
| Media archive **052** (this branch) | Exact public 039R1 MP4, captions, transcript, hosted proof JSON preserved and SHA-256 catalogued | Content hashes establish downloaded-byte identity only; not signing, external timestamp attestation or acceptance by judges. See [release record](docs/RELEASE_BACKUP_052.md) |

**Identity and custody are not truth or causality.** A SHA-256 digest deduplicates bytes; a typed FCG edge declares a relationship; an MMR root commits an ordered execution. None proves that a cloud GPU was attested, that a reviewer is a named human, or that a model's advice is safe. New corrections are successors, not silent rewrites.

## Reproduce locally

Use a clone with Python and no secrets. The bounded 042 branch includes independent custody checks:

```sh
python3 -m unittest discover -s tests -v
python3 agent/intervention042.py verify
sh scripts/setup.sh
.venv/bin/python agent/verify_all.py --json
```

The first two commands were re-executed for branch 052: **11 tests PASS** and 042 custody **PASS**. `verify_all.py` preserves older `CHAIN_ONLY` failures; do not conflate them with successful full-source verification. Historical receipt counts should be read from the executed verifier output, not guessed.

For the earlier local interactive demonstration, use `sh scripts/demo.sh` on a trusted computer (port 8790). **Do not attempt to run Live Judge 050 by opening its static HTML on a Vercel deployment.** The 050 Python HTTP API is private and separately scoped to `127.0.0.1:8850`.

## Hosting, backup and submission links

The Vercel project `antigense-cyberhack` serves static `public/` content through [vercel.json](vercel.json). **Production** stays at [https://antigense-cyberhack.vercel.app/](https://antigense-cyberhack.vercel.app/). This branch adds an archival [`/backup/` landing page](public/backup/index.html) and an independently deployable copy of the *older verified-public* 039R1 MP4. An immutable deployment-specific preview URL should be used as the secondary link after a READY and HTTP readback check. See [052 deployment record](docs/RELEASE_BACKUP_052.md) and [submission link inventory](docs/SUBMISSION_LINKS_052.md).

The new *combined* live-judge footage is being edited separately. Its final URL and bytes are **UNKNOWN** here. Never describe the archived 039R1 video as including 050, and never update the official submission's video field with an unverified URL. The tokens& site is the canonical entry; GitHub and Vercel are supporting evidence, not substitutes for portal acceptance.

## Publication and safety

- **Public:** sanitized video, transcript, hashed archival bytes, read-only status and synthetic proofs.
- **Private:** credentials, .env, local 050 capability, private reviewer notes, unredacted patient data (none needed here).
- **No hosted 050 judge writes** without dedicated authentication, CSRF/rate limiting, access control and authorized infrastructure.
- **No new sponsor calls or spending** are triggered by viewing static pages or running local verification.
- Receipt state: **NOT_SIGNED**. The 052 asset SHA-256 manifest is **not** an MMR commitment.

Original explanatory content © 2026 Biobitworks, CC BY-NC-ND 4.0. Software license not established by this repository's root README; third-party rights retained.
