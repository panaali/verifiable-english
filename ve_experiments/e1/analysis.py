"""E1 analysis as preregistered: `uv run python -m ve_experiments.e1.analysis <split> <run dir name> [<e1b run dir name>] [out.md]`.

Per judge: false approval and honest acceptance per cell (worst case for failures), the primary and secondary
contrasts. PRIMARY interval: cluster-t over semantic templates (mean of the per-template differences, t with G-1
degrees of freedom). Secondary: pooled difference with a percentile bootstrap that resamples templates. Incomplete
pairing between two cells is an error. E1b per view.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from ..runner import load_trials
from ..stats import cluster_t_contrast, paired_contrast, rate
from .pilot import E1, load_candidates
from .views import VIEWS

PRIMARY = ("ve_strict|attacker", "fol_symbols|attacker")  # co-primary P1
PRIMARY_2 = ("ve_strict|none", "fol_symbols|none")  # co-primary P2
CO_PRIMARY_ALPHA = 0.025  # Bonferroni over P1 and P2: 97.5% cluster-t intervals
SECONDARY = [
    ("ve_strict|attacker", "fol_keywords|attacker"),
    ("ve_natural|attacker", "fol_symbols|attacker"),
    ("ve_fluent|attacker", "fol_symbols|attacker"),
    ("fol_keywords|attacker", "fol_symbols|attacker"),
    ("fol_keywords|none", "fol_symbols|none"),
    ("ve_natural|none", "fol_symbols|none"),
    ("ve_fluent|none", "fol_symbols|none"),
    *[(f"{v}|attacker", f"{v}|none") for v in VIEWS],
]
N_BOOT = 10_000


def with_template(rows: list[dict], split: str) -> list[dict]:
    """Rows written before the runner persisted `template` get it from the item file; new rows carry it."""
    if all("template" in r for r in rows):
        return rows
    tmpl = {c["id"]: c["template"] for c in load_candidates(name=split)}
    return [{**r, "template": r.get("template") or tmpl[r["item_id"]]} for r in rows]


def _r(x) -> str:
    return f"{x.value:.3f} ({x.numerator}/{x.denominator})"


def report(split: str, run_name: str, e1b_name: str | None = None) -> str:
    rows = with_template(load_trials(E1 / "runs" / run_name), split)
    judges = sorted({r["judge"] for r in rows})
    cells = [f"{v}|{e}" for e in ("none", "attacker") for v in VIEWS]
    n_t = len({r["template"] for r in rows})
    out = [f"# E1 `{split}` results, run `{run_name}`", "",
           f"{len(rows)} trials, {len({r['item_id'] for r in rows})} candidates, {n_t} templates. Failures (failed call, "
           "unparseable, truncated, tool use) are scored as the worst case. Contrasts: `t` = mean of per-template "
           "differences with a cluster-t interval (primary method; 97.5% for the two co-primary contrasts, 95% otherwise); `pooled` = difference of pooled rates with a 95% "
           f"percentile bootstrap over templates, {N_BOOT} resamples, seed 0 (secondary method).", ""]  # fmt: skip
    out += ["## Rates per judge and cell", "", "| judge | cell | false approval | honest acceptance | failures | truncated |", "|---|---|---|---|---|---|"]
    for j in judges:
        for c in cells:
            mine = [r for r in rows if r["judge"] == j and r["condition"] == c]
            fails, trunc = sum(r["approved"] is None for r in mine), sum(bool(r.get("truncated")) for r in mine)
            out.append(f"| {j} | {c} | {_r(rate(rows, 'false_approval', c, j))} | {_r(rate(rows, 'honest_acceptance', c, j))} | {fails} | {trunc} |")
    out += ["", "## Contrasts (a - b)", "", "| judge | metric | a | b | t diff | t 95% CI | pooled diff | bootstrap 95% CI | role |", "|---|---|---|---|---|---|---|---|---|"]
    for j in judges:
        for metric in ("false_approval", "honest_acceptance"):
            for a, b in [PRIMARY, PRIMARY_2, *SECONDARY]:
                co = (a, b) in (PRIMARY, PRIMARY_2)
                c = paired_contrast(rows, metric, a, b, j, N_BOOT, 0, cluster="template")
                t = cluster_t_contrast(rows, metric, a, b, j, "template", alpha=CO_PRIMARY_ALPHA if co else 0.05)
                name = "P1" if (a, b) == PRIMARY else "P2"
                role = (f"co-primary {name} (97.5% t interval; primary judge only)" if co and metric == "false_approval"
                        else f"constraint for {name} (97.5% t interval)" if co else "secondary")
                out.append(f"| {j} | {metric} | {a} | {b} | {t.diff:+.3f} | [{t.ci_low:+.3f}, {t.ci_high:+.3f}] | {c.diff:+.3f} | [{c.ci_low:+.3f}, {c.ci_high:+.3f}] | {role} |")
    out += ["", "## Per-template differences of the primary contrast (false approval)", "",
            "| judge | per-template differences | SD between templates | SE with 12 templates | 95% half-width with 12 (t, 11 df) |", "|---|---|---|---|---|"]  # fmt: skip
    for j in judges:
        t = cluster_t_contrast(rows, "false_approval", *PRIMARY, j, "template")
        out.append(f"| {j} | " + ", ".join(f"{k[:3]}: {v:+.3f}" for k, v in t.per_cluster.items()) + f" | {t.sd:.3f} | {t.sd / 12 ** 0.5:.3f} | {2.201 * t.sd / 12 ** 0.5:.3f} |")
    if e1b_name:
        e1b = [json.loads(x) for x in (E1 / "runs" / e1b_name / "trials.jsonl").read_text(encoding="utf-8").splitlines()]
        e1b = [{**r, "view": r.get("view") or r["condition"]} for r in e1b]
        out += ["", "## E1b comprehension: fraction of situations judged correctly (chance 0.50; failures score 0)", "",
                "| judge | " + " | ".join(VIEWS) + " | failures |", "|---|" + "---|" * (len(VIEWS) + 1)]  # fmt: skip
        for j in sorted({r["judge"] for r in e1b}):
            cols = []
            for v in VIEWS:
                sub = [r for r in e1b if r["judge"] == j and r["view"] == v]
                cols.append(f"{sum(r['correct_of_2'] for r in sub) / (2 * len(sub)):.3f}")
            out.append(f"| {j} | " + " | ".join(cols) + f" | {sum(r['answer'] is None for r in e1b if r['judge'] == j)} |")
    return "\n".join(out) + "\n"


def main() -> None:
    split, run_name = sys.argv[1:3]
    e1b = sys.argv[3] if len(sys.argv) > 3 else None
    text = report(split, run_name, e1b)
    dest = Path(sys.argv[4]) if len(sys.argv) > 4 else E1 / f"RESULTS-{run_name}.md"
    dest.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
