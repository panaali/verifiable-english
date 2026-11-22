"""Writes results.json: what parse_w6_sentence does with each writer sentence (outcome() in
tests/test_relb_f1f2_grammar.py). Run from the repository root:
    .venv/bin/python -B tests/fixtures/relb_f1f2/ten_sentences/record_results.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import test_relb_f1f2_grammar as t  # noqa: E402
from ve.environment import Environment  # noqa: E402

env = Environment(t.RAW)
got = {str(c["n"]): t.outcome(env, c, s) for c, s in t.ten_sentences()}
(Path(__file__).resolve().parent / "results.json").write_text(
    json.dumps(got, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
for n, row in got.items():
    print(n, row["rule"], row["outcome"], row["equals_rule"], row["reason"], row["spans_read_alone"])
