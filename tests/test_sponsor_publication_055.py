"""Release gate regression: previously submitted homepage must BLOCK."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import importlib.util


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit055", ROOT / "scripts/audit_sponsor_publication_055.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class SponsorPublicationTests(unittest.TestCase):
    def setUp(self):
        self.ledger = (ROOT / "evidence/INDEX.json").read_bytes()
        self.original = (ROOT / "public/index.html").read_bytes()

    def test_frozen_submitted_homepage_must_block(self):
        r = audit.evaluate(self.original, self.ledger, ROOT / "public")
        self.assertEqual(r["verdict"], "BLOCK")
        findings = {(x["code"], x["sponsor"]) for x in r["violations"]}
        self.assertIn(("E_EXECUTED_SPONSOR_MISSING", "ClickHouse"), findings)
        self.assertIn(("E_UNEXECUTED_SPONSOR_FEATURED", "Pi"), findings)
        self.assertEqual(r["source_homepage_sha256"], "80dc78b4e2cd8b23bd9094a725f567de473db27cb9b80629f3f8da7b3424a888")

    def build_valid_site(self, root):
        ledger = json.loads(self.ledger)
        cards = []
        for name, v in sorted(ledger["sponsors"].items()):
            if v.get("status") != "EXECUTED":
                continue
            key = name.casefold()
            folder = root / "data/sponsors"
            folder.mkdir(parents=True, exist_ok=True)
            projection = {
                "sponsor": name, "status": "EXECUTED",
                "evidence_index_sha256": hashlib.sha256(self.ledger).hexdigest(),
                "record_ids": v["records"],
                "provider_receipt_executed_verified_by_this_gate": "NOT_TESTED",
            }
            (folder / f"{key}.json").write_text(json.dumps(projection))
            cards.append(
                f'<div class="card sponsor"><h3>{name}</h3>'
                f'<p>HISTORICAL OBSERVED · EXECUTED</p>'
                f'<a href="data/sponsors/{key}.json">Evidence and historical receipt identifiers</a></div>'
            )
        return ("<!doctype html><html><body>" + "".join(cards) + "</body></html>").encode()

    def test_complete_evidence_bound_page_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = self.build_valid_site(root)
            r = audit.evaluate(valid, self.ledger, root, valid)
            self.assertEqual(r["verdict"], "PASS")
            self.assertEqual(r["violations"], [])
            self.assertEqual(r["public_readback_sha256"], hashlib.sha256(valid).hexdigest())
            self.assertEqual(r["signature"], "NOT_SIGNED")
            self.assertEqual(r["mmr"], "NOT_COMPUTED")

    def test_tampered_evidence_projection_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = self.build_valid_site(root)
            target = root / "data/sponsors/clickhouse.json"
            obj = json.loads(target.read_text())
            obj["record_ids"] = ["fabricated"]
            target.write_text(json.dumps(obj))
            r = audit.evaluate(valid, self.ledger, root)
            self.assertIn("E_SPONSOR_PROJECTION_UNBOUND", [x["code"] for x in r["violations"]])

    def test_page_without_clickhouse_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = self.build_valid_site(root)
            invalid = valid.replace(b"<h3>ClickHouse</h3>", b"<h3>Unused Provider</h3>")
            r = audit.evaluate(invalid, self.ledger, root)
            self.assertIn(("E_EXECUTED_SPONSOR_MISSING", "ClickHouse"), [(x["code"], x["sponsor"]) for x in r["violations"]])

    def test_nonidentical_public_readback_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = self.build_valid_site(root)
            r = audit.evaluate(valid, self.ledger, root, valid + b"\n")
            self.assertIn("E_DEPLOYED_BYTES_DIFFER", [x["code"] for x in r["violations"]])

    def test_unlabeled_execution_status_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = self.build_valid_site(root)
            invalid = valid.replace(b"HISTORICAL OBSERVED", b"NOT_TESTED")
            r = audit.evaluate(invalid, self.ledger, root)
            self.assertIn("E_EXECUTED_SPONSOR_STATUS_AMBIGUOUS", [x["code"] for x in r["violations"]])

    def test_ledger_mutation_invalidates_bound_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = self.build_valid_site(root)
            replacement = self.ledger.replace(b"successor_016", b"successor_999", 1)
            r = audit.evaluate(valid, replacement, root)
            self.assertIn("E_SPONSOR_PROJECTION_UNBOUND", [x["code"] for x in r["violations"]])


if __name__ == "__main__":
    unittest.main()
