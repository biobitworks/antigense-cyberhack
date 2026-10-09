# Antigense — Cyberdefense Hackathon submission update (043)

**State:** PREPARED_NOT_SUBMITTED. Parent PR1 head `7433431` and separate Codex 041 branch `0a1c241`. Does not replace historical receipts, edit public index, change the existing demo, or authorize paid sponsor reruns.

## Project title
**Antigense — Evidence-driven agentic cyberdefense**

## Short description / elevator pitch
A corrupt worker result can trigger a dangerous fail-open authorization decision. Antigense reproduces that failure in a controlled software fixture, uses Semgrep to locate the vulnerable fallback, bounds AI-generated remediation advice behind a review gate, and records the response as content-addressed FCOs linked in an append-only FCG with independently recomputable Merkle/MMR checkpoints.

## Full project description (paste into hackathon form)

Antigense is a bounded security-control prototype for an important class of AI-system failure: a corrupt worker result can become an unsafe authorization decision when software fails open. Instead of treating a plausible model answer or a successful API call as permission to repair a system, Antigense requires independently inspectable evidence and an explicit review transition.

The prototype executes a software-injected byte fault, detects a checksum mismatch, reproduces a deliberately vulnerable fail-open fallback, and uses a pinned Semgrep CE rule to identify it. A narrowly scoped correction is selected by a local review action; a four-case regression matrix verifies that healthy authorized work continues while unauthorized requests are denied. This is a teaching fixture and does **not** simulate a physical hardware failure or apply a patch to production infrastructure.

The differentiator is the custody architecture. Each step is represented by a Fractal Custody Object (FCO), connected by a typed predecessor relationship in the Fractal Custody Graph (FCG), and included in a deterministic Merkle Mountain Range (MMR). Local action, predecessor, committed object bytes, ordered ledger and independent recomputation remain distinct. An actual local browser-bound review action was recorded as event 9 of a 12-leaf run, with a recomputed MMR root; its proof snapshot can be independently checked in a browser. The signatures and actor identity remain unverified, and an archived public snapshot is not a live connection to the operator's machine.

Sponsor usage is evidence-scoped: **Semgrep** executed local before/after scans (one pinned finding before, zero after). **Akash** separately provided an authorized provider-reported GPU deployment, qwen2.5:0.5b inference (HTTP 200) and a successful closure API response; its advice was not applied. **ClickHouse Cloud** ingested and read back historical incident custody rows, with exact bounded fixture reconciliation. **Pi Security** has a prepared intake but no observed API execution. Failures (including historical HTTP 401), unknown billing, missing final closed-state readback and missing GPU/TEE attestation are preserved—not upgraded to successes.

The interactive app, narrated walkthrough, historical execution receipts, public browser-verifiable local FCG proof and technical documentation allow judges to inspect exactly what was built, what was actually run and which assertions remain open. This is a prototype for auditable agentic cyberdefense, not a claim of comprehensive security, experimental model accuracy, trusted wall-clock timing or physical hardware attestation.

## What judges should do (priority order)

1. Watch the **142-second narrated overview** at https://antigense-cyberhack.vercel.app/demo-034.mp4.
2. Inspect the **recorded interactive story** at https://antigense-cyberhack.vercel.app/walkthrough-035.html.
3. Visit the **application** at https://antigense-cyberhack.vercel.app/ (public site replays previous work; live local actions require authorized loopback server).
4. Inspect the **technical explanation** at https://antigense-cyberhack.vercel.app/technical-029.html.
5. **After it is explicitly deployed/read back:** open https://antigense-cyberhack.vercel.app/judges-043.html to click **Recompute local FCG proof**, observe 12 ledger entries, event 9 parent/typed edge and independent MMR replay. This is a static public snapshot of a genuine earlier local run, NOT remote live execution.
6. Review source/receipts in https://github.com/biobitworks/antigense-cyberhack/pull/1 and the independent local verification branch at https://github.com/biobitworks/antigense-cyberhack/pull/2. **Repository is PRIVATE; invite judges or provide a carefully sanitized, authorized public mirror.** A raw private URL cannot prove their access.

## Exact local verification witness included in v043

- Run ID: `run-20261009T204741Z-5cb3db65`
- Project root: `9053be5ed053068d50f22e96acec01d52e466a2ddcb6fa66cf1e406274dd599c`
- MMR root: `02d102de2d19334b582a5a9ebde4e55de184533a607d81cc2b317c000423ddc3`
- Entries: 12 (genesis plus 11 recorded steps)
- Human review: event 9, `08 Local review action`, `DEPENDS_ON_RECORDED_PREDECESSOR`, UNSIGNED_LOCAL_BROWSER_ACTION
- `public/data/live-local-043-proof.json`: served historical local proof bytes retained exact.
- `public/data/live-local-043-index.json`: sanitized pointer, hash and derived four-leaf package commitment.
- Browser: `public/judges-043.html` calls existing `verifyProof()` and performs SHA-256 + full leaf/object/MMR prefix checks.
- New public artifacts remain **NOT_DEPLOYED** until site publication/readback; original `demo-034.mp4` stays unchanged.

## Technology and sponsor roles

Python, JavaScript, SHA-256, deterministic JSON canonicalization, ordered Merkle trees, HYDRALAMP_MMR_V1, FCO/FCG, browser WebCrypto, local macOS telemetry, Semgrep Community Edition (pinned custom rule), ClickHouse Cloud (historical bounded evidence projection), Akash Console GPU (separate prior execution) and qwen2.5:0.5b (untrusted analysis). Pi Security intake only — no Pi API/CLI call observed. Vercel hosts the sanitized public demo; local loopback app performs authenticated review and execution.

## Eligibility / no fabricated evidence

Pre-event ancestry includes Agent Foundry recorder and 008R1 custody toolkit; hackathon successor 009 and later receipts specify new controlled experiment, scans, cloud operations and local custody improvements. Do not imply all underlying infrastructure was built at the event. Repository remains private; judge access and rules require confirmation. The official form at https://tokensand.com/cyberhack/submit requires authentication; submission status has not been confirmed by this document. User must enter team/contact identifiers through the form's privacy-aware fields.

## Video guidance

**No complete new primary recording is needed** to submit the existing 142-second narrated summary. If the currently recording Claude successor is checked for privacy/audio/content, attach it as **additional technical proof**, not as a substitute for a clean overview. Do not publish microphone recordings before review. Judges must see live local actions labeled NEW_LOCAL, old sponsor receipts labeled HISTORICAL_OBSERVED, and a newly performed read-only query as READONLY_OBSERVED only if its own receipt exists.

## Gates and known nulls

- Repo reviewer access: UNRESOLVED
- Official form submission: NOT_CONFIRMED
- Public proof page deployment: NOT_TESTED
- Actual paid Akash rerun: NOT_AUTHORIZED / NOT_PERFORMED
- Final Akash closed-state readback: NOT_TESTED
- Akash billed amount: NOT_COMPUTED
- GPU/TEE attestation: NOT_TESTED
- Pi Security provider call: NOT_TESTED
- Actor identity/signature: UNKNOWN / NOT_SIGNED
- App browser reload and duplicate action verification of 041 successor: NOT_TESTED
- Sponsor-new-runtime replay synchronized with video: NOT_TESTED

## Next action

Review the public proof snapshot for policy/privacy, independently reverify the capture and browser verifier, then deploy only new `judges-043.html` and `data/live-local-043-*.json` via an isolated clean staging build without replacing public run/proof or demos. GET/read back all three files byte-for-byte, record publication receipt, and only then add judge proof URL to the submission form. No deployment from Claude's dirty working tree.
