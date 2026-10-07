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

from conformance import frozen_norm_defaults as nd  # noqa: E402
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


COMPLETED = {"deny": "no", "allow": "yes", "unspecified": "unsaid"}


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
        if line.reached == "reachable":
            # Where no author rule decides, the value is the completion's (spec 3.2; Lean `value3_gap`).
            row["value"] = COMPLETED[line.completion]
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


def generated(*, trees=1000, searched=200, seed=0):
    """The report on the spec 8 differential's generated trees (`norm_defaults_differential.case`):
    with each tree's situation for all `trees` (a translation document half of the time, with
    a `completions` block citing one deny or allow predicate a quarter of the time), and
    through Python's search evidence for the first `searched`."""
    import random
    from conformance import norm_defaults_differential as differential
    cases, expected, kinds = [], [], []
    for index in range(trees):
        rng = random.Random(f"report:{seed + index}")
        domain = ("a", "b", "c") if rng.random() < 0.3 else ("a", "b")
        env, rules, situation = differential.case(seed + index, profiled=True, domain=domain)
        doc = nd.UnspecifiedDocument(env, rules)
        translation = rng.random() < 0.5
        fields, completions = {"translation": translation}, None
        decided = [p for p in doc.filled.order if doc.completion(p) != "unspecified"]
        if decided and rng.random() < 0.25:
            block = {rng.choice(decided): {"cites": ["u1"], "reason": "the source states it"}}
            fields.update(completions=block, unit_ids=["u1", "u2"])
            completions = nd.validate_completions(doc, block, {"u1", "u2"})
        cases.append(report_case(doc, model=situation, **fields))
        expected.append(nd.report(doc, model=situation, translation=translation, completions=completions))
        kinds.append("situation")
        if index < searched:
            lines, evidence = search_evidence(doc, translation=translation, completions=completions)
            cases.append(report_case(doc, evidence=evidence, **fields))
            expected.append(lines)
            kinds.append("searched")
    rows = []
    for start in range(0, len(cases), 500):
        rows.extend(route.run_cases(cases[start:start + 500]))
    mismatches, counts = [], {}
    for index, (lines, row, kind) in enumerate(zip(expected, rows, kinds)):
        for line in lines:
            key = f"{kind}:{line.reached}"
            counts[key] = counts.get(key, 0) + 1
            if line.grounding:
                key = f"{kind}:{line.grounding.split(':')[0]}"
                counts[key] = counts.get(key, 0) + 1
        if problems := compare(lines, row):
            mismatches.append((index, kind, problems))
    return {"cases": len(cases), "counts": counts, "mismatches": mismatches}
