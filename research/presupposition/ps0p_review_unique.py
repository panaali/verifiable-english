#!/usr/bin/env python3
"""PS-0p post-review, parser only; NEVER counted. Is the uniqueness shape (u0002, u0235) writable once a wording is?

With the sort noun "thing" and a lint-clean unary stand-in (`open_problem`, "{0} is unsolved"; ps0p_review R2), the
plan's uniqueness sentence shape and a few plain variants are parsed, and VE's own rendering of the uniqueness formula
is recorded. No `ve` command runs. Writes docs/research/evidence/presupposition/review-uniqueness.json.

    prlimit --as=6442450944 uv run python research/presupposition/ps0p_review_unique.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ps0p_review", HERE / "ps0p_review.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

SENTENCES = [
    "Some thing is unsolved, and every thing that is unsolved is that thing.",
    "Some thing is unsolved, and every thing that is unsolved is the same as that thing.",
    "Exactly one thing is unsolved.",
    "There is exactly one thing that is unsolved.",
    "There is a thing that is unsolved, and every thing that is unsolved is that thing.",
]


def main() -> int:
    r.d.require_cap()
    meta, _body = r.d.split(r.d.RUN / "translation.ve.md")
    m = r.with_predicate(r.with_noun(meta, "thing"), "open_problem", 1, "{0} is unsolved", False)
    env = r.Environment.from_dict(m["environment"])
    target = r.formula("open_problem", 1, None, True)
    rendered = r.render_english(r.formula_from_data(env, target), env) + "."
    out = {"never_counted": True, "stand_in": {"open_problem": "{0} is unsolved"}, "sort_noun": "thing",
           "uniqueness_formula": target, "rendered_by_ve": rendered, "sentences": {}}
    for s in SENTENCES + [rendered]:
        p = r.parse(env, s)
        if "formulas" in p:
            p["is_existence_and_uniqueness"] = p["formulas"] == [target]
        out["sentences"][s] = p
    out["limits"] = r.d.limits()
    (r.d.OUT / "review-uniqueness.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(rendered)
    for s, p in out["sentences"].items():
        print("OK " if p.get("is_existence_and_uniqueness") else "NO ", s.replace("\n", " / ")[:160],
              p.get("error", "")[:120])
    return 0


if __name__ == "__main__":
    sys.exit(main())
