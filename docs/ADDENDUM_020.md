# 020 addendum - Akash troubleshooting + inference
agent/akash020.py: records key SHAPE only (set, length, akml- prefix, stray whitespace), lists /v1/models, then attempts the chat call (default UA, then a named UA if the first fails), retaining status, Inference-Id and a bounded redacted error excerpt. Reuses agent011.py unchanged. Own successor freeze (evidence/successor_020).
Ceiling: managed AkashML inference only; no GPU lease, attestation or confidentiality claim. AI advice untrusted, not applied. Credentials from env only, never recorded.

021: identical to akash020 except site files (public/*), which another session edits concurrently, are excluded from this freeze; they are irrelevant to the Akash call.
