"""Python relay for the `cardinality@0` route (docs/spec/quantities.md 4, QT-A4).

Lean decides everything (service mode `cardinality`; a document's content through mode `document`): the statements, the
region table, the regenerated problem, every certificate's verdict and each diagnostic, verbatim. Python sends the cases
and binds each answer to its request (R8): each statement is the one sent in Lean's spelling, each region a sort, predicates
and bits of the request, the W6a identities those of the request's projection, and a report's id is recomputed (`check_response` types it,
qt-a3d's report). The other identities are Lean's (D7): typed, never recomputed. Anything else is `CheckerUnavailable`,
never a verdict. `prove` runs W6a's search on Lean's regenerated problem and hands the certificate back to Lean, which
alone says whether it holds.
"""
from __future__ import annotations

import json
import re

from .backends.lean_service import CheckerUnavailable
from .environment import Environment, listed_profiles
from .errors import VEError
from .profiles import CARDINALITY_CHAIN, CARDINALITY_CHAIN_PROJECTED

PROFILE = "cardinality@0"
_ID = re.compile(r"[0-9a-f]{64}\Z")
MALFORMED = (AttributeError, IndexError, KeyError, RecursionError, TypeError, ValueError, VEError)


def unbound(what: str) -> CheckerUnavailable:
    return CheckerUnavailable(f"CheckerUnavailable: the Lean cardinality answer is not bound to the request ({what})")


def _require(condition, what: str) -> None:
    if not condition:
        raise unbound(what)


def _same(a, b) -> bool:
    """JSON equality: `True == 1` is none."""
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def is_chain_list(profiles) -> bool:
    """Whether a list is E2's chain list (`Cardinality.Wire.chainProfiles`, from its generated table)."""
    return profiles == CARDINALITY_CHAIN


def is_cardinality(environment) -> bool:
    """Whether environment data lists the profile (routing, not a verdict; a malformed list is Lean's to refuse)."""
    return PROFILE in listed_profiles(environment)


class Identities:
    """What a request's environment fixes: its identity version, and the environments of its W6a projection and that
    projection's core target (`Cardinality.Wire.projectW6`), whose identities Python already models."""

    def __init__(self, environment: dict):
        from .units import erased_environment
        self.identity_version = "v0.2:" + ",".join(environment["profiles"])
        self.w6 = Environment({**{k: v for k, v in environment.items() if k not in ("cardinality", "cardinality_schema")},
                               "profiles": (CARDINALITY_CHAIN_PROJECTED if is_chain_list(environment["profiles"])
                                            else [p for p in environment["profiles"] if p != PROFILE])})
        self.target = erased_environment(self.w6)

    def bind(self, row: dict) -> None:
        _require(_ID.match(row["environment_id"]) and row["w6_environment_id"] == self.w6.environment_id
                 and row["w6_target_environment_id"] == self.target.environment_id, "environment identity")

    def spelled(self, node):
        """`node` as Lean's encoders spell it (`Cardinality.Wire.encode`): a literal lowered on the request's scale, an omitted
        tag written, a printed negative zero unsigned. It only checks an answer, which stays Lean's: where the two lowerings
        differ the answer is refused, never replaced. Whether `node` is admitted is Lean's, and already answered."""
        from .units import DIMENSIONLESS, day_number, decimal_exact
        match node:
            case ["decimal", str(tag), text]:
                return ["num", tag, str(decimal_exact(text, tag, self.w6))]
            case ["date", text]:
                return ["num", "day", str(day_number(text))]
            case ["num", z]:
                return ["num", DIMENSIONLESS, z]
            case ["const", str(name)] if self.w6.constants[name].sort == "$int":
                return ["const", DIMENSIONLESS, name]
            case ["add", list(left), list(right)]:
                return ["add", DIMENSIONLESS, self.spelled(left), self.spelled(right)]
            case ["scale", str(k), list(term)]:
                return ["scale", DIMENSIONLESS, k, self.spelled(term)]
            case ["rounds_to" | "percent_of" | "percent_rounds_to" as op, *rest, str(printed)]:
                zero = printed[:1] == "-" and not printed.strip("-0.")
                return [op, *map(self.spelled, rest), printed[1:] if zero else printed]
            case list():
                return [self.spelled(child) for child in node]
        return node

    def statement(self, answered: dict, sent: dict) -> None:
        """An answered statement or claim is the one sent, in Lean's spelling, under a meaning id (`Wire.decodeStatement`)."""
        _require(_same(answered["formula"], self.spelled(sent["formula"])) and _ID.match(answered["meaning_id"]), "statement")

    def problem(self, row: dict, premises: list, conclusion: dict) -> None:
        self.bind(row)
        _require(type(row["premises"]) is list and len(row["premises"]) == len(premises), "premise count")
        for answered, sent in zip(row["premises"], premises):
            self.statement(answered, sent)
        self.statement(row["conclusion"], conclusion)


def identities(environment: dict) -> Identities:
    """The request's identities, once Lean has admitted its environment: one Python cannot project is no answer."""
    try:
        return Identities(environment)
    except MALFORMED as exc:
        raise unbound(f"its environment does not project: {exc}"[:200]) from exc


def _bind_regions(environment: dict, regions: dict) -> None:
    """Each counted sort is a finite sort of the request, its predicates distinct unary predicates of that sort, each row
    `cardinality__<sort>__<bits>` with one bit per predicate, and each region of a sort has one row. Which sorts and
    predicates a problem counts is Lean's."""
    finite, declared = environment["cardinality"]["finite_sorts"], environment["vocabulary"]["predicates"]
    for sort, predicates in regions["predicates"].items():
        _require(sort in finite and len(set(predicates)) == len(predicates)
                 and all(declared[name]["arguments"] == [sort] for name in predicates), "counted sort or predicate")
    _require(type(regions["constants"]) is list, "region rows")
    names = [row["constant"] for row in regions["constants"]]
    for row in regions["constants"]:
        _require(len(row["bits"]) == len(regions["predicates"][row["sort"]])
                 and row["constant"] == f"cardinality__{row['sort']}__{row['bits']}", "region")
    _require(len(set(names)) == len(names) == sum(2 ** len(p) for p in regions["predicates"].values()), "region count")


def _ask(environment: dict, case: dict, bind) -> dict:
    """Lean's row for a case, bound by `bind(ids, row)`: a rejection raises Lean's diagnostic; a row naming another case,
    or with a member missing or of another type, is no answer, never a Python error."""
    from .backends.relay import rows
    from .discourse import rejection
    answered = rows("cardinality", [case])
    _require(type(answered) is list and len(answered) == 1 and type(answered[0]) is dict, "one row per case")
    row = answered[0]
    _require(row.get("id") == case["id"], "case id")
    if row.get("status") == "error" and type(row.get("error")) is str:
        raise rejection(row)
    _require(row.get("status") == "ok", "status")
    ids = identities(environment)
    try:
        bind(ids, row)
    except MALFORMED as exc:
        raise unbound(f"{type(exc).__name__}: {exc}"[:200]) from exc
    return row


def _confirmed(claimed: dict, row: dict) -> None:
    """What the request cannot say (the order of a sort's predicates, the bridges among the erased premises) only Lean can:
    it refuses a claimed table or problem other than the one it regenerates (spec 4.1), of this answer, not of the request."""
    from .backends.relay import rows
    try:
        _require(_same(rows("cardinality", [claimed]), [row]), "region table or erased problem")
    except MALFORMED as exc:  # a claim the wire cannot carry (`wire_checked`) is no answer either
        raise unbound(f"{type(exc).__name__}: {exc}"[:200]) from exc


def _case(kind: str, environment: dict, premises: list, conclusion: dict, **extra) -> dict:
    return {"id": kind, "kind": kind, "environment": environment, "premises": premises, "conclusion": conclusion, **extra}


def admission(environment: dict, premises: list, conclusion: dict) -> dict:
    """Lean's admission of a problem: the statements, the region table and the regenerated erased problem."""
    def bind(ids, row):
        ids.problem(row, premises, conclusion)
        erased, regions = row["erased"], row["regions"]
        _bind_regions(environment, regions)
        # The rows are in the order of the region premises that open the problem (`nonnegOf`), then the bridges and premises.
        _require(len(erased["premises"]) >= len(premises) + len(regions["constants"]) and all(
            p["core"] == ["le", ["num", "0"], ["const", region["constant"]]]
            for p, region in zip(erased["premises"], regions["constants"])), "region premise")
    case = _case("admission", environment, premises, conclusion)
    row = _ask(environment, case, bind)
    _confirmed({**case, "regions": row["regions"], "erased": row["erased"]}, row)
    return row


def _verdict(environment: dict, premises: list, conclusion: dict, **extra) -> bool:
    def bind(ids, row):
        ids.problem(row, premises, conclusion)
        _require(type(row["valid"]) is bool, "valid")
    return _ask(environment, _case("certificate", environment, premises, conclusion, **extra), bind)["valid"]


def check_certificate(environment: dict, premises: list, conclusion: dict, certificate) -> bool:
    """Lean's verdict on a certificate; a refusal is Lean's diagnostic."""
    return _verdict(environment, premises, conclusion, certificate=certificate)


def countermodel(environment: dict, premises: list, conclusion: dict, model) -> dict:
    """Lean's countermodel verdict with each region's size in the model, in the region table's order."""
    def bind(ids, row):
        ids.problem(row, premises, conclusion)
        _bind_regions(environment, row["regions"])
        _require(type(row["refutes"]) is bool and all(type(s["size"]) is int and s["size"] >= 0 for s in row["sizes"])
                 and [s["constant"] for s in row["sizes"]] == [c["constant"] for c in row["regions"]["constants"]], "sizes")
    case = _case("countermodel", environment, premises, conclusion, model=model)
    row = _ask(environment, case, bind)
    _confirmed({**case, "regions": row["regions"]}, row)
    return row


def bind_report(ids: Identities, graph: dict, report: dict) -> None:
    """A report against its graph: the root is the graph's; the leaves are the nodes without a deduction the root rests on,
    each once, in submitted order (`Graph.leaves`), with their statements; `report_id` is the digest of exactly this report
    (`Cardinality.Run.reportId`), so a duplicated, dropped or reordered leaf row is refused (qt-a3d's gap)."""
    ids.bind(report)
    nodes, claims = {node["name"]: node for node in graph["nodes"]}, report["report"]
    _require(claims["root"]["name"] == graph["root"], "root")
    reached, stack = set(), [graph["root"]]
    while stack:
        if (name := stack.pop()) not in reached:
            reached.add(name)
            stack.extend(nodes[name].get("premises", []))
    _require([leaf["name"] for leaf in claims["leaves"]] ==
             [n["name"] for n in graph["nodes"] if n["name"] in reached and "premises" not in n], "leaves")
    for claim in (claims["root"], *claims["leaves"]):
        ids.statement(claim, nodes[claim["name"]]["statement"])
    from .admission import report_identity
    _require(report["report_id"] == report_identity(ids.identity_version, {
        "environment_id": report["environment_id"], "w6_environment_id": report["w6_environment_id"],
        "w6_target_environment_id": report["w6_target_environment_id"], "document": graph, "report": claims}), "report id")


def document(environment: dict, graph: dict) -> dict:
    """Lean's report on a claim graph (case kind `document`), bound to the graph."""
    return _ask(environment, {"id": "document", "kind": "document", "environment": environment, "document": graph},
                lambda ids, row: bind_report(ids, graph, row))


def paraphrase(environment: dict, statement: dict) -> dict:
    """Lean's English line for a statement and one assumption per finite sort (display only until QT-A6). A line is Lean's
    words: Python checks that it is text, and the count."""
    def bind(ids, row):
        ids.bind(row)
        ids.statement(row["statement"], statement)
        _require(type(row["assumptions"]) is list and len(row["assumptions"]) == len(environment["cardinality"]["finite_sorts"])
                 and all(a.encode() for a in (row["paraphrase"], *row["assumptions"])), "paraphrase")  # text, not empty, encodable
    return _ask(environment, {"id": "paraphrase", "kind": "paraphrase", "environment": environment, "statement": statement},
                bind)


def prove(environment: dict, premises: list, conclusion: dict, *, max_steps: int = 10_000) -> dict | None:
    """A certificate Lean accepts for the problem, or None when the search finds none (inconclusive, never a refutation):
    W6a's `prove_quantity` on Lean's regenerated problem, its region constants declared for the search, its trace bound to
    Lean's identities and handed back with the claimed table and problem. The search is untrusted."""
    from .units import prove_quantity
    row = admission(environment, premises, conclusion)
    raw, erased = identities(environment).w6.to_dict(), row["erased"]
    regions = {c["constant"]: {"description": f"region {c['bits']} of {c['sort']}", "sort": "$int"}
               for c in row["regions"]["constants"]}
    search = Environment({**raw, "vocabulary": {**raw["vocabulary"],
                                                "constants": {**raw["vocabulary"]["constants"], **regions}}})
    statements = [{"format": "ve-quantity@1", "formula": f["Q"]} for f in (*erased["premises"], erased["conclusion"])]
    found = prove_quantity(search, statements[:-1], statements[-1], max_steps=max_steps)
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
    valid = _verdict(environment, premises, conclusion, certificate=certificate, regions=row["regions"], erased=erased)
    return certificate if valid else None


def _counting(unit: dict) -> bool:
    return "cardinality" in (unit.get("content") or {})


def _front_of(text: str, body: bytes, meta: dict, own) -> tuple[dict, bytes]:
    """A reading's document of a chain list row: this body, the request's members, and the request's units with `own` as
    written and every other unit's id and span, no content."""
    from .document.source import _split
    raw = text.encode("utf-8")
    front, source, _ = _split(raw)
    _require(source == body, "reading's body")
    _require(len(front["units"]) == len(meta["units"]) and all(
        (_same(mine, unit) if own(unit) else
         (mine["id"], mine["span"], "content" in mine) == (unit["id"], unit["span"], False))
        for mine, unit in zip(front["units"], meta["units"])), "reading's units")
    _require(all(k in ("environment", "units") or _same(v, meta.get(k, ...)) for k, v in front.items()), "reading's members")
    return front, raw


def bind_composed(meta: dict, body: bytes, row: dict) -> tuple[dict, bytes | None]:
    """A row's `composed` (`Service.Document.composedJson`), there exactly under the chain list: `not_certified` names the
    request's counting units, each reading's document holds what `_front_of` says, and the chain's environment is the
    request's without `cardinality@0` and fields it does not read. The chain's document is there whatever the units are
    (qt-a4b review F1). Returns the front matter the row answers and the chain's text: Lean checks the chain on its own
    request, which names this document (`chain_of`), and refuses a text that is not its chain reading
    (`Service.Document.chainBound`), which is where its verdict comes from."""
    composed = row.get("composed")
    environment = meta["environment"]
    _require((composed is not None) == is_chain_list(environment["profiles"]), "composed")
    if composed is None:
        return meta, None
    counted = [u["id"] for u in meta["units"] if _counting(u)]
    _require(counted == composed["not_certified"] and composed["scope"], "not certified")
    front, _ = _front_of(composed["counting_document"], body, meta, _counting)
    _require(_same(front["environment"], environment), "counting environment")
    lowered, raw = _front_of(composed["chain_document"], body, meta, lambda unit: not _counting(unit))
    chain = lowered["environment"]
    _require(chain["profiles"] == [p for p in environment["profiles"] if p != PROFILE] and
             all(k == "profiles" or _same(v, environment[k]) for k, v in chain.items()), "chain environment")
    return front, raw


def bind_document(ids: Identities, row: dict, declared: list, graph, admitted: bool) -> None:
    """A `document` row of a `cardinality@0` text: each unit's content is its authored statement under its meaning id
    (`Service.Document.contentOf`), and the report is there exactly when `check` asked for it, bound to the graph."""
    try:
        for unit, (authored, _) in zip(row["units"], declared, strict=True):
            if "content" in unit:
                ids.statement(unit["content"], authored["content"]["cardinality"])
                _require(unit["meaning_id"] == unit["content"]["meaning_id"], "unit meaning id")
        _require(("cardinality" in row) == (admitted and graph is not None), "report")
        if "cardinality" in row:
            bind_report(ids, graph, row["cardinality"])
            labels = {node["name"]: node["label"] for node in graph["nodes"] if "label" in node}
            _require(row["cardinality"]["leaf_labels"] == [
                {"name": leaf["name"], "label": labels[leaf["name"]]}
                for leaf in row["cardinality"]["report"]["leaves"] if leaf["name"] in labels], "leaf labels")
    except MALFORMED as exc:
        raise unbound(f"{type(exc).__name__}: {exc}"[:200]) from exc


def document_report(doc: dict) -> dict:
    """`ve document check`'s answer: Lean's coverage and report, bound. A premise set has no Lean route here yet, so that line
    is UNKNOWN, never a Python verdict."""
    return {"format": doc["meta"]["format"], "source_id": doc["source_id"], "document_id": doc["document_id"],
            "coverage": doc["lean"]["coverage"], "reading_plan": doc["reading_plan"],
            "premises": {"status": "UNKNOWN", "reason": "cardinality premise sets have no Lean status route yet"},
            **({"cardinality": doc["cardinality"]} if doc["cardinality"] is not None else {})}
