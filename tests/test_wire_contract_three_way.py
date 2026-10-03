"""One submission compared with the spec record, Python and Lean engines."""

import json
import subprocess
from copy import deepcopy
from pathlib import Path

import pytest

from conformance.soft_norms import multi_fault_base
from conformance.wire_contract_golden import reports as golden_reports
from subprocesses import HANG_TIMEOUT
from tests.test_wire_contract_corpus import CONTRACTS, LIMITS, NAMES, _registry
from tests.test_wire_contract_lean import DEFER, DEMO
from tests.test_wire_contract_soft_lean import FIXTURES, INHERITED, fixture_sources
from tests.test_soft_norms_lean import elaborate, env, should
from ve.admission import admit_document
from ve.errors import VEError
from ve.softnorms import load_soft_document
from ve.softnorms_contract import REGISTRY
from ve.wire import canonical_json
from ve.wire_contract.engine import CLEAN, Deferred, Fault, load, run

from tests.test_wire_contract_lean import LEAN


def _lean(unit, roots, kind):
    assert LEAN.exists(), "build ve_diagnose before running three-way conformance"
    cases = [{"id": str(i), "kind": kind, **root} for i, root in enumerate(roots)]
    result = subprocess.run([str(LEAN), unit, "-"], input=json.dumps(cases),
                            text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert result.returncode == 0, result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    assert all(row["status"] == "ok" for row in rows)
    return rows


def _record(outcome):
    return "clean" if outcome is CLEAN else canonical_json(outcome.record)


def test_spec_golden_reports_match_fixtures():
    root = Path(__file__).resolve().parents[1] / "conformance/wire-contract"
    for filename, expected in golden_reports().items():
        assert json.loads((root / filename).read_text()) == expected


def test_engine_corpus_spec_python_lean():
    """E1–E32: the hand-derived full records agree in all three columns."""
    labels = list(DEMO)
    roots = [DEMO[name][0] for name in labels]
    rows = _lean("demo@0", roots, "corpus")
    for name, root, row in zip(labels, roots, rows):
        outcome = run(CONTRACTS["demo@0"], root, registry=_registry(),
                      contracts=CONTRACTS, limits=LIMITS, names=NAMES)
        expected = DEMO[name][1]
        lean = "clean" if row["outcome"] == "clean" else canonical_json(row["diagnostic"])
        assert (_record(outcome), lean) == (expected, expected), name


def test_deferred_corpus_spec_python_lean():
    """E33–E36 include the specified Python deferral and Lean continuation."""
    labels = list(DEFER)
    rows = _lean("defer@0", [DEFER[name][0] for name in labels], "corpus")
    for name, row in zip(labels, rows):
        root, expected_lean = DEFER[name]
        python = run(CONTRACTS["defer@0"], root, registry=_registry(),
                     contracts=CONTRACTS, limits=LIMITS, names=NAMES)
        lean = "clean" if row["outcome"] == "clean" else canonical_json(row["diagnostic"])
        assert lean == expected_lean, name
        if name in ("E34", "E35", "E36"):
            assert python == Deferred("d2"), name
        else:
            assert _record(python) == expected_lean, name


def test_soft_pilot_spec_python_lean():
    """P1–P17: whole records, except inherited decoder text and its args."""
    contract = load("soft-norms@0")
    named = sorted(FIXTURES)
    sources = fixture_sources()
    roots = [{"environment": env, "norms": rules} for env, rules in sources]
    rows = _lean("soft-norms@0", roots, "soft-elaborate")
    for root, row in zip(roots[:2], rows[:2]):
        assert row["outcome"] == "clean"
        assert run(contract, root, registry=REGISTRY) is CLEAN
    p7_python = run(contract, roots[2], registry=REGISTRY)
    assert (p7_python.record["check"], rows[2]["diagnostic"]["check"]) == ("4.14b", "4.14b")
    assert canonical_json(p7_python.record) == canonical_json(rows[2]["diagnostic"])
    p17_python = run(contract, roots[3], registry=REGISTRY)
    assert (p17_python.record["check"], rows[3]["diagnostic"]["check"]) == ("2.3", "2.3")
    for key in ("contract", "revision", "check", "phase", "code", "class", "path"):
        assert p17_python.record[key] == rows[3]["diagnostic"][key]
    for name, root, row in zip(named, roots[4:], rows[4:]):
        python = run(contract, root, registry=REGISTRY)
        assert isinstance(python, Fault), name
        assert row["outcome"] == "fault", name
        expected = deepcopy(FIXTURES[name][1])
        assert canonical_json(row["diagnostic"]) == canonical_json(expected), name
        if expected["check"] in INHERITED:
            for key in ("text", "args"):
                python.record.pop(key)
                expected.pop(key)
        assert canonical_json(python.record) == canonical_json(expected), name


def test_s4_public_admission_spec_python_lean():
    """S1–S4: the admitted error, Python engine and Lean engine agree with the spec record."""
    sources = []
    raw, norms = multi_fault_base()
    raw["vocabulary"]["soft"]["parties"] = ["p", "Q!"]
    sources.append((raw, norms))
    raw, norms = multi_fault_base()
    norms[0]["norm"]["extra"] = 1
    sources.append((raw, norms))
    raw, norms = multi_fault_base()
    raw["language"] = "x"
    sources.append((raw, norms))
    raw, norms = multi_fault_base()
    norms[3]["norm"]["over"] = ["b1"]
    sources.append((raw, norms))

    # The expected records are copied from section 4.1 and S3–S4 of section 8.1,
    # without consulting either engine or the admission error.
    fields = [
        ("2.7a", "declarations", "SOFT_INVALID_NAME", "InvalidInput",
         "/environment/vocabulary/soft/parties/1", "InvalidInput: invalid soft name Q!", {"value": "Q!"}),
        ("4.1c", "rule-fields", "SOFT_INVALID_INPUT", "InvalidInput",
         "/norms/0/norm", "InvalidInput: invalid norm fields", {}),
        ("1.2", "envelope", "SOFT_UNSUPPORTED_PROFILE", "UnsupportedProfile",
         "/environment/language", "UnsupportedProfile: Unsupported language", {}),
        ("6.8", "semantic", "SOFT_OVER_HARD", "InvalidInput", "",
         "SoftOverHard: rule d3 over b1", {"detail": "rule d3 over b1"}),
    ]
    expected = [dict(zip(("check", "phase", "code", "class", "path", "text", "args"), row),
                     contract="soft-norms@0", revision=4) for row in fields]
    roots = [{"environment": raw, "norms": norms} for raw, norms in sources]
    rows = _lean("soft-norms@0", roots, "soft-elaborate")
    for index, ((raw, norms), root, row, record) in enumerate(zip(sources, roots, rows, expected)):
        with pytest.raises(VEError) as old:
            load_soft_document(deepcopy(raw), deepcopy(norms))
        document = {"units": [{"kind": "norm", "content": deepcopy(unit)} for unit in norms]}
        with pytest.raises(VEError) as caught:
            admit_document(deepcopy(raw), document)
        public = caught.value
        assert type(public) is type(old.value), index
        assert public.code == old.value.code == record["code"], index
        assert public.to_dict() == {**old.value.to_dict(), "message": record["text"],
                                    "diagnostic": record}, index
        python = run(load("soft-norms@0"), root, registry=REGISTRY)
        assert isinstance(python, Fault), index
        assert python.record == row["diagnostic"] == record, index


def admission_sources():
    """The admission case's soft source, and the same with an invalid `mode` in its first unit."""
    rules = [should("a", "x_required", True), should("b", "x_permitted", False)]
    bad = deepcopy(rules)
    bad[0]["norm"]["mode"] = "invalid"
    return (env(), rules), (env(), bad)


def test_admission_adapter_uses_active_norm_units():
    (environment, rules), (_, bad_rules) = admission_sources()
    elaborated = elaborate(Path(__file__).resolve().parents[1] /
                           "lean/.lake/build/bin/ve_soft_norms_route", environment, rules)
    coherence = next(b for b in elaborated["background"] if b.get("label") == "soft:coherence:a,b")
    document = {"units": [{"id": f"u{i}", "span": [i * 10, i * 10 + 5],
                           "kind": "norm", "content": rule} for i, rule in enumerate(rules)],
                "graph": {"root": "leaf", "nodes": [
                    {"name": "leaf", "ast": coherence["ast"], "label": coherence["label"]}]}}
    case = {"environment": environment, "document": document}
    [engine] = _lean("soft-norms@0", [case], "admission")
    assert engine["outcome"] == "clean"
    submitted = {"id": "admission", "kind": "admission", **case}
    legacy = subprocess.run([str(Path(__file__).resolve().parents[1] /
                                 "lean/.lake/build/bin/ve_soft_norms_route"), "-"],
                            input=json.dumps([submitted]), text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert json.loads(legacy.stdout)[0]["status"] == "ok"
    bad = deepcopy(case)
    bad["document"]["units"][0]["content"] = bad_rules[0]
    [lean_bad] = _lean("soft-norms@0", [bad], "admission")
    python_root = REGISTRY.adapters["soft_source"]({"kind": "admission", **bad})
    python_bad = run(load("soft-norms@0"), python_root, registry=REGISTRY)
    assert isinstance(python_bad, Fault)
    assert canonical_json(python_bad.record) == canonical_json(lean_bad["diagnostic"])
    assert lean_bad["diagnostic"]["check"] == "4.3"


FORMS_BASE = {"doc": {"x": 1, "n": 1, "mode": "strict", "pair": ["a", 1], "tag": "t",
                      "sub": {"tag": "s", "part": {"x": 1, "ys": []}},
                      "plain": {"tag": "p", "part": {"x": 1, "ys": ["u"]}}}}


def _forms(edit):
    root = deepcopy(FORMS_BASE)
    edit(root["doc"])
    return root


def _forms_record(check, phase, code, cls, path, text, args=None):
    return canonical_json({"contract": "forms@0", "revision": 2, "check": check, "phase": phase,
                           "code": code, "class": cls, "path": path, "text": text, "args": args or {}})


def _guard_fault(check, path, text, args=None):
    return _forms_record(check, "guards", "FORMS_SHAPE", "InvalidInput", path, text, args)


# Hand-derived from forms@0 and mid@0 (conformance/wire-contract/contracts) by sections 2.3, 2.6 and 2.7:
# every literal form with a case where it holds and one where it does not, the tuple type form, a template
# with literal braces, a raw value holding U+0001, and the include frame of 2.7 under a view and without one.
FORMS = {
    "F1": (FORMS_BASE, "clean"),
    "F2 present holds": (_forms(lambda d: d.update(y=1)), _guard_fault("f2", "/doc", "Forms: x and y")),
    "F3 present fails, absent holds": (
        _forms(lambda d: (d.update(y=1), d.pop("x"))), _guard_fault("f3", "/doc", "Forms: neither x nor z")),
    "F3b absent holds, check holds": (_forms(lambda d: (d.pop("x"), d.update(z=0))), "clean"),
    "F4 differs holds, braces": (
        _forms(lambda d: d.update(n="s")),
        _guard_fault("f4", "/doc/n", 'Forms: n is {"s"}', {"value": '"s"'})),
    "F5 differs fails": (_forms(lambda d: d.update(n="s", mode="loose")), "clean"),
    "F6 is_not holds, tuple fails": (
        _forms(lambda d: d.update(pair=["a", "b"])),
        _guard_fault("f5", "/doc/pair", 'Forms: pair ["a","b"]', {"value": '["a","b"]'})),
    "F7 is_not and is fail": (_forms(lambda d: d.update(pair=["a", "b"], mode=True)), "clean"),
    "F8 is holds, enum fails": (
        _forms(lambda d: d.update(mode="other")),
        _guard_fault("f6", "/doc/mode", 'Forms: mode "other"', {"value": '"other"'})),
    "F9 equals holds, raw U+0001": (
        _forms(lambda d: d.update(tag="a\x01b")),
        _guard_fault("f7", "/doc/tag", "Forms: tag a\x01b", {"value": "a\x01b"})),
    "F10 view then nested include": (
        _forms(lambda d: d["sub"]["part"].update(ys=[7])),
        _forms_record("n1/m2/b2", "nest", "FORMS_NEST", "UnsupportedProfile", "/doc/sub", "Inner: y 0",
                      {"index": "0", "inner_path": "/part/ys/0"})),
    "F11 nested include without view": (
        _forms(lambda d: d["plain"]["part"].update(ys=[7])),
        _forms_record("n2/m2/b2", "nest", "MID_INNER", "ResourceLimit", "/doc/plain/part/ys/0", "Inner: y 0",
                      {"index": "0"})),
    "F12 view, check of the middle contract": (
        _forms(lambda d: d["sub"].update(tag=5)),
        _forms_record("n1/m1", "nest", "FORMS_NEST", "UnsupportedProfile", "/doc/sub", "Mid: tag 5",
                      {"value": "5", "inner_path": "/tag"})),
    "F13 not an object": ({"doc": 3}, _guard_fault("f1", "/doc", "Forms: doc")),
}


def _kinds(kinds):
    return _forms(lambda d: d.update(kinds=kinds))


def _kind_fault(check, path, text, args=None):
    return _forms_record(check, "kinds", "FORMS_SHAPE", "InvalidInput", path, text, args)


K = "/doc/kinds/"
# Phase `kinds`: one target per kind of 2.4. F1 has no `kinds`, so every target is absent and holds.
FORMS.update({
    "F14 null form fails": (dict(FORMS_BASE, nothing=1),
                            _kind_fault("k00", "/nothing", "Kinds: nothing 1", {"value": "1"})),
    "F15 exact_keys fails": (_kinds({"type": True, "exact_keys": {"b": 1}}),
                             _kind_fault("k02", K + "exact_keys", "Kinds: exact keys")),
    "F16 type fails, absent arg": (_kinds({"type": 1}),
                                   _kind_fault("k01", K + "type", "Kinds: type 1", {"value": "1", "other": ""})),
    "F17 keys fails": (_kinds({"keys": {"a": 1, "c": 1}}), _kind_fault("k03", K + "keys", "Kinds: keys")),
    "F18 const fails": (_kinds({"const": "d"}), _kind_fault("k04", K + "const", "Kinds: const d", {"value": "d"})),
    "F19 enum fails": (_kinds({"enum": 3}), _kind_fault("k05", K + "enum", "Kinds: enum 3", {"value": "3"})),
    "F20 max_items, index renderer": (
        _kinds({"max_items": [1, 2]}),
        _kind_fault("k06", K + "max_items", "Kinds: 2 items over 1", {"count": "2", "limit": "1"})),
    "F21 max_bytes fails": (_kinds({"max_bytes": "abc"}),
                            _kind_fault("k07", K + "max_bytes", "Kinds: 3 bytes over 2", {"count": "3", "limit": "2"})),
    "F22 name fails": (_kinds({"name": "A"}), _kind_fault("k08", K + "name", "Kinds: name A", {"value": "A"})),
    "F23 sorted_unique, list renderer": (
        _kinds({"sorted_unique": ["b", "a"]}),
        _kind_fault("k09", K + "sorted_unique", "Kinds: unsorted a, b", {"value": "a, b"})),
    "F24 declared_in fails": (_kinds({"declared_in": "z"}),
                              _kind_fault("k10", K + "declared_in", "Kinds: undeclared z", {"value": "z"})),
    "F25 requires member fails": (_kinds({"requires_member": {}}),
                                  _kind_fault("k11", K + "requires_member", "Kinds: requires member")),
    "F26 requires item fails": (_kinds({"requires_item": []}),
                                _kind_fault("k12", K + "requires_item", "Kinds: requires item")),
    "F27 excludes member fails": (_kinds({"excludes_member": {"a": 1}}),
                                  _kind_fault("k13", K + "excludes_member", "Kinds: excludes member")),
    "F28 excludes item fails": (_kinds({"excludes_item": ["a"]}),
                                _kind_fault("k14", K + "excludes_item", "Kinds: excludes item")),
    "F29 unique_so_far fails": (_kinds({"list": [{"v": 1}, {"v": 1}]}),
                                _kind_fault("k15", K + "list/1/v", "Kinds: repeated 1 at 1",
                                            {"value": "1", "index": "1"})),
    "F30 name on key fails": (_kinds({"map": {"A": 1}}), _kind_fault("k16", K + "map/A", "Kinds: key A",
                                                                     {"key": "A"})),
    "F31 every kind holds": (_kinds({
        "type": True, "exact_keys": {"a": 1}, "keys": {"a": 1}, "const": "c", "enum": 2, "max_items": [1],
        "max_bytes": "ab", "name": "ab", "sorted_unique": ["a", "b"], "declared_in": "a",
        "requires_member": {"a": 1}, "requires_item": ["a"], "excludes_member": {}, "excludes_item": [],
        "list": [{"v": 1}, {"v": 2}, {}], "map": {"ok": 1}, "keyed": 1}), "clean"),
})


def test_forms_corpus_spec_python_lean():
    """Wire review (Astra A, Fable B2, B6): hand-derived records, Python and Lean, on the literal forms, the
    tuple type form, literal braces, U+0001 and a viewed include over a nested include."""
    labels = list(FORMS)
    rows = _lean("forms@0", [FORMS[name][0] for name in labels], "corpus")
    for name, row in zip(labels, rows):
        root, expected = FORMS[name]
        python = run(CONTRACTS["forms@0"], root, registry=_registry(), contracts=CONTRACTS,
                     limits=LIMITS, names=NAMES)
        lean = "clean" if row["outcome"] == "clean" else canonical_json(row["diagnostic"])
        assert (_record(python), lean) == (expected, expected), name


def _lean_outcome(unit, root):
    """`ve_diagnose`'s answer as an engine outcome, for the overlay's `lean` argument (2.8)."""
    from ve.wire_contract.engine import Fault as EngineFault
    [row] = _lean(unit, [root], "corpus")
    return CLEAN if row["outcome"] == "clean" else EngineFault(row["diagnostic"])


def test_overlay_e40_e41_lean_answers_for_a_python_deferral():
    """Spec 8.1, E40 and E41 (wire review, Fable B6): when Python defers and Lean answers, the overlay
    reports Lean's record, or the residual record when Lean's answer is clean."""
    from ve.errors import VEError
    from ve.wire_contract.engine import overlay
    contract = CONTRACTS["defer@0"]
    legacy = VEError("legacy says no")
    e34, e36 = {"v": 1, "w": "x"}, {"v": 1, "w": 2}
    for root in (e34, e36):
        assert run(contract, root, registry=_registry(), contracts=CONTRACTS, limits=LIMITS,
                   names=NAMES) == Deferred("d2")
    e40 = overlay(contract, legacy, Deferred("d2"), lean=lambda: _lean_outcome("defer@0", e34))
    assert canonical_json(e40) == DEFER["E34"][1]
    assert json.loads(DEFER["E34"][1])["check"] == "d3"
    e41 = overlay(contract, legacy, Deferred("d2"), lean=lambda: _lean_outcome("defer@0", e36))
    assert e41 == {"contract": "defer@0", "revision": 1, "check": "residual", "phase": "residual",
                   "code": "DEFER_INVALID_INPUT", "class": "InvalidInput", "path": "", "text": "legacy says no",
                   "args": {}}


def test_engine_corpus_covers_every_form():
    """Spec 8.1's coverage rule (wire review, Fable B6): over the corpus, every T1 kind fails and holds and
    holds on an absent target (`max_count` has no target), every literal form holds and does not, every
    type form matches and does not, and every renderer renders a value and an absent one. Measured by
    instrumenting the Python engine; the same cases run in Lean in the tests above."""
    from collections import defaultdict
    import ve.wire_contract.engine as engine
    from tests.test_wire_contract_corpus import CASES
    seen = defaultdict(set)
    fails, guard, type_of, render = engine._fails, engine._guard, engine._type, engine._render

    def traced_fails(entry, root, items, earlier, names, limits):
        result = fails(entry, root, items, earlier, names, limits)
        kind = entry["kind"] + (":key" if entry.get("on") == "key" else "") + (
            (":member" if "member" in entry else ":item") if entry["kind"] in ("requires", "excludes") else "")
        seen[kind].add("absent" if result[3] is engine.ABSENT and kind != "max_count"
                       else "fail" if result[0] else "hold")
        return result

    def traced_guard(root, items, literals):
        for literal in literals:
            seen["literal " + next(iter(literal))].add(guard(root, items, [literal]))
        return guard(root, items, literals)

    def traced_type(value, form):
        result = type_of(value, form)
        if type(form) is not list:
            seen["type " + (form if type(form) is str else next(iter(form)))].add(result)
        return result

    def traced_render(value, renderer):
        seen["renderer " + renderer].add(value is not engine.ABSENT)
        return render(value, renderer)

    engine._fails, engine._guard, engine._type, engine._render = (traced_fails, traced_guard, traced_type,
                                                                  traced_render)
    try:
        for unit, roots in (("demo@0", [case[1] for case in CASES]), ("defer@0", [r for r, _ in DEFER.values()]),
                            ("forms@0", [r for r, _ in FORMS.values()])):
            for root in roots:
                run(CONTRACTS[unit], root, registry=_registry(), contracts=CONTRACTS, limits=LIMITS, names=NAMES)
    finally:
        engine._fails, engine._guard, engine._type, engine._render = fails, guard, type_of, render
    kinds = ["type", "exact_keys", "keys", "const", "enum", "max_items", "max_bytes", "name", "name:key",
             "sorted_unique", "unique_so_far", "declared_in", "requires:member", "requires:item",
             "excludes:member", "excludes:item"]
    for kind in kinds:
        assert seen[kind] == {"fail", "hold", "absent"}, kind
    assert seen["max_count"] == {"fail", "hold"}
    for literal in ("present", "absent", "equals", "differs", "is", "is_not"):
        assert seen["literal " + literal] == {True, False}, literal
    for form in ("null", "boolean", "integer", "string", "array", "object", "array_of", "tuple"):
        assert seen["type " + form] == {True, False}, form
    for renderer in ("raw", "json", "index", "count", "list"):
        assert True in seen["renderer " + renderer], renderer
    assert any(False in values for key, values in seen.items() if key.startswith("renderer "))
