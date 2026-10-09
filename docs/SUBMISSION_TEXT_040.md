# Submission text (copy and paste) — current as of 2026-10-09

**Title:** Antigense Daisy: error to recovery, with Semgrep and Merkle breakpoints in review

**Video:** https://youtu.be/hpLH88V6PF0
**Repo:** https://github.com/biobitworks/antigense-cyberhack (branch `agent-011-sponsor-evidence`, PR 1)
**Tracks / tools:** Akash, Semgrep, ClickHouse

**Description**
A recorded replay of one controlled incident. A software-injected byte fault makes a worker's result corrupt. Semgrep flags the unsafe fallback, and the pinned repair keeps healthy authorized work running. ClickHouse Cloud ingests the incident, replays it and reads it back exactly. Akash GPU inference runs on a separate custody branch. Each step has a custody address, and the browser recomputes the proofs.

We also review our own AI-written code. Semgrep CE found 1 issue; a full read found 20, including one Semgrep did not flag. A Merkle tree over the code points to a changed file in a few comparisons, and each review step is appended to the graph.

**Limits (state these)**
Recorded replay, not live remediation. The fault is simulated, not hardware. Hashes show integrity, not truth, safety or causality. Review-time savings, GPU attestation, billing and cost savings are not tested. Semgrep Guardian not tested. Nothing is signed.

**Rights**
© 2026 Byron P. Lee / Biobitworks. Explanatory content CC BY-NC-ND 4.0; third-party licenses remain separate. Software license not established here.

Superseded draft: docs/SUBMISSION.md (older, mentions Pi).
