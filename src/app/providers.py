# -*- coding: utf-8 -*-
"""LLM 接口适配：把不同厂商的 API 统一成一次 chat 调用。

密钥只随请求从浏览器传来，不在服务端落盘（遵循 AGENTS.md §8）。
"""
import json
import urllib.request

PROVIDERS = [
    {
        "id": "mock",
        "label": "离线演示（无需 API）",
        "kind": "mock",
        "default_base_url": "",
        "default_model": "demo",
        "need_key": False,
    },
    {
        "id": "openai",
        "label": "OpenAI 兼容（OpenAI / DeepSeek / 通义 / 智谱 …）",
        "kind": "openai",
        "default_base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "need_key": True,
    },
    {
        "id": "ollama",
        "label": "本地 Ollama",
        "kind": "openai",
        "default_base_url": "http://localhost:11434/v1",
        "default_model": "qwen2.5:7b",
        "need_key": False,
    },
    {
        "id": "anthropic",
        "label": "Anthropic Claude",
        "kind": "anthropic",
        "default_base_url": "https://api.anthropic.com",
        "default_model": "claude-3-5-sonnet-latest",
        "need_key": True,
    },
]

PUBLIC_PROVIDERS = [
    {k: p[k] for k in ("id", "label", "default_base_url", "default_model", "need_key")}
    for p in PROVIDERS
]


def _post_json(url, payload, headers, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def chat(provider_id, base_url, api_key, model, system, messages, figure_name=""):
    spec = next((p for p in PROVIDERS if p["id"] == provider_id), None)
    if spec is None:
        raise ValueError(f"未知 API 接口：{provider_id}")

    kind = spec["kind"]
    base_url = (base_url or spec["default_base_url"] or "").rstrip("/")
    model = model or spec["default_model"]

    if kind == "mock":
        last = messages[-1]["content"] if messages else "……"
        name = figure_name or "历史人物"
        return (
            f"（离线演示模式）我是{name}。你问：「{last}」。\n"
            "当前未接入真实模型，这是一条模拟回复。"
            "请在对话框下方选择 API 接口、填入密钥后重试。"
        )

    if kind == "openai":
        url = f"{base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system}, *messages],
            "temperature": 0.8,
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        data = _post_json(url, payload, headers)
        return (data["choices"][0]["message"]["content"] or "").strip()

    if kind == "anthropic":
        url = f"{base_url}/v1/messages"
        payload = {"model": model, "max_tokens": 800, "system": system, "messages": messages}
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key or "",
            "anthropic-version": "2023-06-01",
        }
        data = _post_json(url, payload, headers)
        return "".join(b.get("text", "") for b in data.get("content", [])).strip()

    raise ValueError(f"未实现的接口类型：{kind}")
