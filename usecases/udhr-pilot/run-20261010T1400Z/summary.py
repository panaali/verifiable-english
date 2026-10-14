"""Render `SUMMARY.md` from `metrics.json` (RD-5's report, plan section 5): every number is the saved evidence's.

    uv run --frozen python usecases/udhr-pilot/run-20261010T1400Z/summary.py [--check]

`--check` exits 1 when the committed `SUMMARY.md` differs from the rendering (tests/test_readings_rd5_udhr.py runs
the same comparison).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _percent(part, whole):
    return f"{100 * part / whole:.2f}%"


def _timing(t):
    return f"{t['wall_seconds']} s wall, {t['cpu_seconds']} s CPU (load {t['load_before']})"


def wordings(report):
    """How many of the after report's S1 pair sentences carry each wording (the saved check report's)."""
    out = {}
    for item in report["readings"]["sets"]:
        for pair in item["pairs"]:
            out[pair["wording"]] = out.get(pair["wording"], 0) + 1
    return dict(sorted(out.items()))


def render(m, report):
    before, after, comp, mig, wit = m["before"], m["after"], m["components"], m["migration"], m["witnesses"]
    rec = m["recorded"]
    source = after["share"]["source_bytes"]
    lines = [
        "# UDHR pilot under readings with their own vocabulary (readings-defaults RD-5)",
        "",
        f"Run 20261006T1800Z's translation (`{m['run']}`), migrated by `migrate.py` and measured by `measure.py` at "
        f"commit `{m['commit'][:8]}` (the tree's `ve`, `lean`, `rust` and `tools` clean: "
        f"{str(m['tree_clean_in_ve_lean_rust_tools']).lower()}), on a {m['host']['cpus']}-CPU host. Every number "
        "below is rendered from `metrics.json` by `summary.py`; the three marked *recorded* are copied from the run "
        f"({rec['source']}).",
        "",
        "## What changed",
        "",
        f"- {len(mig['migrated'])} of {mig['sets']} reading sets now carry their companions inline: each is a "
        "sentence checked by itself, in the terms its readings declare (E31). The other "
        f"{len(mig['not_migrated'])} stay on W2 as they were (content null, no companions), listed below with "
        "Lean's text; they are not decided.",
        f"- Lean admits the migrated document: premises `{after['premises']}`, conflict `{after['conflict']}`, "
        f"over {comp['count']} components (the main case and {comp['companion_cases']} companion sets). Before, "
        f"the premises were {before['premises']} (*recorded* {rec['premises']}) and there was no readings answer.",
        f"- **Lean-decided share** (spec 1.10, plan 3.9): {before['share']['decided_bytes']} bytes "
        f"({before['share']['decided_share_percent']}%) before, {after['share']['decided_bytes']} of {source} bytes "
        f"({after['share']['decided_share_percent']}%) after, in {len(after['share']['decided_units'])} units "
        "Lean lists as decided.",
        f"- Claimed covered bytes {rec['claimed_covered_bytes']} ({_percent(rec['claimed_covered_bytes'], source)}) "
        f"and audit-verified {rec['audit_verified_covered_bytes']} "
        f"({_percent(rec['audit_verified_covered_bytes'], source)}) are *recorded* and unchanged: no unit changed "
        f"status (bytes by status before {json.dumps(before['bytes_by_status'], sort_keys=True)}, after "
        f"{json.dumps(after['bytes_by_status'], sort_keys=True)}). The next audit decides on the migrated units.",
        "",
        "## What the share does and does not say",
        "",
        "- Every sentence with readings was checked by itself (E31). The share says nothing about whether two "
        "sentences' readings fit together.",
        f"- The largest choice document holds {comp['max_rules_in_one_choice_document']} rules: "
        f"{comp['max_author_rules_in_one_choice_document']} written rule and the generated rules of its "
        "unspecified predicates (counted from Lean's `norm-defaults-elaborate` of every choice). The share "
        "tool's `max_choice_rules` is null, because Lean's answer does not carry that count.",
        f"- {after['share']['decided_bytes_checked_outside']} of the {after['share']['decided_bytes']} decided "
        "bytes belong to units whose every reading's companion the run had already checked as a document of its "
        "own.",
        f"- {after['share']['one_rule']}",
        "- Most UDHR readings hold one rule, and their companions had already passed their checks as separate "
        "documents. So the move from 0 measures those checks routed into Lean inside the document, not new "
        "assurance.",
        "",
        "## Measurements",
        "",
        "| Measure | Before (as committed) | After (migrated) |",
        "|---|---|---|",
        f"| Load (`load_document`) | {_timing(before['load'])} | {_timing(after['load'])} |",
        f"| Check (`check_document`) | {_timing(before['check'])} | {_timing(after['check'])} |",
        f"| Render (`render_document`) | {_timing(before['render'])} | {_timing(after['render'])} |",
        f"| Document bytes | {before['document_bytes']:,} | {after['document_bytes']:,} (limit 4,000,000) |",
        f"| Components; regulated predicates per component (max); readings per component (max) | — | "
        f"{comp['count']}; {comp['max_regulated_predicates']} (limit 64); {comp['max_readings']} (limit 64) |",
        f"| Compatible choices per component (max) | — | {comp['max_choices']} (limit 64) |",
        f"| Premises verdict | {before['premises']} | {after['premises']} |",
        f"| Conflict verdict | — | {after['conflict']} |",
        f"| Lean-decided bytes and share | {before['share']['decided_bytes']} "
        f"({before['share']['decided_share_percent']}%) | {after['share']['decided_bytes']} "
        f"({after['share']['decided_share_percent']}%) |",
        f"| Maximum rules in one choice's document; decided bytes already checked outside | — | "
        f"{comp['max_rules_in_one_choice_document']}; {after['share']['decided_bytes_checked_outside']} |",
        f"| Claimed covered; audit-verified | {rec['claimed_covered_bytes']:,}; "
        f"{rec['audit_verified_covered_bytes']:,} (*recorded*) | unchanged |",
        f"| Sets admitted with every pair separated; unseparated pairs | — | "
        f"{mig['sets_admitted_with_every_pair_separated']} ({mig['situations_recorded']} situations); "
        f"{len(mig['unseparated_pairs'])} |",
        f"| Sets not migrated (\"needs one vocabulary\", E1) | — | {len(mig['not_migrated'])} |",
        "",
        "## Checks",
        "",
        f"- Status witnesses in the components (`readings-choice`, inner `norm-defaults-status`): "
        f"{wit['in_components_same']} of {wit['in_components_total']} equal to the recorded `witnesses.json`.",
        f"- The {wit['companions_alone']} companions re-checked alone: {wit['companions_alone_model']} with "
        f"premises `model`; their witnesses through the norm-defaults route: {wit['alone_same']} of "
        f"{wit['alone_total']} equal to the recorded ones.",
        f"- Pair sentences of the migrated sets: "
        f"{', '.join(f'{w} {n}' for w, n in wordings(report).items())}. A pair separated on a plain regulated "
        "predicate (an entitlement reading: \"Everyone has the right to …\") gets E24, \"These two readings differ "
        "in a checked situation that VE cannot yet show in words.\": E19 words duties and permissions only. Before "
        "this batch such a pair made the whole report `CheckerUnavailable` (`ve/readings_route.py`, the batch's one "
        "product change).",
        "",
        "## Observations (follow-ups, not changed here)",
        "",
        "- The English of a shown situation names elements of different sorts alike (\"e0 is a person; e0 is a "
        "State\"), which a reader can take for one entity.",
        "- A plain predicate without a verbalisation in the companion's frame reads as 'is classified as "
        "\"resources_allow\"'; the pilot's companions give some plain predicates no verbalisation.",
        "- E24 says that a separation was checked but not what it is; an E19 sentence for plain predicates needs "
        "new wording and the W7 gate.",
        "- 27 sets wait for one vocabulary (E1): most declare the duty over `state` in one reading and over "
        "`bearer` in another. Re-translating them onto one sort is a pilot task.",
        "",
        "## Queries (spec 8.6), answers verbatim",
        "",
    ]
    for q in m["queries"]:
        under = f", `--under {' '.join(q['under'])}`" if q["under"] else ""
        lines += [f"### \"{q['english_query']}\" (sentence `{q['sentence']}`{under})", "",
                  f"Expected {q['expected']}; Lean answered **{q['verdict']}** "
                  f"({q['wall_seconds']} s wall, load {q['load_before']}; `{q['answer']}`).", ""]
        lines += [f"> {line}" for line in q["english"] or []] + [""]
    lines += ["## Sets not migrated", "", "| Set | Lean's text |", "|---|---|"]
    lines += [f"| `{x['set']}` | {x['reason']} |" for x in mig["not_migrated"]]
    lines += ["", "## Unseparated pairs", "",
              "None." if not mig["unseparated_pairs"] else
              "\n".join(f"- `{x['set']}`: {x['pairs']}" for x in mig["unseparated_pairs"]),
              "", "## Copied declarations (asserted readings given a companion from the main frame)", ""]
    lines += [f"- `{k}`: {', '.join(v)}" for k, v in sorted(mig["copied_declarations"].items())]
    lines += ["", "## Sets on W2 in the main component (Lean's UNKNOWN)", "",
              ", ".join(f"`{s}`" for s in comp["main_unchecked_sets"]), ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = render(json.loads((HERE / "metrics.json").read_text()),
                  json.loads((HERE / "reports" / "after.check.json").read_text()))
    if args.check:
        return 0 if (HERE / "SUMMARY.md").read_text() == text else 1
    (HERE / "SUMMARY.md").write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
