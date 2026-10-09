"""Integration controls for live judge 050. All services loopback, no credentials/providers."""
import http.client
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "agent"), str(ROOT / "src")]
import judge_live050 as judge
import custody


class Judge050Test(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.state = judge.JudgeState(Path(self.temp.name) / "run", capability="test-only-capability")
        self.server = judge.create_server(self.state, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port
        self.origin = f"http://127.0.0.1:{self.port}"

    def tearDown(self):
        self.server.stopping.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request(self, method, path, body=None, headers=None):
        headers = {"Host": f"127.0.0.1:{self.port}", **(headers or {})}
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=7)
        conn.request(method, path,
                     body=json.dumps(body).encode() if body is not None else None, headers=headers)
        response = conn.getresponse()
        raw = response.read()
        status = response.status
        conn.close()
        if "application/json" in response.getheader("Content-Type", ""):
            return status, json.loads(raw)
        return status, raw

    def headers(self, token="test-only-capability", origin=None):
        return {"Authorization": f"Bearer {token}",
                "Origin": self.origin if origin is None else origin,
                "Content-Type": "application/json"}

    def test_live_review_increases_mmr_and_is_verified(self):
        code, before = self.request("GET", "/api/public")
        self.assertEqual(code, 200)
        self.assertTrue(before["chain_pass"])
        self.assertEqual(before["mmr"]["leaf_count"], 2)
        code, after = self.request("POST", "/api/review",
                                   {"decision": "DENY", "expected_root": before["mmr"]["root"],
                                    "note": "DEMO: local private security note"},
                                   self.headers())
        self.assertEqual(code, 201)
        self.assertTrue(after["accepted"])
        code, public = self.request("GET", "/api/public")
        self.assertEqual(code, 200)
        self.assertEqual(public["mmr"]["leaf_count"], 3)
        self.assertNotEqual(public["mmr"]["root"], before["mmr"]["root"])
        self.assertNotIn("local private security note", json.dumps(public))
        self.assertNotIn("test-only-capability", json.dumps(public))
        self.assertEqual(public["events"][-1]["decision"], "DENY")
        self.assertTrue(custody.verify(self.state.path / "custody")["PASS"])
        self.assertEqual(public["mmr"]["root"], custody.mmr(custody.rows(self.state.path / "custody"))["root"])
        code, private = self.request("GET", "/api/private",
                                     headers={"Authorization": "Bearer test-only-capability"})
        self.assertEqual(code, 200)
        self.assertEqual(private["private_notes"][0]["note"], "DEMO: local private security note")
        observation = custody.read(self.state.path / "custody" / "step-000003.json")
        self.assertEqual(observation["classification"]["custody_admission"], "ADMITTED")
        self.assertEqual(observation["relation"], "DEPENDS_ON_RECORDED_PREDECESSOR")
        self.assertEqual(observation["SIGNATURE"], "NOT_SIGNED")

    def test_reject_unauthorized_and_stale(self):
        code, initial = self.request("GET", "/api/public")
        self.assertEqual(code, 200)
        payload = {"decision": "ALLOW", "expected_root": initial["mmr"]["root"],
                   "note": "DEMO: private"}
        self.assertEqual(self.request("GET", "/api/private")[0], 403)
        self.assertEqual(self.request("POST", "/api/review", payload, self.headers("incorrect"))[0], 403)
        self.assertEqual(self.request("POST", "/api/review", payload,
                                      self.headers(origin="http://untrusted.site"))[0], 403)
        self.assertEqual(self.request("POST", "/api/review", payload, self.headers())[0], 201)
        self.assertEqual(self.request("POST", "/api/review", payload, self.headers())[0], 409)
        self.assertEqual(self.request("GET", "/api/public")[1]["mmr"]["leaf_count"], 3)

    def test_refuse_notes_outside_synthetic_scope_and_untrusted_hosts(self):
        before = self.request("GET", "/api/public")[1]["mmr"]["root"]
        headers = self.headers()
        bad = {"decision": "ALLOW", "expected_root": before, "note": "patient identifying text"}
        self.assertEqual(self.request("POST", "/api/review", bad, headers)[0], 400)
        self.assertEqual(self.request("GET", "/api/public",
                                      headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.request("GET", "/api/public")[1]["mmr"]["leaf_count"], 2)

    def test_sse_receives_updated_public_commitment(self):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=6)
        connection.request("GET", "/api/stream", headers={"Host": f"127.0.0.1:{self.port}"})
        stream = connection.getresponse()
        self.assertEqual(stream.status, 200)
        initial_data = None
        for _ in range(4):
            ln = stream.fp.readline().decode()
            if ln.startswith("data: "):
                initial_data = json.loads(ln[6:])
                break
        self.assertIsNotNone(initial_data)
        payload = {"decision": "DENY", "expected_root": initial_data["mmr"]["root"],
                   "note": "DEMO: SSE live observation"}
        self.assertEqual(self.request("POST", "/api/review", payload, self.headers())[0], 201)
        updated = None
        for _ in range(24):
            line = stream.fp.readline().decode()
            if line.startswith("data: "):
                value = json.loads(line[6:])
                if value["mmr"]["leaf_count"] == 3:
                    updated = value
                    break
        self.assertIsNotNone(updated, "No real-time public event received")
        self.assertNotIn("SSE live observation", json.dumps(updated))
        self.assertEqual(updated["mmr"]["root"],
                         self.request("GET", "/api/public")[1]["mmr"]["root"])
        connection.close()

    def test_tamper_private_note_fails_validation(self):
        root = self.request("GET", "/api/public")[1]["mmr"]["root"]
        self.assertEqual(self.request("POST", "/api/review",
                                      {"decision": "ALLOW", "expected_root": root, "note": "DEMO: original"},
                                      self.headers())[0], 201)
        p = self.state.notes_path
        p.write_text(p.read_text().replace("DEMO: original", "DEMO: tampered"))
        with self.assertRaises(RuntimeError):
            self.state.private()
        self.assertTrue(custody.verify(self.state.path / "custody")["PASS"])
        # The FCO commitment does not cryptographically protect plaintext unless
        # the private sidecar is compared with its committed hash.

    def test_cannot_overwrite_predecessor_run(self):
        with self.assertRaises(FileExistsError):
            judge.JudgeState(self.state.path, capability="test")

if __name__ == "__main__":
    unittest.main()
