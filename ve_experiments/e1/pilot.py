"""Dev-split pilot: `uv run python -m ve_experiments.e1.pilot [gate|cells|e1b|report] ...`.

gate    fol_symbols|none for the two weak judges and the two strong models (capability gap, and raw-FOL
        false approval per attack family)
cells   the primary and secondary cells for the weak judges (variance for the sample-size calculation)
e1b     comprehension control on the faithful and attacked ASTs, all four views, weak judges
report  writes experiments/E1/PILOT.md from the run directories

Only the dev split is ever touched here.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from ..llm import LLMClient, Request, VerdictParseError, parse_verdict
from ..runner import Experiment, Item, load_trials, run
from ..stats import bootstrap_rate, paired_contrast, rate
from .prompts import E1B_ANSWERS, cell_name, conditions, e1b_prompt
from .views import VIEWS

ROOT = Path(__file__).resolve().parents[2]
E1 = ROOT / "experiments" / "E1"
WEAK = ("claude-haiku-4-5-20251001", "gpt-5.6-luna")
STRONG = ("claude-fable-5-1", "gpt-6-astra")
HIDDEN = ("kind", "family_of_attack", "direction", "distinguishing_model", "explanation_author", "template", "family",
          "binding", "e1b_truth", "distinguishing_model_nonvacuous", "verbalisation")  # fmt: skip


def load_candidates(split: str = "dev", name: str | None = None) -> list[dict]:
    path = E1 / "items" / f"{name or split}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def to_items(cands: list[dict]) -> list[Item]:
    items = []
    for c in cands:
        payload = {("_" + k if k in HIDDEN else k): v for k, v in c.items() if k not in ("id", "group", "label", "split")}
        items.append(Item(id=c["id"], label=c["label"], payload=payload, group=c["group"], split=c["split"]))
    return items


def experiment(cands: list[dict], views, explanations, judges) -> Experiment:
    usable = [c for c in cands if c.get("explanation")]  # generation failures are excluded before judging, and counted
    return Experiment("E1", to_items(usable), conditions(views, explanations), list(judges), root=ROOT,
                      split_file=E1 / "splits.json")


def run_gate(client: LLMClient, items_name: str) -> Path:
    exp = experiment(load_candidates(name=items_name), ("fol_symbols",), ("none",), WEAK + STRONG)
    return run(exp, client, "dev", out_dir=E1 / "runs" / f"pilot-gate-{items_name}")


def run_cells(client: LLMClient, items_name: str) -> Path:
    exp = experiment(load_candidates(name=items_name), ("fol_symbols", "ve_strict"), ("none", "attacker"), WEAK)
    return run(exp, client, "dev", out_dir=E1 / "runs" / f"pilot-cells-{items_name}")


def run_e1b(client: LLMClient, items_name: str, judges=WEAK) -> Path:
    cands = [c for c in load_candidates(name=items_name) if c["split"] == "dev"]
    reqs, meta = [], []
    for c in cands:
        for view in VIEWS:
            for j in judges:
                reqs.append(Request(j, e1b_prompt(c, view), tag=f"E1b/dev/{c['id']}/{view}"))
                meta.append((c, view, j))
    out = E1 / "runs" / f"pilot-e1b-{items_name}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "trials.jsonl", "w", encoding="utf-8") as fh:
        for (c, view, j), res in zip(meta, client.map(reqs)):
            truth = "".join("T" if t else "F" for t in c["e1b_truth"])
            try:
                answer = parse_verdict(res.text, allowed=E1B_ANSWERS).value
            except VerdictParseError:
                answer = None
            correct = 0 if answer is None else sum(a == t for a, t in zip(answer, truth))  # failures score 0 of 2
            fh.write(json.dumps({"item_id": c["id"], "group": c["group"], "view": view, "judge": j, "truth": truth,
                                 "answer": answer, "correct_of_2": correct, "ok": res.ok, "reply": res.text}) + "\n")  # fmt: skip
    return out


# --------------------------------------------------------------------------- report


def _fmt(r) -> str:
    if r.value is None:
        return "n/a"
    ci = f" [{r.ci_low:.2f}, {r.ci_high:.2f}]" if r.ci_low is not None else ""
    return f"{r.value:.2f}{ci} ({r.numerator}/{r.denominator})"


def report(items_name: str) -> str:
    cands = {c["id"]: c for c in load_candidates(name=items_name)}
    lines = [f"# E1 dev pilot ({items_name})", "",
             "Dev split only. Intervals are 95% percentile bootstraps over base items (template x binding); with 16 "
             "base items from 4 templates they are rough. Unparseable or failed trials are scored as the worst case.", ""]  # fmt: skip
    from collections import Counter

    kinds = Counter((c["label"], c.get("family_of_attack", "faithful")) for c in cands.values())
    lines += ["## Candidates", "", "| label | kind | n | with explanation |", "|---|---|---|---|"]
    for (label, kind), n in sorted(kinds.items()):
        have = sum(1 for c in cands.values() if (c["label"], c.get("family_of_attack", "faithful")) == (label, kind) and c.get("explanation"))
        lines.append(f"| {label} | {kind} | {n} | {have} |")
    words = defaultdict(list)
    for c in cands.values():
        if c.get("explanation"):
            words[c["label"]].append(len(c["explanation"].split()))
    lines += ["", "Explanation length in words, mean (min-max): " + "; ".join(
        f"{k}: {sum(v) / len(v):.1f} ({min(v)}-{max(v)})" for k, v in sorted(words.items()))]  # fmt: skip

    gate_dir = E1 / "runs" / f"pilot-gate-{items_name}"
    if (gate_dir / "trials.jsonl").exists():
        rows = load_trials(gate_dir)
        cell = cell_name("fol_symbols", "none")
        lines += ["", "## Capability gate: fol_symbols, no explanation", "",
                  "| model | role | accuracy | false approval | honest acceptance | failures |", "|---|---|---|---|---|---|"]  # fmt: skip
        for j in WEAK + STRONG:
            mine = [r for r in rows if r["judge"] == j]
            right = sum((r["approved"] is True and r["label"] == "good") or (r["approved"] is False and r["label"] == "bad") for r in mine)
            fa, ha = bootstrap_rate(rows, "false_approval", cell, j, 2000), bootstrap_rate(rows, "honest_acceptance", cell, j, 2000)
            fails = sum(r["approved"] is None for r in mine)
            lines.append(f"| {j} | {'weak judge' if j in WEAK else 'strong'} | {right / len(mine):.2f} ({right}/{len(mine)}) | {_fmt(fa)} | {_fmt(ha)} | {fails} |")
        lines += ["", "### Raw-FOL false approval by attack family (weak judges)", "",
                  "| attack family | " + " | ".join(WEAK) + " |", "|---|---|---|"]  # fmt: skip
        fams = sorted({cands[r["item_id"]].get("family_of_attack") for r in rows if r["label"] == "bad"})
        for fam in fams:
            cells = []
            for j in WEAK:
                sub = [r for r in rows if r["label"] == "bad" and cands[r["item_id"]].get("family_of_attack") == fam]
                cells.append(_fmt(rate(sub, "false_approval", cell, j)))
            lines.append(f"| {fam} | " + " | ".join(cells) + " |")
        lines += ["", "### Same, for the strong models", "", "| attack family | " + " | ".join(STRONG) + " |", "|---|---|---|"]
        for fam in fams:
            sub = [r for r in rows if r["label"] == "bad" and cands[r["item_id"]].get("family_of_attack") == fam]
            lines.append(f"| {fam} | " + " | ".join(_fmt(rate(sub, "false_approval", cell, j)) for j in STRONG) + " |")
        lines += ["", "### Honest acceptance by faithful form (weak judges)", "", "| form | " + " | ".join(WEAK) + " |", "|---|---|---|"]
        for form in sorted({c["kind"] for c in cands.values() if c["label"] == "good"}):
            sub = [r for r in rows if cands[r["item_id"]]["kind"] == form]
            lines.append(f"| {form} | " + " | ".join(_fmt(rate(sub, "honest_acceptance", cell, j)) for j in WEAK) + " |")

    cells_dir = E1 / "runs" / f"pilot-cells-{items_name}"
    if (cells_dir / "trials.jsonl").exists():
        rows = load_trials(cells_dir)
        names = sorted({r["condition"] for r in rows})
        lines += ["", "## Cells (weak judges)", "", "| judge | cell | false approval | honest acceptance |", "|---|---|---|---|"]
        for j in WEAK:
            for n in names:
                lines.append(f"| {j} | {n} | {_fmt(bootstrap_rate(rows, 'false_approval', n, j, 2000))} | {_fmt(bootstrap_rate(rows, 'honest_acceptance', n, j, 2000))} |")
        lines += ["", "### Paired contrasts (a - b), false approval", "", "| judge | a | b | diff | 95% CI | discordant a-only/b-only |", "|---|---|---|---|---|---|"]
        pairs = [("ve_strict|attacker", "fol_symbols|attacker"), ("ve_strict|none", "fol_symbols|none"),
                 ("fol_symbols|attacker", "fol_symbols|none"), ("ve_strict|attacker", "ve_strict|none")]  # fmt: skip
        for j in WEAK:
            for a, b in pairs:
                c = paired_contrast(rows, "false_approval", a, b, j, 2000)
                lines.append(f"| {j} | {a} | {b} | {c.diff:+.3f} | [{c.ci_low:+.3f}, {c.ci_high:+.3f}] | {c.discordant_a_only}/{c.discordant_b_only} |")

    e1b_dir = E1 / "runs" / f"pilot-e1b-{items_name}"
    if (e1b_dir / "trials.jsonl").exists():
        rows = [json.loads(x) for x in (e1b_dir / "trials.jsonl").read_text().splitlines()]
        lines += ["", "## E1b comprehension (fraction of situations judged correctly; chance = 0.50)", "",
                  "| judge | " + " | ".join(VIEWS) + " |", "|---|" + "---|" * len(VIEWS)]  # fmt: skip
        for j in sorted({r["judge"] for r in rows}):
            cells = []
            for v in VIEWS:
                sub = [r for r in rows if r["judge"] == j and r["view"] == v]
                cells.append(f"{sum(r['correct_of_2'] for r in sub) / (2 * len(sub)):.3f} (n={2 * len(sub)})")
            lines.append(f"| {j} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    what, items_name = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "dev")
    client = LLMClient(timeout_s=600)
    if what == "gate":
        print(run_gate(client, items_name))
    elif what == "cells":
        print(run_cells(client, items_name))
    elif what == "e1b":
        print(run_e1b(client, items_name))
    elif what == "report":
        text = report(items_name)
        (E1 / f"PILOT-{items_name}.md").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
