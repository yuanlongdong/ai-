import unittest
from runner.providers.doubao import OpinionDraft
from runner.state import MeetingState
from runner.validate import expected_event_id,validate_draft
class ValidateTests(unittest.TestCase):
 def test_event_id_deterministic(self):
  d=OpinionDraft(8,"GPT",True,"proposed","2026-09-11","facts","judgment","reply","plan","questions"); self.assertEqual(expected_event_id(d),expected_event_id(d)); self.assertTrue(expected_event_id(d).startswith("R8-GPT-"))
 def test_round(self):
  d=OpinionDraft(7,"GPT",True,"proposed","2026-09-11","f","j","r","p","q")
  with self.assertRaises(ValueError): validate_draft(d,MeetingState(7,"Doubao","GPT","WAITING_GPT","IN_PROGRESS","R7-DOUBAO-aec4affd"))
