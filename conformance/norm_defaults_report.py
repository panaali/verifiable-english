"""Python against Lean on the norm-defaults@0 report (docs/spec/norm-defaults.md 3.2 and 5).

Lean's `norm-defaults-report` case decides the 3.2 lines of every regulated predicate
(`lean/VE/NormDefaults/Report.lean`). This module builds the cases from Python's
documents and compares Lean's rows with Python's `norm_defaults.report`:

* with a base situation, Lean searches the reached witness itself, so the lines, the
  witness (tuple and filling) and the residual must equal Python's;
* without one, Python's untrusted evidence (the small-model search's filled witnesses and
  the proved `reached:<p>` certificates, `report(prove=True, search_domain_size=2)`, the
  call `ve.document.coverage_defaults` makes) is replayed, and the lines must equal Python's.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve import norm_defaults as nd  # noqa: E402
from ve import norm_defaults_route as route  # noqa: E402


def report_case(document, *, model=None, evidence=None, **fields):
    """A `norm-defaults-report` case over `document`'s source; `evidence` is
    `(witnesses, packages)` for the no-situation path."""
    extra = dict(fields)
    if model is not None:
        extra["model"] = model
    if evidence is not None:
        witnesses, packages = evidence
        extra.update(witnesses=witnesses, packages=packages)
    return route.source_case(document, "norm-defaults-report", **extra)


def search_evidence(document, **options):
    """Python's report without a situation, and the evidence it found, as Lean takes it."""
    lines = nd.report(document, prove=True, search_domain_size=2, **options)
    witnesses, packages = {}, {}
    for line in lines:
        if line.reached == "reachable":
            values, filling = line.witness
            model = document.with_filling(line.situation, filling)
            witnesses[line.predicate] = {"model": model.to_dict(), "tuple": list(values)}
        elif line.certificate:
            packages[f"reached:{line.predicate}"] = line.certificate
    return lines, (witnesses, packages)


def python_rows(lines):
    """Python's report in the shape of Lean's `report` rows (the witness when found here)."""
    rows = []
    for line in lines:
        row = {"predicate": line.predicate, "completion": line.completion, "reached": line.reached,
               "lines": list(line.lines()), "inherits_from": list(line.inherits_from)}
        if line.reached == "reachable" and line.situation is not None and line.witness:
            values, filling = line.witness
            row["witness"] = {"tuple": list(values),
                              "filling": {k: sorted(list(r) for r in v) for k, v in filling.items()}}
        rows.append(row)
    return rows


def python_residual(lines):
    residual = nd.gaps_residual(lines)
    return residual, [line.grounding for line in lines if line.grounding.startswith("UngroundedDefault")]


def compare(lines, row, *, witnesses=True):
    """The differences between Python's report and Lean's row (empty when they agree)."""
    if row.get("status") != "ok":
        return [("error", row.get("error"))]
    expected = python_rows(lines)
    got = [dict(r) for r in row["report"]]
    if not witnesses:
        for r in expected + got:
            r.pop("witness", None)
    problems = [("line", e, g) for e, g in zip(expected, got) if e != g]
    if len(expected) != len(got):
        problems.append(("count", len(expected), len(got)))
    residual, findings = python_residual(lines)
    if row["residual"] != residual:
        problems.append(("residual", residual, row["residual"]))
    if row["findings"] != findings:
        problems.append(("findings", findings, row["findings"]))
    return problems
