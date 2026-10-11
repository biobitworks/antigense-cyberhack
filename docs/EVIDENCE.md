# Evidence

Each claim below links to a custody record in `evidence/`. A record is a chain of steps: every step stores what was observed, true/false checks, and a Merkle commitment, and each step extends a Merkle Mountain Range (MMR). Anyone can recompute every prefix.

```sh
.venv/bin/python agent/verify_all.py          # one line per record
.venv/bin/python agent/verify_all.py --json   # same, machine-readable
```

`verify_all` recomputes each chain and checks the frozen source files against the git commit they were frozen from, so later edits to the working tree can't hide or fake a result. Machine-readable summary: [evidence/INDEX.json](../evidence/INDEX.json).

## Semgrep

| Claim | Record | Key values |
|---|---|---|
| Unsafe fallback found, fix verified | `successor_011` steps `semgrep_before`, `semgrep_after`, `semgrep_regression_matrix` | Semgrep 1.180.0, custom rule `rules/fallback.yaml`; 1 finding before, 0 after; fix denies both unauthorized cases and keeps healthy authorized access |
| Real finding in our own AI-written code | `successor_016` step `own_code_scan_before`; `evidence/semgrep_own_code/` | `python.lang.security.audit.exec-detected` at `agent/agent011.py:89` |
| Fix for that finding | `successor_016` steps `safe_eval_equivalence`, `own_code_scan_after` | exec-free evaluator `agent/safe_eval016.py`; identical behavior on both fixtures; rescan 0 findings, 0 errors |
| Second finding in AI-written code (not in a custody record) | Semgrep Guardian hook, while writing `agent/verify_all.py` | `trailofbits.python.tarfile-extractall-traversal`; replaced archive extraction with per-file reads and a path check; rescan 0 findings |

Limits: the fixture rule is narrow. Registry rules weren't saved as bytes, so a later rescan could differ. Zero findings means only that scan found none.

## Akash

| Claim | Record | Key values |
|---|---|---|
| GPU inference on Akash, then closed | `successor_024` | Console API create 201 (dseq 1791574273055, tx code 0); 7 bids; lease on a provider-reported V100 at ~396 uact/block (cap 10,000); Ollama 0.6.5; `qwen2.5:0.5b` inference HTTP 200 in 3,466 ms, schema-valid advice, not applied; Ollama-reported VRAM = whole model; close 200 `success:true` |
| Authenticated read-only Console call | `successor_023` | `GET /v1/deployments` HTTP 200 in 327.5 ms, 0 deployments |
| Failures, kept | `successor_019` (AkashML 401), `successor_021` (diagnosis: a Console `ac.sk.` key sent to AkashML, which only accepts `akml-` keys), `successor_022` (Cloudflare 1010 with Python's default client name) | — |

Limits: the GPU model is provider-reported, not attested. No TEE or confidentiality claim. Exact spend not measured, and the deployment's final closed state wasn't read back.

## ClickHouse Cloud

| Claim | Record | Key values |
|---|---|---|
| Ingest, replay, query, exact readback | `successor_016` | ClickHouse 26.6.1.2326; 55 records from `successor_011`; replay kept 55 unique occurrences; 4 queries in 122–164 ms; readback 55/55 with matching SHA-256 (`8744be18…`) |
| First attempt, kept | `successor_015` | same data; readback values matched but hashes differed because of number formatting (524.0 vs 524), fixed in 016 |
| Local projection | `successor_012` | open-source `clickhouse local` |

Limits: small data. No scale or latency-at-scale claim. The Cloud host appears only as a SHA-256.

## Agent on the open web

| Claim | Record | Key values |
|---|---|---|
| Monitors the public site within limits | `successor_011` steps `monitor_*`, `neg_*` | allowlist, 10 s timeout, request cap; tested refusal of non-allowlisted URL, unreachable host, timeout, request limit |
| Publishes and reads back a status file | `successor_011` steps `publication`, `publication_readback` | publication refused without authorization and with a stale binding; exact binding deployed and read back byte-for-byte |

## Original incident (historical)

`final_custody`: 12 leaves, project root `fba52510…`, MMR `26bdf817…`. Frozen at commit `6171b7b`; `verify_all` checks its files against that commit.

## Known gaps

- `successor_019`, `successor_020` and `successor_022` report **CHAIN_ONLY**: their chains recompute, but some frozen file bytes exist in no commit. 019 and 020 froze `public/index.html` while another session had uncommitted edits. 020 and 022 also had their addendum files appended to after freezing, which was our custody mistake. We kept them visible rather than rewriting history.
- Receipts are unsigned. Human approvals in the original incident are unauthenticated rehearsals.
- Pi Security was not used (no product access at the event).
- The public demo video is an earlier silent rehearsal.
