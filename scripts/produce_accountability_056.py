#!/usr/bin/env python3
"""Recompute and optionally sign release 056 accountability snapshot.

Signs current evidence bytes with a local machine-scoped Ed25519 key. A verified
signature proves key possession, not human or AI-agent identity, model causality,
a prior timestamp, or a cloud sponsor execution. Never distributes private key.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from custody import canonical, digest, mmr, independent_mmr_root

SOURCES=[
 ("submitted_homepage","public/archive/submission-054/index.html","OBSERVED_SOURCE"),
 ("evidence_index","evidence/INDEX.json","OBSERVED_SOURCE"),
 ("retrospective_block","evidence/audit_055/released_054_homepage_failed_gate.json","EXECUTED_AUDIT"),
 ("preserved_archive","public/archive/submission-054/verify.js","OBSERVED_ARCHIVE"),
 ("corrective_homepage","public/index.html","CANDIDATE_CORRECTION"),
 ("semgrep_projection","public/data/sponsors/semgrep.json","LEDGER_BOUND_PROJECTION"),
 ("akash_projection","public/data/sponsors/akash.json","LEDGER_BOUND_PROJECTION"),
 ("clickhouse_projection","public/data/sponsors/clickhouse.json","LEDGER_BOUND_PROJECTION"),
 ("sponsor_gate_pass","evidence/audit_056/candidate_pass.json","EXECUTED_AUDIT")
]

def output_paths():
 p=ROOT/"public/data/audits"
 return p/"release-accountability-056.json",p/"release-accountability-056.verify.json"

def atomize():
 items=[]
 for idx,(kind,path,state) in enumerate(SOURCES):
  b=(ROOT/path).read_bytes()
  atom={"kind":kind,"source_path":path,"source_sha256":digest(b),"status":state,
        "parent_fco_id":items[-1]["fco_id"] if items else None,
        "typed_relation":"FOLLOWS_DECLARED_AUDIT_SEQUENCE" if items else "GENESIS_REFERENCE",
        "attribution":"UNKNOWN_AGENT_IDENTITY"}
  h=digest(canonical(atom))
  items.append({"atom":atom,"event_hash":h,"fco_id":"fco:sha256:"+h})
 return items

def generate():
 items=atomize()
 final=mmr(items)
 prefixes=[{"leaf_count":i,"root":mmr(items[:i])["root"],
            "independent_verified":mmr(items[:i])["root"]==independent_mmr_root(items[:i])}
           for i in range(1,len(items)+1)]
 assert all(p["independent_verified"] for p in prefixes)
 assert final["root"]==independent_mmr_root(items)
 return {
  "schema":"antigense.accountability_breakpoint.056r1.v1",
  "project":"biobitworks/antigense-cyberhack",
  "predecessor_commit":"5db6ac9e3cc5db5418d84e594107870ed74062e9",
  "claim":"Ordered content commitments for the sponsor-surface release audit, NOT execution or agent attribution",
  "actor_findings":{
    "GitHub_commit_author":"COMMIT_METADATA_ONLY",
    "Codex":"REPORTED_IN_COMMIT_TRAILER; NOT_ATTESTED",
    "ChatGPT":"SELF_REPORTED_ORCHESTRATION_RELEASE_GO; NOT_SIGNED_TURN_RECEIPT",
    "Claude":"UNKNOWN"
  },
  "source_attribution_scope":"IDs and hashes certify provided bytes, not human/model identity, truth or causal responsibility",
  "records":items,
  "mmr":final,
  "prefixes":prefixes,
  "construction":"HYDRALAMP_MMR_V1 source src/custody.py; independently recompute perfect-subtree MMR for every prefix",
  "compilation_signature":"IN_SEPARATE_VERIFIED_RECEIPT",
 }

def key_path():
 return Path.home()/".antigense/custody-keys/release056-ed25519.pem"

def sign(b):
 private_path=key_path()
 private_path.parent.mkdir(parents=True,exist_ok=True)
 os.chmod(private_path.parent,0o700)
 if private_path.exists():
  private=serialization.load_pem_private_key(private_path.read_bytes(),password=None)
  if not isinstance(private,Ed25519PrivateKey): raise ValueError("wrong private key type")
 else:
  private=Ed25519PrivateKey.generate()
  pem=private.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  fd=os.open(str(private_path),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,"wb") as fp:fp.write(pem);fp.flush();os.fsync(fp.fileno())
 pub=private.public_key()
 signature=private.sign(b)
 pub.verify(signature,b)
 raw=pub.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
 return {"schema":"antigense.accountability_signature_056.v1",
         "signed_object_sha256":digest(b),
         "signature_algorithm":"Ed25519",
         "signature_b64":base64.b64encode(signature).decode(),
         "public_key_b64":base64.b64encode(raw).decode(),
         "public_key_sha256_fingerprint":digest(raw),
         "signature_verification":"PASS",
         "key_provenance":"LOCAL_SOFTWARE_KEY_GENERATED_ON_MAGICPROBOX_NO_PERSON_OR_MODEL_IDENTITY_ATTESTATION",
         "external_timestamp":"NOT_TESTED",
         "owner_identity":"UNVERIFIED",
         "historical_cloud_provider_reexecution":"NOT_EXECUTED"}

def verify(sig,b):
 assert sig["signed_object_sha256"]==digest(b)
 pub=Ed25519PublicKey.from_public_bytes(base64.b64decode(sig["public_key_b64"]))
 pub.verify(base64.b64decode(sig["signature_b64"]),b)
 assert sig["public_key_sha256_fingerprint"]==digest(base64.b64decode(sig["public_key_b64"]))
 doc=json.loads(b)
 assert doc["mmr"]==mmr(doc["records"])
 assert doc["mmr"]["root"]==independent_mmr_root(doc["records"])
 assert all(p["root"]==independent_mmr_root(doc["records"][:i])
            for i,p in enumerate(doc["prefixes"],1))
 for item in doc["records"]:
  atom=item["atom"]
  assert digest((ROOT/atom["source_path"]).read_bytes())==atom["source_sha256"]
  assert digest(canonical(atom))==item["event_hash"]
 return True

def main():
 receipt_path,sig_path=output_paths()
 if "--verify" in sys.argv:
  b=receipt_path.read_bytes()
  sig=json.loads(sig_path.read_bytes())
  assert verify(sig,b)
  print(json.dumps({"PASS":True,"leaf_count":len(json.loads(b)["records"]),"mmr_root":json.loads(b)["mmr"]["root"],"signature_verified":True,"public_key_fingerprint":sig["public_key_sha256_fingerprint"]},sort_keys=True))
  return
 if receipt_path.exists() or sig_path.exists():raise FileExistsError("Append-only: existing signed receipt; do not overwrite")
 receipt_path.parent.mkdir(parents=True,exist_ok=True)
 payload=json.dumps(generate(),indent=2,sort_keys=True,ensure_ascii=False)+"\n"
 bytes_=payload.encode()
 sig=sign(bytes_)
 assert verify(sig,bytes_)
 with receipt_path.open("x") as f:f.write(payload)
 with sig_path.open("x") as f:f.write(json.dumps(sig,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"PASS":True,"mmr_root":json.loads(bytes_)["mmr"]["root"],"prefixes":len(json.loads(bytes_)["prefixes"]),"signature_verified":True,"receipt_sha256":digest(bytes_),"public_key_fingerprint":sig["public_key_sha256_fingerprint"]},sort_keys=True))

if __name__=="__main__":main()
