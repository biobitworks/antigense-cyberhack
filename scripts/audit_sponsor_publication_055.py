#!/usr/bin/env python3
"""Deterministic, FAIL-CLOSED sponsor-to-homepage release gate (055).

This is a *presentation/evidence-index reconciliation*, NOT proof of provider
execution, scientific validity, cryptographic signing, or Merkle commitment.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = "antigense.sponsor_publication_gate.v1"
STATUS_ADMITTED = {"EXECUTED"}
CANONICAL_NAMES = {"Pi": "Pi Security"}
EVIDENCE_ROOT = "data/sponsors"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


class SponsorCards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.current = None
        self.depth = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = a.get("class", "").split()
        if self.current is None and tag == "div" and "sponsor" in classes:
            self.current = {"title": "", "text": "", "links": []}
            self.depth = 1
            return
        if self.current is None:
            return
        if tag == "div":
            self.depth += 1
        if tag == "h3":
            self.in_title = True
        if tag == "a":
            self.current["links"].append(a.get("href", ""))

    def handle_endtag(self, tag):
        if self.current is None:
            return
        if tag == "h3":
            self.in_title = False
        if tag == "div":
            self.depth -= 1
            if self.depth == 0:
                self.current["title"] = self.current["title"].strip()
                self.current["text"] = re.sub(r"\s+", " ", self.current["text"]).strip()
                self.cards.append(self.current)
                self.current = None

    def handle_data(self, value):
        if self.current is not None:
            self.current["text"] += value + " "
            if self.in_title:
                self.current["title"] += value


def evaluate(home_bytes, ledger_bytes, public_root, readback_bytes=None):
    source = json.loads(ledger_bytes)
    sponsors = source.get("sponsors")
    if not isinstance(sponsors, dict) or not sponsors:
        raise ValueError("Sponsor index must contain non-empty sponsors mapping")
    parser = SponsorCards()
    parser.feed(home_bytes.decode("utf-8"))
    cards = parser.cards
    reported = {c["title"].casefold(): c for c in cards}
    violations = []

    def fail(code, sponsor, detail):
        violations.append({"code": code, "sponsor": sponsor, "detail": detail})

    if readback_bytes is not None and readback_bytes != home_bytes:
        fail("E_DEPLOYED_BYTES_DIFFER", "homepage", "Public readback differs from source HTML bytes")

    if len(cards) < 3:
        fail("E_INCOMPLETE_SPONSOR_SURFACE", "homepage", "Fewer than three identifiable featured sponsor cards")

    for key, record in sorted(sponsors.items()):
        name = CANONICAL_NAMES.get(key, key)
        card = reported.get(name.casefold())
        executed = record.get("status") in STATUS_ADMITTED
        if executed and not card:
            fail("E_EXECUTED_SPONSOR_MISSING", key, "Executed sponsor absent from featured homepage cards")
            continue
        if not executed and card:
            fail("E_UNEXECUTED_SPONSOR_FEATURED", key, "Homepage features sponsor whose ledger state is "+str(record.get("status")))
            continue
        if not executed:
            continue

        # Static page must display an admitted sponsor status before JavaScript runs.
        msg = card["text"].upper()
        if not ("EXECUTED" in msg or "HISTORICAL OBSERVED" in msg) or "NOT_TESTED" in msg:
            fail("E_EXECUTED_SPONSOR_STATUS_AMBIGUOUS", key, "Static sponsor card is not clearly labeled executed/historical observed")
        if not record.get("records"):
            fail("E_EXECUTED_SPONSOR_NO_RECORDS", key, "Ledger lacks declared record IDs")
            continue

        link = f"{EVIDENCE_ROOT}/{key.casefold()}.json"
        if link not in card["links"]:
            fail("E_EXECUTED_SPONSOR_NO_DIRECT_EVIDENCE_LINK", key, "Expected an in-card direct link to "+link)
            continue
        projection_file = public_root / link
        if not projection_file.is_file():
            fail("E_SPONSOR_PROJECTION_MISSING", key, "Linked public evidence projection file does not exist")
            continue
        try:
            projection = json.loads(projection_file.read_bytes())
        except (ValueError, OSError) as e:
            fail("E_SPONSOR_PROJECTION_INVALID", key, type(e).__name__)
            continue
        if (
            projection.get("sponsor") != key
            or projection.get("status") != "EXECUTED"
            or projection.get("evidence_index_sha256") != digest(ledger_bytes)
            or projection.get("record_ids") != record["records"]
        ):
            fail("E_SPONSOR_PROJECTION_UNBOUND", key, "Projection does not match ledger identity, execution state and record IDs")

    result = {
        "schema": SCHEMA,
        "verdict": "PASS" if not violations else "BLOCK",
        "source_homepage_sha256": digest(home_bytes),
        "sponsor_ledger_sha256": digest(ledger_bytes),
        "public_readback_sha256": digest(readback_bytes) if readback_bytes is not None else "NOT_TESTED",
        "featured_sponsor_titles": [c["title"] for c in cards],
        "required_executed_sponsors": sorted(k for k, v in sponsors.items() if v.get("status") == "EXECUTED"),
        "violations": violations,
        "scope": "Sponsor homepage discoverability, static states, and index-bound public projection; does NOT verify provider execution",
        "signature": "NOT_SIGNED",
        "mmr": "NOT_COMPUTED",
    }
    # Hash identifies exactly these serialized audit bytes; it is not a Merkle root or time attestation.
    result["audit_payload_sha256"] = digest(canonical(result))
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--homepage", type=Path, default=Path("public/index.html"))
    ap.add_argument("--ledger", type=Path, default=Path("evidence/INDEX.json"))
    ap.add_argument("--public-root", type=Path, default=Path("public"))
    ap.add_argument("--public-readback-html", type=Path, help="Exact downloaded production HTML bytes")
    ap.add_argument("--receipt", type=Path, help="Write deterministic JSON; never overwrite an existing receipt")
    args = ap.parse_args()
    try:
        result = evaluate(
            args.homepage.read_bytes(), args.ledger.read_bytes(),
            args.public_root,
            args.public_readback_html.read_bytes() if args.public_readback_html else None
        )
        output = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if args.receipt:
            # Exclusive create: past audited states cannot be silently rewritten.
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            with args.receipt.open("x", encoding="utf-8") as fp:
                fp.write(output)
        print(output, end="")
        return 0 if result["verdict"] == "PASS" else 2
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"INVALID_INPUT: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
