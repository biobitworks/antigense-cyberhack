# Antigense Daisy

**Hardware faults must not become security failures.**

A bounded agent follows one corrupted worker result through a security failure, a fix and recovery. Every step is recorded as a hash-chained receipt that anyone can recompute.

Built for the tokens& Cyberdefense Hackathon (San Francisco, 2026-10-09).
Gallery entry: https://tokensand.com/p/antigense-daisy · Live site: https://antigense-cyberhack.vercel.app

## What happens

1. **Fault.** A declared byte is flipped in software. An integrity check catches the mismatch. No hardware is damaged.
2. **Failure.** A teaching fixture shows the danger: when the health check fails, authorization fails *open*.
3. **Detect.** Semgrep finds the unsafe fallback.
4. **Advise.** An open model running on an Akash GPU explains the finding. Its advice is untrusted and cannot apply a patch.
5. **Fix.** A pinned fix denies unauthorized requests and keeps authorized work running.
6. **Record.** Telemetry is stored in ClickHouse Cloud and read back exactly. A status file is published and read back.

## Sponsor tools: what actually ran

| Tool | Result | Evidence |
|---|---|---|
| Semgrep | 1 finding before the fix, 0 after. A scan of our own AI-written agent code found a real `exec()` call, which we replaced and rescanned clean. | `evidence/successor_011`, `evidence/successor_016`, `evidence/semgrep_own_code` |
| Akash | GPU container deployed through the Akash Console API (provider-reported V100), `qwen2.5:0.5b` inference HTTP 200 in 3.5 s, deployment closed. | `evidence/successor_024` |
| ClickHouse Cloud | 55 records ingested, replayed without duplicates, queried in ~120–190 ms, read back with an exact hash match. | `evidence/successor_016` |
| Pi | Not used. No product access at the event. | — |

Full details, failures and limits: [docs/EVIDENCE.md](docs/EVIDENCE.md). Machine-readable index: [evidence/INDEX.json](evidence/INDEX.json).

## Verify it yourself

```sh
sh scripts/setup.sh                      # local venv incl. Semgrep
.venv/bin/python agent/verify_all.py     # add --json for machine-readable output
```

This recomputes every Merkle/MMR prefix of every record. It also checks frozen source files against the git commit they were frozen from. Expect `PASS` for 8 records and `CHAIN_ONLY` for 3 kept failure records (reasons in [docs/EVIDENCE.md](docs/EVIDENCE.md#known-gaps)). No credentials are needed.

## Limits

- The fault is simulated in software on a small teaching fixture. This is not a whole-system security guarantee.
- Hashes prove the recorded bytes are unchanged. They do not prove truth, safety or causality.
- The GPU type is reported by the provider, not attested. No confidential-computing claim.
- Receipts are unsigned. Failed attempts are kept on purpose.
- Part of the custody framework was built before the event.

## Run locally

```sh
sh scripts/setup.sh && sh scripts/demo.sh        # cockpit at http://127.0.0.1:8790
```

Sponsor runs need your own keys in a local `.env`, which is git-ignored and never committed.

Original explanatory content © 2026 Biobitworks, CC BY-NC-ND 4.0. Software license not established. Third-party rights retained.
