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


class CheckTest(unittest.TestCase):
    def test_mock_check_short_basis_is_partial(self):
        r = assessment.check_source("mock", "", "", "", {"name": "x", "sources": []},
                                    "claim", "有出入", "太短")
        self.assertEqual(r["verdict"], "部分成立")

    def test_mock_check_long_basis_stands(self):
        r = assessment.check_source("mock", "", "", "", {"name": "x", "sources": []},
                                    "claim", "有出入", "依" * 50)
        self.assertEqual(r["verdict"], "站得住")

    def test_parse_check_garbage(self):
        self.assertIn("error", assessment.parse_check("不是 JSON"))

    def test_sources_text_includes_excerpt(self):
        text = assessment._sources_text([{"title": "A", "kind": "一手", "excerpt": "E"}])
        self.assertIn("A", text)
        self.assertIn("E", text)


class CheckRecordTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._orig = store.CHECKS_FILE
        store.CHECKS_FILE = Path(self.tmp.name) / "checks.json"

    def tearDown(self):
        store.CHECKS_FILE = self._orig
        self.tmp.cleanup()

    def test_save_and_list_checks(self):
        self.assertEqual(store.list_checks(), [])
        store.save_check({"figure_id": "a", "verdict": "相符"})
        self.assertEqual(store.list_checks()[0]["verdict"], "相符")


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
