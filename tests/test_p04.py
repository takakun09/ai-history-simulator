# -*- coding: utf-8 -*-
"""P0-4：自评对比、分级支架、核对并入画像、接口校验。"""
import io
import json
import tempfile
import unittest
from pathlib import Path

from src.app import assessment, profile, server, store


def post(path, payload):
    """直接调用路由处理器，不起服务、不占端口。"""
    body = json.dumps(payload).encode("utf-8")
    h = server.Handler.__new__(server.Handler)
    h.path = path
    h.headers = {"Content-Length": str(len(body))}
    h.rfile = io.BytesIO(body)
    h.wfile = io.BytesIO()
    h._status = None
    h.send_response = lambda code, message=None: setattr(h, "_status", code)
    h.send_header = lambda *a, **k: None
    h.end_headers = lambda: None
    h.do_POST()
    return h._status, json.loads(h.wfile.getvalue().decode("utf-8"))


class CheckScoresTest(unittest.TestCase):
    def test_parse_check_keeps_only_three_dimensions_and_clamps(self):
        r = assessment.parse_check(
            '{"verdict":"站得住","scores":{"sourcing":9,"corroboration":-3,'
            '"argumentation":2,"historical_empathy":3}}')
        self.assertEqual(r["scores"], {"sourcing": 3, "corroboration": 0, "argumentation": 2})
        self.assertNotIn("historical_empathy", r["scores"])

    def test_parse_check_skips_bad_numbers(self):
        r = assessment.parse_check('{"scores":{"sourcing":"x","argumentation":1}}')
        self.assertEqual(r["scores"], {"argumentation": 1})

    def test_mock_check_has_scores(self):
        r = assessment._mock_check("相符", "x" * 50)
        self.assertEqual(set(r["scores"]), set(assessment.CHECK_DIMENSIONS))


class ProfileP04Test(unittest.TestCase):
    def test_mixed_kinds_and_self_gap(self):
        rows = [
            {"kind": "decision", "result": {"scores": {"sourcing": 2, "contextualization": 2}},
             "self_scores": {"sourcing": 3, "contextualization": 3}},
            {"kind": "check", "result": {"scores": {"sourcing": 2, "corroboration": 1}}},
        ]
        p = profile.build_profile(rows)
        self.assertEqual(p["by_kind"], {"decision": 1, "check": 1})
        self.assertEqual(p["per_dimension"]["sourcing"]["avg"], 2.0)
        self.assertEqual(p["per_dimension"]["sourcing"]["self_avg"], 3.0)
        self.assertEqual(p["per_dimension"]["sourcing"]["gap"], 1.0)
        self.assertEqual(p["overall_gap"], 1.0)
        self.assertEqual(p["per_dimension"]["corroboration"]["n"], 1)

    def test_tolerates_missing_fields(self):
        p = profile.build_profile([{}, {"kind": "decision"}, {"result": {}}])
        self.assertEqual(p["count"], 3)
        self.assertIsNone(p["overall_gap"])
        self.assertIsNone(p["weakest"])

    def test_empty(self):
        p = profile.build_profile([])
        self.assertEqual(p["count"], 0)
        self.assertEqual(p["by_kind"], {"decision": 0, "check": 0})


class DecideRouteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._f, self._s = store.FIGURES_FILE, store.SUBMISSIONS_FILE
        store.FIGURES_FILE = Path(self.tmp.name) / "figures.json"
        store.SUBMISSIONS_FILE = Path(self.tmp.name) / "submissions.json"

    def tearDown(self):
        store.FIGURES_FILE, store.SUBMISSIONS_FILE = self._f, self._s
        self.tmp.cleanup()

    def _payload(self, self_scores):
        return {
            "figure_id": "zhuge-liang", "dilemma_id": "jieting", "choice_id": "wang-ping",
            "argument": "我选择王平，因为街亭需要持重之将。", "provider": "mock",
            "student_id": "s-test", "self_scores": self_scores, "hints_used": 2,
        }

    def test_missing_self_scores_is_rejected(self):
        status, body = post("/api/decide", self._payload({"sourcing": 2}))
        self.assertEqual(status, 400)
        self.assertIn("自评", body["error"])
        self.assertEqual(store.list_submissions(), [])

    def test_complete_self_scores_is_stored(self):
        full = {k: 2 for k, _, _ in assessment.RUBRIC}
        status, body = post("/api/decide", self._payload(full))
        self.assertEqual(status, 200)
        self.assertIn("result", body)
        row = store.list_submissions()[-1]
        self.assertEqual(row["kind"], "decision")
        self.assertEqual(row["self_scores"], full)
        self.assertEqual(row["hints_used"], 2)
        self.assertIn("sourcing", row["result"]["scores"])

    def test_hints_used_does_not_change_scores(self):
        full = {k: 1 for k, _, _ in assessment.RUBRIC}
        _, a = post("/api/decide", {**self._payload(full), "hints_used": 0})
        _, b = post("/api/decide", {**self._payload(full), "hints_used": 3})
        self.assertEqual(a["result"]["scores"], b["result"]["scores"])


if __name__ == "__main__":
    unittest.main()
