"""S2's row (`readings-elaborate`) is relayed as Lean's answer bound to the request it asked about (R8; AR-17).

`ve/readings_route.py` `elaborate` regenerates nothing: the route, the finding, the choices, the counts and the
elaborated vocabulary, units, slot, names and sizes are Lean's. Python checks the row's schema and its binding: every
set, version, unit, narrowing, coupling, label and choice it names is the request's, counts and indexes are within
the request, and no entry is extra. Genuine answers of the Lean route are mutated one and two faults at a time (every
member dropped, emptied, retyped, duplicated, reordered, a string forged, a number pushed out of range): a fault in
what the row names is `CheckerUnavailable`; a fault in a value Lean derives is relayed as Lean's, unchanged; nothing
else escapes. The tests of the Python regeneration this batch deleted are converted here to Lean's answer on the
same input."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tests.test_readings_s1_lean import env_k, k1_document, lean, norm, reading, reading_set  # noqa: F401
from tests.test_soft_norms_lean import ranks
from ve import readings_route
from ve.errors import CheckerUnavailable, VEError

ROOT = Path(__file__).resolve().parents[1]
FORGED = "zz-forged"
RETYPED = {"null": None, "int": 7, "str": "7", "list": [], "dict": {}, "bool": True}
ASKS_ALL = ["forall", "agent", ["forall", "user", ["binary", "asks", ["var", 1], ["var", 0]]]]
# Members whose values Lean derives (D1): mutated at the root and one level below, a mutant there is relayed
# unchanged or refused by the schema, never anything else. The keys of `generated_predicates` and a precedence
# cause name the request; their forgeries are the tests below (review F1 of AR-17).
DERIVED = (("vocabulary",), ("sizes",), ("generated_predicates",), ("finding", "cause"), ("slot", "*", "ast"),
           ("units", "*", "content"), ("error",))
# Faults in a bound member that leave every name bound: the result is Lean's to give (D1).
RELAYED = {(("choices",), "reorder"), (("units",), "reorder"), (("slot",), "reorder"),  # Lean's order
           (("names", "*", "candidates", "*", "names"), "reorder"),
           (("slot",), "empty"), (("slot", "*"), "drop"),  # which premises the slot holds; each kept label is bound
           (("narrowings_stale",), "empty"), (("narrowings_stale", "*"), "drop"),  # which narrowings are stale
           (("finding",), "retype:null")}  # whether the document superposes


def _stale_case():
    """K1 under a fixed child of its interface rule, with `rs1` recorded again at version 2 and a narrowing left on
    version 1: superposed, one stale narrowing, fixed and reading units in `sup D`."""
    raw = env_k()
    document, _ = k1_document(raw, fixed_units=[
        ("u0", norm("stop-x", "avoid_required", False, over=("no-deception",))), ("u2", ["top"])])
    document["reading_sets"].append({**copy.deepcopy(document["reading_sets"][0]), "version": 2})
    document["narrowings"] = [{"id": "n0", "set": "rs1", "version": 1, "keeps": ["strict"], "by": "reviewer",
                               "reason_spans": ["u2"]}]
    return raw, document


def _holistic_case():
    """M10b of lean/VE/Readings/Examples.lean on K1's vocabulary: two sets whose default readings, ranked `lo` and
    `hi` under holistic outranking, collide on one act, the first switchable by `user`. Superposed with an
    `outweighs` decision and its shared slot label, and exception and switch decisions in the name map."""
    raw = env_k()
    raw["vocabulary"]["soft"] = ranks(["hi", "lo"], "holistic", parties=("user",))
    document, _ = k1_document(raw)
    rs1 = document["reading_sets"][0]
    rs1["readings"][1]["content"]["norm"].update(rank="lo", alterable=["user"])
    rs2 = {**copy.deepcopy(rs1), "id": "rs2", "unit": "u2"}
    rs2["readings"][0]["content"] = norm("be-firm", "avoid_required", False)
    rs2["readings"][1]["content"] = norm("be-firm", "avoid_required", False, "default")
    rs2["readings"][1]["content"]["norm"]["rank"] = "hi"
    document["units"].append({"id": "u2"})
    document["reading_sets"].append(rs2)
    return raw, document


def _recorded():
    """The genuine `readings-elaborate` documents the suite recorded (tests/data/route-cases.jsonl), each once."""
    seen = {}
    for line in (ROOT / "tests/data/route-cases.jsonl").read_text().splitlines():
        mode, case = json.loads(line)
        if mode == "readings-route" and case.get("kind") == "readings-elaborate":
            seen.setdefault(json.dumps([case["environment"], case["document"]], sort_keys=True),
                            (case["environment"], case["document"]))
    return list(seen.values()) + [_stale_case(), _holistic_case()]


def _ask(raw, document, row=None):
    """`elaborate` on `document`; with `row`, the Lean route answers `row`. Returns the relayed answer,
    `("refused", text)` for a relayed refusal, or `("unavailable",)`."""
    real, sent = readings_route.run_lean, []

    def answer(cases, **options):
        sent.extend(real(cases, **options) if row is None else [copy.deepcopy(row)])
        return sent
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(readings_route, "run_lean", answer)
        try:
            return readings_route.elaborate(raw, document["units"], document["reading_sets"],
                                            couplings=document.get("couplings", ()),
                                            narrowings=document.get("narrowings", ()))
        except CheckerUnavailable:
            return ("unavailable",)
        except VEError as exc:
            return ("refused", exc.message if hasattr(exc, "message") else str(exc))
        finally:
            _ask.last = sent[:1]


@pytest.fixture(scope="module")
def genuine(lean):  # noqa: F811
    """Each recorded document with Lean's own row."""
    answers = []
    for raw, document in _recorded():
        _ask(raw, document)
        answers.append((raw, document, _ask.last[0]))
    return answers


def _shown(row):
    """What the relay shows of `row` when it accepts it: the row without `id` and `status`, or its refusal."""
    if row.get("status") == "error" and "error" in row:
        return ("refused", row["error"])
    return {key: value for key, value in row.items() if key not in ("id", "status")}


def _pattern(path):
    return tuple("*" if type(key) is int else key for key in path)


def _root(path):
    """The derived root `path` lies under, or None."""
    return next((root for root in DERIVED if _pattern(path)[:len(root)] == root), None)


def _members(value, path=()):
    """Every member path of `value`; below a derived root only its direct members."""
    yield path
    root = _root(path)
    if root is not None and len(path) > len(root):
        return
    items = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else ()
    for key, item in items:
        yield from _members(item, (*path, key))


def _at(row, path):
    for key in path:
        row = row[key]
    return row


def _kinds(value):
    kinds = ["drop"] + (["empty"] if isinstance(value, (list, dict, str)) and value else [])
    kinds += ["retype:" + name for name, retyped in RETYPED.items() if type(retyped) is not type(value)]
    kinds += (["duplicate"] + (["reorder"] if value[::-1] != value else [])) if isinstance(value, list) and value else []
    return kinds + (["range"] if type(value) is int else []) + (["forge"] if type(value) is str else [])


def _faults(row):
    """Every (path, kind) of one fault in `row`."""
    return [(path, kind) for path in _members(row) if path for kind in _kinds(_at(row, path))]


def _fault(row, path, kind):
    """`row` with the fault `kind` at `path`, on a copy."""
    mutant = copy.deepcopy(row)
    parent, key = _at(mutant, path[:-1]), path[-1]
    value = parent[key]
    if kind == "drop":
        parent.pop(key)
    else:
        parent[key] = {"empty": lambda: type(value)(), "duplicate": lambda: value + [value[0]],
                       "reorder": lambda: value[::-1], "range": lambda: value + 1000,
                       "forge": lambda: FORGED}.get(kind, lambda: RETYPED[kind[len("retype:"):]])()
    return mutant


def _expect(row, path, kind):
    """`refused` for a fault in what the row names, `relayed` for one that leaves it bound, `either` for a fault
    in a value Lean derives (relayed, unless the schema refuses it)."""
    if _root(path) is not None:
        return "either"
    if (_pattern(path), kind) in RELAYED:
        return "relayed"
    if _pattern(path) == ("units", "*") and kind == "drop" and "set" not in _at(row, path):
        return "relayed"  # every reading's unit is bound; which fixed units are in force is Lean's
    return "refused"


def _check(raw, document, mutant, expected):
    got = _ask(raw, document, mutant)
    assert got == ("unavailable",) or got == _shown(mutant), (got, mutant)
    assert expected == "either" or (got == ("unavailable",)) is (expected == "refused"), (expected, got, mutant)


def test_genuine_answers_are_relayed_unchanged(genuine):
    for raw, document, row in genuine:
        assert _ask(raw, document, row) == _shown(row)
    routes = {row.get("route", row["status"]) for _, _, row in genuine}
    assert {"superposed", "enumerated", "error"} <= routes
    assert any(row.get("narrowings_stale") for _, _, row in genuine)


def test_one_fault_in_what_the_row_names_is_unavailable_and_a_derived_one_is_lean_s(genuine):
    counts = {"refused": 0, "relayed": 0, "either": 0}
    for raw, document, row in genuine:
        for path, kind in _faults(row):
            expected = _expect(row, path, kind)
            _check(raw, document, _fault(row, path, kind), expected)
            counts[expected] += 1
    assert min(counts.values()) >= 20, counts


def test_two_faults_are_unavailable_when_one_is_in_what_the_row_names(genuine):
    """A second fault in a value Lean derives never cures a fault in a bound member; two derived faults are relayed
    unchanged or refused by the schema. The two faults are in different members of the row."""
    pairs = 0
    for raw, document, row in genuine:
        faults = _faults(row)
        derived = [fault for fault in faults if _expect(row, *fault) == "either"]
        bound = [fault for fault in faults if _expect(row, *fault) == "refused"]
        for n, first in enumerate(bound + derived):
            second = derived[(7 * n) % len(derived)]
            if first[0][0] == second[0][0]:
                continue
            mutant = _fault(_fault(row, *first), *second)
            _check(raw, document, mutant, "refused" if first in bound else "either")
            pairs += 1
    assert pairs >= 200, pairs


def test_a_forged_refusal_naming_what_the_request_has_not_is_unavailable(genuine):
    """`ReadingsUnsatisfiable` names the request's restrictions, a refusal under a choice its open sets at their
    versions and indexes; a forgery naming anything else is unavailable, a bound one is Lean's text. A text with
    ` under ` names a choice there and nothing else: a part that is not one fails closed (review F2 of AR-17)."""
    raw, document, row = next(answer for answer in genuine if answer[2]["status"] == "error")
    assert row["error"] == "ReadingsUnsatisfiable: keep-default, keep-strict"
    for text, bound in _REFUSALS.items():
        assert _ask(raw, document, {**row, "error": text}) == (("refused", text) if bound else ("unavailable",)), text


_UNDER = "ResourceLimit: generated background under "
# Each refusal text with whether it is bound to the documents of `_stale_case` and the recorded refusal.
_REFUSALS = {"ReadingsUnsatisfiable: keep-default, zz": False, "ReadingsUnsatisfiable: keep-strict, keep-strict": False,
             "ReadingsUnsatisfiable: keep-strict": True, _UNDER + "rs1@1:1": True, _UNDER + "rs1@1:2": False,
             _UNDER + "rs1@2:0": False, _UNDER + "rs9@1:0": False, _UNDER + "rs1@1:0, rs1@1:1": False,
             _UNDER + "rs9@1:0, junk": False, _UNDER + "rs1@1:99, junk": False, _UNDER + "rs1@1:0, junk": False,
             _UNDER + "junk": False, _UNDER: False, "InvalidInput: a text without a choice": True}


def test_f2_a_refusal_under_the_completion_is_bound_as_the_plain_route_s(genuine):
    """Review F2 of AR-17, same class: the completion's relay (`_completion_elaborate`) binds a refusal as the plain
    route does, instead of relaying any error row."""
    raw, document, row = next(answer for answer in genuine if answer[2]["status"] == "error")
    environment = readings_route.wire({**raw, "profiles": sorted({*raw["profiles"], readings_route.NORM_DEFAULTS})})
    case = {"id": row["id"], "kind": "readings-elaborate", "environment": environment,
            "document": readings_route.wire(readings_route.document_wire(
                document["units"], document["reading_sets"], couplings=document.get("couplings", ()),
                narrowings=document.get("narrowings", ())))}
    for text, bound in _REFUSALS.items():
        if bound:
            with pytest.raises(VEError) as caught:
                readings_route._completion_elaborate({**row, "error": text}, case)
            assert not isinstance(caught.value, CheckerUnavailable)
            assert getattr(caught.value, "message", str(caught.value)) == text, text
        else:
            with pytest.raises(CheckerUnavailable):
                readings_route._completion_elaborate({**row, "error": text}, case)


def test_a_slot_label_naming_what_the_request_has_not_is_unavailable(genuine):
    """A label names the request's couplings and narrowings, its open sets at their versions and, for a reading's
    own premise, an index below the set's number of readings, and a shared label a generated `outweighs` decision
    on the request's act and ranks (review F1 of AR-17); Lean's own labels stay bound."""
    forged = ["coupling:zz", "narrowing:zz", "readings:rs9@1:one", "readings:rs1@7:one", "readings:rs1@1:9:quiet",
              "unsaid:pair:avoid_required,help_required", "readings:quiet:outweighs:zz:lo:hi",
              "readings:quiet:outweighs:avoid_required:lo:zz", "readings:quiet:outweighs:avoid_required:hi:lo",
              "readings:quiet:outweighs:help_required:lo:hi", "readings:quiet:excepted:rd-2-no-deception"]
    rows = [(raw, document, row) for raw, document, row in genuine if row.get("route") == "superposed"]
    labels = {entry["label"].rpartition(":")[0] if "quiet:outweighs" in entry["label"] else
              entry["label"].partition(":")[0] for _, _, row in rows for entry in row["slot"]}
    assert {"readings", "coupling", "narrowing", "readings:quiet:outweighs:avoid_required:lo"} <= labels
    for raw, document, row in rows:
        for label in forged:
            assert _ask(raw, document, {**row, "slot": [*row["slot"], {"label": label, "ast": ["top"]}]}) == (
                "unavailable",), label


def _superposed(genuine, holistic=False):
    return next(answer for answer in genuine if answer[2].get("route") == "superposed"
                and any(e["label"].startswith("readings:quiet:") for e in answer[2]["slot"]) is holistic)


def test_f1_a_name_pair_outside_the_request_is_unavailable(genuine):
    """Review F1 of AR-17: the name map is a reading's own names (its rule, and its rule's exception and switch
    decisions) with their names in `sup D`; later answers may cite them (`readings_verdicts._check_sup_answer`), so a
    pair naming a rule outside the request, a qualified name of another position or a decision the rule has not is
    unavailable, and Lean's own map in its own order is relayed."""
    raw, document, row = _superposed(genuine, holistic=True)
    pairs = row["names"][0]["candidates"][1]["names"]
    assert [pair[0] for pair in pairs] == ["no-deception", "soft__excepted__no_deception",
                                            "soft__off__no_deception__user"]
    forged = [lambda p: p.append(["zz-not-a-rule", "rd-1-zz"]),  # the review's probe
              lambda p: p.__setitem__(0, ["no-deception", "rd-9-no-deception"]),
              lambda p: p.__setitem__(0, ["zz", "rd-2-no-deception"]),
              lambda p: p.__setitem__(1, [p[1][0] + "x", p[1][1]]),
              lambda p: p.__setitem__(1, [p[1][0], p[1][1] + "x"]),
              lambda p: p.__setitem__(2, [p[2][0].replace("user", "zz"), p[2][1].replace("user", "zz")]),
              lambda p: p.pop(2), lambda p: p.append(list(p[0]))]
    for forge in forged:
        mutant = copy.deepcopy(row)
        forge(mutant["names"][0]["candidates"][1]["names"])
        assert _ask(raw, document, mutant) == ("unavailable",), mutant["names"]
    mutant = copy.deepcopy(row)
    mutant["names"][0]["candidates"][1]["names"].reverse()
    assert _ask(raw, document, mutant) == _shown(mutant)
    raw, document, row = _superposed(genuine)
    mutant = copy.deepcopy(row)
    mutant["names"][0]["candidates"][0]["names"].append(["zz-not-a-rule", "rd-1-zz"])
    assert _ask(raw, document, mutant) == ("unavailable",)


def test_f1_a_generated_decision_key_outside_the_request_is_unavailable(genuine):
    """Review F1 of AR-17, same class: on the superposed route each generated soft decision's key names a rule of
    `sup D` that has that decision (a default rule's exception, a party it lists for a switch) or an act and two
    ranks of the request; a readings bit has no key; each key once. The decision names are Lean's."""
    raw, document, row = _superposed(genuine, holistic=True)
    keys = [entry["key"] for entry in row["generated_predicates"]]
    assert {"excepted": "rd-2-no-deception"} in keys and {"off": "rd-2-no-deception", "party": "user"} in keys
    assert {"outweighs": "avoid_required", "lower": "lo", "higher": "hi"} in keys
    forged = [{"excepted": "rd-1-no-deception"}, {"excepted": "rd-9-no-deception"}, {"excepted": "zz"},
              {"excepted": "rd-2-no-deception", "bearer": "user"}, {"off": "rd-2-no-deception", "party": "zz"},
              {"off": "rd-4-be-firm", "party": "user"}, {"outweighs": "zz", "lower": "lo", "higher": "hi"},
              {"outweighs": "avoid_required", "lower": "lo", "higher": "zz"},
              {"outweighs": "avoid_required", "lower": "lo", "higher": "lo"}, {"aimed": "zz"}]
    for key in forged:
        mutant = copy.deepcopy(row)
        mutant["generated_predicates"].append({"key": key, "layer": "soft", "name": "zz"})
        assert _ask(raw, document, mutant) == ("unavailable",), key
    for n, entry in enumerate(row["generated_predicates"]):
        mutant = copy.deepcopy(row)
        if entry["layer"] == "readings":
            mutant["generated_predicates"][n]["key"] = {"excepted": "rd-2-no-deception"}
        else:
            mutant["generated_predicates"].append(copy.deepcopy(entry))
        assert _ask(raw, document, mutant) == ("unavailable",), n
    mutant = copy.deepcopy(row)
    mutant["generated_predicates"][-1]["name"] = "zz"
    assert _ask(raw, document, mutant) == _shown(mutant)  # the outweighs decision's name is Lean's


def test_f1_a_precedence_cause_naming_another_rule_is_unavailable(genuine):
    """Review F1 of AR-17 (C, same class): `precedence under <rule>` names a rule a fixed rule is over and a reading
    of the named set declares; Lean's genuine cause is relayed, any other rule is unavailable."""
    raw, document, row = next(answer for answer in genuine
                               if (answer[2].get("finding") or {}).get("cause", "").startswith("precedence under "))
    assert row["finding"]["cause"] == "precedence under waive-x"
    assert _ask(raw, document, row) == _shown(row)
    fixed = [unit["content"]["norm"]["name"] for unit in document["units"] if "norm" in (unit.get("content") or {})]
    for rule in ["zz", "no-deception", *fixed]:
        if rule != "waive-x":
            mutant = {**row, "finding": {**row["finding"], "cause": "precedence under " + rule}}
            assert _ask(raw, document, mutant) == ("unavailable",), rule


# ---------------------------------------------------------------------------------------------------------------
# The Python regeneration's tests, converted to Lean's answer on the same input (tests/test_readings_s2_python.py)


def test_a_fixed_child_over_an_interface_rule_superposes(lean):  # noqa: F811
    """Was `sup_ready` and `uniform_precedence` in `test_superposition_gates_and_qualifies_without_mutating_sources`:
    a fixed rule over an interface rule both readings declare, with like parents, superposes, its `over` naming both
    qualified copies."""
    raw = env_k()
    document, _ = k1_document(raw, fixed_units=[("u0", norm("stop-x", "avoid_required", False,
                                                           over=("no-deception",)))])
    row = _ask(raw, document)
    assert row["route"] == "superposed" and row["finding"] is None
    assert [u["content"]["norm"]["over"] for u in row["units"] if "set" not in u] == [
        ["rd-1-no-deception", "rd-2-no-deception"]]


def test_lean_refuses_the_shapes_python_did_not_superpose(lean):  # noqa: F811
    """Was `test_uniform_precedence_catches_m8_leak_and_shape_rejects_m17`: a pending reading takes the pending
    route, and a coupling naming no set of the document is refused (M17); M8's precedence leak is
    tests/test_readings_s2_lean.py::test_m8_precedence_leak_forces_enumeration."""
    raw = env_k()
    document, _ = k1_document(raw)
    hedged = reading("hedged", ASKS_ALL, {"strict": "any-token"}, kind=["hedged", "probably", "asserted"])
    pending = {"units": document["units"], "reading_sets": [reading_set("rs1", "u1", [
        reading("strict", norm("no-deception", "avoid_required", True), {"hedged": "any-token"}), hedged], {})]}
    assert _ask(raw, pending)["route"] == "pending"
    coupled = {**document, "couplings": [{"id": "c1", "axis": "force", "sets": [
        {"set": "rs1", "version": 1}, {"set": "rs2", "version": 1}]}]}
    assert _ask(raw, coupled) == ("refused", "invalid coupling")
