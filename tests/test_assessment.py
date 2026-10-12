# -*- coding: utf-8 -*-
"""抉择论证评估与提交记录的单元测试。"""
import tempfile
import unittest
from pathlib import Path

from src.app import assessment, store


class AssessmentTest(unittest.TestCase):
    def test_parse_result_extracts_json(self):
        text = ('前言 {"scores":{"sourcing":3,"contextualization":2,"corroboration":1,'
                '"argumentation":3,"historical_empathy":2},"strengths":["a"],'
                '"improvements":["b"],"feedback":"c"} 后记')
        r = assessment.parse_result(text)
        self.assertEqual(r["total"], 11)
        self.assertEqual(r["max_total"], 15)
        self.assertEqual(r["scores"]["sourcing"], 3)

    def test_parse_result_clamps_out_of_range(self):
        r = assessment.parse_result('{"scores":{"sourcing":9,"contextualization":-2}}')
        self.assertEqual(r["scores"]["sourcing"], 3)
        self.assertEqual(r["scores"]["contextualization"], 0)

    def test_parse_result_handles_garbage(self):
        self.assertIn("error", assessment.parse_result("不是 JSON"))

    def test_mock_evaluate_shape(self):
        r = assessment.evaluate("mock", "", "", "", {"name": "x"},
                                {"scenario": "s", "options": []}, "A", "x" * 100)
        self.assertEqual(r["max_total"], 15)
        self.assertIn("feedback", r)


class SubmissionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._orig = store.SUBMISSIONS_FILE
        store.SUBMISSIONS_FILE = Path(self.tmp.name) / "subs.json"

    def tearDown(self):
        store.SUBMISSIONS_FILE = self._orig
        self.tmp.cleanup()

    def test_save_and_list(self):
        self.assertEqual(store.list_submissions(), [])
        store.save_submission({"figure_id": "a", "argument": "x"})
        rows = store.list_submissions()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["figure_id"], "a")


if __name__ == "__main__":
    unittest.main()
