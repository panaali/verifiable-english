"""Python against Lean on the soft and rights branches of norm-defaults@0 (docs/spec/norm-defaults.md
2.3 and 3.3; lean/VE/NormDefaults/Layered.lean).

`fill` runs last: Python's `UnspecifiedSoftDocument` and `UnspecifiedRightsDocument` build
`fill (soften T)` and `fill (soften (correlate D))`; Lean regenerates both from the same
source. For each fixture this compares, Python against Lean:

* the regeneration (order, Background, layers, targets, `Fill_T`, unsaid tables, reached
  formulas), `Soft_T` with `Coh_T` on the filled tree, the rights limitation premises, and
  the base environment the certificates bind, byte for byte;
* every point status (`table3`, enumeration, or UNDECIDED with its two fillings, which
  must also satisfy the route's base premises);
* the conflict verdict: a filled witness is a Lean CONFLICT, and Python's certificates
  over `Background_base(E‴) ++ Soft_T (++ rights) ++ Fill_T` are a Lean CONFLICT-FREE;
* the report, with a situation and with Python's search evidence.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve import norm_defaults as nd  # noqa: E402
from ve import norm_defaults_route as route  # noqa: E402
from ve.ast import _to_data  # noqa: E402
from ve.wire import canonical_json  # noqa: E402
from conformance.norm_defaults import _environment, _regulated  # noqa: E402
from conformance.norm_defaults_report import compare, search_evidence  # noqa: E402

SOFT = ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]
RIGHTS = ["norm-defaults@0", "norms@0", "relational-fol@0", "rights@0", "soft-norms@0"]


def _soft_rule(name, predicate, sign, mode="strict", guard=("top",), sufficient=(), **extra):
    raw = {"name": name, "predicate": predicate, "sign": sign, "guard": list(guard), "unless": [], "over": []}
    if mode == "default":
        raw.update(mode="default", exception={"decided_by": "unstated", "sufficient": list(sufficient),
                                              "necessary": [], "factors": []})
    raw.update(extra)
    return {"norm": raw}


def _situation(domains, relations=None):
    return {"complete": True, "domains": domains, "constants": {}, "relations": relations or {}}


def _gamma(perm):
    """u8: soft (γ), `x_permitted` unspecified (or deny, CONFLICT)."""
    env = _environment({"x_required": _regulated("obligation", "deny", "{0} do x", "x_permitted", ("assistant",)),
                        "x_permitted": _regulated("permission", perm, "{0} do x", args=("assistant",))},
                       sorts=("assistant", "user"), profiles=SOFT)
    situations = [_situation({"assistant": ["a"], "user": []}, {"soft__excepted__s": rows})
                  for rows in ([], [["a"]])]
    return env, [_soft_rule("s", "x_required", True, "default")], situations


def _deception(default, mode):
    """u2: the strict and default readings of u0156.s03."""
    env = _environment({"system_prompt_deception_permitted": _regulated(
        "permission", default, "{0} deceive {1} about the system prompt", args=("claude_instance", "user"))},
        sorts=("claude_instance", "user"), profiles=SOFT)
    rule = _soft_rule("no-system-prompt-deception", "system_prompt_deception_permitted", False, mode)
    decision = "soft__excepted__no_system_prompt_deception"
    situations = [_situation({"claude_instance": ["c"], "user": ["u"]},
                             {decision: rows} if mode == "default" else {}) for rows in ([], [["c", "u"]])]
    return env, [rule], situations


def _cyber(mode):
    """u3: the hard strict and the default readings of u0165.s03."""
    env = _environment({"cyberweapon_creation_permitted": _regulated(
        "permission", "unspecified", "{0} create cyberweapons", args=("claude_instance",))},
        sorts=("claude_instance",), profiles=SOFT)
    extra = {"hard": True} if mode == "strict" else {}
    rule = _soft_rule("no-cyberweapons", "cyberweapon_creation_permitted", False, mode, **extra)
    relations = [{}] if mode == "strict" else [{"soft__excepted__no_cyberweapons": rows} for rows in ([], [["c"]])]
    return env, [rule], [_situation({"claude_instance": ["c"]}, r) for r in relations]


def _coherent():
    """Soft_T with content: an exception with a sufficient condition, and two colliding
    default rules, one guarded by an unspecified permission, so `Coh_T` on `fill U` reads
    an unsaid atom."""
    env = _environment({"x_required": _regulated("obligation", "deny", "{0} do x", "x_permitted", ("assistant",)),
                        "x_permitted": _regulated("permission", "deny", "{0} do x", args=("assistant",)),
                        "y_permitted": _regulated("permission", "unspecified", "{0} do y", args=("assistant",)),
                        "c": {"arguments": ["assistant"], "description": "c"}},
                       sorts=("assistant",), profiles=SOFT)
    y = ["unary", "y_permitted", ["var", 0]]
    rules = [_soft_rule("must-x", "x_required", True, "default", guard=y, sufficient=[["unary", "c", ["var", 0]]]),
             _soft_rule("need-not-x", "x_required", False, "default")]
    situations = [_situation({"assistant": ["a"]}, {"c": c, "soft__excepted__must_x": e,
                                                    "soft__excepted__need_not_x": n})
                  for c, e, n in (([["a"]], [["a"]], []), ([], [], [["a"]]))]
    return env, rules, situations


def coherent_unexcepted():
    """`coherent` with neither rule excepted: `Coh_T` on `fill U` forces `unsaid__y_permitted`
    false, so the filling that makes y permitted is inadmissible. Python's enumeration reads
    `Fill_T` only and its own check then refuses the pair it found (a VEError); Lean's status
    replay requires both fillings of an UNDECIDED pair to satisfy `X`."""
    env, rules, _ = _coherent()
    return env, rules, _situation({"assistant": ["a"]}, {"c": [], "soft__excepted__must_x": [],
                                                       "soft__excepted__need_not_x": []})


ARTICLE_9 = [
    {"right": {"name": "liberty", "holder": "person", "guard": ["top"], "lines": [
        {"kind": "claim", "holder_slot": None, "cites": {},
         "norm": {"name": "art9", "predicate": "arrest_permitted", "sign": False,
                  "guard": ["binary", "arbitrary", ["var", 1], ["var", 0]], "unless": [], "over": []}}]}},
    {"limitation": {"name": "l29", "scope": ["liberty"], "kinds": ["claim"], "decided_by": "unstated",
                    "conditions": [{"name": "law", "role": "necessary", "decided_by": None,
                                    "verbalisation": "determined by law"}], "factors": []}}]


def _arrest(default):
    """u9: rights (γ), the third variant."""
    env = _environment({"arrest_permitted": _regulated("permission", default, "{0} arrest {1}",
                                                       args=("state", "person")),
                        "arbitrary": {"arguments": ["state", "person"], "description": "the arrest is arbitrary",
                                      "verbalisation": "{0} arrests {1} arbitrarily"}},
                       sorts=("state", "person"), profiles=RIGHTS)
    env["vocabulary"]["rights"] = {"holders": ["person"], "bearers": ["state"], "protected": [], "alters": {}}
    situations = [_situation({"state": ["s"], "person": ["p"]},
                             {"arbitrary": [["s", "p"]], "rights__lim__1": lim, "rights__cond__1": lim})
                  for lim in ([], [["s", "p"]])]
    return env, ARTICLE_9, situations


def fixtures():
    """(name, route, environment, source, situations)."""
    for perm in ("unspecified", "deny"):
        yield (f"u8-{perm}", "soft", *_gamma(perm))
    for default in ("unspecified", "deny"):
        for mode in ("strict", "default"):
            yield (f"u2-{default}-{mode}", "soft", *_deception(default, mode))
    for mode in ("strict", "default"):
        yield (f"u3-{mode}", "soft", *_cyber(mode))
    yield ("coherent", "soft", *_coherent())
    for default in ("unspecified", "allow", "deny"):
        yield (f"u9-{default}", "rights", *_arrest(default))


def document(kind, env, source):
    if kind == "rights":
        from ve.rights import RightsEnvironment
        return nd.UnspecifiedRightsDocument(RightsEnvironment(env), source)
    from ve.softnorms import SoftEnvironment
    return nd.UnspecifiedSoftDocument(SoftEnvironment(env), source)


def _wire(value):
    """The restricted Lean JSON input represents an optional null field by omission
    (as `ve.rights_route` sends rights documents)."""
    if isinstance(value, dict):
        return {key: _wire(item) for key, item in value.items() if item is not None}
    if isinstance(value, list):
        return [_wire(item) for item in value]
    return value


def case(kind, env, source, case_kind, **fields):
    return {"id": case_kind, "kind": case_kind, "environment": env,
            ("document" if kind == "rights" else "norms"): _wire(source), **fields}


def filling_json(filling):
    return {name: [list(row) for row in sorted(rows)] for name, rows in filling.items()}


def regeneration_problems(doc, row):
    problems = [field for field, value in route.regeneration(doc).items() if row.get(field) != value]
    base = doc.filled.base_environment()
    if canonical_json(base.to_dict()) != canonical_json(row["base_environment"]):
        problems.append("base_environment")
    for field, premises in (("soft", base.soft_premises), ("rights", base.rights_premises)):
        if row[field] != [{"label": label, "ast": _to_data(f)} for label, f in premises]:
            problems.append(field)
    return problems


def status_cases(kind, env, source, doc, situation):
    cases = []
    for status in doc.statuses(situation):
        fields = {"model": situation, "predicate": status.predicate, "tuple": list(status.values)}
        if status.status == "SETTLED":
            fields["method"] = "table3" if status.evidence == "table3" else "enumerate"
            expected = "SETTLED yes" if status.value else "SETTLED no"
        elif status.status == "UNDECIDED":
            fields.update(method="undecided", yes=filling_json(status.fillings[0]),
                          no=filling_json(status.fillings[1]))
            expected = "UNDECIDED"
        else:
            fields["method"] = "table3"
            expected = "UNKNOWN"
        cases.append((case(kind, env, source, "norm-defaults-status", **fields), expected))
    return cases


def conflict_case(kind, env, source, doc, situation, bindings):
    report = nd.check_conflict(doc, model=situation)
    if report.status == "CONFLICT":
        return report.status, case(kind, env, source, "norm-defaults-conflict", witness={
            "target": report.target, "model": situation, "filling": report.filling, "tuple": list(report.tuple)})
    report = nd.check_conflict(doc, prove=True)
    packages = {target: {**package, **bindings} for target, package in report.certificates.items()}
    return report.status, case(kind, env, source, "norm-defaults-conflict", packages=packages)


def layered_search_evidence(doc, bindings, **options):
    """Python's search evidence in the layered shape: a situation and its filling."""
    lines, (witnesses, packages) = search_evidence(doc, **options)
    for line in lines:
        if line.predicate in witnesses:
            values, filling = line.witness
            witnesses[line.predicate] = {"model": line.situation.to_dict(), "filling": filling_json(filling),
                                         "tuple": list(values)}
    return lines, (witnesses, {k: {**v, **bindings} for k, v in packages.items()})


def run():
    rows = []
    for name, kind, env, source, situations in fixtures():
        doc = document(kind, env, source)
        elaborated = route.run_cases([case(kind, env, source, "norm-defaults-elaborate")])[0]
        if elaborated.get("status") != "ok":
            rows.append({"fixture": name, "mismatches": [("elaborate", elaborated.get("error"))]})
            continue
        bindings = {"environment_id": elaborated["environment_id"], "document_hash": elaborated["document_hash"]}
        mismatches = [("elaborate", p) for p in regeneration_problems(doc, elaborated)]
        cases, expected, kinds = [], [], []
        verdicts, statuses = [], []
        for situation in situations:
            for c, answer in status_cases(kind, env, source, doc, situation):
                cases.append(c), expected.append(answer), kinds.append("status")
                statuses.append(answer)
            verdict, c = conflict_case(kind, env, source, doc, situation, bindings)
            verdicts.append(verdict)
            cases.append(c), expected.append(verdict), kinds.append("conflict")
            lines = nd.report(doc, model=situation, translation=True)
            cases.append(case(kind, env, source, "norm-defaults-report", model=situation, translation=True))
            expected.append(lines), kinds.append("report")
        lines, (witnesses, packages) = layered_search_evidence(doc, bindings, translation=True)
        cases.append(case(kind, env, source, "norm-defaults-report", witnesses=witnesses, packages=packages,
                          translation=True))
        expected.append(lines), kinds.append("report")
        for c, answer, k, row in zip(cases, expected, kinds, route.run_cases(cases)):
            if row.get("status") != "ok":
                mismatches.append((k, row.get("error")))
            elif k == "status" and row["point_status"] != answer:
                mismatches.append((k, c["predicate"], c["tuple"], answer, row["point_status"]))
            elif k == "conflict" and row["verdict"] != answer:
                mismatches.append((k, answer, row["verdict"], row.get("detail")))
            elif k == "report" and (problems := compare(answer, row)):
                mismatches.append((k, problems))
        rows.append({"fixture": name, "cases": len(cases) + 1, "mismatches": mismatches, "conflict": verdicts,
                     "statuses": statuses, "soft": [p["label"] for p in elaborated["soft"]],
                     "rights": [p["label"] for p in elaborated["rights"]],
                     "reached": [line.reached for line in lines]})
    return {"fixtures": rows, "passed": sum(not r["mismatches"] for r in rows)}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=1, default=str))
