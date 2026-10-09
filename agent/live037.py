#!/usr/bin/env python3
"""Live 037: run every sponsor step now, on camera, into a new custody MMR.

Order: monitor public site -> Semgrep before/after + behavior matrix (local) ->
Akash GPU deploy/bid/lease/inference on the Semgrep finding -> close -> closed-state
readback -> ClickHouse Cloud ingest of this run's own steps, replay, query, exact
readback. Each step is appended to evidence/successor_037 as it happens.

While it runs, http://127.0.0.1:8837 shows each checkpoint with its wall-clock
time and recomputes the running MMR root in the browser from the ledger.

Default: no new spend. Akash makes a live READ-ONLY status query of the earlier
successor_024 deployment (dseq 1791574273055). With --akash-deploy, one paid GPU
run instead (operator-authorized), bid cap 10000 uact/block, closed in a finally
block, then closed-state readback. Credentials from env only; never recorded.
Usage: freeze | run [--akash-deploy] | verify
"""
import functools, http.server, importlib.util, json, os, sys, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agent"))


def load(name):
    s = importlib.util.spec_from_file_location(name, ROOT / f"agent/{name}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


G = load("akash_gpu024")          # Console API client, SDL, model (frozen in successor_024)
H = load("ch016")                 # ClickHouse client, row projection (frozen in successor_016)
A = G.A                           # custody runner (agent011)
import safe_eval016 as S

BASE = Path(os.environ.get("LIVE037_BASE", ROOT / "evidence/successor_037b"))  # 037b: agent011.py fixed after PR review; 037 kept (genesis only)
A.KIT = [k for k in A.KIT if not k.startswith("public/")] + [
    "agent/live037.py", "agent/live037.html", "agent/akash_gpu024.py", "agent/ch016.py",
    "agent/safe_eval016.py", "docs/ADDENDUM_037.md"]
A.BASE = BASE
TABLE = "antigense_live_037"
PORT = 8837
STATUS = {"run": None, "phase": "starting", "steps": [], "ledger": []}


class LiveRun(A.Run):
    """Run that also publishes each committed step to the local live page."""

    def step(self, name, state, details, checks, body=None):
        r = super().step(name, state, details, checks, body)
        led = [json.loads(l) for l in (BASE / "ledger.jsonl").read_text().splitlines() if l]
        STATUS["ledger"] = [{k: x[k] for k in ("event_index", "event_hash", "fco_id")} for x in led]
        STATUS["steps"].append({"seq": self.seq, "name": name, "state": state, "ts": time.strftime("%H:%M:%S"),
                                "mmr_root": r["mmr_root"], "leaves": len(led),
                                "summary": {k: details.get(k) for k in SHOW.get(name, ()) if k in details}})
        return r


SHOW = {"live_monitor": ("status", "elapsed_ms"), "live_semgrep_before": ("findings_count",),
        "live_semgrep_after": ("findings_count",), "akash_create": ("status", "dseq"), "akash_bids": ("bid_count", "chosen_gpu"), "akash_prior_deployment_status": ("status", "state", "lease_states"),
        "akash_lease": ("status",), "akash_inference": ("status", "model", "ms", "schema_valid"),
        "akash_close": ("status", "success"), "akash_closed_readback": ("state", "lease_states"),
        "clickhouse_ingest": ("rows_sent", "ms"), "clickhouse_replay": ("rows_sent", "ms"),
        "clickhouse_query": ("rows", "ms"), "clickhouse_readback": ("readback_rows", "hashes_equal")}


def serve():
    page = (ROOT / "agent/live037.html").read_bytes()

    class Hd(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a): pass

        def do_GET(self):
            body, ctype = (json.dumps(STATUS).encode(), "application/json") if self.path.startswith("/status") else (page, "text/html")
            self.send_response(200); self.send_header("Content-Type", ctype); self.send_header("Cache-Control", "no-store")
            self.end_headers(); self.wfile.write(body)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Hd)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def semgrep_steps(R):
    out = {}
    for name, fx in (("live_semgrep_before", "before"), ("live_semgrep_after", "after")):
        s = A.semgrep(ROOT / f"fixtures/{fx}.py"); raw = s.pop("raw", b"")
        s["findings_count"] = len(s.get("findings", []))
        R.step(name, s["state"], s, {"scanner_executed": s["state"] == "OBSERVED", "no_scanner_errors": s.get("errors") == 0,
               "finding_present": s["findings_count"] > 0}, raw)
        out[fx] = s
    m = {fx: S.regress(ROOT / f"fixtures/{fx}.py") for fx in ("before", "after")}
    R.step("live_behavior_matrix", "OBSERVED", m, {"before_fails_open": m["before"]["unhealthy_unauth"] is True,
           "after_denies_unauthorized": not m["after"]["unhealthy_unauth"] and not m["after"]["healthy_unauth"],
           "after_keeps_authorized": m["after"]["healthy_auth"] is True})
    return out


def akash_steps(R, key, finding):
    http, J, API = G.http, G.J, G.API
    dseq = None
    try:
        st, raw, m = http("POST", API + "/v1/deployments", key, {"data": {"sdl": G.SDL, "runtimeLimitHours": 1}})
        d = J(raw).get("data", {}); dseq = d.get("dseq"); tx = d.get("signTx") or {}
        R.step("akash_create", "OBSERVED" if dseq else "FAILED", {"status": st, **m, "dseq": dseq, "tx_code": tx.get("code"),
               "tx_hash": tx.get("transactionHash"), "sdl_sha256": A.sha(G.SDL.encode())}, {"created": bool(dseq), "tx_code_zero": tx.get("code") == 0})
        if not dseq: return
        bids, t0 = [], time.monotonic()
        while time.monotonic() - t0 < 360 and not bids:
            time.sleep(8); st, raw, m = http("GET", API + "/v1/bids?dseq=" + dseq, key); bids = J(raw).get("data") or []
        if bids:
            time.sleep(12); st, raw, m = http("GET", API + "/v1/bids?dseq=" + dseq, key); bids = J(raw).get("data") or bids
        best = min(bids, key=lambda b: float(b["bid"]["price"]["amount"]))["bid"] if bids else None
        gpu = None
        if best:
            for ro in best.get("resources_offer", []):
                gpu = json.dumps(((ro.get("resources") or {}).get("gpu") or {}).get("attributes"), sort_keys=True)[:120]
        R.step("akash_bids", "OBSERVED" if bids else "FAILED", {"bid_count": len(bids), "waited_s": round(time.monotonic() - t0),
               "chosen_provider": best and best["id"]["provider"], "chosen_price_uact": best and best["price"]["amount"], "chosen_gpu": gpu},
               {"bids_received": bool(bids), "price_under_cap": bool(best) and float(best["price"]["amount"]) <= G.MAX_UACT})
        if not best: return
        i = best["id"]
        st, raw, m = http("POST", API + "/v1/leases", key, {"leases": [{"dseq": dseq, "gseq": i["gseq"], "oseq": i["oseq"], "provider": i["provider"]}]}, timeout=120)
        R.step("akash_lease", "OBSERVED" if st == 200 else "FAILED", {"status": st, **m, "provider": i["provider"]}, {"lease_created": st == 200})
        if st != 200: return
        uri, t0 = None, time.monotonic()
        while time.monotonic() - t0 < 480 and not uri:
            st, raw, m = http("GET", API + "/v1/deployments/" + dseq, key)
            for l in J(raw).get("data", {}).get("leases", []):
                u = (((l.get("status") or {}).get("services") or {}).get("llm") or {}).get("uris")
                if u: uri = u[0]
            if not uri: time.sleep(10)
        base = "http://" + (uri or "").split("://")[-1].rstrip("/"); ready, t0, ver = False, time.monotonic(), None
        while uri and time.monotonic() - t0 < 480:
            st, raw, m = http("GET", base + "/api/version", timeout=15)
            if st == 200: ready, ver = True, J(raw).get("version"); break
            time.sleep(10)
        R.step("akash_service_ready", "OBSERVED" if ready else "FAILED", {"uri_host_sha256": A.sha((uri or "").encode()), "ollama_version": ver},
               {"uri_assigned": bool(uri), "service_ready": ready})
        if not ready: return
        st, raw, m = http("POST", base + "/api/pull", body={"model": G.MODEL, "stream": False}, timeout=900)
        R.step("akash_model_pull", "OBSERVED" if st == 200 else "FAILED", {"status": st, **m, "model": G.MODEL}, {"pulled": st == 200})
        if st != 200: return
        prompt = ("Semgrep finding just produced by this run:\n" + json.dumps(finding, sort_keys=True) + "\nRule:\n" +
                  (ROOT / "rules/fallback.yaml").read_text() + "\nCode:\n" + (ROOT / "fixtures/before.py").read_text() +
                  "\nReturn JSON only with string keys summary, root_cause, fix, risk.")
        req = {"model": G.MODEL, "prompt": prompt, "stream": False, "format": "json", "options": {"temperature": 0, "seed": 7}}
        st, raw, m = http("POST", base + "/api/generate", body=req, timeout=300); g = J(raw); txt = g.get("response", "")
        valid, why = A.validate_advice(txt) if st == 200 else (False, "no response")
        R.step("akash_inference", "OBSERVED" if st == 200 and txt else "FAILED", {"status": st, **m, "model": g.get("model"),
               "request_sha256": A.sha(json.dumps(req, sort_keys=True).encode()), "response_sha256": A.sha(raw), "schema_valid": valid,
               "eval_count": g.get("eval_count"), "advice_excerpt": txt[:600], "finding_sha256": A.sha(json.dumps(finding, sort_keys=True).encode())},
               {"actual_akash_gpu_inference": st == 200 and bool(txt), "advice_schema_valid": valid, "advice_applied": False,
                "input_is_this_runs_finding": True, "attestation_verified": False}, raw if st == 200 else None)
        st, raw, m = http("GET", base + "/api/ps", timeout=15); ps = J(raw).get("models", [])
        R.step("akash_vram_reported", "OBSERVED" if st == 200 else "FAILED", {"models": [{"name": x.get("name"), "size_vram": x.get("size_vram")} for x in ps]},
               {"vram_reported_nonzero": any((x.get("size_vram") or 0) > 0 for x in ps), "gpu_attested": False})
    finally:
        if dseq:
            st, raw, m = http("DELETE", API + "/v1/deployments/" + dseq, key, timeout=120)
            ok = st == 200 and (J(raw).get("data") or {}).get("success") is True
            R.step("akash_close", "OBSERVED" if ok else "FAILED", {"status": st, **m, "dseq": dseq, "success": (J(raw).get("data") or {}).get("success")}, {"closed": ok})
            state, leases = None, []
            for _ in range(12):
                time.sleep(10); st, raw, m = http("GET", API + "/v1/deployments/" + dseq, key); d = J(raw).get("data", {})
                state = (d.get("deployment") or {}).get("state"); leases = [l.get("state") for l in d.get("leases", [])]
                if state == "closed": break
            R.step("akash_closed_readback", "OBSERVED" if state == "closed" else "FAILED", {"state": state, "lease_states": leases, "dseq": dseq},
                   {"deployment_state_closed": state == "closed", "no_active_lease": "active" not in leases})


def clickhouse_steps(R):
    H.load_env(); db = H.CH()
    if not db.ready():
        R.step("clickhouse_ingest", "NOT_TESTED", {"reason": "ClickHouse credentials not in env"}, {"credentials_present": False}); return
    H.SRC = BASE; rows = H.normed(H.canonical_rows())
    ddl = H.DDL.replace(H.TABLE, TABLE); db.q(ddl)
    def ingest(name):
        data = "\n".join(json.dumps(r, sort_keys=True) for r in rows).encode()
        raw, m = db.q(f"INSERT INTO {TABLE} FORMAT JSONEachRow", data)
        R.step(name, "OBSERVED", {"rows_sent": len(rows), "ms": m["ms"], "query_id": m["query_id"], "table": TABLE}, {"insert_ok": True})
    ingest("clickhouse_ingest"); ingest("clickhouse_replay")
    sql = f"SELECT seq,name,state,ts FROM {TABLE} FINAL WHERE run_id='{rows[0]['run_id']}' ORDER BY seq"
    raw, m = db.q(sql); res = H.jl(raw)
    R.step("clickhouse_query", "OBSERVED", {"sql": sql, "rows": len(res), "ms": m["ms"], "result_sha256": A.sha(json.dumps(res, sort_keys=True).encode())}, {"rows_returned": len(res) > 0})
    cols = ",".join(c for c, _ in H.COLS); raw, m = db.q(f"SELECT {cols} FROM {TABLE} FINAL WHERE run_id='{rows[0]['run_id']}' ORDER BY occurrence_id")
    back = H.normed(H.jl(raw)); key = lambda r: r["occurrence_id"]
    hb = A.sha(json.dumps(sorted(back, key=key), sort_keys=True).encode()); hc = A.sha(json.dumps(sorted(rows, key=key), sort_keys=True).encode())
    R.step("clickhouse_readback", "OBSERVED" if hb == hc else "FAILED", {"readback_rows": len(back), "canonical_rows": len(rows), "ms": m["ms"],
           "readback_sha256": hb, "canonical_sha256": hc, "hashes_equal": hb == hc}, {"exact_readback": hb == hc, "count_matches": len(back) == len(rows)})


PRIOR_DSEQ = "1791574273055"  # successor_024


def akash_readonly(R, key):
    st, raw, m = G.http("GET", G.API + "/v1/deployments/" + PRIOR_DSEQ, key)
    d = G.J(raw).get("data", {}); state = (d.get("deployment") or {}).get("state")
    leases = [l.get("state") for l in d.get("leases", [])]
    R.step("akash_prior_deployment_status", "OBSERVED" if st == 200 else "FAILED",
           {"status": st, **m, "dseq": PRIOR_DSEQ, "state": state, "lease_states": leases, "record": "evidence/successor_024",
            "scope": "live read-only status of the earlier GPU deployment; no new deployment or spend"},
           {"http_200": st == 200, "deployment_state_closed": state == "closed", "no_active_lease": "active" not in leases, "new_spend": False})


def run():
    if not (BASE / "genesis.json").exists(): raise SystemExit("freeze first")
    if not A.artifacts_ok(BASE): raise SystemExit("governed bytes changed since freeze; make a successor")
    srv = serve(); R = LiveRun(BASE); STATUS["run"] = R.id
    print(f"LIVE page: http://127.0.0.1:{PORT}  run {R.id}", flush=True)
    time.sleep(3)
    if os.environ.get("LIVE037_DRYRUN"): os.environ.pop("AKASH_API_KEY", None); os.environ.pop("AKASHML_API_KEY", None); H.load_env = lambda: None
    key = os.environ.get("AKASH_API_KEY") or (os.environ.get("AKASHML_API_KEY", "") if os.environ.get("AKASHML_API_KEY", "").startswith("ac.sk.") else "")
    H.load_env()
    R.step("live_preflight", "OBSERVED", {"akash_key_present": bool(key), "clickhouse_credentials_present": H.CH().ready(),
           "akash_budget": f"one deployment, bid cap {G.MAX_UACT} uact/block, closed in finally", "credential_values_recorded": False},
           {"akash_key_present": bool(key), "clickhouse_ready": H.CH().ready()})
    STATUS["phase"] = "monitor"
    f = A.fetch("https://" + A.SITE + "/", A.Budget(2))
    R.step("live_monitor", "OBSERVED" if f["status"] == 200 else "FAILED", A.pub(f), {"http_200": f["status"] == 200}, f["_body"] or None)
    STATUS["phase"] = "semgrep"; sg = semgrep_steps(R)
    STATUS["phase"] = "akash"
    if not key: R.step("akash_prior_deployment_status", "NOT_TESTED", {"reason": "no Console key in env"}, {"http_200": False})
    elif "--akash-deploy" in sys.argv: akash_steps(R, key, sg["before"].get("findings"))
    else: akash_readonly(R, key)
    STATUS["phase"] = "clickhouse"; clickhouse_steps(R)
    v = A.verify(BASE); STATUS["phase"] = "done"; STATUS["final"] = {"PASS": v["PASS"], "mmr_root": v["mmr_root"], "leaves": v["leaf_count"]}
    print(f"DONE verify PASS={v['PASS']} leaves={v['leaf_count']} mmr={v['mmr_root']}", flush=True)
    print("page stays up 60 s for the recording; Ctrl-C to stop", flush=True)
    time.sleep(60); srv.shutdown()


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "freeze": print("project_root", A.freeze(BASE)["project_root"])
    elif c == "run": run()
    elif c == "verify": r = A.verify(BASE); print(json.dumps(r, indent=2, sort_keys=True)); sys.exit(0 if r["PASS"] else 1)
    else: sys.exit("usage: freeze|run|verify")
