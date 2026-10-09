# 018 orchestration draft (written BEFORE delegating; status = PLANNED, not executed)

Recovered facts (orchestrator, 2026-10-09):
- No ch015/ch016 process active. 015 (successor_015, 12 leaves, root 54dce23e...) and 016 (successor_016, 15 leaves, root 4661c8f8...) both ran against ClickHouse Cloud; `verify` PASS, NOT_SIGNED. fault_to_response NOT_TESTED/QUARANTINED in both. => ClickHouse lane VERIFIES existing receipts; no re-ingest.
- Semgrep: own-code scan found exec() at agent/agent011.py:89 (016). Guardian (authenticated) not yet used.
- Akash: .env holds AKASHML_* names (values not read). src/cascade.py akash route expects ANTIGENSE_AKASH_URL/TOKEN (Ollama-style) - mismatch with AkashML API to resolve.
- Seedgraph sentence-diagramming contract: unrecovered (UNKNOWN).
- Lane output dirs: evidence/lane018/{context,semgrep,clickhouse,akash,client}. Orchestrator integrates.
Ceilings: hashes = integrity only; behavior needs controlled healthy/fault comparison; nothing SIGNED.
