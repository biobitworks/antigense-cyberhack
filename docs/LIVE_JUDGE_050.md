# Live Judge 050 — guarded real-time interaction (local successor)

**Canonical hackathon project:** [Antigense Daisy](https://tokensand.com/p/antigense-daisy)
**Submission repository:** biobitworks/antigense-cyberhack
**Parent technical state:** 042 commit `265699cde9812977108455707e1ddfeb15093112`
**Branch:** `codex/live-judge-050` (separate worktree, not merged or published)
**Classification:** EXECUTED LOCAL only. Never substitute for sponsor Cloud execution.

## Goal and provenance

Bring the pattern of Kylon/BioBridge-style public interaction and Sauna/BioCustody-style provenance into a *minimal local synthetic judge interaction*, while reusing Antigense's previously implemented strict admission policy, Python FCOs and Merkle/MMR verifier. No Kylon, Voiceworks or BioCustody source code is imported. Their separate live deployments, authentication models, and reported signatures are not verified by this successor.

The local judge role is a **bearer capability**, not a verified person or judge identity. A public spectator sees only a sanitized event stream and roots. An operator may submit one synthetic ALLOW/DENY review with its **expected prior root** and a `DEMO:`-prefixed private note. The review does **not** apply a patch, spend cloud credits, transact, or upgrade any sponsor claim.

## End-to-end path

Source fixture before/after -> local four-case truth oracle -> STRICT_V2 approval gate -> local HTTP review (capability and same-Origin) -> new occurrence FCO -> typed `DEPENDS_ON_RECORDED_PREDECESSOR` -> append-only ordered MMR -> independent recomputation -> public SSE checkpoint -> authenticated private note readback.

- **Public**: `GET /api/public`, `GET /api/stream` (SSE). No token, reviewer note, raw source/private payload, or authority to write.
- **Private**: `GET /api/private` with Bearer capability; validates private-note SHA and length against corresponding source FCO occurrence.
- **Write**: `POST /api/review`, matching `Origin` and exact `Host`; capability; expected previous MMR root; synthetic-only note; valid ALLOW/DENY choice; serialized append; readback verification; no external side effects.
- **Failure cases**: bad origin, missing/incorrect token (403), malformed/non-synthetic payload (400), stale/replayed root (409), tampered private sidecar (409 on private read).

## Reproduce on magicPRObox

```bash
cd /Users/byron/projects/hackathon/antigense-live-judge-050
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 agent/judge_live050.py --port 8850 --output .runtime/judge050-local-run
```

Open **http://127.0.0.1:8850/** from magicPRObox. The process prints the path to `.local_capability`; retrieve that file **locally** on the authorized host and paste the value into the judge-only password field. Do not paste the capability into chat, screenshots, GitHub, public URLs or receipts. The browser uses the credential only in an HTTP header and holds it in page memory. Press **Record judge action** while watching the public custody stream update. Public SSE uses a reconnecting read-only stream; the server is limited to `127.0.0.1`.

**Run isolation:** choose a brand-new `--output` directory for each new run; never overwrite earlier evidence. A local process restart uses a different run and token. All private notes are demo-only and stored locally with owner-only permissions.

## Measurable claims and ceilings

| Question | Admission |
| --- | --- |
| Actual local HTTP review occurred? | Verify local request/response, server note, FCO step and root |
| Event appended at the expected prefix? | Verify `custody.verify`, ordered leaves, peaks, and independently recomputed root |
| Public audience received a real-time update? | Integration test consumes SSE across a concurrent POST |
| Private note or bearer token in public projection? | Rejected by string-level negative tests |
| Browser action represents the authenticated human judge? | UNKNOWN; local capability possession only |
| Signed FCO identity? | NOT_SIGNED; HMAC/Ed25519 not claimed |
| Sponsor API called in this run? | NOT_TESTED; Semgrep, Akash, ClickHouse historical evidence is preserved separately |
| Kylon or Sauna remote session integration? | NOT_TESTED; patterns investigated, no live cross-app connection |
| Hardware/TEE or blockchain attestation? | NOT_TESTED |
| ROI, measured token savings or actual income? | NOT_COMPUTED |
| Published to Tokens&? | NO. Existing entry unchanged |

## Post-demonstration decisions

1. First audit and correct any UI/public-readback gaps; keep predecessor state immutable.
2. For a public hosted judge run, design proper authenticated identity, CSRF enforcement, rate limits, audit retention, signed receipts, safe public projection, and protected server-side secrets. **Do not put the bearer capability in static site assets.**
3. Freeze sponsor-aware same-run comparison oracles before optional Cloud executions. Confirm explicit operator budget and credential scopes.
4. Ingest the same local event stream to ClickHouse as a projection only after canonical source verification and explicit authorization. Compare 55 historical records against current universe separately.
5. Do not modify Tokens& submission or share private repo contents without an explicit publication decision.

## FCO/FCG control note

Each accepted local decision produces a new StepFCO, occurrence ID, typed predecessor edge, and verified Merkle/MMR prefix. Reused fixture content does not conflate distinct decision occurrences. The MMR root commits ordered bytes; it does not establish correctness, causal security, user identity, or external custody. Corrections must create successors. Report an explicit `NOT_TESTED` rather than inferring past sponsor or wallet execution.
