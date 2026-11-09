"""Rights 3.5: a right unit's meaning id binds its normal form, every soft field at its default omitted.

Lean's document and identity modes use one normalizer; Python relays the identity."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.test_norms import obligation, permission
from tests.test_rights import right, rights_document_file, rights_env
from ve import document as D
from ve.document import load as D_load
from ve.errors import CheckerUnavailable, VEError
from ve.readings import rights_meaning_id
from ve.rights import RightsEnvironment

ROOT = Path(__file__).resolve().parents[1]

DEFAULTS = {"mode": "strict", "rank": None, "alterable": [], "exception": None, "hard": False}
EXCEPTION = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}
# A value away from each default that the checker admits (`_soft_raw_env` declares the rank and the party); a
# `default` rule needs an exception and only a `default` rule has one (the `#guard`s beside Lean's
# `rightsNormalForm` keep an exception alone).
NON_DEFAULTS = {"mode": {"mode": "default", "exception": EXCEPTION}, "rank": {"rank": "high"},
                "alterable": {"alterable": ["court"]}, "hard": {"hard": True},
                "exception": {"exception": EXCEPTION, "mode": "default"}}


def _raw_env():
    """`rights_env` with test_rights' marriage power (`marry_permitted` altering `married`)."""
    raw = rights_env()
    predicates = raw["vocabulary"]["predicates"]
    predicates["marry_permitted"] = permission("allow", act="{0} marry", args=("person",))
    predicates["recognise_required"] = obligation("deny", None, act="{0} recognise {1}", args=("state", "person"))
    predicates["married"] = {"arguments": ["person"], "description": "married"}
    raw["vocabulary"]["rights"]["alters"] = {
        "marry_permitted": {"holder_slot": 0, "status": "married", "recognition": "recognise_required"}}
    return raw


def _soft_raw_env():
    """`_raw_env` with a soft block declaring the rank `high` and the party `court`."""
    raw = _raw_env()
    raw["vocabulary"]["soft"] = {"parties": ["court"], "ranks": ["high"], "outranks": [], "ties": [],
                                 "outranking": {"mode": "strict"}}
    return raw


def _env():
    return RightsEnvironment(_raw_env())


def test_rights_meaning_id_binds_environment():
    content = right()
    assert rights_meaning_id(_env(), content) != rights_meaning_id(RightsEnvironment(_soft_raw_env()), content)


def _with(content, slot, **soft):
    content = deepcopy(content)
    body = next(iter(content.values()))
    body["lines"][0][slot].update(soft)
    return content


def _power():
    norm = {"sign": True, "guard": ["top"], "unless": [], "over": []}
    return {"right_lines": {"right": "life", "lines": [
        {"kind": "power", "cites": {},
         "liberty": {"name": "may-marry", "predicate": "marry_permitted", **norm},
         "recognition": {"name": "recognise-marriage", "predicate": "recognise_required", **norm}}]}}


CONTENTS = {"right/norm": (right(), "norm"), "right_lines/liberty": (_power(), "liberty"),
            "right_lines/recognition": (_power(), "recognition")}


def _lean_ids(path):
    row = D._lean_answer(path.read_bytes(), True)
    assert row is not None, "Lean's document mode decides a rights document"
    return [unit["meaning_id"] for unit in row["units"]]


def _python_ids(path):
    with patch.object(D_load, "_lean_answer", return_value=None):
        return [unit["meaning_id"] for unit in D.load_document(path)["units"]]


@pytest.mark.parametrize("where", sorted(CONTENTS))
@pytest.mark.parametrize("field", sorted(DEFAULTS))
def test_rights_meaning_id_omits_soft_defaults(tmp_path, where, field):
    """An omitted soft field, the field at its default and the field `null` (absent on the rights wire) give one id;
    a value away from the default gives another. Lean's `document` mode, which owns the id, gives each the id
    Python's `rights_meaning_id` gives."""
    raw = _soft_raw_env()
    env = RightsEnvironment(raw)
    content, slot = CONTENTS[where]
    variants = [content, _with(content, slot, **{field: DEFAULTS[field]}), _with(content, slot, **{field: None}),
                _with(content, slot, **NON_DEFAULTS[field])]
    python = [rights_meaning_id(env, variant) for variant in variants]
    assert python[1] == python[0] and python[2] == python[0] and python[3] != python[0]
    for index, variant in enumerate(variants):
        (tmp_path / str(index)).mkdir()
        contents = [variant] if where.startswith("right/") else [right(), variant]
        assert _lean_ids(rights_document_file(tmp_path / str(index), contents, env=raw))[-1] == python[index]


def test_the_normal_form_leaves_other_content_and_shapes_unchanged():
    bar = {"bar": {"name": "b30", "reading": "rule", "decided_by": "unstated", "mode": "strict"}}
    odd = {"right": {"name": "life", "lines": "not a list"}}
    env = _env()
    from ve.softnorms import soft_digest
    def raw_id(content):
        return soft_digest(f"ve-meaning-{env.identity_version}\n",
                           {"environment_id": env.environment_id, "ast": content})
    assert rights_meaning_id(env, bar) == raw_id(bar)
    assert rights_meaning_id(env, odd) == raw_id(odd)
    # `hard: 0` is not the default `false`, as Lean's `Json` reads it.
    other_type = _with(right(), "norm", hard=0)
    assert rights_meaning_id(env, other_type) == raw_id(other_type)
    # A `null` that is no soft field, and a soft field's name outside a line's norm objects, are kept.
    kept = _with(right(), "norm", guard=None)
    kept["right"]["lines"][0]["mode"] = "strict"
    kept["right"]["mode"] = None
    assert rights_meaning_id(env, kept) == raw_id(kept)


def test_rights_identity_is_relayed_from_lean(monkeypatch):
    from ve.backends import relay
    env = _env()
    answer = "f" * 64
    cases = []
    def fake_decide(mode, sent):
        cases.extend(sent)
        assert mode == "identity"
        return [{"identity_id": answer}]
    monkeypatch.setattr(relay, "decide", fake_decide)
    content = _with(right(), "norm", mode="strict")
    assert rights_meaning_id(env, content) == answer
    assert cases[0]["kind"] == "rights-meaning" and json.loads(cases[0]["content_json"]) == content


def test_rights_identity_row_is_typed_and_bound():
    from ve.backends.service_schema import Invalid, check_row
    case = {"id": "rights-meaning", "kind": "rights-meaning"}
    row = {"id": "rights-meaning", "status": "ok", "kind": "rights-meaning", "identity_id": "a" * 64}
    check_row("identity", row, case, 0)
    for change in ({"id": "other"}, {"kind": "meaning"}, {"identity_id": True},
                   {"identity_id": ""}, {"identity_id": None}):
        with pytest.raises(Invalid):
            check_row("identity", {**row, **change}, case, 0)
    for missing in row:
        with pytest.raises(Invalid):
            check_row("identity", {k: v for k, v in row.items() if k != missing}, case, 0)


def test_reading_set_binds_defaulted_right_through_the_lean_identity():
    from ve.readings import validate_reading_sets
    env = _env()
    content = _with(right(), "norm", mode="strict", hard=False)
    reading = {"id": "choice", "kind": "right", "content": content,
               "meaning_id": rights_meaning_id(env, content),
               "admission": {"who": "author", "why": "stated", "distinguishing_models": {}}}
    item = {"id": "choices", "unit": "u", "version": 1, "status": "authored",
            "signature": "author", "readings": [reading]}
    validate_reading_sets(env, [item], {"u"})
    reading["meaning_id"] = "0" * 64
    with pytest.raises(VEError, match="reading meaning id does not match content"):
        validate_reading_sets(env, [item], {"u"})


def _documents():
    """The rights fixtures: right and right_lines contents with their soft fields omitted, at their defaults, `null`
    and at a non-default."""
    yield "omitted", [right()]
    yield "defaults", [_with(right(), "norm", **DEFAULTS)]
    yield "nulls", [_with(right(), "norm", **dict.fromkeys(DEFAULTS))]
    yield "default-mode", [_with(right(), "norm", mode="default", exception=EXCEPTION)]
    yield "power-omitted", [right(), _power()]
    yield "power-defaults", [right(), _with(_with(_power(), "liberty", mode="strict", hard=False),
                                            "recognition", alterable=[], rank=None)]


DOCUMENTS = dict(_documents())


@pytest.mark.parametrize("name", list(DOCUMENTS))
def test_lean_and_python_rights_meaning_ids_agree(tmp_path, name):
    """The differential: Lean's `document` mode, Python's retained path and `rights_meaning_id` give each unit one
    id, and a content written with its defaults has the id of the same content without them."""
    contents = DOCUMENTS[name]
    path = rights_document_file(tmp_path, contents, env=_raw_env())
    env = _env()
    expected = [rights_meaning_id(env, content) for content in contents]
    assert _lean_ids(path) == expected
    assert _python_ids(path) == expected
    if name in ("defaults", "nulls"):
        assert expected == [rights_meaning_id(env, right())]
    if name == "power-defaults":
        assert expected == [rights_meaning_id(env, content) for content in DOCUMENTS["power-omitted"]]
    if name == "default-mode":
        assert expected != [rights_meaning_id(env, right())]


# The verdict snapshot (DRI adv0838 item 3 (b)): each fixture's `ve document check` answer, its loaded units without
# their meaning ids (each unit's status is its verdict) and main's meaning ids, recorded on main (6db6ee16d) before
# this change (docs/rights/rights-cfr-1/REPORT.md), one line per fixture. Nothing in the suite rewrites it.
VERDICTS = ROOT / "tests/data/rights-cfr-1-verdicts.jsonl"


def _main():
    return {row["name"]: row for row in map(json.loads, VERDICTS.read_text().splitlines())}


def _answers(directory):
    """Each fixture's check answer, units and unit meaning ids at this tree, as JSON values."""
    answers = {}
    for name, contents in DOCUMENTS.items():
        (directory / name).mkdir()
        path = rights_document_file(directory / name, contents, env=_raw_env())
        units = json.loads(json.dumps(D.load_document(path)["units"], default=str))
        answers[name] = {"check": json.loads(json.dumps(D.check_document(path), default=str)),
                         "units": [{k: v for k, v in unit.items() if k != "meaning_id"} for unit in units],
                         "meaning_ids": [unit["meaning_id"] for unit in units]}
    return answers


def _verdict(answer):
    """The verdicts and reasons of an answer: each unit's status, the coverage by status with the residual and its
    reasons, the premises' status and the rights report (each conflict's verdict and status text)."""
    check, coverage = answer["check"], answer["check"]["coverage"]
    return json.dumps({"units": [(unit["id"], unit["status"]) for unit in answer["units"]],
                       "coverage": {key: coverage[key] for key in (
                           "bytes_by_status", "soft_status", "residual_total", "unformalised_reasons",
                           "rights_residual_labels", "soft_residual_labels")},
                       "premises": check["premises"]["status"], "rights": check["rights"]["report"]}, sort_keys=True)


NORMAL = {"omitted": "omitted", "defaults": "omitted", "nulls": "omitted", "default-mode": "default-mode",
          "power-omitted": "power-omitted", "power-defaults": "power-omitted"}


def test_no_verdict_or_reason_changes(tmp_path):
    """No verdict changes: every fixture's verdicts and reasons are byte-identical to main's before this change, and
    only the meaning ids differ, exactly where a soft default is written: each then has its normal form's id, and a
    fixture's check answer is its normal form's but for the document id."""
    main, now = _main(), _answers(tmp_path)
    for name, normal in NORMAL.items():
        assert _verdict(now[name]) == _verdict(main[name])
        assert now[name]["meaning_ids"] == main[normal]["main_meaning_ids"]
        assert {**now[name]["check"], "document_id": None} == {**now[normal]["check"], "document_id": None}


def test_a_stored_pre_change_id_is_not_its_new_id(tmp_path):
    """Every id main stored for a content written with a soft default is stale: it does not compare equal to the
    recomputed id, which is the id of the same content without the default; a document that states the stale id is
    refused (Lean's `document` mode and Python's retained loader alike) and one that states the new id is not."""
    main, env = _main(), _env()
    for name in ("defaults", "nulls", "power-defaults"):
        new = [rights_meaning_id(env, content) for content in DOCUMENTS[name]]
        stale = [i for i, (old, now) in enumerate(zip(main[name]["main_meaning_ids"], new, strict=True)) if old != now]
        assert stale == ([1] if name.startswith("power") else [0])
    contents = DOCUMENTS["defaults"]
    for stated in (main["defaults"]["main_meaning_ids"][0], rights_meaning_id(env, contents[0])):
        path = rights_document_file(tmp_path, contents, env=_raw_env())
        front = json.loads(path.read_text().split("\n")[1])
        front["units"][0]["meaning_id"] = stated
        path.write_text("---\n" + json.dumps(front) + "\n---\n" + path.read_text().split("---\n", 2)[2])
        for relay in (lambda: D.load_document(path), lambda: _python_ids(path)):
            if stated == main["defaults"]["main_meaning_ids"][0]:
                with pytest.raises(VEError, match="unit meaning id does not match content"):
                    relay()
            else:
                relay()


def test_a_lean_rights_id_away_from_the_normal_form_is_refused(tmp_path):
    """R8 rebind of the changed field: Lean's answer naming, for a rights unit, the id of its content as written
    (main's stale id) or another unit's id is `CheckerUnavailable`; its own answer is accepted."""
    path = rights_document_file(tmp_path, DOCUMENTS["power-defaults"], env=_raw_env())
    real, stale = D_load._lean_answer, _main()["power-defaults"]["main_meaning_ids"]
    good = D.load_document(path)
    assert [unit["meaning_id"] for unit in good["units"]] != stale
    for index, other in ((1, stale[1]), (1, stale[0]), (0, stale[1])):
        def answer(*args, index=index, other=other, **kwargs):
            row = deepcopy(real(*args, **kwargs))
            row["units"][index]["meaning_id"] = other
            return row
        with patch.object(D_load, "_lean_answer", answer), \
                pytest.raises(CheckerUnavailable, match="is not bound to the document sent"):
            D.load_document(path)


def _stored():
    """Every rights content recorded in the fixtures under tests/data."""
    for path in sorted((ROOT / "tests/data").rglob("*.json*")):
        if path.suffix not in (".json", ".jsonl") or path == VERDICTS:
            continue
        text = path.read_text()
        values = [json.loads(line) for line in text.splitlines() if line.strip()] if path.suffix == ".jsonl" \
            else [json.loads(text)]
        stack = list(values)
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                if len(value) == 1 and next(iter(value)) in ("right", "right_lines") and \
                        isinstance(next(iter(value.values())), dict):
                    yield path, value
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)


def test_every_stored_rights_content_is_already_its_normal_form():
    """Rights 3.5 changes no stored id: every recorded rights content is its own normal form."""
    stored = list(_stored())
    assert stored
    from ve.softnorms import soft_digest
    env = _env()
    for _name, content in stored:
        assert rights_meaning_id(env, content) == soft_digest(
            f"ve-meaning-{env.identity_version}\n", {"environment_id": env.environment_id, "ast": content})
