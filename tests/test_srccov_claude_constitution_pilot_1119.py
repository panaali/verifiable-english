"""srccov-claude-constitution-pilot-1119: the carried probe records 26 source sentences that state no rule.

The source-coverage map (manage-agents reviews/source-coverage-1119, pin e53db4e8fc) found these sentences ABSENT only
because their unit record named a missing feature (its amendment 13). Each is background, rationale, an example or a
pointer, and its record in the carried probe
(`usecases/claude-constitution-pilot/run-20261119-defs-carry/probe-translation.probe.md`) now says so: the unit is
unformalised for `other.background`, `other.rationale`, `other.example` or `other.navigation`. The driver's rule 8
(`carry_definitions.py`) writes them. For each record the source sentence is read from the pinned translation's body
(`tests/ce4`, checked against its commit's blob), by the map's byte offsets, and checked by its first and last words
after the project's quote normalisation (`tests.omission_rule.omit_norm`). The record must cover that sentence and no
other text. The tests fail on main before this item, where the records name a missing feature, and pass after it.
The search, the model service and git are not called.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import re

import pytest

from tests import ce4
from tests.omission_rule import REPO, omit_norm

CARRY = REPO / "usecases/claude-constitution-pilot/run-20261119-defs-carry"
PROBE = CARRY / "probe-translation.probe.md"
OLD_PROBE = REPO / "usecases/claude-constitution-pilot/run-20261104T0716Z/probe-translation.probe.md"
ROW = "srccov-claude-constitution-pilot-{}-1119"
BG, RA, EX, NAV = "other.background", "other.rationale", "other.example", "other.navigation"
LINK_END = "#heading=h.5rhpfavub2xt)."  # S0258 ends in a link the body keeps
# (map row, source unit, its bytes in the pinned body, its first and last words, the probe unit, the record's reason)
RECORDS = (
    (16, "S0002", 186, 415, "Anthropic occupies a peculiar", "very technology ourselves.", "u0004.s01", BG),
    (16, "S0025", 4539, 4797, "Most of this document", "range of situations.", "u0011.s05", BG),
    (16, "S0066", 12469, 12535, "This document is likely", "in the future.", "u0022.s01", BG),
    (16, "S0069", 12944, 12998, "It is best thought", "work in progress.", "u0022.s04", BG),
    (16, "S0082", 14989, 15198, "Anthropic needs Claude to", "range of tasks.", "u0028.s03", BG),
    (16, "S0088", 16036, 16185, "Beyond their impact in", "its greatest challenges.", "u0030.s01", BG),
    (16, "S0091", 16665, 16856, "Claude and its successors", "in civilizational flourishing.", "u0030.s04", BG),
    (16, "S0122", 21711, 21822, "It is easy to", "their long-term detriment.", "u0038.s01", BG),
    (16, "S0123", 21823, 21967, "Media and applications that", "interact with them.", "u0038.s02", BG),
    (16, "S0170", 29483, 29578, "These settings often introduce", "and operate safely.", "u0051.s02", BG),
    (16, "S0220", 39535, 39612, "The question of how", "a difficult one.", "u0066.s01", BG),
    (17, "S0016", 2768, 3045, "Clear rules have certain", "into behaving badly.", "u0010.s02", RA),
    (17, "S0017", 3046, 3076, "They also have costs,", "have costs, however.", "u0010.s03", RA),
    (17, "S0019", 3239, 3436, "Good judgment, by contrast,", "transparency, and evaluability.", "u0010.s05", RA),
    (17, "S0029", 5362, 5552, "Second, we think relying", "as unexplained constraints.", "u0012.s03", RA),
    (17, "S0074", 13430, 13535, "In addition to any", "mission of Anthropic.", "u0024.s05", RA),
    (17, "S0076", 13737, 13884, "We worry this could", "one at worst.", "u0025.s02", RA),
    (17, "S0126", 22134, 22259, "We don’t return to", "in our lives.", "u0038.s05", RA),
    (17, "S0298", 53194, 53285, "This behavior makes Claude", "poorly on Anthropic.", "u0086.s01", RA),
    (18, "S0086", 15816, 15910, "People with access to", "be for people.", "u0029.s04", EX),
    (18, "S0107", 19021, 19144, "For example, the user", "one they’re using.", "u0035.s07", EX),
    (18, "S0166", 28866, 28963, "For example, Claude might", "sending them instructions.", "u0050.s02", EX),
    (18, "S0194", 34518, 34652, "Out of context, an", "or relevant information.", "u0058.s03", EX),
    (18, "S0275", 50371, 50507, "For example, suppose the", "of the conversation.", "u0081.s02", EX),
    (19, "S0133", 23328, 23442, "We expect this content", "section by default.", "u0041.s02", NAV),
    (19, "S0258", 46438, 46684, "More details about behaviors", LINK_END, "u0074", NAV),
)
IDS = [f"{ROW.format(r[0])}:{r[1]}" for r in RECORDS]
# The map's amendment 12: a sentence with a modal, a number, a condition or a definition is never recorded out of
# scope. "one" is left out: here it is a pronoun ("a difficult one") or "one of the most", never a count.
RULE_WORDS = re.compile(r"\b(?:must|shall|should|will|may|never|need|means|refers?|defined|includes?|if|unless|when|"
                        r"whenever|where|wherever|once|until|provided that|only if|two|three|four|five|six|seven|"
                        r"eight|nine|ten|dozens?|hundreds?|thousands?|millions?|billions?|millennia|\d+)\b|['’]ll\b")


def read(path):
    _, front, body = path.read_bytes().split(b"---\n", 2)
    return json.loads(front), body


def flat(units):
    for u in units:
        yield u
        yield from flat(u.get("children") or u.get("parts") or [])


@pytest.fixture(scope="module")
def probe():
    """The carried probe's units by id, and the pinned translation's front matter and body (the source)."""
    meta, body = read(PROBE)
    _, front, source = ce4.pinned_bytes().split(b"---\n", 2)
    assert body == source
    return {u["id"]: u for u in flat(meta["units"])}, json.loads(front), source


@pytest.fixture(scope="module")
def driver():
    spec = importlib.util.spec_from_file_location("srccov_carry_driver", CARRY / "carry_definitions.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sentence(source, a, b, first, last):
    """The source sentence at bytes `a` to `b`, checked by its first and last words after quote normalisation."""
    text = source[a:b].decode("utf-8")
    assert omit_norm(text).startswith(omit_norm(first)) and omit_norm(text).endswith(omit_norm(last)), text[:80]
    return text


@pytest.mark.parametrize("record", RECORDS, ids=IDS)
def test_the_unit_records_the_sentence_as_out_of_scope(probe, record):
    """The probe unit covers the sentence and nothing else, and is unformalised for what the sentence is."""
    units, _, source = probe
    _, _, a, b, first, last, uid, reason = record
    text = sentence(source, a, b, first, last)
    unit = units[uid]
    start, stop = unit["span"]
    assert start <= a and b <= stop and source[start:stop].decode("utf-8").strip() == text.strip(), uid
    assert unit["kind"] == ["unformalised", reason] and unit["meaning"] == {"unformalised": reason}, uid
    assert "content" not in unit and not (unit.get("children") or unit.get("parts")), uid


@pytest.mark.parametrize("record", RECORDS, ids=IDS)
def test_the_recorded_sentence_states_no_rule(probe, record):
    """Amendment 12's words: no modal, number, condition or definition in a sentence recorded out of scope (a link's
    target is not read)."""
    _, _, source = probe
    _, _, a, b, first, last, _, _ = record
    words = re.sub(r"\]\([^)]*\)", "]", sentence(source, a, b, first, last))
    assert not RULE_WORDS.findall(words.lower())


def test_rule_8_records_exactly_these_units_and_no_other_unit_changes(probe, driver):
    """The driver's table is this file's; every other unit keeps the kind and meaning it has in run-20261104T0716Z's
    probe (the old run's rules 1 to 4, before rule 8), where rule 8's units name a missing feature."""
    units, _, _ = probe
    assert driver.OUT_OF_SCOPE == {uid: reason for *_, uid, reason in RECORDS}
    assert len(RECORDS) == len({r[1] for r in RECORDS}) == 26
    before = {u["id"]: u for u in flat(read(OLD_PROBE)[0]["units"])}
    assert before.keys() == units.keys()
    for uid, unit in units.items():
        old = before[uid]
        if uid in driver.OUT_OF_SCOPE:
            assert old["kind"][0] == "unformalised" and not old["kind"][1].startswith("other."), uid
        else:
            assert (unit["kind"], unit["meaning"]) == (old["kind"], old["meaning"]), uid


def test_rule_8_refuses_a_unit_it_cannot_record(probe, driver):
    """A unit the front matter lacks, a unit with content, and a unit that is not unformalised are refused."""
    _, front, _ = probe
    for uid in ("u9999", "u0073.s05", "u0001"):
        with pytest.raises(ValueError):
            driver.record_out_of_scope(front, {uid: "other.background"})


def test_the_old_runs_unit_check_holds_but_for_rule_8(probe, driver):
    """The wrapped `unchanged` passes on the driver's rewrite and still fails when any other unit's kind changes."""
    _, front, source = probe
    after, _ = driver.rewrite(front)
    driver.unchanged(front, after, source, source)
    other = copy.deepcopy(after)
    [unit] = [u for u in flat(other["units"]) if u["id"] == "u0051.s01"]
    unit["kind"], unit["meaning"] = ["unformalised", "other.background"], {"unformalised": "other.background"}
    with pytest.raises(AssertionError):
        driver.unchanged(front, other, source, source)
