# Pi Security reproduction and review packet

STATUS: PREPARED / Pi execution NOT_TESTED. No undocumented endpoint assumed. This packet contains only our teaching fixture. Include the current public/data/run.json and public/data/proof.json after local execution.

Prompt for Pi's supported workflow:

> Reproduce the fail-open authorization bypass in fixtures/before.py. The hardware fault is a software-injected byte corruption, not a physical sensor reading. Validate the input-to-fallback attack path and distinguish availability from authorization. Review fixtures/after.py and the four-case test matrix; inspect for the same failure class in the supplied demo repository. Return file/line evidence, a patch review, negatives/unknowns, and supported job/report identifiers with downloadable JSON results. Do not execute host commands or apply generated patches. Describe your deployment and data-retention boundary. Mark any nonexecuted check NOT_TESTED.

Operator import requirements: source Pi job ID/URL, actual returned bytes SHA-256, timestamp, reproduction true/false, fix review true/false, scope and data boundary. Until these exist, this handoff remains NOT_TESTED. Append a new custody object rather than editing our old handoff receipt. Human approval remains a separate current-MMR-bound step; unsigned actor label is not proof of identity.
