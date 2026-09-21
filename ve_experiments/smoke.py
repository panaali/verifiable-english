"""Live smoke test of the model client: `uv run python -m ve_experiments.smoke [model ...]`.

Makes one tiny real call per model (then a second, cached one) and checks strict verdict parsing.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from .llm import LLMClient, Request, parse_verdict

DEFAULT_MODELS = ("claude-haiku-4-5-20251001", "gpt-5.6-luna")
PROMPT = (
    "Claim: every even number greater than 2 is prime.\n"
    "Decide whether the claim is true. Reply with one short sentence, then end your reply with a JSON object\n"
    'on its own line: {"verdict": "approve"} if the claim is true, {"verdict": "reject"} if it is false.'
)


def main(models: list[str]) -> int:
    with tempfile.TemporaryDirectory(prefix="ve-smoke-") as tmp:
        client = LLMClient(cache_dir=Path(tmp), retries=2, timeout_s=120)
        first = client.map(Request(m, PROMPT, tag="smoke") for m in models)
        second = client.map(Request(m, PROMPT, tag="smoke") for m in models)
        failed = 0
        for a, b in zip(first, second):
            try:
                verdict = parse_verdict(a.text).value
            except ValueError as exc:
                verdict = f"PARSE ERROR: {exc}"
            ok = a.ok and verdict == "reject" and b.from_cache and b.text == a.text
            failed += not ok
            print(
                f"{'PASS' if ok else 'FAIL'} {a.model}: verdict={verdict} latency={a.latency_s}s attempts={a.attempts} "
                f"tokens in/out={a.input_tokens}/{a.output_tokens} cached_replay={b.from_cache} error={a.error}"
            )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or list(DEFAULT_MODELS)))
