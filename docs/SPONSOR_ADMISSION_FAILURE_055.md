# Sponsor release admission failure — retrospective 055

## Incident and scope

**Project:** `biobitworks/antigense-cyberhack`
**Parent governed repo state:** `24a6d4137dc38a194a8eccaccc6e4f4d45d577ee` (release 054R1).
**Submitted evidence target:** `https://antigense-cyberhack.vercel.app/` on October 9, 2026.
**Public readback:** HTTP 200; **12,695 bytes**; SHA-256 `80dc78b4e2cd8b23bd9094a725f567de473db27cb9b80629f3f8da7b3424a888`.
**Canonical sponsor index:** `evidence/INDEX.json`; SHA-256 `788fe09575a3ecb9de2694391d11dfee8e0170c44d361210afcafaf06956b26f`.
**Retrospective admission result:** **BLOCK**, six discrete rule violations. Exact local deterministic receipt: `evidence/audit_055/released_054_homepage_failed_gate.json`.

## Findings

| Declared sponsor | Frozen evidence index | Submitted homepage primary card | Release gate result |
|---|---|---|---|
| Semgrep | EXECUTED, successor_011 / successor_016 | Present; static `NOT_TESTED` placeholder; no in-card sponsor evidence link | BLOCK — status not explicit, no direct link |
| Akash | EXECUTED, successor_024 / successor_023 | Present; static `NOT_TESTED` placeholder; no in-card sponsor evidence link | BLOCK — status not explicit, no direct link |
| ClickHouse | EXECUTED, successor_016; failure predecessor successor_015 | **Absent** | **BLOCK — required executed sponsor missing** |
| Pi Security | NOT_USED, event access not available | Featured as third main card | **BLOCK — unexecuted sponsor featured** |

The static JS placeholders might update dynamically after fetch; the gate **deliberately** requires an accurate pre-JavaScript presentation. It does not establish which runtime text any individual judge actually saw. The ClickHouse absence is unambiguous at the homepage content level.

The committed ClickHouse ledger records 55 historical cloud records replayed and 55/55 exact readback, plus a separate 11-checkpoint incident historical readback. These are NOT claims that a Cloud operation was executed during live Judge 050 or during page load.

## Mechanism of failure

Predecessor custody hashes and historical proof recomputation passed, but no mandatory **cross-artifact invariant** existed requiring each `EXECUTED` sponsor entry to appear as an **accurately labeled, directly verifiable landing-page card** and requiring the **published HTML bytes** to match the admitted source. We substituted site reachability/video/Merkle integrity tests for sponsor-claim discoverability.

This is not a failure of SHA-256 or Merkle mathematics: the missing relationship had **never been required as a release oracle**. MMR inclusion of source artifacts cannot assert a user-interface predicate unless that predicate is separately computed and admitted.

## Implemented successor control

`scripts/audit_sponsor_publication_055.py`:

- deterministically extracts featured sponsor cards from the source page;
- derives required sponsors from the frozen `evidence/INDEX.json`, not a hand-authored UI list;
- blocks if any `EXECUTED` sponsor is missing, a `NOT_USED` sponsor is promoted, or card states are ambiguous;
- requires each executed sponsor card to link to `data/sponsors/<name>.json`, a **public evidence projection** with exact ledger SHA-256, sponsor, state and record IDs;
- blocks if supplied deployed HTML bytes differ from frozen source, including valid-HTTP but stale/foreign pages;
- produces deterministic receipt JSON with hashes and independent violation codes. It does **not** attest provider execution.

**7 regression tests:** original missed ClickHouse fails; a properly bound three-sponsor site passes; invented card, altered projection, mismatched readback, misleading static status and changed ledger all block.

`.github/workflows/sponsor-evidence-gate.yml` runs this on relevant PR changes and main updates. **Status checks must also be marked REQUIRED in GitHub branch protection / deployment authorization to ensure no human or agent can bypass them.** That setting has NOT been made by this successor.

The gate requires additional candidate work: public index-bound sponsor projection files and correct homepage content. This audit branch intentionally fails on the historical homepage; that failure is the desired retrospective result. **Do not silently replace the already submitted original homepage.** Reconcile in a separate successor, verify fresh production readback, then record a new release acceptance report.

## Impact and causal ceiling

The user reports potentially hundreds to thousands of dollars in foregone opportunity. **Financial loss amount = NOT_COMPUTED.** **Causal attribution to score/ranking = UNKNOWN** pending organizer rubric, judging comments and counterfactual. The observable delivery defect is independent of those unknowns and requires corrective governance.

## ConversationFCO / breakpoint — 055 (candidate)

- **Parent:** release 054R1 at `24a6d41`; production 054 Vercel source `59c03e1`.
- **Project/repo:** `biobitworks/antigense-cyberhack`; proposed branch `codex/sponsor-audit-gate-055`.
- **Source evidence:** SHA-256-bound `evidence/INDEX.json`, exact submitted `public/index.html`, unchanged public readback.
- **Atom/FCO candidates:** source sponsor statuses, sponsor record IDs, homepage card labels/status/link paths, six individual failure findings, approval/verdict.
- **Typed graph relationship candidates:** `LEDGER_DECLARES_EXECUTION`, `HOMEPAGE_FEATURES`, `CLAIM_REQUIRES_RECEIPT`, `RELEASE_BLOCKED_BY`. These are declared relations and **not causal attribution**.
- **Transition:** retrospectively compute explicit sponsor-presentation oracle (never tested during original submission), preserve predecessor state.
- **Executed:** immutable receipt creation and seven regression tests. No cloud provider re-execution.
- **Decision:** historical 054 release would have been **BLOCK** under 055 policy; no retroactive rewriting of historic GO.
- **Failures:** ClickHouse absent, Pi featured, static statuses ambiguous, sponsor receipt links missing.
- **NOT_TESTED:** score consequences, pre-submission CI enforcement, provider end-to-end replay, full remote judge view.
- **Signature:** NOT_SIGNED.
- **MMR:** NOT_COMPUTED. Only SHA-256 identities computed; no fabricated append/commit.
- **NEXT_ACTION:** create successor *corrected* homepage and public evidence projections; demonstrate gate PASS on candidate and exact deployed-byte readback; require CI status in branch protection/Vercel promotion policy.
