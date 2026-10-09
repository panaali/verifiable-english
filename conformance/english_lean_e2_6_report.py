"""E2.6: the measured section of `docs/lean-first/e2/E2.6.md`, rendered from the saved evidence alone.

    .venv/bin/python -m conformance.english_lean_e2_6_report --write

Every number of the section comes from `docs/lean-first/e2/evidence/e2.6/` (the readability comparison, the A/B
summary, the commit list of `main..HEAD --no-merges`, the seeded mutants) and from the gate result
`conformance/english-lean/e26-gate-result.json` when it is there. `tests/test_english_e26_report.py` checks that the
committed section is this rendering.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
E26 = ROOT / "docs/lean-first/e2/evidence/e2.6"
REPORT = ROOT / "docs/lean-first/e2/E2.6.md"
GATE = ROOT / "conformance/english-lean/e26-gate-result.json"
BEGIN = "<!-- BEGIN GENERATED: python -m conformance.english_lean_e2_6_report --write -->\n"
END = "<!-- END GENERATED -->\n"


def load(name):
    return json.loads((E26 / name).read_text())


def render() -> str:
    readability = load("readability-comparison.json")
    ab = load("ab-summary.json")["summary"]
    commits = load("commits.json")
    mutants = load("mutants.json")["mutants"]
    rules = __import__("conformance.english_lean_e2_ab", fromlist=["RULES"]).RULES
    lines = [BEGIN, "### Readability (spec 2.10)", "",
             f"Writing: **{readability['writing_attempts']}** attempts; **{readability['writing_outcome_changes']}** "
             f"changed outcomes; **{readability['writing_message_changes']}** changed messages, "
             f"**{readability['writing_preserved_changes']}** keeping every base name, location and suggestion; "
             f"regressions **{len(readability['writing_regressions'])}**. Reading: **{readability['reading_items']}** "
             f"items; unavailable **{len(readability['reading_unavailable'])}**; differences from the base "
             f"**{len(readability['reading_differences'])}**; answered by Lean directly: "
             f"{', '.join(readability['lean_reading_items'])}.", "",
             "### Corpus A/B (GE2 item 3)", "",
             f"**{ab['records_per_side']:,}** records per side. Base `{ab['base']}` to head: "
             + ", ".join(f"{k} {v:,}" for k, v in ab["base_head"].items())
             + f". Unexplained verdict or availability rows: **{ab['unexplained']}**; availability rows: "
             f"**{ab['availability']}**.", "",
             "| Verdict rule | Rows | Disposition |", "|---|---:|---|"]
    lines += [f"| `{k}` | {v} | {rules[k][0]} |" for k, v in ab["verdict_rules"].items()]
    e26 = ab["e26"]
    lines += ["", f"Wording and order rows: **{ab['wording_order_rows']}**; keeping the base's names and locations "
              f"**{ab['text_rows_kept_total']}**; listed for the DRI **{ab['text_rows_for_dri_total']}** (by rule in "
              "[ab-dispositions.md](evidence/e2.6/ab-dispositions.md)).", "",
              f"Main `{ab['main']}` to head (E2.6's own rows): "
              + ", ".join(f"{k} {v:,}" for k, v in ab["main_head"].items())
              + f"; by rule {', '.join(f'`{k}` {v}' for k, v in e26['rules'].items())}; wording rows losing a name "
              f"or location **{e26['wording_not_kept']}**; documents gained **{e26['availability_gained']}**, lost "
              f"**{e26['availability_lost']}**; DRI rows changed **{e26['dri_rows_changed_by_e26']}**.", "",
              f"### Commits (`{commits['range']}`)", "", "| Commit | Subject |", "|---|---|"]
    lines += [f"| `{c['commit']}` | {c['subject']} |" for c in commits["commits"]]
    lines += ["", f"### Seeded mutants ({len(mutants)})", "", "| Id | Behaviour | Mutation | Failed |", "|---|---|---|---|"]
    lines += [f"| {m['id']} | {m['behaviour']} | `{m['file']}`: {m['change']} | "
              f"{'; '.join('`' + t + '`' for t in m['failed'])} |" for m in mutants]
    lines += ["", "### Gate", ""]
    if GATE.exists():
        gate = json.loads(GATE.read_text())
        counts = gate["counts"]
        lines.append(f"Status **{gate['status']}** on `{gate['commit_sha'][:8]}` (clean: {not gate['dirty']}): "
                     f"**{counts.get('passed', 0):,}** Python tests passed, **{counts.get('skipped', 0)}** skipped, "
                     f"**{counts.get('failed', 0)}** failed; **{counts.get('rust_passed', 0)}** Rust tests passed; "
                     f"failures recorded: {len(gate['failures'])}.")
    else:
        lines.append("Not run.")
    return "\n".join(lines) + "\n" + END


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    text = REPORT.read_text()
    start, stop = text.index(BEGIN), text.index(END) + len(END)
    rendered = render()
    if args.write:
        REPORT.write_text(text[:start] + rendered + text[stop:])
    elif text[start:stop] != rendered:
        print("the committed section is not the rendering; run --write", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
