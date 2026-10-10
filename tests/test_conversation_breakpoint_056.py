import hashlib,json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ConversationBreakpoint056Tests(unittest.TestCase):
 def test_successor_corrects_sha_without_mutating_predecessor(self):
  old=ROOT/'evidence/audit_056/conversation_breakpoint_056r2.json'
  new=ROOT/'evidence/audit_056/conversation_breakpoint_056r3.json'
  sig=ROOT/'public/data/audits/release-accountability-056.verify.json'
  par=old.read_bytes();o=json.loads(par);n=json.loads(new.read_bytes())
  sha=lambda b:hashlib.sha256(b).hexdigest()
  self.assertEqual(n['parent_conversation_fco_sha256'],sha(par))
  self.assertNotEqual(o['content_identity']['signature_file_sha256'],sha(sig.read_bytes()))
  self.assertEqual(n['content_identity']['signature_file_sha256'],sha(sig.read_bytes()))
  self.assertEqual(n['correction']['prior_reported_hash'],o['content_identity']['signature_file_sha256'])
  self.assertEqual(n['correction']['verification'],'PASS_BYTE_RECOMPUTE')
 def test_historical_homepage_preserved(self):
  b=(ROOT/'public/archive/submission-054/index.html').read_bytes()
  self.assertEqual(hashlib.sha256(b).hexdigest(),'80dc78b4e2cd8b23bd9094a725f567de473db27cb9b80629f3f8da7b3424a888')
