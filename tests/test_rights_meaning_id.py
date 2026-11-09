"""Rights 3.5: a right unit's meaning id binds its normal form, every soft field at its default omitted.

Lean's `document` mode owns the id (`VE.Service.Document.rightsNormalForm`); Python's `rights_meaning_id` relays the
same normal form for the request binding and its own paths, and the differential below holds them equal."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.test_norms import obligation, permission
from tests.test_rights import right, rights_document_file, rights_env
from ve import document as D, readings
from ve.document import load as D_load
from ve.readings import rights_meaning_id
from ve.rights import RightsEnvironment

ROOT = Path(__file__).resolve().parents[1]

DEFAULTS = {"mode": "strict", "rank": None, "alterable": [], "exception": None, "hard": False}
NON_DEFAULTS = {"mode": "default", "rank": "high", "alterable": ["court"], "hard": True,
                "exception": {"decided_by": "court"}}


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


def _env():
    return RightsEnvironment(_raw_env())


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


EXCEPTION = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}


CONTENTS = {"right/norm": (right(), "norm"), "right_lines/liberty": (_power(), "liberty"),
            "right_lines/recognition": (_power(), "recognition")}


@pytest.mark.parametrize("where", sorted(CONTENTS))
@pytest.mark.parametrize("field", sorted(DEFAULTS))
def test_rights_meaning_id_omits_soft_defaults(where, field):
    """An omitted soft field, the field at its default and the field `null` (absent on the rights wire) give one id;
    a value away from the default gives another."""
    env = _env()
    content, slot = CONTENTS[where]
    omitted = rights_meaning_id(env, content)
    assert rights_meaning_id(env, _with(content, slot, **{field: DEFAULTS[field]})) == omitted
    assert rights_meaning_id(env, _with(content, slot, **{field: None})) == omitted
    assert rights_meaning_id(env, _with(content, slot, **{field: NON_DEFAULTS[field]})) != omitted


def test_the_normal_form_leaves_other_content_and_shapes_unchanged():
    bar = {"bar": {"name": "b30", "reading": "rule", "decided_by": "unstated", "mode": "strict"}}
    odd = {"right": {"name": "life", "lines": "not a list"}}
    assert readings.rights_normal_form(bar) == bar and readings.rights_normal_form(odd) == odd
    # `hard: 0` is not the default `false`, as Lean's `Json` reads it.
    assert readings.rights_normal_form(_with(right(), "norm", hard=0)) == _with(right(), "norm", hard=0)


def _lean_ids(path):
    row = D._lean_answer(path.read_bytes(), True)
    assert row is not None, "Lean's document mode decides a rights document"
    return [unit["meaning_id"] for unit in row["units"]]


def _python_ids(path):
    with patch.object(D_load, "_lean_answer", return_value=None):
        return [unit["meaning_id"] for unit in D.load_document(path)["units"]]


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


# The verdict snapshot (DRI adv0838 item 3 (b)), written by `python -m tests.test_rights_meaning_id --write` on main
# before this change (docs/rights/rights-cfr-1/REPORT.md): each fixture's `ve document check` answer, its loaded units
# without their meaning ids (each unit's status is its verdict) and, apart, main's meaning ids.
VERDICTS = ROOT / "tests/data/rights-cfr-1-verdicts.json"


def verdicts(directory):
    """Each fixture's check answer, units and unit meaning ids, as JSON values."""
    answers = {}
    for name, contents in DOCUMENTS.items():
        (directory / name).mkdir()
        path = rights_document_file(directory / name, contents, env=_raw_env())
        units = json.loads(json.dumps(D.load_document(path)["units"], default=str))
        answers[name] = {"check": json.loads(json.dumps(D.check_document(path), default=str)),
                         "units": [{k: v for k, v in unit.items() if k != "meaning_id"} for unit in units],
                         "meaning_ids": [unit["meaning_id"] for unit in units]}
    return answers


def test_no_verdict_or_reason_changes(tmp_path):
    """No verdict changes: every fixture's check answer and loaded units are byte-identical to main's before this
    change, with only the meaning ids differing; those differ exactly where a soft default was written."""
    before = json.loads(VERDICTS.read_text())
    after = verdicts(tmp_path)
    for name in DOCUMENTS:
        assert json.dumps(after[name]["check"], sort_keys=True) == json.dumps(before[name]["check"], sort_keys=True)
        assert json.dumps(after[name]["units"], sort_keys=True) == json.dumps(before[name]["units"], sort_keys=True)
    for name, normal in (("omitted", "omitted"), ("defaults", "omitted"), ("nulls", "omitted"),
                         ("default-mode", "default-mode"), ("power-omitted", "power-omitted"),
                         ("power-defaults", "power-omitted")):
        assert after[name]["meaning_ids"] == before[normal]["meaning_ids"]


def test_a_stored_pre_change_id_is_not_its_new_id(tmp_path):
    """Every id main stored for a content written with a soft default is stale: it does not compare equal to the
    recomputed id, which is the id of the same content without the default."""
    before = json.loads(VERDICTS.read_text())
    env = _env()
    for name in ("defaults", "nulls", "power-defaults"):
        new = [rights_meaning_id(env, content) for content in DOCUMENTS[name]]
        stale = [i for i, (old, now) in enumerate(zip(before[name]["meaning_ids"], new, strict=True)) if old != now]
        assert stale == ([1] if name.startswith("power") else [0])


def _stored():
    """Every stored rights content with its meaning id in the recorded fixtures."""
    for name in ("tests/data/relay-gate-cases.jsonl", "tests/data/route-cases.jsonl",
                 "tests/data/scope/rights-reach-absent-main.json"):
        text = (ROOT / name).read_text()
        values = [json.loads(line) for line in text.splitlines() if line.strip()] if name.endswith("jsonl") \
            else [json.loads(text)]
        stack = list(values)
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                content = value.get("content")
                if isinstance(content, dict) and len(content) == 1 and next(iter(content)) in ("right", "right_lines"):
                    yield name, content
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)


def test_every_stored_rights_content_is_already_its_normal_form():
    """Rights 3.5 changes no stored id: every recorded rights content is its own normal form."""
    stored = list(_stored())
    assert len(stored) == 8
    for _name, content in stored:
        assert readings.rights_normal_form(content) == content


if __name__ == "__main__":
    import sys
    import tempfile
    if sys.argv[1:] != ["--write"]:
        sys.exit("usage: python -m tests.test_rights_meaning_id --write")
    with tempfile.TemporaryDirectory() as directory:
        VERDICTS.write_text(json.dumps(verdicts(Path(directory)), indent=1, sort_keys=True) + "\n")
