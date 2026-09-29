"""Gate 2 parity: rerun the Stage 0 probe matrix under a backend authority and diff it.

Usage: ``uv run python tools/stage2_parity.py --authority lean [--json out.json] [--write]``.

Every probe of ``tests/probe_matrix.py`` is rerun twice, under ``VE_AUTHORITY=python``
and under the selected authority, and compared with the frozen Python baseline
``conformance/baseline-2026-09/python.json`` under the baseline projection. A cell is

* ``regression``: S became R/U/X, an S cell changed its verdict status, or an R/U cell changed its code (the plan's
  section 2.3 rule; X is ``CheckerUnavailable``);
* ``different``: same cell and status, different complete output;
* ``baseline drift``: the backend differs from the baseline exactly as today's
  Python does (a Python change after Stage 0, such as a new record field);
* ``same, adapter``: identical, and the operation's own adapter ran on the
  backend (its verdict came from the backend path);
* ``same, constituents``: identical, but only constituent adapters ran (for
  example Background or typing inside a certificate replay whose verdict is
  still Python's);
* ``same, python``: identical, but no adapter was dispatched, so Python alone
  answered and the cell says nothing about backend coverage.

``--write`` regenerates ``docs/spec/stage2-parity.md``; ``--show OPERATION`` prints
the first non-matching cell of one operation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests import probe_matrix as probe  # noqa: E402
from ve.backends import dispatch  # noqa: E402
from ve.errors import CheckerUnavailable  # noqa: E402

REPORT = ROOT / "docs/spec/stage2-parity.md"
CLASSES = ("regression", "different", "baseline drift", "same, adapter", "same, constituents",
           "same, python")
# The dispatch operation of each probed public operation's own adapter.
ADAPTERS = {
    "admission": "admission", "background": "background", "countermodel_check": "countermodel_check",
    "countermodel_search": "countermodel_search", "countermodel_search_min_domain": "countermodel_search",
    "countermodel_search_nonempty": "countermodel_search",
    "countermodel_search_nonvacuous": "countermodel_search",
    "countermodel_search_semantic_nonvacuity": "countermodel_search",
    "distinguishing_model": "distinguishing_model", "evaluate": "evaluate", "evaluate_trace": "evaluate",
    "dependency_order": "dependency_order", "label": "label", "typing": "typing",
}
_routed: set[str] = set()
_backend = "python"
_python_outcome = probe.outcome


def _observe(op: str, authority: str) -> None:
    if authority != "python":
        _routed.add(op)


def _outcome(call, *, expected=()):
    """Run one probed call under the backend; its inputs were built under Python."""
    _routed.clear()
    os.environ["VE_AUTHORITY"] = _backend
    try:
        result = _python_outcome(call, expected=expected)
    except CheckerUnavailable as exc:
        result = {"cell": "X", "status": "CheckerUnavailable", "output": exc.to_dict()}
    finally:
        os.environ["VE_AUTHORITY"] = "python"
    return {**result, "routed": sorted(_routed)}


def _key(row) -> tuple:
    return (row.get("language", "ve.core@0.2"), tuple(row["profiles"]), row["operation"], row["input_class"])


def _projected(row):
    return (row["cell"], row["status"], probe.baseline_projection(row["output"]))


def _classify(old, new, now=None, own=None) -> str:
    if _projected(old) == _projected(new):
        if own is not None and own in new.get("routed", ()):
            return "same, adapter"
        return "same, constituents" if new.get("routed") else "same, python"
    if now is not None and _projected(now) == _projected(new):
        return "baseline drift"
    if old["cell"] != new["cell"] or old["status"] != new["status"]:
        return "regression"
    return "different"


def _worst(classes) -> str:
    return next(name for name in CLASSES if name in classes)


def compare(baseline: dict, now: dict, current: dict, only: str | None = None) -> dict:
    cells = []
    old_rows = {_key(row): row for row in baseline["cells"] if only in (None, row["operation"])}
    now_rows = {_key(row): row for row in now["cells"]}
    new_rows = {_key(row): row for row in current["cells"]}
    if not old_rows.keys() == now_rows.keys() == new_rows.keys():
        raise SystemExit(f"probe keys changed: {sorted(set(old_rows) ^ set(new_rows))[:5]}")
    for key, old in old_rows.items():
        new = new_rows[key]
        klass = _classify(old, new, now_rows[key], ADAPTERS.get(key[2]))
        cells.append({"key": list(key), "class": klass, "routed": new.get("routed", []),
                      "python": [old["cell"], old["status"]], "backend": [new["cell"], new["status"]],
                      **({"outputs": [probe.baseline_projection(old["output"]),
                                      probe.baseline_projection(new["output"])]}
                         if klass in ("regression", "different") else {})})
    probes = []
    for section in ("graph_probes", "budget_boundaries", "feature_probes") if only is None else ():
        for name, old in baseline[section].items():
            new, same_now = current[section][name], now[section][name]
            if section == "graph_probes":
                # check_argument is called directly, not through `outcome`; no adapter routes it yet.
                old, new, same_now = ({"cell": "S", "status": "", "output": row}
                                      for row in (old, new, same_now))
                klass, routed = _classify(old, new, same_now), []
            elif section == "budget_boundaries":
                sides = [side for side in old if isinstance(old[side], dict)]
                klass = _worst([_classify(old[s], new[s], same_now[s]) for s in sides])
                routed = sorted({op for s in sides for op in new[s].get("routed", [])})
            else:
                klass, routed = _classify(old, new, same_now), new.get("routed", [])
            probes.append({"section": section, "name": name, "class": klass, "routed": routed})
    return {"authority": current["authority"], "cells": cells, "probes": probes}


def render(result: dict) -> str:
    by_op: dict[str, Counter] = {}
    for cell in result["cells"]:
        by_op.setdefault(cell["key"][2], Counter())[cell["class"]] += 1
    totals = Counter(cell["class"] for cell in result["cells"])
    lines = ["# Stage 2 parity against the Stage 0 baseline", "",
             f"Generated by `uv run python tools/stage2_parity.py --authority {result['authority']} --write`.",
             "Each Stage 0 probe is rerun under today's Python and under the backend authority and compared with "
             "`conformance/baseline-2026-09/python.json` under the baseline projection. "
             "`regression` is an S cell that became R, U or X (`CheckerUnavailable`) or changed its verdict status, or an R/U cell whose code "
             "changed; `different` keeps the cell and status but changes the complete record; `baseline drift` "
             "differs from the baseline exactly as today's Python does; `same, adapter` is identical with the "
             "operation's own adapter executed on the backend; `same, constituents` is identical with only "
             "constituent adapters (Background, typing, evaluation) on the backend while the operation's verdict "
             "is still Python's; `same, python` is identical because no adapter was dispatched. Only "
             "`same, adapter` is backend coverage of the operation.", "",
             f"Totals over {len(result['cells'])} cells: " +
             ", ".join(f"{name} {totals[name]}" for name in CLASSES) + ".", "",
             "| Operation | " + " | ".join(CLASSES) + " |", "|---|" + "---:|" * len(CLASSES)]
    for op in sorted(by_op):
        lines.append(f"| `{op}` | " + " | ".join(str(by_op[op][name]) for name in CLASSES) + " |")
    lines += ["", "## Regressions and differences by backend outcome", "",
              "| Operation | Class | Python | Backend | Cells |", "|---|---|---|---|---:|"]
    rows = Counter((c["key"][2], c["class"], tuple(c["python"]), tuple(c["backend"]))
                   for c in result["cells"] if c["class"] in ("regression", "different"))
    for (op, klass, old, new), count in sorted(rows.items()):
        lines.append(f"| `{op}` | {klass} | {old[0]}: `{old[1]}` | {new[0]}: `{new[1]}` | {count} |")
    lines += ["", "## Named probes", "", "| Section | Probe | Class | Routed |", "|---|---|---|---|"]
    for row in result["probes"]:
        lines.append(f"| {row['section']} | `{row['name']}` | {row['class']} | {', '.join(row['routed'])} |")
    return "\n".join(lines) + "\n"


def _generate(authority: str) -> dict:
    # Probe inputs (environments, models, source text, proofs to replay) are
    # built by the retained Python; only each probed call runs on `authority`.
    # The graph probes call check_argument outside `outcome`, so they run on Python.
    global _backend
    _backend = authority
    os.environ["VE_AUTHORITY"] = "python"
    return {**probe.generate(), "authority": authority}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--authority", default="lean", choices=("python", "shadow", "lean", "rust-experimental"))
    parser.add_argument("--json", type=Path, help="write the per-cell comparison here")
    parser.add_argument("--write", action="store_true", help=f"regenerate {REPORT.relative_to(ROOT)}")
    parser.add_argument("--show", metavar="OPERATION", help="print the first non-matching cell of OPERATION")
    args = parser.parse_args(argv)
    dispatch.observers.append(_observe)
    probe.outcome = _outcome
    if args.show:
        probe.OPERATIONS = tuple(op for op in probe.OPERATIONS if op == args.show)
        probe.graph_baselines = probe.boundary_baselines = probe.feature_baselines = dict
    now = _generate("python")
    current = now if args.authority == "python" else _generate(args.authority)
    baseline = json.loads((probe.OUT / "python.json").read_text())
    if args.show:
        for run in (now, current):
            run["cells"] = [row for row in run["cells"] if row["operation"] == args.show]
        result = compare(baseline, now, current, only=args.show)
        shown = next((c for c in result["cells"] if c["class"] in ("regression", "different")), None)
        print(json.dumps(shown, indent=1, sort_keys=True))
        return 0
    result = compare(baseline, now, current)
    if args.json:
        args.json.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    text = render(result)
    if args.write:
        REPORT.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
