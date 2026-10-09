# 037 addendum - live run

agent/live037.py runs the sponsor steps now and appends each to evidence/successor_037 as it happens. agent/live037.html, served on 127.0.0.1:8837 during the run, shows each checkpoint with its wall-clock time and recomputes every MMR prefix in the browser.

Default (no new spend): live Semgrep before/after + behavior matrix; live ClickHouse Cloud ingest, replay, query and exact readback of this run's own steps; live read-only Akash Console status of the earlier successor_024 deployment (dseq 1791574273055).
With --akash-deploy (operator-authorized, one run): new 1-GPU deployment, inference on this run's own Semgrep finding, close in a finally block, then closed-state readback. Bid cap 10000 uact/block.

Ceilings: GPU provider-reported, not attested; receipts unsigned; wall-clock times from the local clock; hashes prove byte integrity, not truth or causality. Credentials from env only. Not interaction-generated persistent FCG state.

037b: agent/agent011.py was fixed after PR review (unauthorized status kept out of public/, real Akash failure reasons, Semgrep-unavailable path, exec-free regression). successor_037 (genesis only, never run) is kept; live runs use successor_037b.
