import unittest
from runner.state import MeetingState,next_state
class StateTests(unittest.TestCase):
 def test_turn_advances(self):
  s=next_state(MeetingState(7,"Doubao","GPT","WAITING_GPT","IN_PROGRESS","R7-DOUBAO-aec4affd"),"GPT","R8-GPT-12345678"); self.assertEqual((s.round,s.next_writer,s.status),(8,"Doubao","WAITING_DOUBAO"))
 def test_wrong_writer(self):
  with self.assertRaises(ValueError): next_state(MeetingState(7,"Doubao","GPT","WAITING_GPT","IN_PROGRESS","R7-DOUBAO-aec4affd"),"Doubao","R8-DOUBAO-12345678")
