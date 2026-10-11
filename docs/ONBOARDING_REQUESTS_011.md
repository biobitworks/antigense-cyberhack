# Minimal onboarding requests (BLOCKED operations)

## Akash (AkashML) - to turn akash_inference from NOT_TESTED to OBSERVED
Need from Byron (privately, never in git): an AkashML API key with credits, and one model id from the Models page.
Run: `AKASHML_API_KEY=... AKASHML_MODEL=<id> .venv/bin/python agent/agent011.py run`
Ceiling if it works: managed inference only (docs: OpenAI-compatible, base https://api.akashml.com/v1). No GPU lease, attestation or confidentiality claim.

## Pi Security - to turn pi_security_review from NOT_TESTED to OBSERVED
pi.security publishes no API/CLI/docs; access is by demo request or on-site sponsor contact.
Ask the Pi judges/staff: (1) a supported hackathon interface for submitting a sanitized reproduction (fixtures/before.py + rules/fallback.yaml + fix) and receiving a report; (2) job/report ID and export format; (3) retention/egress terms. Only an actual Pi job/report ID counts. pi.dev, crypto tools, our human gate and prepared packets do not.
