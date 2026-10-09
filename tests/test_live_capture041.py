"""Contract and negative controls for the video live readback verifier."""
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "agent"))
import custody
from live_capture041 import verify_bundle


def fixture():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td)
        g=custody.freeze(base, ROOT)
        custody.append_step(base, {"name":"test event","state":"OBSERVED","checks":{"ok":True}})
        rows=custody.rows(base)
        proof={"genesis":g,"ledger":rows,
               "objects":[json.loads((base/r["object_file"]).read_text()) for r in rows[1:]],
               "prefixes":[json.loads((base/f"prefix-{i:06d}.json").read_text())
                           for i in range(1,len(rows)+1)]}
        run={"id":"unit-fixture","project_root":g["project_root"],
             "mmr_root":custody.mmr(rows)["root"]}
        return proof,run


class ReadbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof,cls.receipt_run=fixture()

    def test_valid_chain(self):
        self.assertEqual(verify_bundle(self.proof,self.receipt_run),self.receipt_run["mmr_root"])

    def assert_tamper_rejected(self,modifier):
        p=copy.deepcopy(self.proof)
        modifier(p)
        with self.assertRaises(ValueError):
            verify_bundle(p,self.receipt_run)

    def test_changed_observation(self):
        self.assert_tamper_rejected(lambda p:p["objects"][0]["observation"].update(name="tamper"))

    def test_changed_typed_edge(self):
        self.assert_tamper_rejected(lambda p:p["objects"][0].update(relation="IMPLIES_CAUSATION"))

    def test_changed_prefix(self):
        self.assert_tamper_rejected(lambda p:p["prefixes"][-1].update(root="0"*64))

    def test_changed_event_hash(self):
        self.assert_tamper_rejected(lambda p:p["ledger"][-1].update(event_hash="a"*64))

    def test_changed_project_binding(self):
        self.assert_tamper_rejected(lambda p:p["genesis"].update(project_root="b"*64))


if __name__=="__main__":
    unittest.main()
