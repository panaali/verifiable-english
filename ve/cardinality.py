"""Python relay for the `cardinality@0` route (docs/spec/quantities.md 4, QT-A4).

Lean decides everything (service mode `cardinality`; a document's content through mode `document`, whose
`Service.Document.cardinalityReport` is the same report): the statements, the region table, the regenerated erased
problem, every certificate's verdict and each diagnostic, verbatim. Python sends the cases with `rows` and binds each
answer to its request (R8): the identities are the digests of the request's environment and of the row's own values,
every statement is the one sent, every region is a sort, a predicate and a bit string of the request, and a report's id
is recomputed (`check_response` types it). Anything else is `CheckerUnavailable`, never a verdict. `prove` runs W6a's
search on Lean's regenerated problem and hands the certificate back to Lean, which alone says whether it holds.
"""
from __future__ import annotations

import json

from .backends.lean_service import CheckerUnavailable
from .environment import Environment, listed_profiles
from .errors import VEError
from .wire import digest

PROFILE = "cardinality@0"
_FORMAT = "ve-cardinality@1"
_W6_FORMAT = "ve-quantity@1"


def unbound(what: str) -> CheckerUnavailable:
    return CheckerUnavailable(f"CheckerUnavailable: the Lean cardinality answer is not bound to the request ({what})")


def _require(condition, what: str) -> None:
    if not condition:
        raise unbound(what)


def _same(a, b) -> bool:
    """JSON equality: `True == 1` is none."""
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def is_cardinality(environment) -> bool:
    """Whether environment data lists the profile (routing, not a verdict; any malformed list is Lean's to refuse)."""
    return PROFILE in listed_profiles(environment)


class Identities:
    """The three environment identities of a request (spec 4.1), from the request alone: the cardinality environment's
    and those of its W6a projection and that projection's core target (`Cardinality.Wire.projectW6`)."""

    def __init__(self, environment: dict):
        from .units import erased_environment
        self.identity_version = "v0.2:" + ",".join(environment["profiles"])
        self.environment_id = digest(f"ve-environment-{self.identity_version}\n", environment)
        self.w6 = Environment({**{k: v for k, v in environment.items() if k not in ("cardinality", "cardinality_schema")},
                               "profiles": [p for p in environment["profiles"] if p != PROFILE]})
        self.target = erased_environment(self.w6)

    def bind(self, row: dict) -> None:
        _require(row["environment_id"] == self.environment_id and row["w6_environment_id"] == self.w6.environment_id
                 and row["w6_target_environment_id"] == self.target.environment_id, "environment identity")

    def statement(self, answered: dict, sent: dict) -> None:
        """An answered statement or claim is the one sent, under its meaning id (`Wire.decodeStatement`)."""
        canonical = {"format": _FORMAT, "formula": answered["formula"]}
        _require(_same(answered["formula"], sent["formula"]), "statement")
        _require(answered["meaning_id"] == digest(f"ve-meaning-{self.identity_version}\n",
                                                  {"environment_id": self.environment_id, "ast": canonical}),
                 "meaning id")

    def erased(self, answered: dict) -> None:
        """A regenerated formula's two W6a identities are those of the row's own forms (`Time.Wire.statementIds`)."""
        annotated = {"format": _W6_FORMAT, "formula": answered["Q"], "traces": []}
        _require(answered["meaning_id"] == digest(f"ve-meaning-{self.w6.identity_version}\n",
                                                  {"environment_id": self.w6.environment_id, "ast": annotated})
                 and answered["core_meaning_id"] == digest(f"ve-meaning-{self.target.identity_version}\n",
                                                           {"environment_id": self.target.environment_id,
                                                            "ast": answered["core"]}), "erased identity")


def identities(environment: dict) -> Identities:
    """The request's identities, once Lean has admitted its environment: one Python cannot project is no answer."""
    try:
        return Identities(environment)
    except (KeyError, TypeError, ValueError, VEError) as exc:
        raise unbound(f"its environment does not project: {exc}"[:200]) from exc


def _bind_regions(environment: dict, regions: dict) -> None:
    """The region table against the request: each counted sort is a finite sort of the request, its predicates are
    distinct unary predicates of that sort, each row is `cardinality__<sort>__<bits>` with one bit per predicate, and
    every region of a sort has exactly one row. Which sorts and predicates a problem counts is Lean's."""
    finite = environment["cardinality"]["finite_sorts"]
    declared = environment["vocabulary"]["predicates"]
    _require(all(sort in finite for sort in regions["predicates"]), "counted sort")
    for sort, predicates in regions["predicates"].items():
        _require(len(set(predicates)) == len(predicates)
                 and all(name in declared and declared[name]["arguments"] == [sort] for name in predicates), "predicate")
    seen = set()
    for row in regions["constants"]:
        _require(row["sort"] in regions["predicates"] and len(row["bits"]) == len(regions["predicates"][row["sort"]])
                 and row["constant"] == f"cardinality__{row['sort']}__{row['bits']}"
                 and row["constant"] not in seen, "region")
        seen.add(row["constant"])
    _require(len(seen) == sum(2 ** len(p) for p in regions["predicates"].values()), "region count")


def _one(mode: str, case: dict) -> dict:
    """Lean's one row for a case; a rejection row raises Lean's diagnostic, and a row naming no case, or another, is no
    answer."""
    from .backends.relay import rows
    from .discourse import rejection
    answered = rows(mode, [case])
    _require(type(answered) is list and len(answered) == 1 and type(answered[0]) is dict, "one row per case")
    row = answered[0]
    if row.get("status") == "error" and row.get("id") == case["id"] and type(row.get("error")) is str:
        raise rejection(row)
    _require(row.get("status") == "ok" and row.get("id") == case["id"], "row")
    return row


def _bound(check):
    """A binder over an untrusted row: a member missing or of another type is unbound, never a Python error."""
    def bound(*args):
        try:
            return check(*args)
        except (AttributeError, IndexError, KeyError, RecursionError, TypeError, ValueError, VEError) as exc:
            raise unbound(f"{type(exc).__name__}: {exc}"[:200]) from exc
    return bound


@_bound
def _bind_problem(ids: Identities, premises: list, conclusion: dict, row: dict) -> dict:
    ids.bind(row)
    _require(type(row["premises"]) is list and len(row["premises"]) == len(premises), "premise count")
    for answered, sent in zip(row["premises"], premises):
        ids.statement(answered, sent)
    ids.statement(row["conclusion"], conclusion)
    return row


def _confirmed(claimed: dict, row: dict) -> None:
    """What the request cannot say (the order of a sort's predicates, the bridges among the erased premises) only Lean
    can: it refuses a claimed table or problem other than the one it regenerates (spec 4.1). That refusal is of this
    answer, not of the request."""
    from .backends.relay import rows
    _require(_same(rows("cardinality", [claimed]), [row]), "region table or erased problem")


def _case(kind: str, environment: dict, premises: list, conclusion: dict, **extra) -> dict:
    return {"id": kind, "kind": kind, "environment": environment, "premises": premises, "conclusion": conclusion,
            **extra}


@_bound
def _bind_admission(ids, environment, premises, conclusion, row) -> dict:
    _bind_problem(ids, premises, conclusion, row)
    erased = row["erased"]
    for formula in (*erased["premises"], erased["conclusion"]):
        ids.erased(formula)
    _require(len(erased["premises"]) >= len(premises) + len(row["regions"]["constants"]), "erased premise count")
    _bind_regions(environment, row["regions"])
    # The rows are in the order of the region premises that open the erased problem (`nonnegOf`).
    _require(all(p["core"] == ["le", ["num", "0"], ["const", region["constant"]]]
                 for p, region in zip(erased["premises"], row["regions"]["constants"], strict=False)), "region premise")
    return row


def admission(environment: dict, premises: list, conclusion: dict) -> dict:
    """Lean's admission of a problem: the statements, the region table and the regenerated erased problem."""
    case = _case("admission", environment, premises, conclusion)
    row = _one("cardinality", case)
    _bind_admission(identities(environment), environment, premises, conclusion, row)
    _confirmed({**case, "regions": row["regions"], "erased": row["erased"]}, row)
    return row


def check_certificate(environment: dict, premises: list, conclusion: dict, certificate) -> bool:
    """Lean's verdict on a certificate (spec 4.1); a refusal is Lean's diagnostic."""
    row = _one("cardinality", _case("certificate", environment, premises, conclusion, certificate=certificate))
    _bind_problem(identities(environment), premises, conclusion, row)
    _require(type(row.get("valid")) is bool, "valid")
    return row["valid"]


@_bound
def _bind_countermodel(ids, environment, premises, conclusion, row) -> dict:
    _bind_problem(ids, premises, conclusion, row)
    _require(type(row["refutes"]) is bool, "refutes")
    _bind_regions(environment, row["regions"])
    _require(_same([s["constant"] for s in row["sizes"]], [c["constant"] for c in row["regions"]["constants"]])
             and all(type(s["size"]) is int and s["size"] >= 0 for s in row["sizes"]), "sizes")
    return row


def countermodel(environment: dict, premises: list, conclusion: dict, model) -> dict:
    """Lean's countermodel verdict with each region's size in the model, in the region table's order."""
    case = _case("countermodel", environment, premises, conclusion, model=model)
    row = _one("cardinality", case)
    _bind_countermodel(identities(environment), environment, premises, conclusion, row)
    _confirmed({**case, "regions": row["regions"]}, row)
    return row


@_bound
def bind_report(ids: Identities, graph: dict, report: dict) -> dict:
    """A document's report against its graph: the root is the graph's, the leaves are exactly the nodes without a
    deduction the root rests on, each once and in submitted order (`Graph.leaves`), with their statements, and
    `report_id` is the digest of exactly this report (`Cardinality.Run.reportId`, qt-a3d: the schema types it and does
    not recompute it), so a duplicated, dropped or reordered leaf row is refused."""
    ids.bind(report)
    nodes = {node["name"]: node for node in graph["nodes"]}
    claims = report["report"]
    _require(claims["root"]["name"] == graph["root"], "root")
    ids.statement(claims["root"], nodes[graph["root"]]["statement"])
    reached, stack = set(), [graph["root"]]
    while stack:
        name = stack.pop()
        if name not in reached:
            reached.add(name)
            stack.extend(nodes[name].get("premises", []))
    _require([leaf["name"] for leaf in claims["leaves"]] ==
             [n["name"] for n in graph["nodes"] if n["name"] in reached and "premises" not in n], "leaves")
    for leaf in claims["leaves"]:
        ids.statement(leaf, nodes[leaf["name"]]["statement"])
    expected = digest(f"ve-report-{ids.identity_version}\n", {
        "environment_id": ids.environment_id, "w6_environment_id": ids.w6.environment_id,
        "w6_target_environment_id": ids.target.environment_id, "document": graph, "report": claims})
    _require(report["report_id"] == expected, "report id")
    return report


def document(environment: dict, graph: dict) -> dict:
    """Lean's report on a claim graph (case kind `document`), bound to the graph."""
    row = _one("cardinality", {"id": "document", "kind": "document", "environment": environment, "document": graph})
    return bind_report(identities(environment), graph, row)


@_bound
def _bind_paraphrase(ids, environment, statement, row) -> dict:
    ids.bind(row)
    ids.statement(row["statement"], statement)
    # A line is Lean's words: Python checks that it is text, and that there is one assumption per finite sort.
    _require(type(row["assumptions"]) is list
             and len(row["assumptions"]) == len(environment["cardinality"]["finite_sorts"])
             and all(type(a) is str and a and a.encode() for a in (row["paraphrase"], *row["assumptions"])), "paraphrase")
    return row


def paraphrase(environment: dict, statement: dict) -> dict:
    """Lean's English line for a statement and one assumption per finite sort (display only until QT-A6)."""
    row = _one("cardinality", {"id": "paraphrase", "kind": "paraphrase", "environment": environment,
                               "statement": statement})
    return _bind_paraphrase(identities(environment), environment, statement, row)


def prove(environment: dict, premises: list, conclusion: dict, *, max_steps: int = 10_000) -> dict | None:
    """A certificate Lean accepts for the problem, or None when the search finds none: W6a's `prove_quantity` on Lean's
    regenerated problem, in the projection's vocabulary with its region constants declared, its trace bound to Lean's
    identities and handed back with the claimed table and problem (Lean refuses another). The search is untrusted and
    its failure is inconclusive, never a refutation."""
    from .units import prove_quantity
    row = admission(environment, premises, conclusion)
    ids = identities(environment)
    raw = ids.w6.to_dict()
    constants = {c["constant"]: {"description": f"the size of region {c['bits']} of {c['sort']}", "sort": "$int"}
                 for c in row["regions"]["constants"]}
    vocabulary = {**raw["vocabulary"], "constants": {**raw["vocabulary"]["constants"], **constants}}
    search = Environment({**raw, "vocabulary": vocabulary})
    erased = row["erased"]
    annotated = [{"format": _W6_FORMAT, "formula": formula["Q"]} for formula in (*erased["premises"], erased["conclusion"])]
    found = prove_quantity(search, annotated[:-1], annotated[-1], max_steps=max_steps)
    if found is None:
        return None
    certificate = {
        "format": "ve-cardinality-certificate@1", "environment_id": row["environment_id"],
        "premise_meaning_ids": [p["meaning_id"] for p in row["premises"]],
        "conclusion_meaning_id": row["conclusion"]["meaning_id"],
        "w6": {**found, "environment_id": row["w6_environment_id"],
               "premise_meaning_ids": [p["meaning_id"] for p in erased["premises"]],
               "conclusion_meaning_id": erased["conclusion"]["meaning_id"],
               "core": {**found["core"], "environment_id": row["w6_target_environment_id"],
                        "premise_meaning_ids": [p["core_meaning_id"] for p in erased["premises"]],
                        "conclusion_meaning_id": erased["conclusion"]["core_meaning_id"]}}}
    verdict = _one("cardinality", _case("certificate", environment, premises, conclusion, certificate=certificate,
                                        regions=row["regions"], erased=erased))
    _bind_problem(ids, premises, conclusion, verdict)
    _require(type(verdict.get("valid")) is bool, "valid")
    return certificate if verdict["valid"] else None


@_bound
def bind_units(ids: Identities, units: list, declared: list) -> None:
    """Each answered unit's content is its authored statement under its meaning id (`Service.Document.contentOf`)."""
    for unit, (authored, _) in zip(units, declared, strict=True):
        if "content" in unit:
            ids.statement(unit["content"], authored["content"]["cardinality"])
            _require(unit["meaning_id"] == unit["content"]["meaning_id"], "unit meaning id")


def document_report(doc: dict) -> dict:
    """`ve document check`'s answer for a `cardinality@0` document: Lean's coverage and report, as loaded and bound. Its
    premise set has no Lean route yet, so that line is UNKNOWN, never a Python verdict."""
    return {"format": doc["meta"]["format"], "source_id": doc["source_id"], "document_id": doc["document_id"],
            "coverage": doc["lean"]["coverage"], "reading_plan": doc["reading_plan"],
            "premises": {"status": "UNKNOWN", "reason": "cardinality premise sets have no Lean status route yet"},
            **({"cardinality": doc["cardinality"]} if doc["cardinality"] is not None else {})}
