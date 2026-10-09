#!/usr/bin/env python3
"""Automated LIVE HTTP/SSE demonstration. Known synthetic-only capability, no cloud calls."""
import argparse
import http.client
import json
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "agent"), str(ROOT / "src")]
import custody
from judge_live050 import JudgeState, create_server


def call(port, method, route, body=None, headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=8)
    hdr = {"Host": f"127.0.0.1:{port}", **(headers or {})}
    if body is not None:
        hdr["Content-Type"] = "application/json"
    connection.request(method, route, body=json.dumps(body) if body is not None else None,
                       headers=hdr)
    resp = connection.getresponse()
    data = json.loads(resp.read())
    status = resp.status
    connection.close()
    return status, data


def run(directory: Path, output: Path) -> dict:
    # A public test credential, never a live/private user's identity.
    cap = "LOCAL_SYNTHETIC_TEST_CAPABILITY_050"
    state = JudgeState(directory, capability=cap)
    server = create_server(state, 0)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    auth = {"Authorization": "Bearer " + cap,
            "Origin": f"http://127.0.0.1:{port}"}
    try:
        a, first = call(port, "GET", "/api/public")
        assert a == 200 and first["chain_pass"] and first["mmr"]["leaf_count"] == 2
        baseline = first["mmr"]["root"]
        no_read = call(port, "GET", "/api/private")[0]
        payload = {"decision": "DENY", "expected_root": baseline,
                   "note": "DEMO: synthetic security review denial"}
        denied = call(port, "POST", "/api/review", payload,
                      {"Origin": auth["Origin"]})[0]
        wrong_origin = call(port, "POST", "/api/review", payload,
                            {**auth, "Origin": "http://example.invalid"})[0]
        status, denied_action = call(port, "POST", "/api/review", payload, auth)
        assert status == 201 and denied_action["accepted"]
        a, interim = call(port, "GET", "/api/public")
        assert a == 200 and interim["mmr"]["leaf_count"] == 3
        replay = call(port, "POST", "/api/review", payload, auth)[0]
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=8)
        conn.request("GET", "/api/stream", headers={"Host": f"127.0.0.1:{port}"})
        stream = conn.getresponse()
        assert stream.status == 200
        first_stream = None
        for _ in range(10):
            line = stream.fp.readline().decode()
            if line.startswith("data: "):
                first_stream = json.loads(line[6:])
                break
        assert first_stream and first_stream["mmr"]["root"] == interim["mmr"]["root"]
        second_payload = {"decision": "ALLOW", "expected_root": interim["mmr"]["root"],
                          "note": "DEMO: synthetic tested review approval"}
        status, allowed_action = call(port, "POST", "/api/review", second_payload, auth)
        assert status == 201 and allowed_action["accepted"]
        stream_changed = False
        for _ in range(30):
            line = stream.fp.readline().decode()
            if line.startswith("data: "):
                item = json.loads(line[6:])
                if item["mmr"]["leaf_count"] == 4:
                    stream_changed = True
                    break
        conn.close()
        assert stream_changed
        final = call(port, "GET", "/api/public")
        private = call(port, "GET", "/api/private", headers={"Authorization": auth["Authorization"]})
        assert final[0] == 200 and private[0] == 200
        assert len(private[1]["private_notes"]) == 2
        assert not any(n["note"] in json.dumps(final[1]) for n in private[1]["private_notes"])
        assert cap not in json.dumps(final[1])
        check = custody.verify(state.path / "custody")
        ordered = custody.rows(state.path / "custody")
        mmr = custody.mmr(ordered)
        assert check["PASS"] and mmr["root"] == custody.independent_mmr_root(ordered)
        assert check["mmr_root"] == final[1]["mmr"]["root"]
        report = {
            "schema": "antigense.judge050.smoke_receipt.v1",
            "source": "AUTOMATED_LOCAL_HTTP; synthetic bearer capability; NOT HUMAN",
            "parent_commit": "265699cde9812977108455707e1ddfeb15093112",
            "initial_root": baseline,
            "final_root": mmr["root"],
            "leaves": len(ordered),
            "peaks": mmr["peaks"],
            "proof_algorithm": mmr["algorithm"],
            "independent_recomputation": True,
            "frozen_source_valid": final[1]["frozen_artifacts_bound"],
            "runtime_code_bound": final[1]["runtime_code_bound"],
            "checks": {"unauthorized_private_read": no_read,
                       "unauthorized_write": denied,
                       "cross_origin_write": wrong_origin,
                       "stale_replay": replay,
                       "denial_recorded": denied_action["receipt"]["index"],
                       "allow_recorded": allowed_action["receipt"]["index"],
                       "public_stream_updated": stream_changed,
                       "private_journal_exact_readback": len(private[1]["private_notes"]) == 2,
                       "public_redaction": True},
            "signature": "NOT_SIGNED",
            "identity": "UNVERIFIED_LOCAL_TEST_CAPABILITY",
            "sponsor_calls_this_run": "NOT_TESTED",
            "ROI": "NOT_COMPUTED",
            "private_content_in_receipt": False,
        }
        if not (no_read == denied == wrong_origin == 403 and replay == 409):
            raise AssertionError("Negative control did not reject")
        if output.exists():
            raise FileExistsError("Refuse to rewrite saved smoke evidence")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return report
    finally:
        server.stopping.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output_dir, args.receipt)
    print(json.dumps({k: result[k] for k in
                      ("initial_root", "final_root", "leaves", "checks", "signature")}, indent=2))
