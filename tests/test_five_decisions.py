import unittest

from five_decisions import decide, mask_rows


class FiveDecisionsTest(unittest.TestCase):
    def test_write_sql_blocked(self):
        self.assertEqual(decide({"tool": "query_run", "sql": "delete from recipients"})[0], "block")

    def test_pii_rows_masked(self):
        call = {"tool": "query_run", "sql": "select email from recipients", "returns_rows": True, "fields": ["email"]}
        self.assertEqual(decide(call)[0], "allow_masked")
        self.assertEqual(mask_rows([{"email": "ana@example.com"}])[0]["email"], "a***@***")

    def test_js_is_dry_run(self):
        self.assertEqual(decide({"tool": "js_execute"})[0], "dry_run")

    def test_big_send_needs_two_approvers(self):
        d, reason, _ = decide({"tool": "delivery_send", "qa_passed": True, "volume": 200000})
        self.assertEqual(d, "needs_approval")
        self.assertIn("2 human", reason)

    def test_failed_qa_blocks_send(self):
        self.assertEqual(decide({"tool": "delivery_send", "qa_passed": False})[0], "block")

    def test_unknown_tool_fails_closed(self):
        self.assertEqual(decide({"tool": "privacy_purge_pause"})[0], "block")


if __name__ == "__main__":
    unittest.main()
