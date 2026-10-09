#!/usr/bin/env python3
"""Local-only Antigense judge interface: SSE public projection + private review.

Security boundary: loopback, per-process high-entropy capability, Origin/Host
checks, explicit action, stale-MMR rejection, append-only source receipts.
No public deployment, Akash spend, wallet, remote sponsor calls or PHI.
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
import secrets
import sys
import tempfile
import threading
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import custody
import cascade

HOST = "127.0.0.1"
DEFAULT_PORT = 8850
CLIENT = ROOT / "public/judge-live-050.html"
SCRIPT = ROOT / "public/judge-live-050.js"
PARENT_COMMIT = "265699cde9812977108455707e1ddfeb15093112"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def oracle_pass() -> bool:
    return all(cascade.auth("after", a, h) == (a and h)
               for a in (False, True) for h in (False, True))


class JudgeState:
    def __init__(self, location: Path, *, capability: str | None = None):
        self.lock = threading.RLock()
        self.path = Path(location)
        if self.path.exists():
            raise FileExistsError("New judge run requires an unused directory; no predecessor overwrite")
        self.path.mkdir(parents=True, mode=0o700)
        self.capability = capability or secrets.token_urlsafe(36)
        self.notes_path = self.path / "private_notes.jsonl"
        self.notes_path.touch(mode=0o600)
        os.chmod(self.notes_path, 0o600)
        self.project = custody.freeze(self.path / "custody", ROOT)
        self.events = []
        self._append("judge_session_open", "NONE", "", actor="LOCAL_SYSTEM", authorized=True)

    def _append(self, event: str, decision: str, note: str, *,
                actor: str = "UNVERIFIED_LOCAL_CAPABILITY", authorized: bool = False) -> dict:
        assert event in ("judge_session_open", "judge_review_recorded")
        assert decision in ("NONE", "ALLOW", "DENY")
        note_bytes = note.encode("utf-8")
        checks = {
            "security_policy_pass": oracle_pass(),
            "authorized_session": authorized,
            "valid_review_decision": decision in ("ALLOW", "DENY") if event == "judge_review_recorded" else True,
        }
        observation = {
            "schema": "antigense.judge050.review_occurrence.v1",
            "name": event, "state": "OBSERVED",
            "admission_policy": "STRICT_V2",
            "required_checks": list(checks),
            "checks": checks,
            "details": {
                "decision": decision,
                "actor": actor,
                "note_sha256": sha(note_bytes),
                "note_length_utf8": len(note_bytes),
                "note_visibility": "PRIVATE_LOCAL_ONLY",
                "upstream_commit": PARENT_COMMIT,
                "source_digest": sha(Path(__file__).read_bytes()),
                "review_is_cryptographically_signed": False,
                "applies_patch": False,
                "origin": "LOCAL_HTTP_ACTION" if event == "judge_review_recorded" else "LOCAL_PROCESS",
            },
        }
        result = custody.append_step(self.path / "custody", observation)
        state = custody.verify(self.path / "custody")
        if not state["PASS"]:
            raise RuntimeError("Custody failed readback after append")
        row = custody.rows(self.path / "custody")[-1]
        receipt = {
            "index": row["event_index"], "kind": event, "decision": decision,
            "occurrence_fco_id": row["fco_id"], "mmr_root": result["mmr_root"],
            "predecessor": custody.rows(self.path / "custody")[-2]["fco_id"] if len(custody.rows(self.path / "custody")) > 1 else None,
            "signed": False,
        }
        self.events.append(receipt)
        if event == "judge_review_recorded":
            private = {"index": receipt["index"], "fco_id": receipt["occurrence_fco_id"],
                       "note": note, "note_sha256": sha(note_bytes)}
            with self.notes_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(private, sort_keys=True) + "\n")
                f.flush()
                os.fsync(f.fileno())
        return receipt

    def public(self) -> dict:
        with self.lock:
            state = custody.verify(self.path / "custody")
            source_bound = all(
                custody.read(self.path / "custody" / f"step-{row['event_index']:06d}.json")[
                    "observation"]["details"]["source_digest"] == sha(Path(__file__).read_bytes())
                for row in custody.rows(self.path / "custody")[1:]
            )
            artifacts_bound = custody.verify_artifacts(self.path / "custody", ROOT)
            return {
                "schema": "antigense.judge050.public.v1",
                "scope": "LOOPBACK_SIMULATED_JUDGE; NOT_SIGNED; NOT_PUBLISHED",
                "parent_commit": PARENT_COMMIT,
                "submission": "https://tokensand.com/p/antigense-daisy",
                "chain_pass": state["PASS"] and source_bound and artifacts_bound,
                "runtime_code_bound": source_bound,
                "frozen_artifacts_bound": artifacts_bound, "mmr": {
                    "algorithm": "HYDRALAMP_MMR_V1",
                    "leaf_count": state["leaf_count"], "root": state["mmr_root"]},
                "events": list(self.events),
                "private_note_content": "REDACTED",
            }

    def private(self) -> dict:
        with self.lock:
            s = self.public()
            notes = [json.loads(x) for x in self.notes_path.read_text().splitlines() if x]
            events_by_index = {x["index"]: x for x in self.events if x["kind"] == "judge_review_recorded"}
            if len(notes) != len(events_by_index):
                raise RuntimeError("Private journal / FCO review count mismatch")
            for note in notes:
                idx = note["index"]
                step = custody.read(self.path / "custody" / f"step-{idx:06d}.json")
                evidence = step["observation"]["details"]
                if (idx not in events_by_index or
                    note["fco_id"] != events_by_index[idx]["occurrence_fco_id"] or
                    evidence["note_sha256"] != sha(note["note"].encode("utf-8")) or
                    note["note_sha256"] != evidence["note_sha256"] or
                    evidence["note_length_utf8"] != len(note["note"].encode("utf-8"))):
                    raise RuntimeError("Private journal content not consistent with source FCO")
            return {**s, "private_notes": notes, "private_role": "LOCAL_CAPABILITY_ONLY",
                    "credential_identity": "NOT_VERIFIED", "private_note_content": "AUTHORIZED_READBACK"}

    def review(self, action: str, expected_root: str, note: str) -> dict:
        if action not in ("ALLOW", "DENY"):
            raise ValueError("Invalid review decision")
        if not isinstance(note, str) or not note.startswith("DEMO:") or len(note.encode()) > 240:
            raise ValueError("Only short DEMO: synthetic notes are permitted")
        with self.lock:
            state = custody.verify(self.path / "custody")
            if not state["PASS"]:
                raise RuntimeError("Prior custody check failed")
            if expected_root != state["mmr_root"]:
                raise LookupError("Stale expected MMR root")
            return self._append("judge_review_recorded", action, note, authorized=True)


class JudgeHandler(http.server.BaseHTTPRequestHandler):
    server_version = "AntigenseJudge050"
    def log_message(self, *args):  # no credentials/notes or request bodies in log
        pass

    @property
    def state(self) -> JudgeState:
        return self.server.judge_state

    def valid_host(self) -> bool:
        return self.headers.get("Host") == f"{HOST}:{self.server.server_port}"

    def valid_capability(self) -> bool:
        value = self.headers.get("Authorization", "")
        return (value.startswith("Bearer ") and
                secrets.compare_digest(value[7:], self.state.capability))

    def send(self, payload, status=200, content_type="application/json"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload, sort_keys=True).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.valid_host():
            return self.send({"error": "invalid_host"}, 403)
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/judge-live-050.html"):
            return self.send(CLIENT.read_bytes(), content_type="text/html; charset=utf-8")
        if path == "/judge-live-050.js":
            return self.send(SCRIPT.read_bytes(), content_type="application/javascript")
        if path == "/api/public":
            return self.send(self.state.public())
        if path == "/api/private":
            if not self.valid_capability():
                return self.send({"error": "unauthorized"}, 403)
            try:
                return self.send(self.state.private())
            except (RuntimeError, ValueError, KeyError, OSError):
                return self.send({"error": "private_integrity_failure"}, 409)
        if path == "/api/stream":
            # SSE is public-only and never serializes the reviewer note or token.
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            deadline = time.monotonic() + 12
            last = None
            try:
                while time.monotonic() < deadline and not self.server.stopping.is_set():
                    view = self.state.public()
                    root = view["mmr"]["root"]
                    if root != last:
                        self.wfile.write(b"event: checkpoint\n")
                        self.wfile.write(b"data: " + json.dumps(view, sort_keys=True).encode() + b"\n\n")
                        self.wfile.flush()
                        last = root
                    else:
                        self.wfile.write(b": heartbeat\n\n")
                        self.wfile.flush()
                    time.sleep(0.25)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError, KeyError):
                pass
            return
        return self.send({"error": "not_found"}, 404)

    def do_POST(self):
        if not self.valid_host():
            return self.send({"error": "invalid_host"}, 403)
        if self.headers.get("Origin") != f"http://{HOST}:{self.server.server_port}":
            return self.send({"error": "bad_origin"}, 403)
        if not self.valid_capability():
            return self.send({"error": "unauthorized"}, 403)
        if urllib.parse.urlparse(self.path).path != "/api/review":
            return self.send({"error": "not_found"}, 404)
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n < 2 or n > 1024:
                return self.send({"error": "bad_size"}, 400)
            body = json.loads(self.rfile.read(n))
            if not isinstance(body, dict) or set(body) != {"decision", "expected_root", "note"}:
                return self.send({"error": "bad_fields"}, 400)
            if not isinstance(body["expected_root"], str):
                return self.send({"error": "bad_root"}, 400)
            result = self.state.review(body["decision"], body["expected_root"], body["note"])
            return self.send({"accepted": True, "receipt": result}, 201)
        except LookupError:
            return self.send({"error": "stale_mmr_root"}, 409)
        except (ValueError, TypeError, UnicodeError, json.JSONDecodeError):
            return self.send({"error": "invalid_review"}, 400)
        except Exception:
            return self.send({"error": "custody_failure"}, 500)


def create_server(state: JudgeState, port: int = DEFAULT_PORT):
    server = http.server.ThreadingHTTPServer((HOST, port), JudgeHandler)
    server.judge_state = state
    server.daemon_threads = True
    server.stopping = threading.Event()
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(tempfile.mkdtemp(prefix="antigense-judge050-")) / "run"
    state = JudgeState(output)
    server = create_server(state, args.port)
    key_path = state.path / ".local_capability"
    fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as writer:
        writer.write(state.capability + "\n")
    print(f"LOCAL_JUDGE_URL=http://{HOST}:{server.server_port}", flush=True)
    print(f"PRIVATE_CAPABILITY_FILE={key_path}", flush=True)
    print(f"PRIVATE_OUTPUT={state.path}", flush=True)
    print("Do not publish the capability or private output. Ctrl-C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stopping.set()
        server.server_close()


if __name__ == "__main__":
    main()
