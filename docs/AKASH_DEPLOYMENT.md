# Akash GPU integration runbook — PREPARED, NOT_DEPLOYED

Use the sponsor’s supported funded sandbox, not an arbitrary public API. No lease has been created and no spend authorized. The package adapter accepts an authenticated HTTPS Ollama-compatible endpoint and sends only declared fixture facts. It does not validate Akash ownership or hardware attestation.

1. Confirm sponsored credits, maximum spend, supported model, model license and GPU/provider inventory.
2. Select GPU-capable provider; for sensitive data request `params.tee: cpu-gpu` using the official current SDL example: https://akash.network/docs/learn/core-concepts/confidential-compute/ . TEE only accepts compatible providers and publicly pullable images; never bake secrets into an image or SDL intended for public submission.
3. Use an authenticated HTTPS gateway with a private inference upstream. Do not expose the official bare Ollama port example as a private API. Confirm authentication, TLS validation, request-size limit and denied unauthorized requests.
4. Record deployment sequence, provider, lease identity, model and container digest. Obtain fresh nonce-bound CPU and GPU quotes; independently verify manufacturer roots, certificate chain, expected measurements and TLS channel binding. Our Merkle verifier cannot replace an attestation verifier.
5. Set ANTIGENSE_AKASH_URL and ANTIGENSE_AKASH_TOKEN locally outside git; use `python src/cascade.py run --ai akash`. The endpoint sees synthetic incident facts, not raw host telemetry or private repository code. A response creates an OBSERVED inference receipt; GPU execution and attestation remain NOT_TESTED until separately validated.
6. Pi reviews the resulting packet through its supported sandbox, with actual returned artifacts. Append their actual execution evidence rather than editing the pending receipt.
7. Close the lease, record termination/billing and final evidence hashes.

Measured outputs: inference request/result hashes, model, latency, response status, actual GPU identity and spend. Need baseline accuracy evaluation before claiming GPU inference improves detection. Local arithmetic replay does not justify GPU usage by itself; GPU value is the model inference or later real Titan dataset evaluation. Current limits: no signed attestation adapter, automatic deployment, billing cap enforcer or Pi API adapter.
