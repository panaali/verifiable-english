#!/usr/bin/env python3
"""Joint native chat counts: OpenRouter wire JSON stdin, integer stdout.

Only tokenizer downloads use the network; no inference/provider APIs are used.
Pinned public assets and upstream identity evidence live in tokenizers/sources.json.
The served provider's template must still agree in the preflight smoke check.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import httpx
from jinja2.sandbox import ImmutableSandboxedEnvironment
from tokenizers import Tokenizer

HERE = Path(__file__).resolve().parent
CACHE = HERE.parents[1] / ".cache/p1-tokenizers"
LLAMA = "meta-llama/llama-3.1-8b-instruct"
QWEN = "qwen/qwen-2.5-72b-instruct"
QWEN_DEFAULT_SYSTEM = "{{- '<|im_start|>system\\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\\n' }}"
LLAMA_DATE_TEMPLATE = ('{{- "Cutting Knowledge Date: December 2023\\n" }}\n'
                       '{{- "Today Date: " + date_string + "\\n\\n" }}')


def verify_blob(data, expected):
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if actual != expected:
        raise ValueError("pinned native tokenizer asset hash mismatch")
    return data


def tokenizer_bytes(spec, cache, *, cached_only=False):
    path = cache / (spec["git_blob_sha1"] + ".json")
    if path.exists():
        return verify_blob(path.read_bytes(), spec["git_blob_sha1"])
    if cached_only:
        raise ValueError("pinned native tokenizer not cached; downloads forbidden")
    url = f'https://huggingface.co/{spec["repo"]}/resolve/{spec["revision"]}/tokenizer.json'
    response = httpx.get(url, follow_redirects=True, timeout=120)
    response.raise_for_status()
    data = verify_blob(response.content, spec["git_blob_sha1"])
    cache.mkdir(parents=True, exist_ok=True)
    # Atomic cache publication; parallel counters may download the same pinned bytes.
    import tempfile
    with tempfile.NamedTemporaryFile(dir=cache, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)
    return data


def raise_exception(message):
    raise ValueError(message)


def chat_text(wire, config):
    """Render the native template, including tools and generation header.

    Match HF's tojson filter (no HTML escaping, Unicode preserved). OpenAI wire
    argument strings are parsed to objects as required by HF chat templates.
    For Llama text-only requests, omit the HF-injected date header: this exactly
    reconciles the retained DeepInfra smoke (21 tokens, versus HF's 41). Tool
    requests retain the pinned upstream template; the smoke does not establish
    their served formatting. Never remove date-like text from message content.
    For Qwen text-only requests without a system message, omit HF's default
    system message: retained P5 DeepInfra usage is 17, versus HF's 38. Explicit
    system messages and tool templates remain intact. response_format and
    max_tokens are generation controls, not text added to the chat template.
    """
    messages = deepcopy(wire["messages"])
    if not messages:
        raise ValueError("empty conversation")
    for message in messages:
        if message.get("role") not in ("system", "user", "assistant", "tool"):
            raise ValueError("unsupported chat role")
        if message.get("content") is None and message.get("tool_calls"):
            message["content"] = ""
        if not isinstance(message.get("content"), str):
            raise ValueError("only text chat content is supported")
        for call in message.get("tool_calls", []):
            function = call["function"]
            if isinstance(function["arguments"], str):
                function["arguments"] = json.loads(function["arguments"])
            if not isinstance(function["arguments"], dict):
                raise ValueError("tool arguments must be a JSON object")
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True,
                                       extensions=["jinja2.ext.loopcontrols"])
    env.filters["tojson"] = lambda value, **kw: json.dumps(value, ensure_ascii=False, **kw)
    env.globals["raise_exception"] = raise_exception
    special = {k: v for k, v in config.items() if k.endswith("_token") and isinstance(v, str)}
    template = config["chat_template"]
    if wire.get("model") == QWEN and not wire.get("tools") and messages[0]["role"] != "system":
        if template.count(QWEN_DEFAULT_SYSTEM) != 1:
            raise ValueError("unrecognized Qwen default system template; panel blocked")
        template = template.replace(QWEN_DEFAULT_SYSTEM, "")
    if wire.get("model") == LLAMA and not wire.get("tools"):
        if template.count(LLAMA_DATE_TEMPLATE) != 1:
            raise ValueError("unrecognized Llama date template; panel blocked")
        template = template.replace(LLAMA_DATE_TEMPLATE, "")
    return env.from_string(template).render(
        messages=messages, tools=wire.get("tools") or None,
        add_generation_prompt=True, **special)


class NativeCounter:
    def __init__(self, cache=CACHE, *, cached_only=False):
        self.cache = Path(cache)
        self.cached_only = cached_only
        self.sources = json.loads((HERE / "tokenizers/sources.json").read_text())
        self.loaded = {}

    def __call__(self, wire):
        model = wire["model"]
        if model not in self.sources:
            raise ValueError(f"no verified native tokenizer for {model}; panel blocked")
        if model not in self.loaded:
            spec = self.sources[model]
            config = verify_blob((HERE / "tokenizers" / spec["config_file"]).read_bytes(),
                                 spec["files"]["tokenizer_config.json"]["git_blob_sha1"])
            tokenizer = Tokenizer.from_str(tokenizer_bytes(spec["files"]["tokenizer.json"], self.cache,
                                                          cached_only=self.cached_only).decode())
            tokenizer.no_truncation()
            tokenizer.no_padding()
            self.loaded[model] = tokenizer, json.loads(config)
        tokenizer, config = self.loaded[model]
        # The template already supplies every special token. Encode the entire
        # rendered conversation once, never a sum of independently encoded fields.
        return len(tokenizer.encode(chat_text(wire, config), add_special_tokens=False).ids)


def main():
    try:
        print(NativeCounter()(json.load(sys.stdin)))
        return 0
    except Exception as exc:
        print(f"native counter blocked: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
