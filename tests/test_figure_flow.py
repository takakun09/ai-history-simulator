# -*- coding: utf-8 -*-
"""自定义人物：保存后学生端可见 + URL 编码 id 可解析。"""
import io
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import quote

from src.app import server, store


def _handler(path):
    h = server.Handler.__new__(server.Handler)
    h.path = path
    h.headers = {"Content-Length": "0"}
    h.rfile = io.BytesIO(b"{}")
    h.wfile = io.BytesIO()
    h._status = None
    h.send_response = lambda code, message=None: setattr(h, "_status", code)
    h.send_header = lambda *a, **k: None
    h.end_headers = lambda: None
    return h


def post(path, payload):
    body = json.dumps(payload).encode("utf-8")
    h = _handler(path)
    h.headers = {"Content-Length": str(len(body))}
    h.rfile = io.BytesIO(body)
    h.do_POST()
    return h._status, json.loads(h.wfile.getvalue().decode("utf-8"))


def get(path):
    h = _handler(path)
    h.do_GET()
    return h._status, json.loads(h.wfile.getvalue().decode("utf-8"))


class FigureFlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._orig = store.FIGURES_FILE
        store.FIGURES_FILE = Path(self.tmp.name) / "figures.json"

    def tearDown(self):
        store.FIGURES_FILE = self._orig
        self.tmp.cleanup()

    def test_published_figure_appears_for_students(self):
        status, _ = post("/api/figures", {"id": "zhang-qian", "name": "张骞",
                                          "published": True, "system_prompt": "x"})
        self.assertEqual(status, 200)
        _, body = get("/api/figures?scope=student")
        ids = [f["id"] for f in body["figures"]]
        self.assertIn("zhang-qian", ids)

    def test_unpublished_figure_hidden_from_students(self):
        post("/api/figures", {"id": "draft", "name": "草稿", "published": False})
        _, body = get("/api/figures?scope=student")
        self.assertNotIn("draft", [f["id"] for f in body["figures"]])
        _, teacher = get("/api/figures?scope=teacher")
        self.assertIn("draft", [f["id"] for f in teacher["figures"]])

    def test_url_encoded_id_resolves(self):
        """ID 含中文或空格时，聊天页仍能取到人物（此前会 404）。"""
        name = "张骞 测试"
        post("/api/figures", {"id": name, "name": "张骞", "published": True})
        status, body = get("/api/figures/" + quote(name))
        self.assertEqual(status, 200)
        self.assertEqual(body["name"], "张骞")

    def test_unknown_id_returns_404(self):
        status, _ = get("/api/figures/not-exist")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
