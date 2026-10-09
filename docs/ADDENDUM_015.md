# 015 addendum - ClickHouse projection
agent/ch015.py projects canonical successor_011 FCO/JSONL records into a dedicated ClickHouse table (antigense_events_015, ReplacingMergeTree keyed by occurrence_id), runs incident queries, replays the ingest to test idempotence, reads every row back and reconciles exactly against the canonical records. The database is a rebuildable projection; a mismatch is FAILED and canonical records are never edited.
Credentials: CLICKHOUSE_HOST/USER/PASSWORD from env or a hidden getpass prompt; never written. Host recorded only as SHA-256. TLS verification is never disabled; redirects are rejected.
Ceiling: tens of rows; no scale/latency-at-scale claim; no prize-eligibility claim. SELECT 1 (014) is connectivity only. Inherits CUSTODY_CONTRACT_011.json unchanged.
Not done here: dashboard display of the query result; Akash inference; fault-to-response interval (no valid fault timestamp in these records => NOT_COMPUTED).
