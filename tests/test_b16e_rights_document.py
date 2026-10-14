"""Batch 16e: rights@0 documents (with and without the readings@1 head) are Lean document answers.

The class the 16e review found (F1) is a document Lean's `document` mode could not decide; every such document
must now be decided by Lean with the retained path's public outcome, or answered `CheckerUnavailable` for a listed
part (`Service.Document.RightsDoc.unowned`). The measurement compares every outcome with the prior path (F2)."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
import runpy
from unittest.mock import patch

import pytest

from conformance import rights_differential as generator
from tools.lean_first_diff import outcome
from ve import document as D
from ve.backends import relay
from ve.backends.service_schema import Context, Invalid, ROWS
from ve.errors import CheckerUnavailable, VEError

ROOT = Path(__file__).resolve().parents[1]
MEASURE = ROOT / "docs/lean-first/b16e/measure.py"


def _text(seed: int, headed: bool = False) -> str:
    raw, units = generator.document(seed)
    if headed:
        raw = {**raw, "profiles": sorted([*raw["profiles"], "readings@1"])}
    return generator.document_text(raw, units)


def _split(text: str):
    boundary = text.index("\n---\n", 4)
    return json.loads(text[4:boundary]), text[boundary + 5:]


def _join(meta, body) -> str:
    return "---\n" + json.dumps(meta) + "\n---\n" + body


def _both(path: Path):
    """(Lean decides, the public outcomes on the Lean path, the same on the retained path) of check and render."""
    raw = path.read_bytes()
    try:
        decided = D._lean_answer(raw, True) is not None
    except VEError:
        decided = True
    new = [outcome(lambda: D.check_document(path)), outcome(lambda: D.render_document(path))]
    with patch.object(D, "_lean_answer", return_value=None):
        old = [outcome(lambda: D.check_document(path)), outcome(lambda: D.render_document(path))]
    return decided, new, old


# ------------------------------------------------------------------------------------------- F1 and F2 probes

def test_f1_probe_valid_rights_cases_are_decided_by_lean():
    """16e review PROBE F1 (the measurement stopped on valid `s0`, retained as CheckerUnavailable): the first
    cases of the ledger, plain and under the readings@1 head, are accepted by Lean with the prior path's report."""
    measure = runpy.run_path(str(MEASURE))
    for case, text in (("s0", _text(0)), ("s0/readings@1", _text(0, headed=True)), ("s1", _text(1))):
        raw = text.encode()
        row = measure["decision"](case, raw, hashlib.sha256(raw).hexdigest())
        assert row["decision"] == "ok", row


def test_f1_probe_invalid_rights_cases_are_rejected_by_lean_as_before():
    measure = runpy.run_path(str(MEASURE))
    for seed in (6, 9):  # a second bar; a citation of an unknown unit
        raw = _text(seed).encode()
        row = measure["decision"](f"s{seed}", raw, hashlib.sha256(raw).hexdigest())
        assert row["decision"] == "error" and "prior_error" not in row, row


def test_f2_probe_a_seeded_rejection_of_a_valid_case_fails_the_measurement():
    """16e review PROBE F2: a Lean `VEError` on valid `s0` was counted as a decided case."""
    measure = runpy.run_path(str(MEASURE))
    raw = _text(0).encode()
    with patch.object(measure["D"], "_lean_answer", side_effect=VEError("InvalidInput: seeded rejection")):
        with pytest.raises(RuntimeError, match="prior path accepts"):
            measure["decision"]("s0", raw, hashlib.sha256(raw).hexdigest())


def test_f2_a_forged_accepted_report_fails_the_measurement():
    measure = runpy.run_path(str(MEASURE))
    raw = _text(0).encode()
    original = D._lean_document

    def forged(*args, **kwargs):
        doc = original(*args, **kwargs)
        doc["lean"]["coverage"]["bytes_by_status"] = {"CHECKED": doc["lean"]["coverage"]["source_bytes"]}
        return doc
    with patch.object(measure["D"], "_lean_document", side_effect=forged):
        with pytest.raises(RuntimeError, match="differs from the prior path"):
            measure["decision"]("s0", raw, hashlib.sha256(raw).hexdigest())


# ----------------------------------------------------------------------------- the class: both paths agree

def test_rights_corpus_sample_is_lean_decided_with_the_prior_outcome(tmp_path):
    decided = 0
    for seed in range(0, 24):
        for headed in ((False, True) if seed % 4 == 0 else (False,)):
            path = tmp_path / f"s{seed}-{headed}.ve.md"
            path.write_text(_text(seed, headed))
            lean, new, old = _both(path)
            assert new == old, (seed, headed)
            if "returned" in new[0]:
                assert lean, (seed, headed)
                decided += 1
    assert decided >= 20


VALUES = (7, True, None, [], {}, "x")
KINDS = ("norm", "asserted", "right", "limitation", "bar", "right_lines", ["hedged", "likely", "norm"],
         ["attributed", "a", "says", "norm"], "exposition")


def _mutants(meta):
    """1-fault mutants of a rights document: each unit's kind swapped; each unit field and each rights block member
    retyped (null, number, Boolean, list, object, string) or dropped; an open meaning on a generated name; explicit
    statuses; added citations and formula content; two units as the parts of a MIXED unit; the parts the mode
    leaves to the retained path (reading sets, couplings, graph) and the other front-matter lists."""
    units = meta["units"]
    for i, unit in enumerate(units):
        for kind in KINDS:
            yield f"kind {i} {kind}", lambda m, i=i, kind=kind: m["units"][i].__setitem__("kind", kind)
        for field in ("meaning", "support", "status", "meaning_id", "content", "id"):
            for value in VALUES:
                yield f"{field} {i} {value!r}", lambda m, i=i, f=field, v=value: m["units"][i].__setitem__(f, v)
            yield f"drop {field} {i}", lambda m, i=i, f=field: m["units"][i].pop(f, None)
        if "content" not in unit:
            continue
        key = next(iter(unit["content"]))
        yield f"open {i}", lambda m, i=i: m["units"][i].__setitem__("meaning", {"open": ["rights__lim__1"]})
        for status in ("CHECKED", "OPEN"):
            yield f"status {i} {status}", lambda m, i=i, s=status: m["units"][i].__setitem__("status", s)
        yield f"cites {i}", lambda m, i=i: m["units"][i]["content"].__setitem__("cites", {"exception": ["u1"]})
        yield f"ast {i}", lambda m, i=i: m["units"][i].__setitem__("content", {"ast": ["top"]})
        if type(unit["content"][key]) is dict:
            for member in list(unit["content"][key]):
                for value in VALUES:
                    yield (f"{key}.{member} {i} {value!r}",
                           lambda m, i=i, k=key, f=member, v=value: m["units"][i]["content"][k].__setitem__(f, v))
                yield f"drop {key}.{member} {i}", lambda m, i=i, k=key, f=member: m["units"][i]["content"][k].pop(f)
            yield from _nested(i, key, unit["content"][key])


def _nested(i, key, body):
    """One level deeper: the first line of a right (its fields and each rule's or citation's members), the first
    condition of a limitation, and each member of a norm's nested objects (its exception)."""
    def at(m, *path):
        target = m["units"][i]["content"][key]
        for step in path:
            target = target[step]
        return target
    objects = []
    if key in ("right", "right_lines") and type(body.get("lines")) is list and body["lines"]:
        line = body["lines"][0]
        objects.append((("lines", 0), line))
        objects.extend((("lines", 0, field), value) for field, value in line.items() if type(value) is dict)
    if key == "limitation" and type(body.get("conditions")) is list and body["conditions"]:
        objects.append((("conditions", 0), body["conditions"][0]))
    if key == "norm":
        objects.extend(((field,), value) for field, value in body.items() if type(value) is dict)
    for path, value in objects:
        for member in list(value):
            for wrong in VALUES:
                yield (f"{key}.{path}.{member} {i} {wrong!r}",
                       lambda m, p=path, f=member, v=wrong: at(m, *p).__setitem__(f, v))
            yield f"drop {key}.{path}.{member} {i}", lambda m, p=path, f=member: at(m, *p).pop(f)

    def mixed(m):
        first, second = m["units"][0], m["units"][1]
        for part in (first, second):
            part.setdefault("status", "CHECKED")
        m["units"][0:2] = [{"id": "mix", "span": [first["span"][0], second["span"][1]], "status": "MIXED",
                            "parts": [first, second]}]
    yield "mixed", mixed
    for key, value in (("reading_sets", []), ("couplings", []), ("graph", {"nodes": [], "edges": []}),
                       ("open_terms", []), ("narrowings", []), ("lemmas", []), ("weights", [])):
        yield f"meta {key}", lambda m, k=key, v=value: m.__setitem__(k, v)


@pytest.mark.parametrize("seed,headed", [(0, False), (2, False), (16, True)])
def test_rights_mutants_get_the_prior_outcome_wherever_lean_decides(tmp_path, seed, headed):
    """Every 1-fault mutant (and a sample of 2-fault ones) that Lean decides gets the retained path's public
    outcome, (code, text) included; a mutant Lean does not decide keeps the retained path by construction."""
    meta, body = _split(_text(seed, headed))
    ones = list(_mutants(meta))
    rng = random.Random(seed)
    pairs = [(f"{a[0]} + {b[0]}", (a[1], b[1])) for a, b in (rng.sample(ones, 2) for _ in range(20))]
    decided = 0
    for name, changes in [(n, (c,)) for n, c in ones] + pairs:
        mutant = deepcopy(meta)
        try:
            for change in changes:
                change(mutant)
        except (KeyError, IndexError, TypeError, AttributeError):
            continue  # the second fault no longer applies
        path = tmp_path / "mutant.ve.md"
        path.write_text(_join(mutant, body))
        lean, new, old = _both(path)
        assert new == old, name
        decided += lean
    assert decided >= 200


def test_a_non_string_unit_id_is_the_unit_checks_diagnostic_on_both_paths(tmp_path):
    """The retained path tested a list id against the attached ids (a frozenset) and crashed with TypeError."""
    meta, body = _split(_text(0))
    meta["units"][3]["id"] = []
    path = tmp_path / "list-id.ve.md"
    path.write_text(_join(meta, body))
    lean, new, old = _both(path)
    assert lean and new == old
    assert new[0]["raised"] == {"code": "InvalidInput", "message": "duplicate or invalid unit id"}


def test_a_null_alterable_party_list_is_read_as_absent_on_both_paths(tmp_path):
    """The retained path's soft rule container failed on `alterable: null`, which Lean reads as absent."""
    meta, body = _split(_text(0))
    norm = next(u for u in meta["units"] if u["kind"] == "norm")
    norm["content"]["norm"]["alterable"] = None
    path = tmp_path / "null-alterable.ve.md"
    path.write_text(_join(meta, body))
    lean, new, old = _both(path)
    assert lean and new == old and "returned" in new[0]


def test_a_null_citation_is_read_as_absent_and_typed_in_the_answer(tmp_path):
    """The rights route reads `cites: {"guard": null}` as no citation (the wire drops it); the answer copies the
    block as written, so its schema types the null (a schema that did not refused Lean's accepted answer)."""
    meta, body = _split(_text(0))
    meta["units"][0]["content"]["right"]["lines"][0]["cites"] = {"guard": None}
    path = tmp_path / "null-citation.ve.md"
    path.write_text(_join(meta, body))
    lean, new, old = _both(path)
    assert lean and new == old and "returned" in new[0]


@pytest.mark.parametrize("purpose", [7, True, None, [], {}, ["narrow"], "narrow"])
def test_f4_copied_ignored_condition_metadata_accepts_every_json_type(tmp_path, purpose):
    """PROBE F4: purposes is copied and bound, while the rights decoder ignores its value."""
    meta, body = _split(_text(2))
    limitation = next(u for u in meta["units"] if u["kind"] == "limitation")["content"]["limitation"]
    limitation["conditions"][0]["purposes"] = purpose
    path = tmp_path / "purpose.ve.md"
    path.write_text(_join(meta, body))
    lean, new, old = _both(path)
    assert lean and new == old and "returned" in new[0] and "returned" in new[1]


@pytest.mark.parametrize("case", ["null_citation", "condition_decider", "bar_decider"])
@pytest.mark.parametrize("value", ["missing", "null"])
def test_f5_optional_rights_metadata_renders_after_acceptance(tmp_path, case, value):
    """PROBE F5: accepted absent and null metadata have the same rendering on both document paths."""
    meta, body = _split(_text(0 if case == "null_citation" else 2))
    if case == "null_citation":
        target = meta["units"][0]["content"]["right"]["lines"][0]
        field = "cites"
    else:
        kind = "bar" if case == "bar_decider" else "limitation"
        target = next(u for u in meta["units"] if u["kind"] == kind)["content"][kind]
        if case == "condition_decider":
            target = target["conditions"][0]
        field = "decided_by"
    if value == "missing":
        target.pop(field, None)
    else:
        target[field] = {"guard": None} if case == "null_citation" else None
    path = tmp_path / "optional.ve.md"
    path.write_text(_join(meta, body))
    lean, new, old = _both(path)
    assert lean and new == old and "returned" in new[0] and "returned" in new[1]
    if case == "null_citation":
        assert "It cites unit None" not in new[1]["returned"]
    elif case == "bar_decider":
        assert "The source names no decider of whether an act is so aimed." in new[1]["returned"]


def test_a_right_without_a_holder_guard_is_built_on_both_paths(tmp_path):
    """The rights route reads an absent holder guard as `top`; the retained path's container read `body["guard"]`."""
    meta, body = _split(_text(0))
    meta["units"][0]["content"]["right"].pop("guard")
    path = tmp_path / "no-guard.ve.md"
    path.write_text(_join(meta, body))
    lean, new, old = _both(path)
    assert lean and new == old and "returned" in new[0]


def test_a_norm_unit_holding_a_rights_block_is_refused_by_lean():
    meta, body = _split(_text(0))
    meta["units"][0]["kind"] = "norm"
    with pytest.raises(VEError, match="UnsupportedProfile: rights@0 is required"):
        D._lean_answer(_join(meta, body).encode(), True)


@pytest.mark.parametrize("key", ["reading_sets", "couplings", "graph"])
def test_the_unowned_parts_of_a_rights_document_keep_the_retained_path(key):
    meta, body = _split(_text(0))
    meta[key] = {"nodes": [], "edges": []} if key == "graph" else []
    _, reason = relay.answer("document", {"id": "document", "document": _join(meta, body), "admit": True})
    assert isinstance(reason, CheckerUnavailable) and f"a rights document with {key}" in str(reason)


def test_soft_norms_is_owned_only_beneath_rights():
    from conformance import document_wrapper as dw

    meta, body = _split(_text(0))
    assert D._lean_answer(_join(meta, body).encode(), True) is not None
    meta["environment"]["profiles"].remove("rights@0")
    _, reason = relay.answer("document", {"id": "document", "document": _join(meta, body), "admit": True})
    assert "document checks under soft-norms@0 need its Lean profile route" in str(reason)
    assert dw.OWNED_BENEATH == {"soft-norms@0": "rights@0"}


# ------------------------------------------------------------------- the answer's new fields: typed and bound

def _row(seed: int = 2):
    text = _text(seed)
    raw = text.encode()
    row = D._lean_answer(raw, True)
    meta, source, _ = D._split(raw)
    return text, raw, row, meta, source, list(D._parts(meta["units"]))


def _leaves(value, path):
    yield path, value
    if type(value) is dict:
        for key, child in value.items():
            yield from _leaves(child, (*path, key))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from _leaves(child, (*path, index))


def _replace(row, path, value):
    changed = deepcopy(row)
    target = changed
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return changed


def test_every_rights_and_soft_field_is_typed_and_every_row_bound():
    text, raw, row, meta, source, declared = _row()
    case = Context({"id": "document", "document": text, "admit": True})
    schema = ROWS["document"][0]
    schema(row, case, {})
    kinds = {u["kind"] for u in row["units"]}
    assert {"right", "limitation", "bar", "norm"} <= kinds
    retyped = 0
    for index, unit in enumerate(row["units"]):
        for path, value in _leaves(unit, ("units", index)):
            if path[-1] in ("id", "span", "meaning", "support", "status") and len(path) == 3:
                continue  # W2's fields, the 16b/16c tests' own
            wrong = (7 if type(value) in (str, bool) or value is None else True if type(value) is int else
                     [] if type(value) is dict else {} if type(value) is list else 7)
            changed = _replace(row, path, wrong)
            retyped += 1
            try:
                schema(changed, case, {})
            except Invalid:
                continue
            with pytest.raises((ValueError, CheckerUnavailable), match="not bound|disagrees"):
                D._bind_document_answer(source, meta, declared, changed)
    assert retyped >= 100


@pytest.mark.parametrize("where", ["right", "limitation", "bar", "norm", "kind"])
def test_a_forged_but_typed_field_is_refused_by_the_binding(monkeypatch, where):
    text, raw, row, meta, source, declared = _row()
    forged = deepcopy(row)
    unit = next(u for u in forged["units"] if u["kind"] == ("right" if where == "kind" else where))
    if where == "kind":
        unit["kind"] = "limitation"
    elif where == "norm":
        unit["content"]["norm"]["name"] += "-forged"
    else:
        unit["content"][where]["name"] += "-forged"
    ROWS["document"][0](forged, Context({"id": "document", "document": text, "admit": True}), {})
    with pytest.raises(ValueError, match="disagrees"):
        D._bind_document_answer(source, meta, declared, forged)


def test_a_meaning_id_over_another_environment_is_unbound(monkeypatch, tmp_path):
    text, raw, row, meta, source, declared = _row()
    path = tmp_path / "document.ve.md"
    path.write_text(text)
    for kind in ("right", "norm"):
        forged = deepcopy(row)
        unit = next(u for u in forged["units"] if u["kind"] == kind)
        unit["meaning_id"] = hashlib.sha256(unit["meaning_id"].encode()).hexdigest()
        monkeypatch.setattr(relay, "answer", lambda *_, forged=forged: (forged, None))
        with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
            D.load_document(path)


def test_value_mutants_of_copied_content_are_refused_by_the_binding():
    """The relay mutation gate's by-design entry B7 (tools/relay-gate-allow.json): the transport schema accepts these
    valid shapes of copied content; the document binding refuses each, as it differs from the authored content."""
    text, raw, row, meta, source, declared = _row()
    right = next(i for i, u in enumerate(row["units"]) if u["kind"] == "right")
    norm = next(i for i, u in enumerate(row["units"]) if u["kind"] == "norm")
    mutants = []
    changed = deepcopy(row)
    changed["units"][right]["content"]["right"].pop("guard")
    mutants.append(changed)
    changed = deepcopy(row)
    changed["units"][right]["content"]["right"]["guard"] = None
    mutants.append(changed)
    changed = deepcopy(row)
    lines = changed["units"][right]["content"]["right"]["lines"]
    lines.append(deepcopy(lines[0]))
    mutants.append(changed)
    changed = deepcopy(row)
    over = changed["units"][norm]["content"]["norm"]["over"]
    over.extend(over[:1] or ["claim-1"])
    mutants.append(changed)
    for changed in mutants:
        with pytest.raises(ValueError, match="disagrees"):
            D._bind_document_answer(source, meta, declared, changed)
