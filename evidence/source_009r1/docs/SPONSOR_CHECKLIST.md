# Priority sponsor quality gates

All three are partners with judges in the event listing. User confirmed Pi Security via https://www.pi.security/about . Judges: Akash Greg Osuri; Semgrep Daghan Altas; Pi Mike Caballero and Rishiraj Chandra. Track rules, credit caps and prebuilt eligibility remain UNKNOWN until organizer/sponsor confirmation. No first-of-kind claims.

| Sponsor | Material role | Private/local support verified from primary docs | Execution acceptance gate | Remaining risk |
|---|---|---|---|---|
| Semgrep | Locate fail-open fallback, preserve findings, rescan pinned fix | Local CE scans; local rules; --metrics=off and --disable-version-check. Do not run logged-in cloud CI when local privacy is desired | Before scan has rule finding and exact source/rule/output hashes; no scanner errors; after scan clear; independent regression matrix passes | Custom rule is narrow; no whole-project security proof. CE use may differ from hackathon prize criteria |
| Akash | GPU inference for incident synthesis, optionally Titan model evaluation | CPU/GPU TEE support documented; confidential mode only on compatible providers; public container images currently required | Funded lease record + GPU/model identity + sanitized prompt/result hash + latency; confidential claim additionally requires fresh CPU/GPU quotes, trusted chains/measurements and TLS binding | Credits/lease not configured; adapter not an attestation verifier; shared API does not prove privacy; remote is not local |
| Pi Security | Reproduce report, review exploit/fix/variants and return remediation evidence | Public product/terms describe platform/SaaS; definitive self-hosted/private-network API documentation NOT_FOUND | Sponsor-supported sandbox/private connection; actual request/job/report ID; reproduction and patch review; returned artifact hash; human review recorded | API and private/local deployment UNKNOWN; manual packet and our gate are not Pi execution |

Primary docs: https://docs.semgrep.dev/cli-reference ; https://docs.semgrep.dev/metrics ; https://akash.network/docs/learn/core-concepts/confidential-compute/ ; https://www.pi.security/about ; https://www.pi.security/terms-and-conditions ; event https://luma.com/cyberhack . Checked 2026-10-09. Product claims are not our execution evidence.

Ask Akash onsite: GPU credits and max spend; shortest supported GPU inference path; which provider currently accepts cpu-gpu TEE; authenticated TLS endpoint and supported nonce/channel-bound attestation verifier; model/license; closing lease and billing check. Raw code/host telemetry never required for the minimal prompt.

Ask Semgrep onsite: does local CE/custom-rule usage qualify; preferred sponsored product; whether agentic triage can stay local; required finding/scan artifacts and permitted data transfer. If cloud triage needed, use the teaching fixture only.

Ask Pi onsite: supported hackathon API/CLI/sandbox; customer-managed/private/local mode and its exact trust boundary; retention/training/egress; how to submit our sanitized packet and export reproducible review artifacts; sponsor judge success criteria. Do not substitute unrelated pi.dev coding agent or Pi cryptocurrency tooling.

Value metrics to report: actual finding count, before/after target hash, unauthorized denial matrix, measured inference latency, actual GPU model/lease identity, human gate latency (only if actually measured), stale approval rejection and tamper rejection. Do not claim dollar ROI, detection accuracy or physical safety from one fixture.
