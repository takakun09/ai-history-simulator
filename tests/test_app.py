# -*- coding: utf-8 -*-
"""零依赖单元测试：python3 -m unittest discover -s tests"""
import tempfile
import unittest
from pathlib import Path

from src.app import providers, store


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._orig = store.FIGURES_FILE
        store.FIGURES_FILE = Path(self.tmp.name) / "figures.json"

    def tearDown(self):
        store.FIGURES_FILE = self._orig
        self.tmp.cleanup()

    def test_seed_has_three_figures(self):
        self.assertEqual(len(store.list_figures()), 3)

    def test_upsert_and_delete(self):
        store.upsert_figure({"id": "x", "name": "X", "published": True})
        self.assertEqual(store.get_figure("x")["name"], "X")
        self.assertTrue(store.delete_figure("x"))
        self.assertIsNone(store.get_figure("x"))
        self.assertFalse(store.delete_figure("x"))

    def test_published_filter(self):
        store.upsert_figure({"id": "y", "name": "Y", "published": False})
        self.assertNotIn("y", [f["id"] for f in store.list_figures(published_only=True)])
        self.assertIn("y", [f["id"] for f in store.list_figures(published_only=False)])


class ProvidersTest(unittest.TestCase):
    def test_mock_reply(self):
        out = providers.chat("mock", "", "", "", "sys", [{"role": "user", "content": "hi"}], "诸葛亮")
        self.assertIn("诸葛亮", out)

    def test_unknown_provider_raises(self):
        with self.assertRaises(ValueError):
            providers.chat("nope", "", "", "", "s", [], "")

    def test_public_providers_hide_kind(self):
        self.assertTrue(providers.PUBLIC_PROVIDERS)
        for p in providers.PUBLIC_PROVIDERS:
            self.assertNotIn("kind", p)
            self.assertIn("id", p)


if __name__ == "__main__":
    unittest.main()
