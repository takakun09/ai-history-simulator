# -*- coding: utf-8 -*-
"""零依赖 HTTP 服务：静态前端 + 人物 CRUD + 对话代理。

运行： python3 -m src.app.server
"""
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import assessment, profile, providers, rubric, store

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("text/javascript", ".js")

LANG_SUFFIX = {
    "en": "\n\nLanguage: reply in English.",
    "tw": "\n\n語言：請使用繁體中文回答。",
}


def with_lang(system, lang):
    return (system or "") + LANG_SUFFIX.get(lang or "zh", "")


ROUTES = {"/": "index.html", "/chat": "chat.html", "/teacher": "teacher.html",
          "/analytics": "analytics.html"}


class Handler(BaseHTTPRequestHandler):
    server_version = "HistorySim/0.1"

    def log_message(self, *args):  # 静默访问日志
        pass

    # ---------- helpers ----------
    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _send_file(self, rel):
        path = (WEB / rel).resolve()
        if not str(path).startswith(str(WEB)) or not path.is_file():
            self._json({"error": "not found"}, 404)
            return
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8" if ctype.startswith("text") or ctype == "image/svg+xml" else ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ---------- GET ----------
    def do_GET(self):
        parsed = urlparse(self.path)
        path, query = parsed.path, parse_qs(parsed.query)

        if path == "/api/providers":
            return self._json({"providers": providers.PUBLIC_PROVIDERS})
        if path == "/api/figures":
            scope = (query.get("scope") or ["student"])[0]
            return self._json({"figures": store.list_figures(published_only=(scope == "student"))})
        if path == "/api/rubric":
            return self._json(rubric.guide_payload())
        if path == "/api/profile":
            sid = (query.get("student_id") or [""])[0]
            rows = [r for r in store.list_submissions()
                    if not sid or r.get("student_id") == sid]
            return self._json({"profile": profile.build_profile(rows)})
        if path == "/api/analytics":
            subs = store.list_submissions()
            checks = store.list_checks()
            prof = profile.build_profile(subs)
            hinted = [int(r.get("hints_used") or 0) for r in subs]
            hint_usage = {
                "n": len(hinted),
                "avg": round(sum(hinted) / len(hinted), 2) if hinted else 0,
                "used_share": round(100 * sum(1 for h in hinted if h > 0) / len(hinted))
                if hinted else 0,
            }
            return self._json({
                "profile": prof,
                "hint_usage": hint_usage,
                "self_gap": prof.get("overall_gap"),
                "counts": {"decisions": len(subs), "checks": len(checks),
                           "figures": len(store.list_figures())},
                "recent": list(reversed(subs[-20:])),
            })
        if path.startswith("/api/figures/"):
            fig = store.get_figure(path.rsplit("/", 1)[-1])
            return self._json(fig) if fig else self._json({"error": "not found"}, 404)

        rel = ROUTES.get(path) or path.lstrip("/")
        return self._send_file(rel)

    # ---------- POST ----------
    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self._read_body()
        except json.JSONDecodeError:
            return self._json({"error": "invalid json"}, 400)

        if path == "/api/figures":
            if not body.get("id"):
                return self._json({"error": "缺少 id"}, 400)
            return self._json({"figure": store.upsert_figure(body)})

        if path == "/api/chat":
            fig = store.get_figure(body.get("figure_id", ""))
            if not fig:
                return self._json({"error": "人物不存在"}, 404)
            messages = body.get("messages") or []
            try:
                reply = providers.chat(
                    provider_id=body.get("provider", "mock"),
                    base_url=body.get("base_url", ""),
                    api_key=body.get("api_key", ""),
                    model=body.get("model", ""),
                    system=with_lang(fig.get("system_prompt", ""), body.get("lang")),
                    messages=messages,
                    figure_name=fig.get("name", ""),
                )
            except Exception as exc:  # 把上游错误回给前端，便于演示排错
                return self._json({"error": f"{type(exc).__name__}: {exc}"}, 502)
            return self._json({"reply": reply})

        if path == "/api/decide":
            fig = store.get_figure(body.get("figure_id", ""))
            if not fig:
                return self._json({"error": "人物不存在"}, 404)
            dilemma = next((d for d in fig.get("dilemmas", [])
                            if d.get("id") == body.get("dilemma_id")), None)
            if not dilemma:
                return self._json({"error": "抉择不存在"}, 404)
            opt = next((o for o in dilemma.get("options", [])
                        if o.get("id") == body.get("choice_id")), None)
            argument = (body.get("argument") or "").strip()
            if not argument:
                return self._json({"error": "请先写下你的论证"}, 400)

            raw_self = body.get("self_scores") or {}
            try:
                self_scores = {
                    key: max(0, min(assessment.MAX_PER_ITEM, int(raw_self[key])))
                    for key, _, _ in assessment.RUBRIC
                }
            except (KeyError, TypeError, ValueError):
                return self._json({"error": "请先完成自评（5 个维度都要选）"}, 400)
            try:
                hints_used = max(0, int(body.get("hints_used") or 0))
            except (TypeError, ValueError):
                hints_used = 0

            try:
                result = assessment.evaluate(
                    body.get("provider", "mock"), body.get("base_url", ""),
                    body.get("api_key", ""), body.get("model", ""),
                    fig, dilemma, (opt or {}).get("text", ""), argument,
                    double_score=bool(body.get("double_score")),
                    lang=body.get("lang", "zh"),
                )
            except Exception as exc:
                return self._json({"error": f"{type(exc).__name__}: {exc}"}, 502)
            import datetime
            store.save_submission({
                "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
                "kind": "decision",
                "student_id": body.get("student_id", ""),
                "figure_id": fig["id"], "figure": fig.get("name", ""),
                "dilemma_id": dilemma["id"], "dilemma": dilemma.get("title", ""),
                "choice": (opt or {}).get("text", ""), "argument": argument,
                "self_scores": self_scores, "hints_used": hints_used, "result": result,
            })
            return self._json({"result": result})

        if path == "/api/check":
            fig = store.get_figure(body.get("figure_id", ""))
            if not fig:
                return self._json({"error": "人物不存在"}, 404)
            claim = (body.get("claim") or "").strip()
            verdict = (body.get("verdict") or "").strip()
            basis = (body.get("basis") or "").strip()
            if not claim:
                return self._json({"error": "缺少要核对的说法"}, 400)
            if not verdict:
                return self._json({"error": "请选择你的判断"}, 400)
            if not basis:
                return self._json({"error": "请写下你的依据"}, 400)
            try:
                result = assessment.check_source(
                    body.get("provider", "mock"), body.get("base_url", ""),
                    body.get("api_key", ""), body.get("model", ""),
                    fig, claim, verdict, basis, lang=body.get("lang", "zh"),
                )
            except Exception as exc:
                return self._json({"error": f"{type(exc).__name__}: {exc}"}, 502)
            import datetime
            store.save_check({
                "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
                "kind": "check",
                "student_id": body.get("student_id", ""),
                "figure_id": fig["id"], "figure": fig.get("name", ""),
                "claim": claim, "verdict": verdict, "basis": basis, "result": result,
            })
            return self._json({"result": result})

        return self._json({"error": "not found"}, 404)

    # ---------- DELETE ----------
    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/api/figures/"):
            ok = store.delete_figure(path.rsplit("/", 1)[-1])
            return self._json({"deleted": ok})
        return self._json({"error": "not found"}, 404)


def main(host="127.0.0.1", port=8777):
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"AI 历史人物模拟器 Demo 运行中 → http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
