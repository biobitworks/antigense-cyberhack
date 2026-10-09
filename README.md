# Antigense — Hardware faults must not become security failures

A reproducible, local-first Cyberhack demo centered on **Akash, Semgrep and Pi Security** (P1 interpreted as Pi; confirm onsite). A software-injected corrupt worker result trips an integrity check; a deliberately unsafe fallback demonstrates an authorization bypass. Semgrep scans the exact code. AI proposes a response, a local review action authorizes the pinned fix, and deterministic checks verify recovery. Every stage computes a Merkle commitment and appends to a verified HydraLamp-compatible MMR.

## Run privately

Python 3.10+; Semgrep in an isolated virtual environment. No cloud credentials needed for the local lane.

```sh
sh scripts/setup.sh
sh scripts/demo.sh
```

Open http://127.0.0.1:8790 . Click Run bounded scenario, inspect the receipts, then Approve pinned fix. Only the teaching fixture changes active selection. No host security settings, processes or files outside this project are patched. Session token plus strict Host/Origin checks protect browser mutations. This is a local demo boundary, not a multi-user security product.

CLI: `.venv/bin/python src/cascade.py run --ai local`; approve with the returned exact current MMR root: `.venv/bin/python src/cascade.py approve --expected-mmr ROOT --actor operator --provenance local-console`. Verify: `.venv/bin/python src/cascade.py verify`.

Local AI uses an already installed Ollama model `qwen2.5-coder:7b`; no model downloads. If unavailable, the receipt says NOT_TESTED/FAILED. Akash is an optional sanitized inference route: set ANTIGENSE_AKASH_URL to your authenticated HTTPS Ollama-compatible `/api/generate` endpoint and ANTIGENSE_AKASH_TOKEN privately, select `--ai akash`. Never call an arbitrary shared public endpoint confidential. Verify lease identity, GPU identity, fresh nonce, CPU+GPU report certificate chains, measurements and TLS binding separately. We do not implement that attestation verifier yet. Pi's public API/local mode is unconfirmed; use docs/PI_INTAKE.md with sponsor onboarding. Neither local AI nor our review gate is a Pi integration.

## Evidence and claims

- Fault: SIMULATED_BYTE_XOR in software; not a physical GPU failure or malicious attack.
- Arithmetic, checksum, boolean exploit and regression matrix: executed, not narrated.
- Semgrep: actual local CE scan when installed; fixed local rule, metrics/version check disabled, token removed. A clean custom-rule scan does not prove general security.
- 3D: virtual schematic, not CAD or discovered internal geometry. Local CPU count, memory, load and service time are OS observations; GPU temperature/power/ECC and attestation UNKNOWN.
- AI: model text is non-deterministic untrusted advice; hash commits the observed bytes. Deterministic policy and verifier do not trust that advice.
- Human: unsigned local approval records an action; browser/console actor labels do not establish human identity or proof of possession.
- Public Vercel MVP: sanitized recorded replay, no private telemetry endpoint or credentials. Local mode polls actual host observations separately from replay.
- IEEE datasets reviewed, not downloaded/trained on; see docs/DATASET_REVIEW.md.

Project freeze covers the fixed source list in src/custody.py. Each FCO contains classification, true/false checks, yes/no renderings, anticube UNKNOWN/SELF_SAFE null and calculated delta-G*. G* is an unvalidated information-state diagnostic, not a physical quantity or safety score. Hash integrity is not truth or causality. MMR is separate successor of 008R1; PREDECESSOR_008.json retains old roots. Full prefix recomputation is implemented; compact externally signed proofs are not.

## Submission

See docs/SUBMISSION.md, docs/VOICE_SCRIPT.md, docs/SPONSOR_CHECKLIST.md and docs/DATASET_REVIEW.md. Private repository and sanitized public MVP are separate from local execution. Prebuilt-work eligibility and sponsor track rules remain UNKNOWN until organizers confirm. Provisional name; trademark availability not checked.
