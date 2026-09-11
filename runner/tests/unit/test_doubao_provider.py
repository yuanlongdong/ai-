import unittest

from runner.providers.doubao import DoubaoProvider, MockDoubaoProvider, body_sha8


class TestMockDoubaoProvider(unittest.TestCase):
    def test_draft_fields_nonempty_and_round_semantics(self):
        draft = MockDoubaoProvider().generate_opinion(
            "共享上下文", "对方观点", {"round": 6, "next_writer": "Doubao"}
        )
        self.assertTrue(draft.adds)
        self.assertEqual(draft.round, 7)  # round = status.round + 1
        self.assertIn("新增判断", draft.body())
        self.assertIn("待确认问题", draft.body())
        self.assertGreater(len(draft.new_judgment), 0)

    def test_to_markdown_contains_front_matter(self):
        draft = MockDoubaoProvider().generate_opinion("c", "v", {"round": 1})
        md = draft.to_markdown()
        self.assertIn("round: 2", md)
        self.assertIn("writer: Doubao", md)
        self.assertIn("## 新增判断", md)
        self.assertTrue(md.startswith("---"))


class TestBodySha8(unittest.TestCase):
    def test_stable_and_distinct(self):
        self.assertEqual(body_sha8("abc"), body_sha8("abc"))
        self.assertNotEqual(body_sha8("abc"), body_sha8("abd"))
        self.assertEqual(len(body_sha8("abc")), 8)


class TestDoubaoProvider(unittest.TestCase):
    def test_missing_key_raises(self):
        provider = DoubaoProvider(api_key=None)
        with self.assertRaises(RuntimeError):
            provider.generate_opinion("c", "v", {"round": 1})

    def test_mock_does_not_touch_status(self):
        status = {"round": 2, "next_writer": "Doubao"}
        draft = MockDoubaoProvider().generate_opinion("c", "v", status)
        self.assertEqual(status, {"round": 2, "next_writer": "Doubao"})  # 只读


if __name__ == "__main__":
    unittest.main()
