# 012 addendum
Adds agent/telemetry012.py: loads successor_011 step observations into a local open-source ClickHouse (clickhouse local, MergeTree table under .runtime/ch) and queries them. Contract: inherits CUSTODY_CONTRACT_011.json unchanged.
Ceiling: local open-source ClickHouse 26.x only; not ClickHouse Cloud, no credits, small data (tens of rows), no scale or latency-at-scale claim.
