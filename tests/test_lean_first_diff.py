"""`tools/lean_first_diff.py`: the base-against-head comparison of the lean-first gate (5.1 item 2)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

import pytest

from tools import lean_first_diff as diff
from ve.backends.service_schema import same_json
from ve.errors import CheckerUnavailable, InvalidModel, UnknownSymbol

ROOT = Path(__file__).resolve().parents[1]
SOURCE, OTHER_SOURCE = "0" * 64, "1" * 64
ENV_ID, OTHER_ENV_ID = "e" * 64, "f" * 64
# The records are of the conformance corpus's `environment` operation unless named otherwise.
OK = {"returned": {"environment_id": ENV_ID, "record": {"values": [True]}}}
REJECTED = {"raised": {"code": "UnknownSymbol", "message": "UnknownSymbol: Unknown predicate 'p'"}}
MODEL_OK = {"returned": {"model_id": ENV_ID, "record": {}}}
GROUP = ("conformance", "python")


def _write(path: Path, outcomes: dict, source=SOURCE, authority="python", corpus="conformance") -> str:
    """One record per case; a case `name#op` is case `name` of operation `op` (default `environment`,
    a pilot's `document_check`)."""
    def record(case, outcome):
        name, _, op = case.partition("#")
        if corpus == "pilots":
            return {"corpus": corpus, "authority": "default", "case": name, "op": "document_check",
                    "source_sha256": hashlib.sha1(name.encode()).hexdigest(), "outcome": outcome}
        return {"corpus": corpus, "authority": authority, "case": f"evaluation/{name}", "op": op or "environment",
                "source_sha256": source, "outcome": outcome}
    path.write_text("".join(json.dumps(record(case, outcome)) + "\n" for case, outcome in outcomes.items()))
    return str(path)


# An accepted and a rejected input, the same on both sides, as every real corpus holds.
CONTROLS = {"control-accepted": OK, "control-rejected": REJECTED}


def _cases(cases, corpus="conformance"):
    return {(f"evaluation/{case}" if corpus == "conformance" else case): ops for case, ops in cases.items()}


def _expected(expected: dict, corpus="conformance") -> dict:
    """`expected_cases`' form of {group: cases}: a set names cases recorded through their one operation
    (`environment`, a pilot's `document_check`); a dict gives each case its operations' function."""
    op = "document_check" if corpus == "pilots" else "environment"
    return {group: _cases(cases if isinstance(cases, dict) else {case: diff.only(op) for case in cases}, corpus)
            for group, cases in expected.items()}


def _compare(tmp_path, base, head, delta=None, base_source=SOURCE, head_source=SOURCE, expected=None,
             controls=True, corpus="conformance"):
    group = GROUP if corpus == "conformance" else ("pilots", "default")
    if controls:
        base, head = {**CONTROLS, **base}, {**CONTROLS, **head}
    if expected is None:
        expected = {group: {case.split("#")[0] for case in [*base, *head]}}
    elif controls:
        expected = {key: {**{case: diff.only("environment") for case in CONTROLS},
                          **(cases if isinstance(cases, dict) else {case: diff.only("environment") for case in cases})}
                    for key, cases in expected.items()}
    return diff.compare(_write(tmp_path / "base.jsonl", base, base_source, corpus=corpus),
                        _write(tmp_path / "head.jsonl", head, head_source, corpus=corpus), delta,
                        expected=_expected(expected, corpus))


def _entry(case, **fields):
    return {"corpus": "conformance", "authority": "python", "case": f"evaluation/{case}", "op": "environment",
            **fields}


def test_identical_runs_have_no_difference(tmp_path):
    result = _compare(tmp_path, {"a": OK, "b": REJECTED}, {"a": OK, "b": REJECTED}, controls=False)
    assert result["totals"] == {"same": 2} and result["unlisted"] == 0


@pytest.mark.parametrize("head, klass", [
    ({"returned": {"environment_id": ENV_ID, "record": {"values": [False]}}}, "verdict"),
    ({"returned": {"environment_id": OTHER_ENV_ID, "record": {"values": [True]}}}, "verdict"),
    ({"returned": {"environment_id": ENV_ID, "record": {}}}, "verdict"),
    ({"raised": {"code": "CheckerUnavailable", "message": "CheckerUnavailable: down"}}, "availability"),
    (REJECTED, "verdict"),
])
def test_each_change_of_an_answer_is_classed(tmp_path, head, klass):
    result = _compare(tmp_path, {"a": OK, "b": OK}, {"a": head, "b": OK})
    assert [row["class"] for row in result["differences"]] == [klass] and result["unlisted"] == 1


def test_a_rejection_with_another_code_is_order_and_its_text_alone_is_wording(tmp_path):
    other = {"raised": {"code": "TypeMismatch", "message": "TypeMismatch: x"}}
    reworded = {"raised": {"code": "UnknownSymbol", "message": "Unknown predicate 'p'"}}
    result = _compare(tmp_path, {"a": REJECTED, "b": reworded}, {"a": other, "b": REJECTED})
    assert [row["class"] for row in result["differences"]] == ["order", "wording"]


def test_only_signed_wording_pairs_and_records_are_accepted(tmp_path):
    reworded = {"raised": {"code": "UnknownSymbol", "message": "Unknown predicate 'p'"}}
    pair = {"base": "Unknown predicate 'p'", "head": "UnknownSymbol: Unknown predicate 'p'"}
    assert _compare(tmp_path, {"a": reworded}, {"a": REJECTED}, {"wording": [pair]})["unlisted"] == 0
    assert _compare(tmp_path, {"a": reworded}, {"a": REJECTED},
                    {"wording": [{**pair, "head": "other"}]})["unlisted"] == 1
    changed = {"returned": {"environment_id": ENV_ID, "record": {"values": [False]}}}
    entry = _entry("a", base=OK, head=changed)
    assert _compare(tmp_path, {"a": OK}, {"a": changed}, {"verdict": [entry]})["unlisted"] == 0
    assert _compare(tmp_path, {"a": OK}, {"a": changed}, {"order": [entry]})["unlisted"] == 1
    assert _compare(tmp_path, {"a": OK}, {"a": changed}, {"verdict": [{**entry, "head": OK}]})["unlisted"] == 1


def test_a_reports_description_is_one_wording_pair(tmp_path):
    """Batch 3: a report's `checked_by` changes as a whole (a member dropped included) and is wording, accepted
    only when its canonical texts are a signed pair; a verdict beside it is still a verdict. A pilot's report
    that is a JSON object is recorded parsed (`pilot_check`), so its members are compared one by one."""
    def pilot(checked_by, sets=1):
        return {"exit": 0, "stdout": {"readings": {"checked_by": checked_by, "sets": sets}}, "stderr": []}
    rejected = {"r": {"exit": 1, "stdout": "{}", "stderr": []}}
    base, head = {"a": pilot({"lean": "L", "rust": "R"}), **rejected}, {"a": pilot({"lean": "L"}), **rejected}
    pair = {"base": '{"lean": "L", "rust": "R"}', "head": '{"lean": "L"}'}

    def compare(head, delta=None):
        return _compare(tmp_path, base, head, delta, controls=False, corpus="pilots")
    result = compare(head, {"wording": [pair]})
    assert [row["class"] for row in result["differences"]] == ["wording"] and result["unlisted"] == 0
    assert compare(head)["unlisted"] == 1
    result = compare({**head, "a": pilot({"lean": "L"}, sets=2)}, {"wording": [pair]})
    assert [row["class"] for row in result["differences"]] == ["verdict"] and result["unlisted"] == 1


def _after_op(held):
    """Case `a`'s operations: `environment`, then `model` when it returned (as `CONFORMANCE_OPS` chains)."""
    return {"environment"} | ({"model"} if "returned" in (held.get("environment") or {}) else set())


def test_a_missing_record_is_a_difference(tmp_path):
    """An operation that runs on one side only, since what it builds on returned there only."""
    result = _compare(tmp_path, {"a": OK, "a#model": MODEL_OK}, {"a": REJECTED}, expected={GROUP: {"a": _after_op}})
    assert result["unlisted"] == 2
    assert [(row["op"], row["class"], row["head"]) for row in result["differences"]] == [
        ("environment", "verdict", REJECTED), ("model", "verdict", None)]


# lf-0 looprecheck1 B1: a recording holds every operation each case requires, not only the case.

@pytest.mark.parametrize("base, head", [
    ({"a": OK, "a#model": MODEL_OK}, {"a": OK}),                 # a required operation dropped
    ({"a": OK}, {"a": OK}),                                      # ... on both sides
    ({"a": REJECTED, "a#model": MODEL_OK}, {"a": REJECTED}),     # an operation nothing requires
    ({"a": OK, "a#model": MODEL_OK, "a#canonicalize": {"returned": "x."}},
     {"a": OK, "a#model": MODEL_OK, "a#canonicalize": {"returned": "x."}}),
])
def test_a_recording_must_hold_exactly_the_operations_of_each_case(tmp_path, base, head):
    with pytest.raises(diff.Unusable, match="does not hold the conformance/python operations"):
        _compare(tmp_path, base, head, expected={GROUP: {"a": _after_op}})
    # A probe or pilot case is recorded through its one operation.
    with pytest.raises(diff.Unusable, match="operations"):
        _compare(tmp_path, {"a": OK}, {"a": OK}, expected={GROUP: {"a": diff.only("parse")}})


def test_runs_over_different_corpus_files_are_refused(tmp_path):
    with pytest.raises(diff.Unusable, match="different corpus files"):
        _compare(tmp_path, {"a": OK}, {"a": OK}, head_source=OTHER_SOURCE)


# lf-0 review B3: evidence that cannot show preservation gives no verdict.

def test_empty_recordings_are_unusable(tmp_path):
    with pytest.raises(diff.Unusable, match="does not hold"):
        _compare(tmp_path, {}, {}, expected={GROUP: {"a"}}, controls=False)
    with pytest.raises(diff.Unusable, match="no case"):
        _compare(tmp_path, {}, {}, expected={GROUP: set()}, controls=False)
    with pytest.raises(diff.Unusable, match="no recording"):
        diff.compare(str(tmp_path / "absent"), str(tmp_path / "absent"), None,
                     expected=_expected({GROUP: {"a"}}))


@pytest.mark.parametrize("base, head", [
    ({"a": OK}, {"a": OK, "b": OK}),            # a case missing on one side
    ({"a": OK, "b": OK}, {"a": OK}),
    ({"a": OK, "b": OK, "z": OK}, {"a": OK, "b": OK, "z": OK}),  # a case the corpus does not define
])
def test_a_recording_must_hold_exactly_the_corpus(tmp_path, base, head):
    with pytest.raises(diff.Unusable, match="does not hold"):
        _compare(tmp_path, base, head, expected={GROUP: {"a", "b"}})


def test_a_missing_authority_is_unusable(tmp_path):
    with pytest.raises(diff.Unusable, match="conformance/lean"):
        _compare(tmp_path, {"a": OK}, {"a": OK}, expected={GROUP: {"a"}, ("conformance", "lean"): {"a"}})


DOWN = {"raised": {"code": "CheckerUnavailable", "message": "CheckerUnavailable: down"}}
PILOT_DOWN = {"exit": 5, "stderr": [], "stdout": '{"status": "CheckerUnavailable"}'}


@pytest.mark.parametrize("down, corpus", [(DOWN, "conformance"), (PILOT_DOWN, "pilots"), ({"timeout": 600}, "pilots")],
                         ids=["raised", "pilot-exit", "pilot-timeout"])
def test_wholly_unavailable_recordings_are_unusable(tmp_path, down, corpus):
    with pytest.raises(diff.Unusable, match=r"every \w+/\w+ record is unavailable"):
        _compare(tmp_path, {"a": down, "b": down}, {"a": down, "b": down}, controls=False, corpus=corpus)


@pytest.mark.parametrize("constant, corpus", [(OK, "conformance"), (REJECTED, "conformance"),
                                              ({"exit": 0, "stdout": "{}", "stderr": []}, "pilots"),
                                              ({"exit": 1, "stdout": "{}", "stderr": []}, "pilots")],
                         ids=["accepted", "rejected", "pilot-exit-0", "pilot-exit-1"])
def test_constant_answer_recordings_are_unusable(tmp_path, constant, corpus):
    """Two recordings of a checker that accepts (or rejects) everything compare equal: no evidence."""
    with pytest.raises(diff.Unusable, match=r"every \w+/\w+ record is"):
        _compare(tmp_path, {"a": constant, "b": constant}, {"a": constant, "b": constant}, controls=False,
                 corpus=corpus)


def test_a_record_unavailable_on_both_sides_needs_a_signed_reason(tmp_path):
    entry = _entry("b")
    other = {"raised": {"code": "CheckerUnavailable", "message": "CheckerUnavailable: other"}}
    for head in (DOWN, other):
        result = _compare(tmp_path, {"a": OK, "b": DOWN}, {"a": OK, "b": head})
        assert result["unlisted"] == 1 and result["differences"][0]["class"] == "unavailable"
        assert _compare(tmp_path, {"a": OK, "b": DOWN}, {"a": OK, "b": head},
                        {"unavailable": [{**entry, "reason": "the readings route needs 1,540 s"}]})["unlisted"] == 0
        for reason in ({}, {"reason": ""}, {"reason": 7}):
            assert _compare(tmp_path, {"a": OK, "b": DOWN}, {"a": OK, "b": head},
                            {"unavailable": [{**entry, **reason}]})["unlisted"] == 1
    # A signed unavailable record does not accept an availability change.
    result = _compare(tmp_path, {"a": OK, "b": DOWN}, {"a": OK, "b": OK},
                      {"unavailable": [{**entry, "reason": "r"}]})
    assert result["unlisted"] == 1 and result["differences"][0]["class"] == "availability"


def test_the_command_exits_2_on_unusable_evidence(tmp_path):
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")
    assert diff.main(["compare", str(empty), str(empty), "--corpus", "conformance", "--authority", "python"]) == 2


def test_expected_cases_come_from_the_corpora():
    expected = diff.expected_cases(ROOT, ("probe", "conformance"), ("python", "lean"))
    assert set(expected) == {("probe", "python"), ("probe", "lean"), ("conformance", "python"),
                             ("conformance", "lean")}
    baseline = json.loads((ROOT / diff.PROBE_BASELINE).read_text())
    assert len(expected["probe", "lean"]) == len(baseline["cells"]) + sum(
        len(baseline[section]) for section in diff.PROBE_SECTIONS) > 0
    assert len(expected["conformance", "python"]) == sum(
        len(json.loads((ROOT / f"conformance/{name}.json").read_text())) for name in diff.CONFORMANCE)


# lf-0 review C: type changes are differences.

@pytest.mark.parametrize("old, new", [([True], [1]), ([False], [0]), ([1], [1.0]), ([0], [False])])
def test_a_type_change_is_a_verdict_difference(tmp_path, old, new):
    base = {"returned": {"environment_id": ENV_ID, "record": {"values": old}}}
    head = {"returned": {"environment_id": ENV_ID, "record": {"values": new}}}
    result = _compare(tmp_path, {"a": base}, {"a": head})
    assert [row["class"] for row in result["differences"]] == ["verdict"] and result["unlisted"] == 1
    entry = _entry("a", base={"returned": {"environment_id": ENV_ID, "record": {"values": new}}}, head=head)
    # A listed entry naming the other type does not accept it either.
    assert _compare(tmp_path, {"a": base}, {"a": head}, {"verdict": [entry]})["unlisted"] == 1
    assert _compare(tmp_path, {"a": base}, {"a": head}, {"verdict": [{**entry, "base": base}]})["unlisted"] == 0


def test_public_records_are_mig3s():
    assert diff.outcome(lambda: (_ for _ in ()).throw(UnknownSymbol("x"))) == {
        "raised": {"code": "UnknownSymbol", "message": "UnknownSymbol: x"}}
    assert diff.outcome(lambda: (_ for _ in ()).throw(InvalidModel("InvalidModel(g): y", generator="g")))[
        "raised"]["generator"] == "g"
    assert diff.outcome(lambda: (_ for _ in ()).throw(CheckerUnavailable("CheckerUnavailable: z")))[
        "raised"]["code"] == "CheckerUnavailable"
    assert diff.public({"record_id": 1, "checker_build": 2, "kept": (1, 2)}) == {"kept": [1, 2]}


def test_the_conformance_corpus_records_every_operation(monkeypatch):
    """The recorder and the completeness check read one table (`CONFORMANCE_OPS`): a recording is
    complete, and the looprecheck1 B1 reproducer, the same recording with only its `environment`
    records, or without one later operation, is unusable."""
    monkeypatch.setenv("VE_AUTHORITY", "python")
    monkeypatch.setattr(diff, "CONFORMANCE", ("validation", "countermodels", "closure"))
    records = {("conformance", "python", r["case"], r["op"]): {"outcome": r["outcome"]}
               for r in diff.conformance_records(ROOT, "python")}
    assert {key[3] for key in records} == {op for op, _, _ in diff.CONFORMANCE_OPS}
    expected = diff.expected_cases(ROOT, ("conformance",), ("python",))
    assert {key[2] for key in records} == expected["conformance", "python"].keys()
    diff.completeness("recording", records, expected)
    environment_only = {key: row for key, row in records.items() if key[3] == "environment"}
    assert len(environment_only) < len(records)
    with pytest.raises(diff.Unusable, match="required operations missing"):
        diff.completeness("recording", environment_only, expected)
    for op, _, _ in diff.CONFORMANCE_OPS[1:]:
        dropped = next(key for key in records if key[3] == op)
        with pytest.raises(diff.Unusable, match=re.escape(f"1 required operations missing (first {dropped[2:]!r})")):
            diff.completeness("recording", {k: v for k, v in records.items() if k != dropped}, expected)


def test_a_message_with_a_line_separator_is_one_record(tmp_path):
    base = {"a": {"raised": {"code": "InvalidInput", "message": "x y\x85z"}}}
    path = _write(tmp_path / "r.jsonl", base)
    assert len(diff.load(path)) == 1


# lf-0 fix3 B1: every recording line is checked against the recorder's schema before it is used.

def _recording(tmp_path, name, records) -> str:
    path = tmp_path / name
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
    return str(path)


@pytest.fixture(scope="module")
def conformance_recording():
    """A genuine recording of three conformance files under Python, and their expected cases."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("VE_AUTHORITY", "python")
        patch.setattr(diff, "CONFORMANCE", ("validation", "countermodels", "closure"))
        records = [{"corpus": "conformance", "authority": "python", **r}
                   for r in diff.conformance_records(ROOT, "python")]
        expected = diff.expected_cases(ROOT, ("conformance",), ("python",))
    return records, expected


def test_the_fix3_reproducer_empty_outcomes_are_unusable(tmp_path, conformance_recording):
    """The recheck's reproducer: only the environment records, successful outcomes replaced by `{}`.
    Without the schema the empty outcomes suppressed every later operation and counted as acceptances."""
    records, expected = conformance_recording
    whole = _recording(tmp_path, "whole.jsonl", records)
    again = _recording(tmp_path, "again.jsonl", records)
    assert diff.compare(whole, again, None, expected=expected)["unlisted"] == 0
    emptied = [{**r, "outcome": {} if "returned" in r["outcome"] else r["outcome"]}
               for r in records if r["op"] == "environment"]
    path = _recording(tmp_path, "emptied.jsonl", emptied)
    with pytest.raises(diff.Unusable, match=r"line \d+ is no record the recorder writes"):
        diff.compare(path, _recording(tmp_path, "emptied-again.jsonl", emptied), None, expected=expected)
    with pytest.raises(diff.Unusable, match="no record the recorder writes"):
        diff.compare(whole, path, None, expected=expected)


def _pilot_record(tmp_path):
    document = ROOT / "usecases/bluedot-grant/causal.ve.md"
    env = {**__import__("os").environ, "PYTHONPATH": str(ROOT)}
    env.pop("VE_AUTHORITY", None)
    blob = hashlib.sha1(b"blob %d\0" % document.stat().st_size + document.read_bytes()).hexdigest()
    return {"corpus": "pilots", "authority": "default", "case": "pilot/x:usecases/causal.ve.md",
            "op": "document_check", "source_sha256": blob, "outcome": diff.pilot_check(ROOT, document, env)}


def _genuine(records, tmp_path):
    """One genuine record of each shape: every conformance operation's returned and raised outcome
    (with and without span or path), every probe operation's cell kinds and sections, a pilot."""
    baseline = json.loads((ROOT / diff.PROBE_BASELINE).read_text())
    probes = [{"corpus": "probe", "authority": "python", **r}
              for r in diff.probe_rows(baseline, diff.digest(ROOT / "tests/probe_matrix.py"))]
    def shape(r):
        o = r["outcome"]
        kind = ("raised", tuple(sorted(o["raised"]))) if "raised" in o else ("returned",) if "returned" in o \
            else (o.get("cell"), tuple(sorted(o))) if r["op"] != "budget_boundaries" else tuple(sorted(o))
        return (r["corpus"], r["op"] if r["corpus"] == "conformance" or r["op"].endswith(("probes", "boundaries"))
                else "cell", kind)
    out = {}
    for r in [*records, *probes]:
        out.setdefault(shape(r), r)
    out[("pilots",)] = _pilot_record(tmp_path)
    return out


# The payloads `compare` diffs as typed JSON (any change is a difference the delta must sign): an
# environment's or model's record, a formula, a trace, a graph package or report, a success's output,
# an error's structured diagnostic, a pilot's report. A mutant replaces a payload whole; its interior is
# content.
PAYLOADS = {"record", "explanation", "package", "diagnostic", "stdout"}


def _payload(path, parent) -> bool:
    return bool(path) and (path[-1] in PAYLOADS or path[-2:] == ("formulas", 0) or path[-1] == "output" and (
        parent.get("cell") == "S" or "package" in parent))


def _nodes(value, path=(), parent=None):
    """Every node of `value` with its path and parent (a list through its first element), payloads as leaves."""
    yield path, value, parent or {}
    if _payload(path, parent or {}):
        return
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _nodes(item, path + (key,), value)
    elif isinstance(value, list) and value:
        yield from _nodes(value[0], path + (0,), {})


# What the producers write only when set (`VEError.to_dict`, `CheckerUnavailable.to_dict`, a section's
# probe outcome), and the fields whose value may be null (`Optional`).
OPTIONAL = {"path", "span", "diagnostic", "generator", "operation", "backend", "routed", "backend_rejection"}
NULLABLE = {"value", "conclusion_value", "explanation"}


def _producible(path, parent, value, new) -> bool:
    """Whether the recorder can write `new` where it wrote `value`, as far as the types go."""
    if new is _DROP:
        return path[-1] in OPTIONAL
    if type(new) is type(value) or new is None and path[-1] in NULLABLE:
        return True
    # A success's result is any JSON; a pilot's report is a JSON object or its raw text.
    return path[-1] == "output" and parent.get("cell") == "S" or path[-1] == "stdout" and type(new) in (dict, str)


_DROP = object()
# Each field dropped, emptied ("" [] {}), nulled and retyped (7, true, a string).
_REPLACEMENTS = {"drop": _DROP, "empty-text": "", "empty-array": [], "empty-object": {}, "null": None,
                 "number": 7, "true": True, "text": "x"}


def _replace(value, path, new):
    if not path:
        return new
    out = dict(value) if isinstance(value, dict) else list(value)
    if new is _DROP and len(path) == 1:
        del out[path[0]]
    else:
        out[path[0]] = _replace(value[path[0]], path[1:], new)
    return out


def test_every_mutated_record_is_unusable(tmp_path, conformance_recording):
    """Table-driven over every field of one genuine record of each shape: dropped, emptied, nulled and
    retyped, a record the recorder cannot write is unusable evidence. A mutant the recorder can write
    (`_producible`: a value of the same kind, null where null is a value, an optional field dropped)
    that the schema admits is another outcome: `compare` judges its content (its class and the delta)."""
    genuine = _genuine(conformance_recording[0], tmp_path)
    assert {key[:2] for key in genuine} >= {("conformance", op) for op, _, _ in diff.CONFORMANCE_OPS} | {
        ("probe", "cell"), ("probe", "graph_probes"), ("probe", "budget_boundaries"), ("probe", "feature_probes"),
        ("pilots",)}
    refused, content, wrong = 0, 0, []
    for key, record in genuine.items():
        assert diff.record_problem(record) is None, key
        for path, value, parent in _nodes(record):
            if not path:
                continue
            for label, new in _REPLACEMENTS.items():
                if new is not _DROP and same_json(new, value) or new is _DROP and isinstance(path[-1], int):
                    continue
                mutant = _replace(record, path, new)
                if _producible(path, parent, value, new) and diff.record_problem(mutant) is None:
                    content += 1
                    continue
                try:
                    diff.load(_recording(tmp_path, "mutant.jsonl", [mutant]))
                    wrong.append(f"{key} {'.'.join(map(str, path))} {label}: accepted")
                except diff.Unusable:
                    refused += 1
    assert not wrong, "\n".join(wrong)
    assert refused > 5 * content > 0


@pytest.mark.parametrize("change", ["conformance-file", "probe-matrix", "duplicate-field"])
def test_records_of_one_corpus_file_name_one_digest(tmp_path, change):
    """Mixed identity: two records of one corpus file with different digests, or a line naming a
    field twice (the second would win), is unusable."""
    cell = {"corpus": "probe", "authority": "python", "op": "typing", "source_sha256": SOURCE,
            "outcome": {"cell": "S", "status": "accepted", "output": None}}
    if change == "conformance-file":
        lines = [json.dumps({"corpus": "conformance", "authority": "python", "case": f"evaluation/{name}",
                             "op": "environment", "source_sha256": source, "outcome": OK})
                 for name, source in (("a", SOURCE), ("b", OTHER_SOURCE))]
    elif change == "probe-matrix":
        lines = [json.dumps({**cell, "case": "a"}), json.dumps({**cell, "case": "b", "authority": "lean",
                                                                 "source_sha256": OTHER_SOURCE})]
    else:
        lines = [json.dumps({**cell, "case": "a"})[:-1] + ', "case": "b"}']
    path = tmp_path / "r.jsonl"
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(diff.Unusable, match="another digest|duplicate field"):
        diff.load(str(path))
    # The control: the same records with one digest are usable.
    if change != "duplicate-field":
        path.write_text("\n".join(line.replace(OTHER_SOURCE, SOURCE) for line in lines) + "\n")
        assert len(diff.load(str(path))) == 2


@pytest.mark.parametrize("outcome", [
    {}, {"returned": None}, {"raised": None}, {"raised": {"code": "UnknownSymbol"}},
    {"raised": {"code": "UnknownSymbol", "message": None}}, {"raised": {"message": "x"}},
    {"raised": {"code": "", "message": "x"}}, {"returned": "x.", "raised": REJECTED["raised"]},
], ids=["empty", "null-returned", "null-raised", "no-message", "null-message", "no-code", "empty-code", "both"])
def test_an_outcome_the_recorder_cannot_write_is_unusable(tmp_path, outcome):
    with pytest.raises(diff.Unusable, match="no record the recorder writes"):
        _compare(tmp_path, {"a#canonicalize": outcome}, {"a#canonicalize": {"returned": "x."}})


def test_the_schema_names_every_operation_of_the_recorder():
    """The schema's conformance operations are `CONFORMANCE_OPS`', and its probe sections `PROBE_SECTIONS`."""
    schema = json.loads((diff.SCHEMA / "record.json").read_text())["$defs"]
    assert schema["conformance"]["properties"]["op"]["enum"] == [op for op, _, _ in diff.CONFORMANCE_OPS]
    branches = schema["probe"]["allOf"]
    assert branches[-1]["if"]["properties"]["op"]["not"]["enum"] == list(diff.PROBE_SECTIONS)
    assert [b["if"]["properties"]["op"]["const"] for b in branches[:-1]] == list(diff.PROBE_SECTIONS)


def test_readings_records_are_checked_against_their_schema(tmp_path):
    """Batch 3's readings corpus: Lean's relayed row or the route's diagnostic, under the one authority
    `default`, read from the corpus file of one digest (`readings_records`); anything else is unusable."""
    from ve.errors import VEError

    def record(outcome, **fields):
        return {"corpus": "readings", "authority": "default", "case": "differential/c0", "op": "readings_validate",
                "source_sha256": SOURCE, "outcome": outcome, **fields}
    row = {"id": "readings-s1", "status": "ok", "content_bearing": False}
    accepted = record(diff.outcome(lambda: row))
    rejected = record(diff.outcome(lambda: (_ for _ in ()).throw(VEError("ReadingInterface: rs1: twin-only"))))
    assert diff.record_problem(accepted) is None and diff.record_problem(rejected) is None
    for bad in (record({}), record({"returned": {**row, "status": "error"}}),
                record({"returned": {k: v for k, v in row.items() if k != "content_bearing"}}),
                record({"raised": {"message": "x"}}), record(accepted["outcome"], authority="lean"),
                record(accepted["outcome"], op="document_check"), record(accepted["outcome"], source_sha256="x")):
        assert diff.record_problem(bad) is not None, bad
    assert diff.authorities_of("readings") == ("default",)
    names = diff.readings_cases()
    assert names[:2] == ["differential/c0", "differential/c1"] and len(names) == len(set(names)) > diff.READINGS_COUNT
    expected = diff.expected_cases(ROOT, ("readings",))
    assert list(expected) == [("readings", "default")] and set(expected["readings", "default"]) == set(names)


# lf-1 review B and rechecks B and 3 B (the class of route_parity.py's empty pass), on the lf-0 evidence rules.

def test_compare_refuses_the_same_file(tmp_path):
    run = _write(tmp_path / "run.jsonl", {**CONTROLS, "a": OK})
    with pytest.raises(diff.Unusable, match="same file"):
        diff.compare(run, run, None, expected=_expected({GROUP: {*CONTROLS, "a"}}))
    assert diff.main(["compare", run, run, "--corpus", "conformance", "--authority", "python"]) == 2


def test_a_delta_entry_without_its_outcomes_lists_nothing(tmp_path):
    """A listed record must name both outcomes: an entry without `head` used to accept a record missing
    from HEAD (None == None)."""
    entry = {"corpus": "conformance", "authority": "python", "case": "evaluation/a", "op": "model", "base": MODEL_OK}
    delta = {"verdict": [_entry("a", base=OK, head=REJECTED), entry]}
    result = _compare(tmp_path, {"a": OK, "a#model": MODEL_OK}, {"a": REJECTED}, delta,
                      expected={GROUP: {"a": _after_op}})
    assert result["unlisted"] == 1
    delta["verdict"][1] = {**entry, "head": None}
    assert _compare(tmp_path, {"a": OK, "a#model": MODEL_OK}, {"a": REJECTED}, delta,
                    expected={GROUP: {"a": _after_op}})["unlisted"] == 0


def test_a_delta_listing_a_record_twice_is_unusable(tmp_path):
    """The latency tool's overwrite class (lf-1 recheck B): a record listed in two entries kept only the last."""
    changed = {"returned": {"environment_id": ENV_ID, "record": {"values": [False]}}}
    entry = _entry("a", base=OK, head=changed)
    for delta in ({"verdict": [entry, entry]}, {"order": [{**entry, "head": REJECTED}], "verdict": [entry]}):
        with pytest.raises(diff.Unusable, match="twice"):
            _compare(tmp_path, {"a": OK}, {"a": changed}, delta)


@pytest.mark.parametrize("old, new", [(True, 1), (False, 0), (1, 1.0), (0, False), (1.0, 1), (0, -0.0)])
def test_a_retyped_value_is_a_verdict_change(old, new):
    """lf-1 recheck 3 B: the comparison is type-strict JSON equality (`service_schema.same_json`)."""
    assert diff.change_class({"returned": {"values": [old]}}, {"returned": {"values": [new]}}) == "verdict"
    assert not diff.same(old, new)


def test_a_wording_pair_matches_only_its_own_types(tmp_path):
    """A signed pair names its texts exactly, as JSON: the text `1` is not the number 1."""
    base = {"raised": {"code": "UnknownSymbol", "message": "1"}}
    head = {"raised": {"code": "UnknownSymbol", "message": "2"}}
    assert _compare(tmp_path, {"a": base}, {"a": head}, {"wording": [{"base": "1", "head": "2"}]})["unlisted"] == 0
    for pair in ({"base": 1, "head": "2"}, {"base": True, "head": "2"}, {"base": "1", "head": 2.0}):
        assert _compare(tmp_path, {"a": base}, {"a": head}, {"wording": [pair]})["unlisted"] == 1


@pytest.mark.parametrize("case", [1, True, None, 1.0, ["a"]])
def test_a_record_key_that_is_not_a_string_is_unusable(tmp_path, case):
    """Keys `1` and `true` would pair two different records (Python hashes them alike): a record is refused
    by the recorder's schema, a delta entry by its key."""
    path = tmp_path / "r.jsonl"
    path.write_text(json.dumps({"corpus": "conformance", "authority": "python", "case": case, "op": "environment",
                                "source_sha256": SOURCE, "outcome": OK}) + "\n")
    with pytest.raises(diff.Unusable):
        diff.load(str(path))
    entry = {**_entry("a", base=OK, head=OK), "case": case}
    with pytest.raises(diff.Unusable, match="must be strings"):
        _compare(tmp_path, {"a": OK}, {"a": OK}, {"verdict": [entry]})


def test_stage2_parity_classifies_a_retyped_output_as_a_change():
    """The same class in `tools/stage2_parity.py`: its projection was compared with `==`."""
    from tools import stage2_parity
    row = {"cell": "A", "status": "ok", "output": {"values": [True]}}
    assert stage2_parity._classify(row, dict(row)) .startswith("same")
    for new in (1, 1.0):
        assert stage2_parity._classify(row, {**row, "output": {"values": [new]}}) == "different"
