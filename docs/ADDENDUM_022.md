# 022 addendum - Akash Console API (read-only)
agent/akash_console022.py makes one authenticated read-only call, GET https://console-api.akash.network/v1/deployments?limit=5, with the operator's Console API key (prefix ac.sk.; read from AKASH_API_KEY or, if it carries that prefix, AKASHML_API_KEY). Records HTTP status, latency, deployment count and response hash; owner addresses and deployment contents are not recorded.
Ceiling: authenticated Akash Console API execution only. No deployment, lease, GPU, inference, attestation or spend. Site files excluded from freeze.

023: identical except a named User-Agent; 022 failed with Cloudflare error 1010 (client signature blocked) before reaching Akash.
