"""The fidmech frozen data: cues.json and logic_words.json pinned by sha256 (plan sections 1 and 3.0), their loaders'
refusals, the quantifier decision, and the three use cases' ruled_out.json files (plan 2c: a list, `[]` at first).

A change to either pinned file changes every L1a, L3 and L4 result, so it shows as an edit of this test in review;
changed after a first FSF or PF check run, it marks that document in-sample in the report (plan 3.0 rule 5).
"""
import hashlib
import json
from pathlib import Path

import pytest

from tools.fidmech import sentchecks as C

ROOT = Path(__file__).resolve().parents[1]
PINS = {"cues.json": "1ab93331f16da521a1b8bacbb193f8a118f1060d391866510db66216e9feb926",
        "logic_words.json": "1c7c6308e9e511af3e777e254b60a80a45467653eca6962e3ab126d42c40f389"}
DOCS = ("anthropic-rsp", "safety-framework", "openai-preparedness")


@pytest.mark.parametrize("name", PINS)
def test_the_frozen_data_file_has_its_pinned_sha256(name):
    assert hashlib.sha256((ROOT / "tools/fidmech" / name).read_bytes()).hexdigest() == PINS[name]


def test_the_logic_word_classes_are_the_frozen_ones_and_the_quantifiers_stay_out():
    logic = C.load_logic_words()
    classes = [[w for w, _ in c] for c in logic.classes]
    for cls in (["within"], ["after"], ["before", "prior to"], ["once", "upon"], ["unless", "except"],
                ["only", "solely", "exclusively"], ["until"], ["at least"], ["at most"], ["never"]):
        assert cls in classes
    flat = {w for c in classes for w in c}
    assert not flat & {"all", "every", "each", "any", "no", "in", "following"}
    assert logic.template == {"if", "unless", "not"}


def test_a_logic_word_matches_whole_words_only():
    logic = C.load_logic_words()
    cls = next(c for c in logic.classes if c[0][0] == "once")
    assert logic.members("Upon receipt we act.", cls) == ["upon"]
    assert logic.members("We act concurrently.", cls) == []
    prior = next(c for c in logic.classes if c[0][0] == "before")
    assert logic.members("prior\nto release", prior) == ["prior to"]


@pytest.mark.parametrize("change, message", [
    (lambda d: d.update(schema="other/1"), "schema"),
    (lambda d: d["classes"].append(["within"]), "two classes"),
    (lambda d: d["classes"].append(["each"]), "in a class and out"),
    (lambda d: d["classes"].append([]), "non-empty list"),
])
def test_the_logic_words_loader_refuses_a_malformed_file(change, message, tmp_path):
    data = json.loads((ROOT / "tools/fidmech/logic_words.json").read_text(encoding="utf-8"))
    change(data)
    (tmp_path / "l.json").write_text(json.dumps(data))
    with pytest.raises(C.DataError, match=message):
        C.load_logic_words(tmp_path / "l.json")


@pytest.mark.parametrize("change, message", [
    (lambda d: d.update(schema="other/1"), "schema"),
    (lambda d: d.update(modal=[]), "non-empty list"),
    (lambda d: d.update(min_words_by_kind="5"), "integer"),
    (lambda d: d["first_person"].update(hedges=[""]), "non-empty list"),
])
def test_the_cues_loader_refuses_a_malformed_file(change, message, tmp_path):
    data = json.loads((ROOT / "tools/fidmech/cues.json").read_text(encoding="utf-8"))
    change(data)
    (tmp_path / "c.json").write_text(json.dumps(data))
    with pytest.raises(C.DataError if message != "integer" else ValueError, match=message):
        C.load_cues("anthropic-rsp", tmp_path / "c.json")


@pytest.mark.parametrize("doc", DOCS)
def test_each_use_case_has_a_ruled_out_list_whose_entries_have_a_reason(doc):
    data = json.loads((ROOT / "usecases" / doc / "fidmech/ruled_out.json").read_text(encoding="utf-8"))
    assert isinstance(data, list)
    for entry in data:
        assert set(entry) == C.RULED_OUT_KEYS and entry["reason"].strip() and entry["by"].strip()
