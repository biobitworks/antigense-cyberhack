"""Guarded intervention 042: independent fault and security-oracle checks."""
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import custody
import cascade
from fixture_eval042 import authorize_file


class GuardedIntervention042(unittest.TestCase):
    def test_legacy_f1_witness_is_retained_not_rewritten(self):
        obs = {"name": "historical_bug", "state": "OBSERVED",
               "checks": {"security_policy_pass": False}}
        cls, _ = custody.derive(obs, [])
        self.assertEqual(cls["custody_admission"], "ADMITTED")
        self.assertEqual(cls["checks"]["provided.security_policy_pass"], False)

    def test_strict_v2_blocks_false_or_missing_security_gate(self):
        obs = {"name": "incident", "state": "OBSERVED",
               "admission_policy": "STRICT_V2",
               "required_checks": ["security_policy_pass"],
               "checks": {"security_policy_pass": False}}
        self.assertEqual(custody.derive(obs, [])[0]["custody_admission"], "QUARANTINED")
        obs["checks"] = {"unrelated_positive": True}
        self.assertEqual(custody.derive(obs, [])[0]["custody_admission"], "QUARANTINED")
        obs["required_checks"] = []
        self.assertEqual(custody.derive(obs, [])[0]["custody_admission"], "QUARANTINED")

    def test_strict_v2_admits_explicit_positive_oracle_only(self):
        obs = {"name": "incident", "state": "OBSERVED",
               "admission_policy": "STRICT_V2",
               "required_checks": ["security_policy_pass", "oracle_pass"],
               "checks": {"security_policy_pass": True, "oracle_pass": True,
                          "negative_control_expected": False}}
        cls, _ = custody.derive(obs, [])
        self.assertEqual(cls["custody_admission"], "ADMITTED")
        self.assertEqual(cls["checks"]["provided.negative_control_expected"], False)

    def test_append_defaults_to_strict_v2_without_rewriting_legacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            custody.freeze(base, ROOT)
            custody.append_step(base, {
                "name": "no_required_oracle", "state": "OBSERVED",
                "checks": {"security_policy_pass": True}
            })
            obj = custody.read(base / "step-000002.json")
            self.assertEqual(obj["observation"]["admission_policy"], "STRICT_V2")
            self.assertEqual(obj["classification"]["custody_admission"], "QUARANTINED")
            self.assertTrue(custody.verify(base)["PASS"])

    def test_authorization_oracle_all_four_cases(self):
        for a in (False, True):
            for h in (False, True):
                self.assertEqual(cascade.auth("before", a, h), True if not h else a)
                self.assertEqual(cascade.auth("after", a, h), a and h)

    def test_no_module_execution_on_malicious_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            marker = base / "should-not-exist"
            malicious = base / "evil.py"
            malicious.write_text(
                f'open({str(marker)!r}, "w").write("ran")\\n'
                'def authorize(authorized, worker_healthy):\\n'
                '    return True\\n'.replace('\\\\n', '\\n')
            )
            with self.assertRaises((ValueError, SyntaxError)):
                authorize_file(malicious, False, False)
            self.assertFalse(marker.exists())

    def test_valid_python_with_module_side_effect_is_rejected(self):
        import ast
        with tempfile.TemporaryDirectory() as tmp:
            marker = pathlib.Path(tmp) / "marker.txt"
            source = (
                f"open({str(marker)!r}, 'w').write('executed')\n"
                "def authorize(authorized, worker_healthy):\n"
                "    return True\n"
            )
            ast.parse(source)  # The adversarial control must be syntactically valid.
            path = pathlib.Path(tmp) / "injected.py"
            path.write_text(source)
            with self.assertRaises(ValueError):
                authorize_file(path, False, False)
            self.assertFalse(marker.exists())

    def test_no_calls_inside_authorization_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "unexpected.py"
            path.write_text("def authorize(authorized, worker_healthy):\n"
                            "    return bool(authorized)\n")
            with self.assertRaises(ValueError):
                authorize_file(path, True, True)


if __name__ == "__main__":
    unittest.main()
