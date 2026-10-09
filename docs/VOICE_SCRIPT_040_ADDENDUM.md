# Addendum narration for scenes 11-12 (NOT YET RECORDED — Byron to record or approve)

Scenes 1-10 keep the existing narration unchanged (original file hash 12be0853…5389ba, 142.144 s). Only scenes 11-12 are new factual content.
Record these as a separate file; do not re-record the existing passage. Targets: scene 11 about 20 s, scene 12 about 30 s.

## Scene 11 — Semgrep, then a full code review (~20 s)
"Semgrep scanned our own AI-written code and found one issue: an exec call that runs fixture code. A controlled test confirmed the risk, and an exec-free replacement avoids it. A full read of the code found sixteen findings, including a second place that runs fixtures, which Semgrep did not flag. Semgrep detected one of the sixteen."

## Scene 12 — Merkle breakpoints and the graph update (~30 s)
"Every code file is a leaf in a Merkle tree, and your browser recomputes the root. Change one byte and the tree points to that file in six comparisons instead of twenty-five. Each review step is appended to the graph with typed edges, and that chain recomputes too. Eight of twenty-five files changed since the last reviewed commit, so only those need a fresh look. Review time saved is not tested."

## Claim check (every number traces to evidence/review040/run2)
- Semgrep CE 1.180.0, p/python + p/security-audit + p/secrets, 1 finding (exec-detected, agent011.py:89).
- 16 review findings; Semgrep CE detected 1 (evidence/review040/reviews.json).
- 6 comparisons for the agent011 tamper trial (fcg_steps.json step 6); 25 files.
- 8 of 25 files changed since commit 43c2c65.
- Review-time saving: NOT_TESTED. Semgrep wall-time numbers are shown on screen but not narrated as a benefit.
