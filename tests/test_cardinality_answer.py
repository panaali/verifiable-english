"""The relay never accepts a Lean cardinality answer that is not an answer to its request (quantities QT-A4, R8). Genuine
answers of each case kind are mutated one and two faults at a time (each member dropped, emptied, retyped, duplicated,
reordered, an index out of range): every mutant is `CheckerUnavailable` or changes nothing the relay returns."""
from __future__ import annotations

import ast
import copy
import json
import random
import sys
import types
from pathlib import Path

import pytest

from tests.test_cardinality_lean import CASES, ENV, FA1, GRAPH, PLAIN, TOP, chain_text, text
from ve import cardinality
from ve.admission import report_identity
from ve.backends import relay
from ve.document.lean import _lean_answer, _lean_document
from ve.errors import CheckerUnavailable

REAL_ROWS = relay.rows
RETYPED = (7, True, None, [], {}, 1.5, "\ud800", "absent", -1, 999, ["x"], [[[[[]]]]])
CM = CASES["fa1b-countermodel"]
PROBLEM = (FA1["environment"], FA1["premises"], FA1["conclusion"])
CALLS = {"admission": lambda: cardinality.admission(*PROBLEM),
         "certificate": lambda: cardinality.check_certificate(*PROBLEM, CASES["fa1-certificate"]["certificate"]),
         "countermodel": lambda: cardinality.countermodel(CM["environment"], CM["premises"], CM["conclusion"], CM["model"]),
         "document": lambda: cardinality.document(ENV, GRAPH["document"]),
         "paraphrase": lambda: cardinality.paraphrase(FA1["environment"], FA1["premises"][0])}
COUNT = ["count", "fomc_policymaker", ["any"]]
# A statement Lean answers in another spelling: each literal last in its list, where `_nodes` reaches it.
RESPELLED = {"decimal": ["le", ["num", "bp", "2"], ["decimal", "bp", "1.5"]], "date": ["date_on", ["num", "day", "1"], ["date", "2026-01-01"]],
             "untagged": ["le", ["num", "1"], ["add", ["num", "1"], ["scale", "2", ["num", "1"]]]], "const": ["le", ["num", "1"], ["const", "plain"]]}
CALLS |= {f"{name}-respelled": lambda f=formula: cardinality.paraphrase(PLAIN, {"format": TOP["format"], "formula": f})
          for name, formula in {**{k: ["quantity", v] for k, v in RESPELLED.items()},
                                "printed": ["percent_of", COUNT, COUNT, "-0.0"]}.items()}
UNREACHED = {**GRAPH["document"], "nodes": [*GRAPH["document"]["nodes"], {"name": "aside", "statement": TOP}]}
CALLS |= {"no-premises": lambda: cardinality.admission(FA1["environment"], [], TOP),
          "unreached": lambda: cardinality.document(ENV, UNREACHED)}


def _known(relay_module=cardinality):
    """`identities`, a function of the request alone, once per environment of these tests."""
    known = {json.dumps(e, sort_keys=True): relay_module.Identities(e) for e in (FA1["environment"], ENV, PLAIN)}
    return lambda environment: known[json.dumps(environment, sort_keys=True)]


def _nodes(value, path=(), depth=5):
    """Each member to `depth`, with its path, and a list's first and last rows: a deeper formula node or a middle row is
    one more of its kind."""
    if path:
        yield path, value
    if depth and type(value) is dict:
        for key, child in value.items():
            yield from _nodes(child, (*path, key), depth - 1)
    elif depth and type(value) is list:
        for index in sorted({0, len(value) - 1}) if value else ():
            yield from _nodes(value[index], (*path, index), depth - 1)


def _replaced(row, path, value):
    out = copy.deepcopy(row)
    parent = out
    for step in path[:-1]:
        parent = parent[step]
    if value is _replaced:
        del parent[path[-1]]
    else:
        parent[path[-1]] = value
    return out


def _mutants(row):
    for path, value in _nodes(row):
        yield f"{path} dropped", _replaced(row, path, _replaced)
        for other in RETYPED:
            if other != value or type(other) is not type(value):
                yield f"{path} := {other!r}", _replaced(row, path, other)
        if type(value) is str:
            yield f"{path} := ''", _replaced(row, path, "")
            yield f"{path} shifted", _replaced(row, path, value + "0")
        if type(value) is int and type(value) is not bool:
            yield f"{path} out of range", _replaced(row, path, value + 1)
        if type(value) is list and value:
            for name, other in (("emptied", []), ("first duplicated", [value[0], *value]), ("reversed", value[::-1]),
                                ("last duplicated", [*value, value[-1]]), ("first dropped", value[1:])):
                if other != value:
                    yield f"{path} {name}", _replaced(row, path, other)


def _answered(monkeypatch, row, call=0):
    """The Lean service answers `row` to the relay's `call`th `rows` (to all of them when it is None); every other runs."""
    seen = []

    def rows(mode, cases, **options):
        seen.append(mode)
        return [copy.deepcopy(row)] if call is None or len(seen) - 1 == call else REAL_ROWS(mode, cases, **options)
    monkeypatch.setattr(relay, "rows", rows)


@pytest.fixture
def genuine(monkeypatch):
    """A case kind's genuine row and answer; `identities`, a function of the request alone, looked up per mutant."""
    monkeypatch.setattr(cardinality, "identities", _known())
    seen = []

    def recording(mode, cases, **options):
        seen.append(REAL_ROWS(mode, cases, **options))
        return seen[-1]

    def of(kind):
        seen.clear()
        with monkeypatch.context() as patch:
            patch.setattr(relay, "rows", recording)
            answer = CALLS[kind]()
        return seen[0][0], answer
    return of


def _lean_s(name):
    """What R8 leaves to Lean, bound to nothing: another wording of a line, and a countermodel's verdict and sizes, each of
    the same type. A member retyped, emptied or missing, or another number of lines, is the relay's."""
    return (name.startswith(("('paraphrase',)", "('assumptions',")) and name.endswith((" shifted", ":= 'absent'", ":= ['x']"))) or (
        name.startswith("('sizes',") and "'size'" in name and any(x in name for x in ("out of range", ":= 7", ":= 999")))


def _lean_confirms(name):
    """What only Lean's confirmation (`_confirmed`) can refuse, as the request cannot say it: the erased problem past its
    region premises and the order of a sort's predicates. The rest of a service answering every call alike is the relay's."""
    return name.startswith("('erased',") or ("('regions', 'predicates'" in name and name.endswith(" reversed"))


def _changed(call, answer) -> bool:
    try:
        return not cardinality._same(call(), answer)
    except CheckerUnavailable:
        return False


@pytest.mark.parametrize("call", [0, None], ids=["lean-confirms", "answered-alike"])
@pytest.mark.parametrize("kind", list(CALLS))
def test_every_one_fault_mutant_is_refused_or_changes_nothing(monkeypatch, genuine, kind, call):
    """Twice: Lean's confirmation can hide a check of the relay, so a service answering every call alike has none."""
    row, answer = genuine(kind)
    assert not _changed(CALLS[kind], answer)
    accepted = []
    for name, mutant in _mutants(row):
        _answered(monkeypatch, mutant, call=call)
        if _changed(CALLS[kind], answer) and not (_lean_s(name) or (call is None and _lean_confirms(name))):
            accepted.append(name)
    assert not accepted


@pytest.mark.parametrize("kind", list(CALLS))
def test_two_faults_at_a_time_are_refused_or_change_nothing(monkeypatch, genuine, kind):
    row, answer = genuine(kind)
    rng, pool, accepted = random.Random(f"qt-a4 {kind}"), list(_mutants(row)), []
    for name, first in rng.sample(pool, min(120, len(pool))):
        if nodes := list(_nodes(first)):
            fault, path = rng.choice((*RETYPED, _replaced)), rng.choice(nodes)[0]
            other, mutant = f"{path} := {fault!r}", _replaced(first, path, fault)
            _answered(monkeypatch, mutant)
            if mutant != first and _changed(CALLS[kind], answer) and not (_lean_s(name) and _lean_s(other)):
                accepted.append((name, other))
    assert not accepted


@pytest.mark.parametrize("change", [
    lambda r: r["regions"]["constants"][0].update(constant="cardinality__fomc_policymaker__absent"),
    lambda r: r["regions"]["constants"][0].update(bits="1"),
    lambda r: r["regions"]["constants"][0].update(sort="user"),
    lambda r: r["regions"]["constants"].append(r["regions"]["constants"][0]),
    lambda r: r["regions"]["constants"].pop(),
    lambda r: r["regions"]["constants"].reverse(),
    lambda r: r["regions"]["predicates"]["fomc_policymaker"].__setitem__(0, "absent"),
    lambda r: r["regions"]["predicates"]["fomc_policymaker"].__setitem__(0, "curious"),
    lambda r: r["regions"]["predicates"]["fomc_policymaker"].reverse(),
    lambda r: r["regions"]["predicates"].update(absent=[]),
    lambda r: r["erased"]["premises"].pop(4),
    lambda r: r["erased"]["premises"].insert(4, r["erased"]["premises"][4])],
    ids=["renamed", "bits", "sort", "duplicated", "dropped", "reordered", "undeclared", "other-sort", "predicates-reversed",
         "counted-sort", "bridge-dropped", "bridge-duplicated"])
def test_the_region_table_and_problem_are_bound(monkeypatch, genuine, change):
    row, _ = genuine("admission")
    mutant = copy.deepcopy(row)
    change(mutant)
    _answered(monkeypatch, mutant)
    with pytest.raises(CheckerUnavailable):
        CALLS["admission"]()


def test_a_renamed_region_is_refused_by_the_relay_itself(monkeypatch, genuine):
    """The seeded bug's fixture (plan QT-A4): a service answering every call alike, so Lean's confirmation cannot help, and
    the name changed in the table and its size alike, so only the binding to the request's sort and bits refuses it."""
    row, _ = genuine("countermodel")
    mutant = copy.deepcopy(row)
    mutant["regions"]["constants"][0]["constant"] = mutant["sizes"][0]["constant"] = "cardinality__fomc_policymaker__absent"
    _answered(monkeypatch, mutant, call=None)
    with pytest.raises(CheckerUnavailable, match="region"):
        CALLS["countermodel"]()


def _another_statement(statement):
    """Another statement under a well-formed meaning id: only the comparison with the request refuses it."""
    statement.update(formula=TOP["formula"], meaning_id="0" * 64)


def _region_renamed(row, old, new):
    """A region's name changed in its table row and the problem alike, so the region premises still agree."""
    for member in ("regions", "erased", "sizes"):
        if member in row:
            row[member] = json.loads(json.dumps(row[member]).replace(old, new))


def _counted(row, sort, predicates):
    """A table counting `predicates` of `sort`, whole and consistent with the problem's region premises: only the binding of
    the sort and predicates to the request can refuse it."""
    old, bits = row["regions"]["constants"], [format(i, f"0{len(predicates)}b") for i in range(2 ** len(predicates))]
    names = [f"cardinality__{sort}__{b}" for b in bits]
    row["regions"] = {"predicates": {sort: predicates},
                      "constants": [{"constant": n, "sort": sort, "bits": b} for n, b in zip(names, bits)]}
    if "sizes" in row:
        row["sizes"] = [{"constant": n, "size": 0} for n in names]
    if "erased" in row:
        row["erased"]["premises"] = [{**row["erased"]["premises"][0], "core": ["le", ["num", "0"], ["const", n]]} for n in names] + \
            row["erased"]["premises"][len(old):]


def _forged(row):
    """The `report_id` a report's other members would need, so the row check answers for itself."""
    row["report_id"] = report_identity(cardinality.identities(ENV).identity_version, {
        **{k: row[k] for k in ("environment_id", "w6_environment_id", "w6_target_environment_id")},
        "document": GRAPH["document"], "report": row["report"]})


REGION = "cardinality__fomc_policymaker__00"
ALIKE = {
    "table-reordered": ("admission", lambda r: r["regions"]["constants"].reverse()),
    "another-statement": ("admission", lambda r: _another_statement(r["premises"][0])),
    "sizes-dropped": ("countermodel", lambda r: r["sizes"].pop()),
    "sizes-reordered": ("countermodel", lambda r: r["sizes"].reverse()),
    "size-bool": ("countermodel", lambda r: r["sizes"][0].update(size=True)),
    "size-negative": ("countermodel", lambda r: r["sizes"][0].update(size=-1)),
    "size-text": ("countermodel", lambda r: r["sizes"][0].update(size="3")),
    # Review F2: each is the relay's alone. Its table agrees with the problem, and no Lean call can tell.
    "admission-region-renamed": ("admission", lambda r: _region_renamed(r, REGION, "cardinality__fomc_policymaker__absent")),
    "admission-sort-not-finite": ("admission", lambda r: _counted(r, "user", ["curious"])),
    "admission-predicate-other-sort": ("admission", lambda r: _counted(r, "fomc_policymaker", ["curious"])),
    "admission-predicate-undeclared": ("admission", lambda r: _counted(r, "fomc_policymaker", ["absent"])),
    "admission-predicate-twice": ("admission", lambda r: r["regions"]["predicates"]["fomc_policymaker"].__setitem__(
        1, r["regions"]["predicates"]["fomc_policymaker"][0])),
    "countermodel-sort-not-finite": ("countermodel", lambda r: _counted(r, "user", ["curious"])),
    "admission-bits-long": ("admission", lambda r: (r["regions"]["constants"][0].update(bits="000"),
                                                    _region_renamed(r, REGION, "cardinality__fomc_policymaker__000"))),
    "lines-short": ("paraphrase", lambda r: r["assumptions"].clear()),
    "lines-long": ("paraphrase", lambda r: r["assumptions"].append("Another.")),
    "lines-mapping": ("paraphrase", lambda r: r.update(assumptions={"Another.": 1})),
    "lines-text": ("paraphrase", lambda r: r.update(paraphrase=7)),
    "lines-empty": ("paraphrase", lambda r: r.update(paraphrase="")),
    "lines-surrogate": ("paraphrase", lambda r: r["assumptions"].__setitem__(0, "\ud800")),
    "decimal-another-number": ("decimal-respelled", lambda r: r["statement"]["formula"][1][2].__setitem__(2, "151")),
    "decimal-another-tag": ("decimal-respelled", lambda r: r["statement"]["formula"][1][2].__setitem__(1, "day")),
    "date-another-day": ("date-respelled", lambda r: r["statement"]["formula"][1][2].__setitem__(2, "20455")),
    "tag-another": ("untagged-respelled", lambda r: r["statement"]["formula"][1][1].__setitem__(1, "bp")),
    "tag-left-out": ("untagged-respelled", lambda r: r["statement"]["formula"][1][1].pop(1)),
    "printed-another": ("printed-respelled", lambda r: r["statement"]["formula"].__setitem__(3, "0.1")),
    "printed-left-negative": ("printed-respelled", lambda r: r["statement"]["formula"].__setitem__(3, "-0.0")),
    "report-identity": ("document", lambda r: (r.update(w6_environment_id="0" * 64), _forged(r))),
    "report-root": ("document", lambda r: (r["report"].update(root=r["report"]["leaves"][0]), _forged(r))),
    "report-leaves": ("document", lambda r: (r["report"]["leaves"].reverse(), _forged(r))),
    "report-statement": ("document", lambda r: (r["report"]["leaves"][0].update(formula=TOP["formula"]), _forged(r)))}


@pytest.mark.parametrize("kind, change", ALIKE.values(), ids=ALIKE)
def test_the_relay_s_own_checks_hold_when_lean_cannot_confirm(monkeypatch, genuine, kind, change):
    """A service answering every call alike: Lean's confirmation sees the same row, so each of these is the binder's."""
    row, _ = genuine(kind)
    mutant = copy.deepcopy(row)
    change(mutant)
    _answered(monkeypatch, mutant, call=None)
    with pytest.raises(CheckerUnavailable):
        CALLS[kind]()


@pytest.mark.parametrize("change", [
    lambda r: r["report"]["leaves"].append(r["report"]["leaves"][0]),
    lambda r: r["report"]["leaves"].pop(),
    lambda r: r["report"]["leaves"].reverse(),
    lambda r: r["report"]["leaves"].clear(),
    lambda r: r["report"]["leaves"][0].update(name="absent"),
    lambda r: r["report"]["leaves"][0].update(r["report"]["root"])],
    ids=["duplicated", "dropped", "reordered", "emptied", "no-node", "the-deduction"])
def test_a_report_s_rows_are_bound_with_and_without_a_matching_id(monkeypatch, genuine, change):
    """qt-a3d's gap: the schema has `uniqueStrings` only, so a duplicated leaf row is the relay's. The second mutant also
    carries the `report_id` it would need, so the row check answers for itself."""
    row, _ = genuine("document")
    mutant = copy.deepcopy(row)
    change(mutant)
    forged = copy.deepcopy(mutant)
    _forged(forged)
    for answered in (mutant, forged):
        _answered(monkeypatch, answered)
        with pytest.raises(CheckerUnavailable):
            CALLS["document"]()


def test_object_key_order_is_no_part_of_an_answer(monkeypatch, genuine):
    row, answer = genuine("admission")
    _answered(monkeypatch, {**{key: row[key] for key in reversed(list(row))}, "regions": dict(reversed(row["regions"].items()))})
    assert cardinality._same(CALLS["admission"](), answer)


def test_a_search_s_verdict_is_lean_s_and_typed(monkeypatch, genuine):
    """A verdict of another type is no answer: `prove` reads Lean's replay of what it found (`rows` calls 0 and 1 admit)."""
    row, _ = genuine("certificate")
    _answered(monkeypatch, {**row, "valid": False}, call=2)
    assert cardinality.prove(*PROBLEM) is None
    _answered(monkeypatch, {**row, "valid": 1}, call=2)
    with pytest.raises(CheckerUnavailable):
        cardinality.prove(*PROBLEM)


@pytest.fixture
def part(tmp_path, monkeypatch):
    """A part document as sent, its path and Lean's genuine row, with `identities` looked up per mutant."""
    raw = text(GRAPH["document"]["nodes"])
    path = tmp_path / "part.ve.md"
    path.write_bytes(raw)
    row = _lean_answer(raw, True, tmp_path, {})
    monkeypatch.setattr(cardinality, "identities", _known())
    return raw, path, row


def _shown(doc):
    return doc["source_id"], doc["document_id"], doc["units"], doc["cardinality"], doc["lean"]


def test_every_mutant_of_a_document_row_is_refused_or_changes_nothing(part):
    raw, path, row = part
    answer = _shown(_lean_document(raw, path, row, admitted=True))
    assert answer[3]["report"]["root"]["name"] == "root"
    accepted = []
    for name, mutant in _mutants(row):
        try:
            if _shown(_lean_document(raw, path, mutant, admitted=True)) != answer:
                accepted.append(name)
        except CheckerUnavailable:
            pass
    assert not accepted


def test_a_row_s_leaf_labels_are_bound_to_the_request_graph(tmp_path, monkeypatch):
    """Past Lean: the relay's own check on `leaf_labels`, each row named by the request's graph, none empty or extra."""
    raw = text([{"name": "only", "statement": TOP, "label": "asserted"}])
    path = tmp_path / "part.ve.md"
    path.write_bytes(raw)
    row = _lean_answer(raw, True, tmp_path, {})
    monkeypatch.setattr(cardinality, "identities", _known())
    good = {"name": "only", "label": "asserted"}
    assert row["cardinality"]["leaf_labels"] == [good]
    assert _lean_document(raw, path, row, admitted=True)["cardinality"]["leaf_labels"] == [good]
    for labels in ([], [good, good], [{**good, "label": "bridge:accepts(fomc,only)"}], [{**good, "name": "absent"}], [{}],
                   [{"name": "only"}], [{"label": "asserted"}], [good, {"name": "absent", "label": "asserted"}]):
        mutant = copy.deepcopy(row)
        mutant["cardinality"]["leaf_labels"] = labels
        with pytest.raises(CheckerUnavailable):
            _lean_document(raw, path, mutant, admitted=True)


def _chain_mutants(row):
    composed, front = row["composed"], json.loads(row["composed"]["chain_document"].split("\n---\n")[0][4:])
    body = row["composed"]["chain_document"].split("\n---\n", 1)[1]

    def lowered(change):
        changed = copy.deepcopy(front)
        change(changed)
        return "---\n" + json.dumps(changed) + "\n---\n" + body
    yield from ({"not_certified": []}, {"not_certified": ["absent"]}, {"not_certified": ["one", "one"]}, {"not_certified": ["two"]},
                {"scope": ""}, {"chain_document": None}, {"counting_document": composed["chain_document"]},
                {"chain_document": composed["counting_document"]},
                {"chain_document": "---\n" + json.dumps(front) + "\n---\nanother body\n"},
                {"chain_document": lowered(lambda f: f["units"].pop(0))},
                {"chain_document": lowered(lambda f: f["units"][1].update(content={"ast": ["bottom"]}))},
                {"chain_document": lowered(lambda f: f["units"][0].update(span=[0, 1]))},
                {"chain_document": lowered(lambda f: f["units"][0].update(content={"cardinality": TOP}))},
                {"chain_document": lowered(lambda f: f["environment"].update(profiles=["relational-fol@0"]))},
                {"chain_document": lowered(lambda f: f["environment"].update(extra=1))},
                {"chain_document": lowered(lambda f: f.update(reading_sets=[]))})


def test_a_chain_list_row_is_bound_to_the_request(tmp_path, monkeypatch):
    """Past Lean: `composed` names the request's units in each reading, its own environment and body, none empty or extra."""
    raw = chain_text([("one", {"cardinality": TOP}), ("two", {"ast": ["top"]})])
    path = tmp_path / "chain.ve.md"
    path.write_bytes(raw)
    row = _lean_answer(raw, True, tmp_path, {})
    doc = _lean_document(raw, path, row, admitted=True)
    assert doc["composed"]["not_certified"] == ["one"] and doc["chain"]["units"][1]["id"] == "two"
    for change in _chain_mutants(row):
        with pytest.raises(CheckerUnavailable):
            _lean_document(raw, path, {**row, "composed": {**row["composed"], **change}}, admitted=True)
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, {k: v for k, v in row.items() if k != "composed"}, admitted=True)
    # The other side: a row under W6a's lists holds no `composed`.
    other = text([{"name": "only", "statement": TOP}], graph=False)
    plain = _lean_answer(other, True, tmp_path, {})
    assert _lean_document(other, path, plain, admitted=True) and "composed" not in plain
    with pytest.raises(CheckerUnavailable):
        _lean_document(other, path, {**plain, "composed": row["composed"]}, admitted=True)


def test_a_document_row_answers_the_case_it_asked(part):
    """The report is there exactly when `check` asked for it, and a unit's statement is the authored one."""
    raw, path, row = part
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, row, admitted=False)
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, {k: v for k, v in row.items() if k != "cardinality"}, admitted=True)
    other = copy.deepcopy(row)
    other["units"][0]["content"]["formula"] = ["quantity", ["top"]]
    with pytest.raises(CheckerUnavailable):
        _lean_document(raw, path, other, admitted=True)


def _checks(tree):
    """Each check of the relay, enumerated so a new one is in: a conjunct of a `_require`, a statement calling one of the
    module's own binders, a respelling rule. Yields the node holding it, the member and the member without the check."""
    own = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)} - {"_require"}
    true, none = ast.Constant(True, lineno=1, col_offset=0), ast.Constant(None, lineno=1, col_offset=0)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "_require":
            yield node, "args", [true, *node.args[1:]]
            for part in ast.walk(node.args[0]):
                if isinstance(part, ast.BoolOp) and isinstance(part.op, ast.And):
                    yield from ((part, "values", [*part.values[:i], true, *part.values[i + 1:]]) for i in range(len(part.values)))
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and (
                getattr(node.value.func, "id", getattr(node.value.func, "attr", "")) in own):
            yield node, "value", none
        elif isinstance(node, ast.Match):
            yield from ((node, "cases", [*node.cases[:i], *node.cases[i + 1:]]) for i in range(len(node.cases)))


def _relay_without(tree, holder, member, without) -> types.ModuleType:
    """The relay with one check gone, loaded beside the real one; nothing is written."""
    kept = getattr(holder, member)
    setattr(holder, member, without)
    try:
        code = compile(tree, "ve/cardinality.py", "exec")
    finally:
        setattr(holder, member, kept)
    module = types.ModuleType("ve.cardinality_without")
    module.__package__ = "ve"
    exec(code, module.__dict__)
    module.identities = _known(module)
    return module


def test_every_check_of_the_relay_is_one_a_test_can_fail(monkeypatch, genuine, part):
    """Review F2's class: a check Lean's confirmation hides, or a fuzz exempts, is one no test can fail. Each check is dropped
    in turn, and some answer must then be treated otherwise: the rows of `ALIKE`, then every one-fault mutant, each answered
    alike and with a genuine confirmation. A respelling rule dropped refuses a genuine answer, so that counts too."""
    import ve
    this, real_relay = sys.modules[__name__], cardinality
    raw, path, part_row = part
    bare = text(GRAPH["document"]["nodes"], graph=False)
    documents = {"part": (raw, True), "not-admitted": (raw, False), "no-graph": (bare, True)}
    rows_of = {kind: genuine(kind)[0] for kind in CALLS}
    rows_of |= {"part": part_row, "not-admitted": part_row, "no-graph": _lean_answer(bare, True, path.parent, {})}
    queue = []
    monkeypatch.setattr(relay, "rows", lambda mode, cases, **options: queue.pop(0) if len(queue) > 1 else queue[0])
    monkeypatch.setattr(this, "cardinality", real_relay)
    monkeypatch.setattr(ve, "cardinality", real_relay)

    def outcome(module, kind, first, then):
        this.cardinality = ve.cardinality = module
        queue[:] = [[a] if type(a) is dict else a for a in (first, then)]
        try:
            if kind in documents:
                done = _shown(_lean_document(documents[kind][0], path, first, admitted=documents[kind][1]))
            else:
                done = CALLS[kind]()
            return json.dumps(done, sort_keys=True, default=str)
        except CheckerUnavailable:
            return "refused"
        except Exception as exc:  # a malformed row past the dropped check is otherwise treated too
            return type(exc).__name__

    def answers():
        for kind, change in ALIKE.values():
            mutant = copy.deepcopy(rows_of[kind])
            change(mutant)
            yield kind, mutant, mutant
        row = rows_of["paraphrase"]
        yield from (("paraphrase", shape, shape) for shape in ((row,), [row, row], [7], [], None))
        for kind, row in rows_of.items():
            yield kind, row, row
            for _, mutant in _mutants(row):
                yield kind, mutant, mutant
                if kind in ("admission", "countermodel"):  # the two that ask Lean to confirm
                    yield kind, mutant, row
    pool, real = list(answers()), {}

    def treated_otherwise(module, at):
        if at not in real:
            real[at] = outcome(real_relay, *pool[at])
        return outcome(module, *pool[at]) != real[at]
    tree = ast.parse(Path(real_relay.__file__).read_text(encoding="utf-8"))
    survivors = []
    for holder, member, without in _checks(tree):
        module = _relay_without(tree, holder, member, without)
        if not any(treated_otherwise(module, at) for at in range(len(pool))):
            gone = [ast.unparse(k)[:80] for k in getattr(holder, member) if k not in without] if member != "value" else [ast.unparse(holder)]
            survivors.append(f"{holder.lineno}: {gone}")
    assert not survivors, "\n".join(survivors)
