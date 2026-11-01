"""The starter packs, their pins and the coverage measurement (senses plan B8, 7.2; sn-b8). Lean judges every pack
(`Dictionary.wf` through `ve senses check`); Python reads bytes, relays and counts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from ve.__main__ import main
from ve.backends import senses as route
from ve.environment import Environment
from ve.senses import bundled_pack, review_status

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "conformance"))
sys.path.insert(0, str(ROOT / "tests"))
import senses_usecases as coverage  # noqa: E402
from test_senses_route import PACK as FIXTURES, WORLDS  # noqa: E402

# Each pack, the use case whose environment (without the covered predicates) reads its fixture, and the fixture.
PACKS = {
    "policies@1": ("agent-policy", '"f_main" resides in workspace.', ["binary", "sense__resides_1"]),
    "software-services@1": ("fluent", "Every service that is deployed is reviewed.", ["forall", "service"]),
}
PINS = json.loads((ROOT / "ve/senses/reviewed-packs.json").read_text())


def senses_env(usecase):
    case = coverage.USECASES[usecase]
    overlay = coverage._json(case["overlay"]) if case["overlay"] else None
    return coverage.reduced(case["env"](), overlay, case["covered"])


def check(tmp_path, capsys, env, pack: bytes, source: str):
    (tmp_path / "env.json").write_text(json.dumps(env.to_dict()))
    (tmp_path / "pack.json").write_bytes(pack)
    (tmp_path / "text.txt").write_text(source)
    code = main(["senses", "check", "--env", str(tmp_path / "env.json"), "--pack", str(tmp_path / "pack.json"),
                 str(tmp_path / "text.txt")])
    return code, json.loads(capsys.readouterr().out)


@pytest.mark.parametrize("name", PACKS)
def test_each_pack_decodes_by_leans_wf(tmp_path, capsys, name):
    usecase, source, head = PACKS[name]
    env, _ = senses_env(usecase)
    code, out = check(tmp_path, capsys, env, bundled_pack(name), source)
    assert code == 0, out["reading"]
    assert out["reading"]["status"] == "one" and out["reading"]["units"][0]["formula"][:len(head)] == head


@pytest.mark.parametrize("name", PACKS)
def test_a_malformed_copy_reaches_the_cli_with_leans_text(tmp_path, capsys, name):
    """A copy whose first wording drops its word: the CLI prints Lean's W3 failure exactly as the relay returns it."""
    usecase, source, _ = PACKS[name]
    env, _ = senses_env(usecase)
    data = json.loads(bundled_pack(name))
    first = data["senses"][0]
    first["wording"] = first["wording"].replace(first["word"], "xq")
    bad = json.dumps(data).encode()
    code, out = check(tmp_path, capsys, env, bad, source)
    assert code == 3 and out["reading"] == route.read(env, source, [bad])["reading"]
    assert out["reading"]["code"] == "InvalidDictionary" and out["reading"]["failure"][:2] == ["W3", first["word"]]


def test_every_starter_pack_is_pinned_and_the_fixture_pack_is_not():
    assert sorted(pin["name"] for pin in PINS) == sorted(PACKS)
    assert all(pin["pack"] == f"ve/senses/packs/{pin['name']}.json" for pin in PINS)
    assert review_status("fixtures@1", route.read(*WORLDS["joke"]()[:1], "x.", [FIXTURES])["dictionary_id"]) \
        == "unreviewed"


@pytest.mark.parametrize("pin", PINS, ids=lambda pin: pin["name"])
def test_each_pin_is_leans_identity_of_the_pack_bytes(pin):
    """i4: the pinned digest is Lean's `dictionary_id` of the pack's bytes (reviewed); one changed byte of the
    description gives another identity, which is unreviewed."""
    env, _ = senses_env(PACKS[pin["name"]][0])
    pack = (ROOT / pin["pack"]).read_bytes()
    assert json.loads(pack)["name"] == pin["name"]
    identity = route.read(env, "x.", [pack])["dictionary_id"]
    assert identity == pin["dictionary_id"] and review_status(pin["name"], identity) == "reviewed"
    changed = pack.replace(b'"description": "', b'"description": "A', 1)
    other = route.read(env, "x.", [changed])["dictionary_id"]
    assert other != identity and review_status(pin["name"], other) == "unreviewed"


UNARY = ["unary", "deployed", ["const", "legacy"]]


@pytest.mark.parametrize("base, senses, same", [
    (UNARY, ["unary", "sense__deployed_1", ["const", "legacy"]], True),
    (UNARY, UNARY, False),  # a covered predicate keeps no name of its own
    (UNARY, ["unary", "sense__deployed_1", ["const", "alice"]], False),
    (["not", UNARY], ["unary", "sense__deployed_1", ["const", "legacy"]], False),
    (["binary", "owns", ["const", "alice"], ["const", "legacy"]],
     ["binary", "owns", ["const", "alice"], ["const", "legacy"]], True),  # not covered: unchanged
    (["binary", "owns", ["const", "alice"], ["const", "legacy"]],
     ["binary", "sense__owns_1", ["const", "alice"], ["const", "legacy"]], False),
])
def test_same_formula_up_to_renaming(base, senses, same):
    assert coverage.same_up_to_renaming(base, senses, ("deployed",), {}, {}) is same


def test_a_renaming_is_one_sense_id_per_predicate_over_the_use_case():
    renaming, inverse = {}, {}
    assert coverage.same_up_to_renaming(UNARY, ["unary", "s1", ["const", "legacy"]], ("deployed",), renaming, inverse)
    assert not coverage.same_up_to_renaming(UNARY, ["unary", "s2", ["const", "legacy"]], ("deployed",), renaming,
                                            inverse)
    reviewed = ["unary", "reviewed", ["const", "legacy"]]
    assert not coverage.same_up_to_renaming(reviewed, ["unary", "s1", ["const", "legacy"]], ("deployed", "reviewed"),
                                            renaming, inverse)


def classify(env_raw, overlay, pack, sentence, covered):
    env = Environment(env_raw)
    senses, senses_overlay = coverage.reduced(env_raw, overlay, covered)
    return coverage.classify(env, overlay, senses, senses_overlay, pack, sentence, covered, {}, {})


FLUENT = coverage._json("examples/fluent/environment.json")


def test_a_sentence_that_reads_the_same_under_the_pack():
    row = classify(FLUENT, None, bundled_pack("software-services@1"), "Every service that is deployed is reviewed.",
                   ("deployed", "reviewed"))
    assert row["class"] == "same"


def test_a_sentence_that_needs_a_line():
    """`funny` has two senses in the fixture pack: the reading is open, and the candidate of the first sense is the
    base formula, so the sentence needs that candidate's Lean line."""
    env, overlay = WORLDS["own-funny"]()
    row = classify(env.to_dict(), overlay, FIXTURES, "The riddle is funny.", ("funny",))
    assert row == {"sentence": "The riddle is funny.", "class": "needs_line",
                   "lines": ["In this document, funny means amusing."]}


def test_a_sentence_that_no_longer_reads_keeps_leans_reason():
    row = classify(FLUENT, None, bundled_pack("policies@1"), "Every service that is deployed is reviewed.",
                   ("deployed",))
    assert row["class"] == "no_longer_reads" and row["code"] == "Collision" and row["details"]


def test_a_sentence_the_base_does_not_read_is_counted_apart():
    row = classify(FLUENT, None, bundled_pack("software-services@1"), "The inventory was exported on Monday.",
                   ("deployed",))
    assert row["class"] == "base_unread" and row["code"] == "NoDerivation"
