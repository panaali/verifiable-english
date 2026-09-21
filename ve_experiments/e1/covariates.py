"""Per-view length covariates and the ve_fluent contraction rate on real items:
`uv run python -m ve_experiments.e1.covariates dev`."""

from __future__ import annotations

import re
import statistics as st
import sys

from .pilot import E1, load_candidates
from .views import VIEWS, render

TOKEN = re.compile(r"\w+|[^\w\s]")
GUARD = re.compile(r"for every \w+ \w+ (that|such that) ")


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "dev"
    cands = load_candidates(name=name)
    lines = [f"# View covariates on `{name}` ({len(cands)} candidates)", "",
             "Tokens are `\\w+|[^\\w\\s]` matches (words and single symbols), not model tokens.", "",
             "| view | mean chars | median chars | mean tokens | median tokens |", "|---|---|---|---|---|"]  # fmt: skip
    texts = {v: [render(c["environment"], c["ast"], v) for c in cands] for v in VIEWS}
    for v in VIEWS:
        chars, toks = [len(t) for t in texts[v]], [len(TOKEN.findall(t)) for t in texts[v]]
        lines.append(f"| {v} | {st.mean(chars):.1f} | {st.median(chars):.0f} | {st.mean(toks):.1f} | {st.median(toks):.0f} |")
    fl = texts["ve_fluent"]
    guard = sum(bool(GUARD.search(t)) for t in fl)
    explicit = sum(("if (" in t) or ("such that (both" in t) for t in fl)
    lines += ["", "## ve_fluent contraction", "",
              f"- {guard}/{len(fl)} ({guard / len(fl):.0%}) use a relative-clause guard on a universal (`for every N V that ...` or `such that ...`).",
              f"- {explicit}/{len(fl)} ({explicit / len(fl):.0%}) contain an uncontracted `if (...)` or `such that (both ...)`.",
              "- By label: " + "; ".join(
                  f"{lab}: guard {sum(bool(GUARD.search(t)) for t, c in zip(fl, cands) if c['label'] == lab)}/{sum(c['label'] == lab for c in cands)}"
                  for lab in ("good", "bad"))]  # fmt: skip
    text = "\n".join(lines) + "\n"
    (E1 / f"COVARIATES-{name}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
