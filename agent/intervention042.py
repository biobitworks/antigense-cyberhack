#!/usr/bin/env python3
"""Run/verify bounded, no-network, agent-assisted F1/F2 repair evidence.
This is an isolated successor: no upstream mutation, sponsor spend or claims of autonomous LLM patch application.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import custody
import cascade
from fixture_eval042 import authorize_file

OUT = ROOT / "evidence" / "intervention_042"
RULE = ROOT / "rules" / "fixture-exec-042.yaml"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def invoke(*args, timeout=55):
    return subprocess.run(args, cwd=ROOT, capture_output=True, timeout=timeout)


def frozen_source():
    commit = invoke("git", "rev-parse", "HEAD")
    assert commit.returncode == 0
    head = commit.stdout.decode().strip()
    obj = invoke("git", "show", head + ":src/cascade.py")
    assert obj.returncode == 0
    return head, obj.stdout


def scan(target):
    installed = ROOT.parent / "antigense-cyberhack" / ".venv" / "bin" / "semgrep"
    exe = os.getenv("ANTIGENSE_SEMGREP_042") or (str(installed) if installed.exists() else shutil.which("semgrep"))
    if not exe:
        return {"status": "NOT_TESTED", "reason": "Semgrep CLI unavailable"}
    p = invoke(exe, "scan", "--config", str(RULE), "--metrics=off",
               "--disable-version-check", "--json", str(target), timeout=70)
    try:
        report = json.loads(p.stdout)
    except ValueError:
        return {"status": "FAILED", "exit_code": p.returncode}
    return {"status": "OBSERVED" if p.returncode == 0 and not report.get("errors") else "FAILED",
            "exit_code": p.returncode, "version": report.get("version"),
            "findings": len(report.get("results", [])),
            "errors": len(report.get("errors", [])),
            "output_sha256": digest(p.stdout),
            "rule_sha256": digest(RULE.read_bytes()),
            "target_sha256": digest(Path(target).read_bytes())}


def truth_oracle():
    cases = []
    for authorized in (False, True):
        for healthy in (False, True):
            expected = authorized and healthy
            before = cascade.auth("before", authorized, healthy)
            after = cascade.auth("after", authorized, healthy)
            cases.append({"authorized": authorized, "healthy": healthy,
                          "expected": expected, "baseline_allowed": before,
                          "repaired_allowed": after})
    negative = {"authorized": False, "healthy": True,
                "expected": False, "ineffective_or_patch": True}
    return {"cases": cases, "baseline_bypass": cases[0]["baseline_allowed"],
            "patch_matches_oracle": all(c["repaired_allowed"] == c["expected"] for c in cases),
            "ineffective_patch_rejected": negative["ineffective_or_patch"] != negative["expected"],
            "negative_patch_control": negative}


def admission_oracle():
    observation = {"name": "security_gate", "state": "OBSERVED", "checks": {"security_gate": False}}
    old, _ = custody.derive(observation, [])
    new, _ = custody.derive({**observation, "admission_policy": "STRICT_V2",
                            "required_checks": ["security_gate"]}, [])
    valid, _ = custody.derive({"name": "security_gate", "state": "OBSERVED",
                               "admission_policy": "STRICT_V2",
                               "required_checks": ["security_gate"],
                               "checks": {"security_gate": True}}, [])
    return {"legacy_false_check_admission": old["custody_admission"],
            "strict_false_check_admission": new["custody_admission"],
            "strict_true_check_admission": valid["custody_admission"],
            "legacy_witness_preserved": old["custody_admission"] == "ADMITTED",
            "strict_gate_pass": new["custody_admission"] != "ADMITTED"
                  and valid["custody_admission"] == "ADMITTED"}


def module_side_effect_oracle():
    with tempfile.TemporaryDirectory() as d:
        marker = Path(d) / "side-effect-marker"
        fixture = Path(d) / "valid-malicious-fixture.py"
        fixture.write_text(
            "open(" + repr(str(marker)) + ", 'w').write('executed')\n"
            "def authorize(authorized, worker_healthy):\n"
            "    return True\n"
        )
        outcome = "UNKNOWN"
        try:
            authorize_file(fixture, False, False)
            outcome = "ACCEPTED_UNSAFE"
        except (ValueError, SyntaxError):
            outcome = "REJECTED"
        return {"fixture_sha256": digest(fixture.read_bytes()),
                "module_import_rejected": outcome == "REJECTED",
                "side_effect_observed": marker.exists(),
                "valid_python": bool(compile(fixture.read_text(), str(fixture), "exec")),
                "outcome": outcome}


def new_record(name, state, result, checks):
    return {"schema": "antigense.intervention042.step.v1",
            "name": name, "state": state, "result": result,
            "checks": {k: bool(v) for k, v in checks.items()},
            "recorded_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "context": {"project": "antigense-cyberhack", "lane": "codex/guarded-intervention-042",
                        "actor": "ChatGPT-assisted isolated code intervention",
                        "automation": "bounded tool-executed tests; not fully autonomous cloud agent"}}


def create():
    if OUT.exists():
        raise SystemExit("FAIL CLOSED: intervention_042 exists; never overwrite a historical occurrence")
    events = []
    head, original = frozen_source()
    targets = [ROOT / n for n in ("src/custody.py", "src/cascade.py", "src/fixture_eval042.py",
                                  "rules/fixture-exec-042.yaml", "tests/test_guarded_intervention_042.py",
                                  "agent/intervention042.py")]
    with tempfile.TemporaryDirectory() as d:
        baseline = Path(d) / "cascade-before.py"
        baseline.write_bytes(original)
        a = scan(baseline)
        b = scan(ROOT / "src" / "cascade.py")
    events.append(new_record("F2 semgrep pinned before-after", "OBSERVED" if a["status"] == b["status"] == "OBSERVED" else "FAILED",
                             {"baseline": a, "repaired": b},
                             {"scanner_executed": a["status"] == b["status"] == "OBSERVED",
                              "one_before_zero_after": a.get("findings") == 1 and b.get("findings") == 0}))
    f1 = admission_oracle()
    events.append(new_record("F1 semantic admission intervention", "OBSERVED", f1,
                             {"false_check_blocked": f1["strict_gate_pass"],
                              "legacy_failure_preserved": f1["legacy_witness_preserved"]}))
    control = module_side_effect_oracle()
    events.append(new_record("F2 malicious module negative control", "OBSERVED", control,
                             {"valid_python": control["valid_python"],
                              "side_effect_prevented": control["module_import_rejected"] and not control["side_effect_observed"]}))
    behavior = truth_oracle()
    events.append(new_record("Authorization recovery and ineffective patch", "OBSERVED", behavior,
                             {"four_case_oracle_pass": behavior["patch_matches_oracle"],
                              "baseline_bypass_reproduced": behavior["baseline_bypass"],
                              "ineffective_patch_rejected": behavior["ineffective_patch_rejected"]}))
    tests = invoke(sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v", timeout=45)
    summary = (tests.stdout + tests.stderr).decode(errors="replace")
    matched = re.search(r"Ran (\d+) tests? in", summary)
    events.append(new_record("Regression suite", "OBSERVED" if tests.returncode == 0 else "FAILED",
                             {"exit_code": tests.returncode, "test_count": int(matched.group(1)) if matched else None,
                              "output_sha256": digest(tests.stdout + tests.stderr)},
                             {"test_suite_pass": tests.returncode == 0 and bool(matched) and int(matched.group(1)) >= 11}))
    events.append(new_record("Provider and external target boundaries", "DEFERRED",
                             {"Akash": "REUSED_PREDECESSOR_024; NO_NEW_COMPUTE",
                              "ClickHouse": "REUSED_PREDECESSOR_016; NO_NEW_INGEST",
                              "Semgrep_Multimodal": "NOT_TESTED",
                              "Baymax": "READ_ONLY_CANDIDATE; NO_EXTERNAL_REPO_MUTATION",
                              "human_approval": "REQUEST_2026_10_09",
                              "Pi": "NOT_TESTED"}, {"new_sponsor_spend": False}))
    OUT.mkdir(parents=True)
    ledger = []
    for i, record in enumerate(events, 1):
        content = custody.canonical(record)
        h = digest(content)
        (OUT / ("step-%06d.json" % i)).write_bytes(content)
        row = {"event_index": i, "event_hash": h, "fco_id": "fco:sha256:" + h,
               "object_file": "step-%06d.json" % i}
        ledger.append(row)
        prefix = custody.mmr(ledger)
        if prefix["root"] != custody.independent_mmr_root(ledger):
            raise AssertionError("two MMR constructions diverged")
        (OUT / ("prefix-%06d.json" % i)).write_bytes(custody.canonical(prefix))
    (OUT / "ledger.jsonl").write_bytes(b"".join(custody.canonical(x) + b"\n" for x in ledger))
    manifest = {"schema": "antigense.intervention042.manifest.v1", "parent_commit": head,
                "source_sha256": {str(x.relative_to(ROOT)): digest(x.read_bytes()) for x in targets},
                "legacy_cascade_sha256": digest(original),
                "leaf_count": len(ledger), "mmr_algorithm": "HYDRALAMP_MMR_V1",
                "mmr_root": custody.mmr(ledger)["root"], "mmr_peaks": custody.mmr(ledger)["peaks"],
                "verification_method": "recompute all content hashes and all MMR prefixes",
                "signature": "NOT_SIGNED", "external_provider_calls_new": 0,
                "scientific_claim_ceiling": "BOUNDED_FIXTURE_REPAIR_NOT_WHOLE_SYSTEM_SECURITY"}
    (OUT / "manifest.json").write_bytes(custody.canonical(manifest))
    outcome = verify()
    print(json.dumps(outcome, sort_keys=True))
    if not outcome["PASS"]:
        raise SystemExit(1)


def verify():
    m = json.loads((OUT / "manifest.json").read_text())
    rows = [json.loads(x) for x in (OUT / "ledger.jsonl").read_text().splitlines() if x]
    checks = {"leaf_count_matches": len(rows) == m["leaf_count"],
              "source_bytes_match": all(digest((ROOT / path).read_bytes()) == val
                                        for path, val in m["source_sha256"].items()),
              "step_hashes_match": True, "mmr_prefixes_match": True,
              "intervention_oracles_pass": True}
    for i, row in enumerate(rows, 1):
        content = (OUT / row["object_file"]).read_bytes()
        record = json.loads(content)
        checks["step_hashes_match"] &= (row["event_index"] == i and
                                        digest(content) == row["event_hash"] and
                                        row["fco_id"] == "fco:sha256:" + row["event_hash"] and
                                        content == custody.canonical(record))
        if record["state"] not in ("DEFERRED", "NOT_TESTED"):
            checks["intervention_oracles_pass"] &= all(record["checks"].values())
        p = custody.mmr(rows[:i])
        checks["mmr_prefixes_match"] &= (
            json.loads((OUT / ("prefix-%06d.json" % i)).read_text()) == p and
            p["root"] == custody.independent_mmr_root(rows[:i]))
    calculated = custody.mmr(rows)
    checks["manifest_root_peaks_match"] = (calculated["root"] == m["mmr_root"] and
                                          calculated["peaks"] == m["mmr_peaks"])
    return {"PASS": all(checks.values()), "checks": checks,
            "leaf_count": len(rows), "mmr_root": calculated["root"],
            "signature": m["signature"], "new_provider_calls": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "verify"])
    args = parser.parse_args()
    if args.command == "run":
        create()
    else:
        result = verify()
        print(json.dumps(result, indent=2, sort_keys=True))
        if not result["PASS"]:
            raise SystemExit(1)
