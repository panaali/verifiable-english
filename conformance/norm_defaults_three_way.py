"""Three-way conformance for norm-defaults@0 on the spec fixtures (docs/spec/norm-defaults.md 8, 9).

Python builds `fill U`, `Fill_T` and every piece of evidence; the Lean route
`ve_norm_defaults_route` regenerates `fill U` from the same source and replays
the evidence; Rust evaluates Python's filled premise lists as untrusted inputs
(`conformance/norm_defaults.py`, `rust/ve-core/tests/norm_defaults.rs`).

For each fixture on the norms route this checks, Python against Lean:
* the regeneration (order, Background, layers of `T‴`, targets, `Fill_T`,
  unsaid tables, reached formulas) byte for byte;
* every `table3` entry is Lean's `table3` entry (definite with the same value, or
  unknown in both), and every point status (SETTLED by `table3` or enumeration,
  UNDECIDED with its two fillings) is the status Lean's replay reports;
* the conflict verdict: a filled witness is a Lean CONFLICT, and certificates
  over `Background_base(E‴) ++ Fill_T` are a Lean CONFLICT-FREE;
* the gap and default-reached lines: a reachable witness is Lean `reachable`,
  a certificate is Lean `gaps: none`;
* an entailment certificate over `Background(E‴) ++ Fill_T ++ T‴` is valid on
  Lean's `norm-defaults-certificate`;
* W2 admission of a document whose graph cites every Background, layer and
  `Fill_T` leaf gives the same answer (report and report id) in both.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.admission import admit_document  # noqa: E402
from ve.ast import And, formula_from_data, formula_to_data  # noqa: E402
from ve.background import background  # noqa: E402
from ve.entailment import prove_entailment  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve import norm_defaults as nd  # noqa: E402
from ve import norm_defaults_route as route  # noqa: E402
from ve.norms import NormDocument  # noqa: E402
from conformance.norm_defaults import (ROW_GUARDS, _environment, _norm, _regulated, between,  # noqa: E402
                                       rows_close, rows_situations, sources, switch_counterexample)

NORMS_ROUTE = ("u1", "u5a", "u5b", "u5c", "u6", "u7", "u12")
ACT = {"complete": True, "domains": {"act": ["a", "b"]}, "constants": {}, "relations": {}}


def variants():
    """The deny and allow variants of u1 and u6 (spec 9), u15's unreached switch, and the
    review regressions: a symbol placed between the members of a pair (B1), rows of one symbol
    that must not read a close made at another of its rows (B1, loop recheck), a point whose
    cone is small in a situation with more unsaid atoms than `MAX_UNSAID_ATOMS` (B2), and
    6.3's counterexample to taking the switch certificate from the unswitched document (A1)."""
    u1 = next(raw for name, raw in _raw_sources() if name == "u1")
    for default in ("allow", "deny"):
        env, units, situations = u1
        env = _switch(env, "csam_generation_permitted", default)
        yield f"u1-{default}", env, units, situations
    env, units, situations = next(raw for name, raw in _raw_sources() if name == "u6")
    yield "u6-deny", _switch(env, "y_permitted", "deny"), units, situations
    for default in ("deny", "unspecified"):
        yield f"u15-{default}", _environment({"x_permitted": _regulated("permission", default)}), \
            [_norm("never", "x_permitted", False)], [ACT]
    yield "b1-between", *between(), [{**ACT, "relations": {"c": [["a"]]}}]
    for kind in ROW_GUARDS:
        yield f"b1-rows-{kind}", *rows_close(kind), rows_situations(kind)
    y = ["unary", "y_permitted", ["var", 0]]
    yield "b2-wide", _environment({
        "x_permitted": _regulated("permission", "deny"),
        "y_permitted": _regulated("permission", "unspecified", "{0} be tried")}), \
        [_norm("r", "x_permitted", True, ["or", y, ["not", y]])], \
        [{**ACT, "domains": {"act": ["a"] + [f"a{i}" for i in range(1, 13)]}}]
    for default in ("deny", "unspecified"):
        yield f"a1-switch-{default}", *switch_counterexample(default), [{**ACT, "domains": {"act": ["a"]}}]



def _switch(env, predicate, default):
    env = {**env, "vocabulary": {**env["vocabulary"], "predicates": dict(env["vocabulary"]["predicates"])}}
    decl = env["vocabulary"]["predicates"][predicate]
    env["vocabulary"]["predicates"][predicate] = {**decl, "regulated": {**decl["regulated"], "default": default}}
    return env


def _raw_sources():
    """(name, (environment, units, situations)) of the norms-route fixtures, as source JSON."""
    for name, document, situations in sources():
        if name in NORMS_ROUTE:
            yield name, (document.env.to_dict(), [{"norm": r.to_dict()["norm"]} for r in document.author.rules],
                         situations)


def fixtures():
    for name, (env, units, situations) in _raw_sources():
        yield name, env, units, situations
    yield from variants()


def _filling_json(filling):
    return {name: [list(row) for row in sorted(rows)] for name, rows in filling.items()}


def table3_cases(document, situation):
    """One Lean `table3` case per point, with Python's `table3` entry."""
    cases = []
    for (predicate, values), value in document.table3(situation).items():
        case = route.source_case(document, "norm-defaults-status", model=situation.to_dict(),
                                 predicate=predicate, tuple=list(values), method="table3")
        cases.append((case, "UNKNOWN" if value is None else "SETTLED yes" if value else "SETTLED no"))
    return cases


def status_cases(document, situation):
    """One Lean status case per point, with Python's status and its evidence."""
    cases = []
    for status in document.statuses(situation):
        case = route.source_case(document, "norm-defaults-status", model=situation.to_dict(),
                                 predicate=status.predicate, tuple=list(status.values))
        if status.status == "SETTLED":
            case["method"] = "table3" if status.evidence == "table3" else "enumerate"
            expected = "SETTLED yes" if status.value else "SETTLED no"
        elif status.status == "UNDECIDED":
            case.update(method="undecided", yes=_filling_json(status.fillings[0]),
                        no=_filling_json(status.fillings[1]))
            expected = "UNDECIDED"
        else:
            case["method"] = "table3"
            expected = "UNKNOWN"
        cases.append((case, expected))
    return cases


def conflict_case(document, raw_situation):
    """Python's verdict and the Lean case that replays its evidence."""
    report = nd.check_conflict(document, model=raw_situation)
    if report.status == "CONFLICT":
        filling = {k: frozenset(tuple(r) for r in v) for k, v in report.filling.items()}
        model = document.with_filling(document.situation(raw_situation), filling)
        case = route.source_case(document, "norm-defaults-conflict", witness={
            "target": report.target, "model": model.to_dict(), "tuple": list(report.tuple)})
        return report, case
    report = nd.check_conflict(document, prove=True)
    return report, route.source_case(document, "norm-defaults-conflict",
                                     packages=dict(report.certificates))


def gap_cases(document, raw_situation):
    cases = []
    for line in nd.report(document, model=raw_situation, prove=True):
        if line.reached == "reachable":
            values, filling = line.witness
            model = document.with_filling(line.situation, filling)
            case = route.source_case(document, "norm-defaults-gaps", predicate=line.predicate,
                                     model=model.to_dict(), tuple=list(values))
        else:
            packages = {f"reached:{line.predicate}": line.certificate} if line.certificate else {}
            case = route.source_case(document, "norm-defaults-gaps", predicate=line.predicate,
                                     packages=packages)
        cases.append((case, line.reached))
    return cases


def _conjunction(formulas):
    result = formulas[0]
    for formula in formulas[1:]:
        result = And(result, formula)
    return result


def certificate_case(document):
    """`Background(E‴) ++ Fill_T ++ T‴ ⊢ ⋀ (Fill_T ++ T‴)`, produced in Python."""
    formulas = [f for _, f in document.fill_premises] + [f for _, f in document.filled.premises()]
    conclusion = _conjunction(formulas)
    certificate = route.prove_filled_entailment(document, (), conclusion)
    return route.source_case(document, "norm-defaults-certificate", premises=[],
                             conclusion=formula_to_data(document.filled.env, conclusion),
                             certificate=certificate)


def admission_document(document):
    """Norm units for the author rules and a graph citing every Background, layer and
    `Fill_T` leaf of `fill U`, joined by one certified deduction."""
    env = document.filled.env
    units = [{"id": f"n{i}", "span": [10 * i, 10 * i + 5], "kind": "norm", "content": rule.to_dict()}
             for i, rule in enumerate(document.author.rules)]
    generated = list(background(env))
    nodes = [{"name": f"b{i}", "ast": formula_to_data(env, p.formula, _generated=True),
              "label": f"background:{p.generator}"} for i, p in enumerate(generated)]
    nodes += [{"name": f"l{i}", "ast": formula_to_data(env, f), "label": label}
              for i, (label, f) in enumerate(document.filled.premises())]
    nodes += [{"name": f"f{i}", "ast": formula_to_data(env, f), "label": label}
              for i, (label, f) in enumerate(document.fill_premises)]
    stated = [formula_from_data(env, n["ast"]) for n in nodes[len(generated):]]
    if not stated:
        return {"units": units, "graph": {"root": nodes[0]["name"], "nodes": nodes}} if nodes else None
    conclusion = _conjunction(stated)
    proof = prove_entailment(env, tuple(stated), conclusion)
    if proof.status != "Found":
        raise AssertionError(f"admission fixture: {proof.status}")
    nodes.append({"name": "all", "ast": formula_to_data(env, conclusion),
                  "premises": [n["name"] for n in nodes], "certificate": proof.certificate})
    return {"units": units, "graph": {"root": "all", "nodes": nodes}}


def run():
    rows = []
    for name, raw_env, units, situations in fixtures():
        env = Environment(raw_env)
        document = nd.UnspecifiedDocument(env, [NormDocument._decode(u) for u in units])
        cases, expected, kinds = [], [], []

        def add(case, answer, kind):
            case = {**case, "id": f"{name}:{len(cases)}"}
            cases.append(case)
            expected.append(answer)
            kinds.append(kind)
        add(route.source_case(document, "norm-defaults-elaborate"), None, "elaborate")
        verdicts = []
        for raw in situations:
            situation = document.situation(raw)
            for case, answer in table3_cases(document, situation):
                add(case, answer, "table3")
            for case, answer in status_cases(document, situation):
                add(case, answer, "status")
            report, case = conflict_case(document, raw)
            verdicts.append(report.status)
            add(case, report.status, "conflict")
            for case, answer in gap_cases(document, raw):
                add(case, answer, "gaps")
        add(certificate_case(document), True, "certificate")
        admission = admission_document(document)
        python_admission = admit_document(raw_env, admission) if admission is not None else None
        if admission is not None:
            add({"kind": "admission", "environment": raw_env, "document": admission},
                python_admission, "admission")
        results = route.run_cases(cases)
        mismatches = []
        for case, answer, kind, row in zip(cases, expected, kinds, results):
            if row.get("status") != "ok":
                mismatches.append((case["id"], kind, row.get("error")))
                continue
            got = {"elaborate": lambda: _regenerated(document, row),
                   "status": lambda: row["point_status"],
                   "table3": lambda: row["point_status"],
                   "conflict": lambda: row["verdict"],
                   "gaps": lambda: row["gaps"],
                   "certificate": lambda: row["valid"],
                   "admission": lambda: {k: v for k, v in row.items() if k not in ("id", "status")}}[kind]()
            if got != answer:
                mismatches.append((case["id"], kind, got, answer))
        rows.append({"fixture": name, "cases": len(cases), "kinds": sorted(set(kinds)),
                     "conflict": verdicts, "mismatches": mismatches,
                     "statuses": [a for a, k in zip(expected, kinds) if k == "status"],
                     "evidence": [c.get("method") for c, k in zip(cases, kinds) if k == "status"],
                     "gaps": [a for a, k in zip(expected, kinds) if k == "gaps"]})
    return {"fixtures": rows, "passed": sum(not r["mismatches"] for r in rows)}


def _regenerated(document, row):
    route.check_regenerated(document, row)
    return None


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=1))
