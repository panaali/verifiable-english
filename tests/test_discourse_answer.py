"""The Python relay never accepts a Lean discourse answer that is not an answer to the document it
asked about (lf-4 review B; FINDING-CLASSES 8 and 15). Genuine answers of the Lean route are
mutated one and two faults at a time (every member dropped, emptied, retyped, duplicated,
reordered, an index pushed out of range); every mutant is `CheckerUnavailable` or changes nothing
the relay shows (`ve document check`, `render` and `readings`), and nothing else escapes."""
import copy
import json

import pytest

from tests.test_discourse import _correlated, _sample, _write
from tests.test_discourse_lean import DOC_CONSTANTS, env, text, unary, validity_doc
from ve import discourse
from ve.backends import relay
from ve.backends.lean_service import _decode_json
from ve.document import check_document, main, render_document
from ve.errors import CheckerUnavailable

EXEMPT = ["unary", "exempt", ["const", "api"]]
REQUIRES = [{"kind": "requires", "a": ["rs5", 1, "a"], "b": ["rs6", 1, "a"]},
            {"kind": "requires", "a": ["rs5", 1, "b"], "b": ["rs6", 1, "b"]}]
# the members `lean_admission` and `validate_discourse` read; every other member is Lean's alone
READ = ("id", "status", "admitted", "report_id", "references", "statuses", "validity", "bound",
        "joint", "joint_choices", "joint_formula")
RETYPED = (7, True, None, [], {}, "x", -1, 999)


def _document(tmp_path, name):
    """A genuine document and a conclusion over its vocabulary: SOME over two required choices,
    four unconstrained choices, no open set at all, a joint set over its budget (UNKNOWN), and a
    checked validity claim."""
    if name == "validity":
        doc = validity_doc("This document is a valid VE document.", "this_policy", True)
        path = tmp_path / "validity.ve.md"
        path.write_text(text(doc, env(constants=DOC_CONSTANTS)))
        return path, unary("reviewed", "api")
    source, front = {"some": lambda: _correlated(tmp_path, REQUIRES, readings=(EXEMPT, ["not", EXEMPT])),
                     "free": lambda: _correlated(tmp_path, [], readings=(EXEMPT, ["not", EXEMPT])),
                     "none": lambda: _sample(tmp_path),
                     "over": lambda: _correlated(tmp_path, [], sets=7)}[name]()
    return _write(tmp_path, front, source), EXEMPT


def _shown(path, conclusion, capsys):
    """Everything the relay shows of a document: its check, its rendering and its readings verdict."""
    check = check_document(path)
    render = render_document(path)
    main(["readings", str(path), "--conclusion", str(conclusion)])
    return check, render, json.loads(capsys.readouterr().out)


def _answered(monkeypatch, row):
    """The Lean discourse route (service mode `discourse`) answers `row`; every other mode runs. The relay
    reads it as it reads the service's rows (`relay.rows`)."""
    real = relay.rows

    def rows(mode, cases, **options):
        if mode == "discourse":
            return [copy.deepcopy(row)]
        return real(mode, cases, **options)
    monkeypatch.setattr(relay, "rows", rows)


def _nodes(value, path=()):
    """Every node of a JSON value with its path."""
    yield path, value
    if type(value) is dict:
        for key, child in value.items():
            yield from _nodes(child, (*path, key))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from _nodes(child, (*path, index))


def _replaced(row, path, value):
    out = copy.deepcopy(row)
    parent = out
    for step in path[:-1]:
        parent = parent[step]
    parent[path[-1]] = value
    return out


def _mutants(row):
    """One-fault mutants of the members the relay reads, and their two-fault versions where a
    changed number of joint choices is matched by a changed `joint` count."""
    for path, value in _nodes({k: row[k] for k in READ if k in row}):
        if not path or path[0] == "joint_formula" and len(path) > 4:
            continue  # a deep node of the disjunction is one more formula node of the same kind
        for other in RETYPED:
            if other != value or type(other) is not type(value):
                yield f"{path} := {other!r}", _replaced(row, path, other)
        if type(value) is int and type(value) is not bool:
            for other in (value + 1, value - 1):
                yield f"{path} := {other}", _replaced(row, path, other)
        if type(value) is str:
            yield f"{path} := ''", _replaced(row, path, "")
        if type(value) is list and value:
            variants = {"duplicated first": [value[0], *value], "duplicated last": [*value, value[-1]],
                        "first replaced by last": [value[-1], *value[1:]],
                        "last replaced by first": [*value[:-1], value[0]],
                        "reversed": value[::-1], "first dropped": value[1:]}
            for name, other in variants.items():
                if other == value:
                    continue
                mutant = _replaced(row, path, other)
                yield f"{path} {name}", mutant
                if path == ("joint_choices",) and len(other) != len(value):
                    yield f"{path} {name}, joint counted", {**mutant, "joint": len(other)}
        if type(value) is dict:
            for key in value:
                smaller = {k: v for k, v in value.items() if k != key}
                yield f"{path} without {key}", _replaced(row, path, smaller)
    for key in row:
        yield f"without {key}", {k: v for k, v in row.items() if k != key}


@pytest.mark.parametrize("name", ["some", "free", "none", "over", "validity"])
def test_genuine_answer_mutants_never_pass_as_answers(tmp_path, monkeypatch, capsys, name):
    """Every mutant of a genuine answer is no answer or an answer the relay shows identically."""
    path, ast = _document(tmp_path, name)
    conclusion = tmp_path / "conclusion.json"
    conclusion.write_text(json.dumps(ast))
    genuine = discourse.lean_admission(path.read_bytes(), tmp_path)
    shown = _shown(path, conclusion, capsys)
    _answered(monkeypatch, genuine)
    assert _shown(path, conclusion, capsys) == shown  # the stub replays the genuine answer
    accepted = []
    for label, mutant in _mutants(genuine):
        _answered(monkeypatch, mutant)
        try:
            if _shown(path, conclusion, capsys) != shown:
                accepted.append(label)
        except CheckerUnavailable:
            pass
    assert not accepted, accepted


def test_duplicate_and_out_of_range_choices_are_no_answer(tmp_path, monkeypatch, capsys):
    """The review's reproductions: a genuine SOME answer whose second choice is replaced by its first
    read as ALL, and a reading index 999 escaped as `IndexError`; both are `CheckerUnavailable`."""
    path, _ = _document(tmp_path, "some")
    conclusion = tmp_path / "conclusion.json"
    conclusion.write_text(json.dumps(EXEMPT))
    genuine = discourse.lean_admission(path.read_bytes(), tmp_path)
    assert genuine["joint_choices"] == [[["rs5", 1, 0], ["rs6", 1, 0]], [["rs5", 1, 1], ["rs6", 1, 1]]]
    assert _shown(path, conclusion, capsys)[2]["verdict"] == "SOME"
    first = genuine["joint_choices"][0]
    for choices in ([first, first], [first, [["rs5", 1, 999], ["rs6", 1, 999]]],
                    [first, [["rs5", 1, 1], ["rs6", 1, 2]]], genuine["joint_choices"][::-1]):
        _answered(monkeypatch, {**genuine, "joint_choices": choices})
        with pytest.raises(CheckerUnavailable, match=r"^CheckerUnavailable: .* another document \(joint choices\)$"):
            main(["readings", str(path), "--conclusion", str(conclusion)])
    # the disjunction its choices denote, and no other
    _answered(monkeypatch, {**genuine, "joint_formula": EXEMPT})
    with pytest.raises(CheckerUnavailable, match=r"\(joint formula\)$"):
        check_document(path)


def test_genuine_answers_are_bound(tmp_path):
    """Every genuine answer, whatever its joint set, passes the relay's binding (the check never
    rejects what Lean answers about the document)."""
    constraints = [[], REQUIRES, REQUIRES[:1], [{"kind": "excludes", "a": ["rs5", 1, "a"], "b": ["rs6", 1, "b"]}]]
    for sets in (2, 3, 6, 7):
        for constraint in constraints:
            source, front = _correlated(tmp_path, constraint, sets=sets)
            result = check_document(_write(tmp_path, front, source))
            assert result["joint_choices"]["status"] == ("UNKNOWN" if 2 ** sets > 64 else "complete"), result


def test_joint_status_and_unit_set_are_bound(tmp_path, monkeypatch):
    """Answers no single fault reaches: an UNKNOWN joint set within the budget, a completed one over
    it (its first choice, with the disjunction that choice denotes), and statuses over another set
    of units (one unit swapped for a unit the document does not have)."""
    path, _ = _document(tmp_path, "some")
    genuine = discourse.lean_admission(path.read_bytes(), tmp_path)
    unknown = {k: v for k, v in genuine.items() if k not in ("joint_choices", "joint_formula")}
    _answered(monkeypatch, {**unknown, "admitted": "UNKNOWN", "joint": "ResourceLimit: joint choices"})
    with pytest.raises(CheckerUnavailable, match=r"\(joint\)$"):
        check_document(path)
    statuses = dict(genuine["statuses"])
    statuses["u99"] = statuses.pop("u1")
    _answered(monkeypatch, {**genuine, "statuses": statuses})
    with pytest.raises(CheckerUnavailable, match=r"\(statuses\)$"):
        check_document(path)
    monkeypatch.undo()
    path, _ = _document(tmp_path, "over")
    genuine = discourse.lean_admission(path.read_bytes(), tmp_path)
    assert genuine["admitted"] == "UNKNOWN"
    reviewed = unary("reviewed", "api")
    first = [[f"rs{5 + k}", 1, 0] for k in range(7)]
    conjunction = reviewed
    for _ in range(6):
        conjunction = ["and", reviewed, conjunction]
    _answered(monkeypatch, {**genuine, "admitted": True, "joint": 1, "joint_choices": [first],
                            "joint_formula": conjunction})
    with pytest.raises(CheckerUnavailable, match=r"\(joint\)$"):
        check_document(path)


def _reordered(value, order):
    """The JSON value with every object's keys in `order` (`reversed` or `sorted`), at every depth."""
    if type(value) is dict:
        return {k: _reordered(value[k], order) for k in order(value)}
    if type(value) is list:
        return [_reordered(v, order) for v in value]
    return value


@pytest.mark.parametrize("name", ["some", "free", "none", "over", "validity"])
def test_object_key_order_is_no_part_of_the_answer(tmp_path, monkeypatch, capsys, name):
    """A JSON object is unordered (Lean emits its keys lexically, not in document order): every
    genuine answer with the keys of every object reversed or sorted, at every depth, is shown
    identically, never `CheckerUnavailable` (lf-4 looprecheck1 B, statuses and validity order)."""
    path, ast = _document(tmp_path, name)
    conclusion = tmp_path / "conclusion.json"
    conclusion.write_text(json.dumps(ast))
    genuine = discourse.lean_admission(path.read_bytes(), tmp_path)
    shown = _shown(path, conclusion, capsys)
    for order in (reversed, sorted):
        _answered(monkeypatch, _reordered(genuine, order))
        assert _shown(path, conclusion, capsys) == shown, order


def _renamed(front, renamed):
    """The front matter with its units renamed (`renamed`, old id to new), everywhere a unit is named."""
    for record in front["units"]:
        record["id"] = renamed[record["id"]]
    for record in (*front["discourse"]["mentions"], *front.get("reading_sets", [])):
        record["unit"] = renamed[record["unit"]]
    return front


def test_units_and_claims_out_of_lexical_order_are_admitted(tmp_path):
    """The review's reproductions: units whose document order is not their ids' lexical order (`z`,
    `a`, and u1 to u10) and validity claims listed `u2`, `u1` are genuine admissions."""
    source, front = _sample(tmp_path)
    path = _write(tmp_path, _renamed(front, {"u1": "z", "u2": "a"}), source)
    assert list(discourse.lean_admission(path.read_bytes(), tmp_path)["statuses"]) == ["a", "z"]
    assert check_document(path)["references"][0]["unit"] == "a"
    source, front = _correlated(tmp_path, [], sets=8)
    path = _write(tmp_path, front, source)
    assert list(discourse.lean_admission(path.read_bytes(), tmp_path)["statuses"])[:3] == ["u1", "u10", "u2"]
    assert check_document(path)["joint_choices"]["status"] == "UNKNOWN"
    doc = validity_doc("This document is a valid VE document.", "this_policy", True,
                       before=["This document is a valid VE document."])
    claims = doc["discourse"]["validity"]
    claims.insert(0, {**claims[0], "unit": "u2"})
    claims[1]["unit"] = "u1"
    assert [c["unit"] for c in claims] == ["u2", "u1"]
    path = tmp_path / "validity.ve.md"
    path.write_text(text(doc, env(constants=DOC_CONSTANTS)))
    assert check_document(path)["validity"] == {"u1": "checked", "u2": "checked"}


def test_a_joint_set_deeper_than_pythons_call_depth_is_admitted(tmp_path):
    """The review's reproduction: 1,000 singleton open reading sets, no constraints, padded unit
    ids (so the statuses are in document order). Lean admits exactly one joint choice, a
    conjunction 1,000 deep; the relay binds it without recursion (Python's call depth is 1,000)."""
    source, front = _correlated(tmp_path, [], sets=1000, readings=(EXEMPT, ["not", EXEMPT]))
    _renamed(front, {u["id"]: f"u{int(u['id'][1:]):04d}" for u in front["units"]})
    for rs in front["reading_sets"]:  # one reading, so no distinguishing model
        del rs["readings"][1], rs["models"]
        rs["readings"][0]["admission"]["distinguishing_models"] = {}
    path = _write(tmp_path, front, source)
    genuine = discourse.lean_admission(path.read_bytes(), tmp_path)
    assert genuine["joint"] == 1 and list(genuine["statuses"]) == [u["id"] for u in front["units"]]
    assert check_document(path)["joint_choices"] == {"status": "complete", "count": 1, "constraints": 0}


def test_an_answer_deeper_than_the_c_stack_is_no_answer(tmp_path):
    """Nesting no JSON reader on the C stack reads (a joint disjunction 200,000 deep) is no answer, never
    an escaping `RecursionError`: the service's client decodes every response line with `_decode_json`,
    which refuses it (`ValueError`), and `LeanService` makes a line it cannot decode `CheckerUnavailable`
    (tests/test_lean_service.py, the malformed responses)."""
    path, _ = _document(tmp_path, "some")
    row = json.dumps([{**discourse.lean_admission(path.read_bytes(), tmp_path), "joint_formula": "DEEP"}])
    depth = 200_000
    deep = '["or", ["top"], ' * depth + '["top"]' + "]" * depth
    with pytest.raises(ValueError):
        _decode_json(row.replace('"DEEP"', deep).encode())
