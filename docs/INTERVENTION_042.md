# Intervention 042 — F1/F2 bounded agent-assisted repair

Project: biobitworks/antigense-cyberhack
Branch: codex/guarded-intervention-042 (isolated worktree)
Predecessor: agent-011-sponsor-evidence at c2a1a46; docs/HANDOFF_040.md findings F1/F2.
Actor: ChatGPT GPT-6 using authorized Desktop Commander tools. Human-requested code remediation, not autonomous Akash patch application.
Clinical/production scope: NONE. Teaching fixture and custody kernel only.

## Changed source
1. src/cascade.py: remove dynamic import execution; restrict fixture IDs.
2. src/fixture_eval042.py: AST-only boolean evaluator; rejects module-level effects and unsupported syntax.
3. src/custody.py: legacy version remains replayable; new append events select STRICT_V2, missing/false required checks quarantine.
4. rules/fixture-exec-042.yaml: scoped Semgrep static rule for exec_module.
5. tests/test_guarded_intervention_042.py: F1 semantic tests, 2x2 policy oracle, malicious fixture controls, ineffective-patch test.
6. agent/intervention042.py: reproducible controlled runner and independent per-prefix MMR verifier.

## Executed and observed
- Semgrep F2 rule on pinned old/new code: 1 finding before; 0 after; no scanner errors.
- F1 false-check witness: LEGACY_V1 admits an OBSERVED occurrence despite failed check; STRICT_V2 quarantines the equivalent declared-required false check.
- Four authorization truth-table cases: all repaired outcomes match authorized AND worker_healthy.
- Deliberately ineffective OR policy: rejected by independent truth table.
- Valid Python module-level side-effect fixture: rejected without executing its side effect.
- Regression tests: 11 passed (3 earlier tests and 8 additional).
- Merkle/MMR: six source-bound, content-addressed step receipts, verified every step and prefix using append and independent perfect-tree decomposition.
- Existing agent/verify_all.py --json executed without changing historical PASS and CHAIN_ONLY categories.

Evidence is in evidence/intervention_042. Run python3 agent/intervention042.py verify; it recomputes canonical bytes, all leaf hashes, each prefix, peaks and root.

Computed HYDRALAMP_MMR_V1 root:
43522a82b0c2a4428cda56366f65689757d70085031e26997e90b583b846e5a0

Status: VERIFIED_LOCAL / NOT_SIGNED / NO_NEW_SPONSOR_CALLS.
A hash establishes identity/integrity, not scientific truth or proof of intervention causality.

## Unresolved (retain explicitly)
- F1: required_checks are currently caller-declared; independent policy pinning against omitted/substituted critical checks has NOT_TESTED status. This needs successor 043.
- F2: other dynamic-execution sinks not covered by this narrowed repair are NOT_TESTED.
- Semgrep Multimodal and authenticated Guardian project use are NOT_TESTED; Semgrep CE local rule was OBSERVED.
- Akash successor_024 GPU inference remains a SEPARATE OBSERVED historic advisory call. No model-generated patch applied by Akash in lane 042. GPU hardware reported, attestation NOT_TESTED.
- ClickHouse successor_016 readback is historic OBSERVED; this 042 lane did not ingest or query cloud state.
- Baymax is a separate third-party read-only candidate. No code modified or medical data accessed. Its AGENTS.md requires synthetic health data and forbids unapproved shared-db modifications.
- No provider credentials, production patch, regulatory compliance, clinical safety, or autonomous closed-loop efficiency claim.
- No cryptographic signature or independently attested execution time.

## Next action
Create append-only successor 043: freeze required predicates outside untrusted event payloads, inject omitted/substituted critical-check attacks, test new policy admission against an independent oracle, recompute all receipts, and optionally compare Akash, local Ollarma and a deterministic patch baseline without conflating sponsor connectivity with successful intervention.
