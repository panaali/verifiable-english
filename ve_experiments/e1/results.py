"""Compose experiments/E1/RESULTS.md: `uv run python -m ve_experiments.e1.results <split> <run> <e1b run> <out.md> [units]`.

The preregistered analysis (analysis.report) plus the descriptive breakdowns the PREREG promises: by attack family,
by direction, without the empty-sort-only attacks; exclusions; truncation and failure counts; covariates.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from ..runner import load_trials
from ..stats import rate
from .analysis import PRIMARY, PRIMARY_2, report, with_template
from .pilot import E1, load_candidates


def breakdowns(split: str, run_name: str) -> list[str]:
    rows = with_template(load_trials(E1 / "runs" / run_name), split)
    cands = {c["id"]: c for c in load_candidates(name=split)}
    cells = [PRIMARY[1], PRIMARY[0], PRIMARY_2[1], PRIMARY_2[0]]
    out = ["## Descriptive breakdowns of false approval in the co-primary cells (no intervals, no decisions)", ""]
    groupings = {
        "attack family": lambda c: c.get("family_of_attack"),
        "direction (oracle)": lambda c: c.get("direction"),
        "empty-sort-only attack": lambda c: "only when a sort is empty" if c.get("oracle_empty_sorts_only") else "also with inhabited sorts",
    }
    for title, key in groupings.items():
        out += [f"### By {title}", "", "| judge | group | n | " + " | ".join(cells) + " |", "|---|---|---|" + "---|" * len(cells)]
        for j in sorted({r["judge"] for r in rows}):
            for g in sorted({key(c) for c in cands.values() if c["label"] == "bad"}, key=str):
                sub = [r for r in rows if r["label"] == "bad" and key(cands[r["item_id"]]) == g]
                vals = [rate(sub, "false_approval", c, j) for c in cells]
                out.append(f"| {j} | {g} | {vals[0].denominator} | " + " | ".join(f"{v.value:.3f}" for v in vals) + " |")
        out.append("")
    return out


def housekeeping(split: str, run_name: str, e1b_name: str, units: str) -> list[str]:
    rows = load_trials(E1 / "runs" / run_name)
    e1b = load_trials(E1 / "runs" / e1b_name)
    cands = load_candidates(name=split)
    rej = [json.loads(x) for x in (E1 / "items" / f"{split}.rejected.jsonl").read_text(encoding="utf-8").splitlines()]
    reasons = Counter((r["kind"].split(":")[0], r["reason"].split(":")[0][:40]) for r in rej)
    man = json.loads((E1 / "runs" / run_name / "manifest.json").read_text())
    out = ["## Exclusions, failures, provenance", "",
           f"- Candidates judged: {len({r['item_id'] for r in rows})} of {len(cands)} built "
           f"({sum(c['label'] == 'good' for c in cands)} good, {sum(c['label'] == 'bad' for c in cands)} bad); candidates without an "
           f"explanation: {sum(not c.get('explanation') for c in cands)}.",
           "- Excluded before any judge call (kind, reason: count): " + "; ".join(f"{k} {r}: {n}" for (k, r), n in sorted(reasons.items())) + ".",
           "- No trial was excluded."]  # fmt: skip
    for name, rs in (("E1", rows), ("E1b", e1b)):
        for j in sorted({r["judge"] for r in rs}):
            mine = [r for r in rs if r["judge"] == j]
            out.append(f"- {name}, {j}: {len(mine)} trials; failed calls {sum(not r['ok'] for r in mine)}, truncated "
                       f"{sum(bool(r.get('truncated')) for r in mine)}, tool use {sum(bool(r.get('tool_events')) for r in mine)}, "
                       f"no valid verdict in total {sum(r['verdict'] is None for r in mine)} (all scored as the worst case).")  # fmt: skip
    out += [f"- PREREG: commit {man.get('prereg_commit')}, blob {man.get('prereg_blob')}; run at git {man.get('git_head')}.",
            f"- Compute: {units}", ""]
    cov = E1 / f"COVARIATES-{split}.md"
    if cov.exists():
        out += ["## Covariates", "", *cov.read_text(encoding="utf-8").splitlines()[1:], ""]
    return out


def main() -> None:
    split, run_name, e1b_name, dest = sys.argv[1:5]
    units = sys.argv[5] if len(sys.argv) > 5 else "not recorded"
    text = report(split, run_name, e1b_name) + "\n" + "\n".join(breakdowns(split, run_name) + housekeeping(split, run_name, e1b_name, units))
    Path(dest).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
