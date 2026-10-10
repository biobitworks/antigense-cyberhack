# Antigense 056 corrective sponsor homepage

This is a post-competition successor, NOT what judges saw when the event was submitted.
The predecessor homepage is preserved under `public/archive/submission-054/` with HTML
SHA-256 `80dc78b4e2cd8b23bd9094a725f567de473db27cb9b80629f3f8da7b3424a888`.

The corrected homepage admits Semgrep (successor_011/016), Akash (successor_023/024),
and ClickHouse (successor_016). It retains Pi Security as NOT_USED, not as a featured
executed sponsor. Public sponsor projections reference the frozen ledger SHA-256
`788fe09575a3ecb9de2694391d11dfee8e0170c44d361210afcafaf06956b26f`.

**055 sponsor release admission:** PASS on corrected source, whereas preserved predecessor
BLOCKS with 6 distinct violations. Source test suite 18/18 PASS. A Vercel build must run
the Python admission gate and abort for missing sponsors; a required GitHub status also
verifies the independently recomputed release 056 MMR and its Ed25519 signature.

**056 accountability:** `public/data/audits/release-accountability-056.json`
contains 9 ordered leaves, peaks, all independently recomputed prefixes and root:
`2c49d2ffd87a6439f28281ae86d377937d3ec04c72f89ce9889c62b772af6833`.
The receipt has a verifiable **Ed25519** signature in
`public/data/audits/release-accountability-056.verify.json`; public key SHA-256
`99c793dc9c99290204c763314718ef61c40783b6fee4cf8b394c96874ee850be`.
Signing key remains only in the authorized magicPRObox local key vault. This signature
proves key possession, not human identity, model attribution, action time, judging
causality or actual sponsor provider execution.

The nine leaves are *selected retrospective audit atoms*. They are not a cryptographic
record of every historical conversation turn or every agent action. Original 056
candidate MMR root `691e3bab…` from a different candidate compilation is a
**predecessor candidate**, not this verified successor; do not conflate roots.

**NOT_TESTED:** hardware/TEE attestation, human identity attestation, future
manual Vercel API bypass, alleged score causality, and external timestamp signing.
Production-readback receipt must be a later successor, never backfilled.
