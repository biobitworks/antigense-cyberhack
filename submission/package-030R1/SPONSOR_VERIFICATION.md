# Sponsor verification — 2026-10-09

| Sponsor | Recorded work | Verified scope |
|---|---|---|
| Semgrep | v1.180.0, fixture scan 1 finding before and 0 after | Exact target/rule/output hashes bound to recomputed incident MMR. Local custom rule, not proof of Guardian installation or repository-wide security. |
| ClickHouse | Authenticated Cloud ingest of 11 incident rows, repeated insertion, exact readback; HTTP200, 160.706 ms query | Preserved occurrence count and matching projected values. Recorded successful operation; no new cloud request made during this verification. |
| Akash | Deployment, lease, model pull, inference HTTP200 in 3466.4 ms; schema valid, advice not applied; close HTTP200 success:true | All 11 custody leaves and artifact bytes match. Server-reported VRAM 1,299,800,320 bytes; hardware attestation, billing and final closed-state readback remain unverified. |

The orchestrator freshly recomputed the 13-leaf incident MMR 66c3e6e8a64f36f1290a598606d6b9034de1bca62ef559d058e5013d95c12723 and verified the governed source snapshot. It also ran the GPU verifier, which recomputed all prefixes and artifact bytes with 11 leaves and MMR f67a3e74aa52f606784faec7cece9da6b071ff1984e762d72c662031a881b244. No new paid workload was launched.

Separate branches preserve separate run identities. Hash integrity is not remote hardware attestation, physical causality or proof of actual savings. Pi is not counted. Historical screenshots and the old silent video do not show the new GPU result.
