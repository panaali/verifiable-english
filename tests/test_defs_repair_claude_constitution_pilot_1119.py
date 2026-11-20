"""defs-repair-claude-constitution-pilot-1119: the legends the pilot's rules use carry the source's definitions.

For each kept row of the 'definitions carried' audit (manage-agents reviews/defs-carried-1119), the source passage is
read here by its file lines from the pinned translation (`tests/ce4`, checked against its commit's blob). Its body is
the source the probe translates. The list marks and bold marks are dropped and the lines joined by one space. The
passage must then occur in the description of the legend the row names in the carried probe
(`usecases/claude-constitution-pilot/run-20261119-defs-carry/probe-translation.probe.md`), after the project's quote
normalisation (`tests.omission_rule.omit_norm`). Each row's rules must use that legend's term, so the carrier is not
some other legend. The test fails on main before this item and passes after it. The carried probe is its driver's
rewrite of the pinned translation, and it differs from run-20261104T0716Z's probe only in those legends and in the
identities the environment hashes (DRI decision 2026-11-19 item 1). The search, the model service and git are not
called.
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
HC = [f"u0165.s0{i}" for i in range(1, 8)]
CLAUDE = ((655, 655, "The name “Claude” is often used", "documents like this one."),)
USERS = ((99, 99, "Users: Those who interact", "than mistakenly assuming there is."),
         (101, 101, "Whether someone should be treated", "what kind of entity they are."))
DECEPTION = ((292, 292, "Deception involves attempting", "what was happening."),)
ANTHROPIC = (97, 97, "Anthropic: We are the entity", "than operators or users.")
GUIDELINES = ((34, 34, "Compliant with Anthropic’s guidelines:", "where they’re relevant."),
              (247, 247, "Beyond the broad principles", "in particular circumstances."), ANTHROPIC)
OPERATOR_RULES = ["u0062.s01", "u0123.s01.p1", "u0123.s02.p1", "u0123.s03"]
# (audit row id, legend, the rules that use it, its source passages: first and last file line, first and last words)
ROWS = (
    ("defs-claude-constitution-pilot-1-1119", ("sorts", "claude_instance"),
     ["u0036.s05", "u0052.s01", "u0073.s05", "u0125.s04.p2", "u0156.s03", *HC, "u0168.s01", "u0263.s04.p2"], CLAUDE),
    ("defs-claude-constitution-pilot-2-1119", ("constants", "claude"), ["u0248"], CLAUDE),
    ("defs-claude-constitution-pilot-3-1119", ("sorts", "operator"), OPERATOR_RULES,
     ((98, 98, "Operators: Companies", "within their platforms."), *USERS)),
    ("defs-claude-constitution-pilot-4-1119", ("sorts", "user"), ["u0156.s03"], USERS),
    ("defs-claude-constitution-pilot-5-1119", ("predicates", "instruction_deceptive_tactics_harming_users"),
     OPERATOR_RULES, DECEPTION),
    ("defs-claude-constitution-pilot-6-1119", ("predicates", "system_prompt_deception_permitted"), ["u0156.s03"],
     DECEPTION),
    ("defs-claude-constitution-pilot-7-1119", ("predicates", "judgment_use_required"), ["u0052.s01"],
     ((111, 111, "Conversational inputs: Tool call", "performing a search)."),
      (113, 113, "And if any outputs", "instructions from a principal."))),
    ("defs-claude-constitution-pilot-8-1119", ("predicates", "instruction_dishonest_looking_within_honesty"),
     ["u0123.s01.p1"], ((282, 290, "There are many different components", "their own reasoning process."),)),
    ("defs-claude-constitution-pilot-9-1119", ("predicates", "instruction_act_against_guidelines"), OPERATOR_RULES,
     GUIDELINES),
    ("defs-claude-constitution-pilot-10-1119", ("predicates", "compliance_against_guidelines"), ["u0073.s05"],
     GUIDELINES),
    ("defs-claude-constitution-pilot-11-1119", ("predicates", "compliance_unsafe"), ["u0073.s05"],
     ((32, 32, "Broadly safe: Not", "phase of development."),)),
    ("defs-claude-constitution-pilot-12-1119", ("predicates", "compliance_unethical"), ["u0073.s05"],
     ((33, 33, "Broadly ethical: Having", "dangerous or harmful."),)),
    ("defs-claude-constitution-pilot-13-1119", ("predicates", "clear_and_substantial_undermining_of_oversight"),
     ["u0165.s04"], ((609, 609, "That is, per the hard constraints", "forms of power-seeking."),
                     (41, 41, "Supporting human oversight", "safety below."), ANTHROPIC)),
    ("defs-claude-constitution-pilot-14-1119", ("predicates", "illegitimate_absolute_control"), ["u0165.s06"],
     ((476, 480, "Assessing the legitimacy", "to escape accountability."),)),
    ("defs-claude-constitution-pilot-15-1119", ("predicates", "seemingly_compelling_argument_to_cross_line"),
     ["u0168.s01"], ((436, 444, "The current hard constraints", "material (CSAM)."),
                     (446, 446, "These represent absolute restrictions", "outweigh them."),
                     (456, 456, "Hard constraints are restrictions", "otherwise promote."),
                     (460, 460, "Hard constraints are centrally meant", "into such a category."))),
)


def read(path):
    _, front, body = path.read_bytes().split(b"---\n", 2)
    return json.loads(front), body


@pytest.fixture(scope="module")
def probe():
    """The carried probe's front matter and the pinned translation's lines (the source)."""
    return read(PROBE)[0], ce4.pinned_bytes().decode("utf-8").split("\n")


@pytest.fixture(scope="module")
def driver():
    spec = importlib.util.spec_from_file_location("defs_carry_driver", CARRY / "carry_definitions.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_passage(lines, first, last, start, end):
    """File lines `first` to `last` without list or bold marks, joined by one space, from `start` through `end`.
    The passage must begin a sentence or a list entry and close a sentence: the audit's full-span rule."""
    joined = " ".join(re.sub(r"^\s*(?:[*-]|\d+\.)\s+", "", line).replace("**", "").strip()
                      for line in lines[first - 1:last] if line.strip())
    i = joined.find(start)
    assert i >= 0 and joined.find(start, i + 1) < 0, (first, start)
    assert i == 0 or joined[:i].endswith((". ", ".) ")), (first, joined[max(0, i - 30):i])
    j = joined.find(end, i)
    assert j >= 0 and end.endswith("."), (first, end)
    return joined[i:j + len(end)]


def uses(meta, uid, kind, name):
    """Whether unit `uid` (its content or its reading candidates) names the term: a predicate or constant by name,
    a sort through the arguments of a predicate it names."""
    [unit] = [u for u in _flat(meta["units"]) if u["id"] == uid]
    readings = [R["readings"] for R in meta["reading_sets"] if R["unit"] == uid]
    blob = json.dumps([unit.get("content"), readings])
    predicates = meta["environment"]["vocabulary"]["predicates"]
    named = [p for p in predicates if f'"{p}"' in blob]
    if kind == "sorts":
        return any(name in predicates[p]["arguments"] for p in named)
    return name in named


def _flat(units):
    for u in units:
        yield u
        yield from _flat(u.get("children") or u.get("parts") or [])


@pytest.mark.parametrize("row", ROWS, ids=[r[0] for r in ROWS])
def test_the_legend_carries_the_source_definition_word_for_word(probe, row):
    meta, lines = probe
    _, (kind, name), rules, spans = row
    description = meta["environment"]["vocabulary"][kind][name]["description"]
    for first, last, start, end in spans:
        quote = source_passage(lines, first, last, start, end)
        assert omit_norm(quote) in omit_norm(description), (name, quote[:80])


@pytest.mark.parametrize("row", ROWS, ids=[r[0] for r in ROWS])
def test_the_rules_of_the_row_use_the_legends_term(probe, row):
    meta, lines = probe
    _, (kind, name), rules, _ = row
    for uid in rules:
        if uid == "u0248":
            # The English fence names Claude; the vocabulary's only name for it is the constant `claude`.
            [unit] = [u for u in _flat(meta["units"]) if u["id"] == uid]
            fence = lines.index(f"```ve {uid}")
            assert unit["content"] == {"fence": uid} and lines[fence + 1] == "Claude is not human."
            assert (kind, name) == ("constants", "claude") and name in meta["environment"]["vocabulary"][kind]
            continue
        assert uses(meta, uid, kind, name), (uid, name)


def test_the_legends_only_grow():
    """The carry appends: each legend keeps its earlier description as its start (the pinned translation's)."""
    _, front, _ = ce4.pinned_bytes().split(b"---\n", 2)
    before = json.loads(front)["environment"]["vocabulary"]
    after = read(PROBE)[0]["environment"]["vocabulary"]
    for _, (kind, name), _, _ in ROWS:
        old, new = before[kind][name]["description"], after[kind][name]["description"]
        assert new.startswith(old + " ") and len(new) > len(old) + 1, name


def without_identities(meta):
    """The front matter without what the environment's identity hashes: candidate ids and situation ids."""
    meta = copy.deepcopy(meta)
    for R in meta["reading_sets"]:
        R["situations"] = sorted(json.dumps(v, sort_keys=True) for v in R.get("situations", {}).values())
        for r in R["readings"]:
            r.pop("meaning_id", None)
            r["admission"]["distinguishing_models"] = sorted(r["admission"]["distinguishing_models"])
    return meta


def test_only_the_rows_legends_and_the_identities_change(driver):
    """Against run-20261104T0716Z's probe: the same body; the same front matter once candidate and situation ids are
    set aside, the 15 legends given back their old descriptions and the 26 unit records of rule 8
    (srccov-claude-constitution-pilot-1119) their old reasons. Its formulas and situations stay."""
    old, old_body = read(OLD_PROBE)
    new, new_body = read(PROBE)
    assert new_body == old_body == ce4.pinned_bytes().split(b"---\n", 2)[2]
    restored = copy.deepcopy(new)
    keys = {key for _, key, _, _ in ROWS}
    assert len(keys) == 15
    for kind, name in keys:
        entry = restored["environment"]["vocabulary"][kind][name]
        assert entry["description"] != old["environment"]["vocabulary"][kind][name]["description"]
        entry["description"] = old["environment"]["vocabulary"][kind][name]["description"]
    assert len(driver.OUT_OF_SCOPE) == 26
    old_units = {u["id"]: u for u in _flat(old["units"])}
    for unit in _flat(restored["units"]):
        if unit["id"] in driver.OUT_OF_SCOPE:
            assert unit["kind"] != old_units[unit["id"]]["kind"], unit["id"]
            unit["kind"], unit["meaning"] = old_units[unit["id"]]["kind"], old_units[unit["id"]]["meaning"]
    assert without_identities(restored) == without_identities(old)
    assert [r["meaning_id"] for R in new["reading_sets"] for r in R["readings"]] != \
        [r["meaning_id"] for R in old["reading_sets"] for r in R["readings"]]


def test_the_committed_probe_is_the_drivers_rewrite(driver):
    """The carried probe is the driver's rewrite of the pinned translation (the old run's rules, then rule 7), with
    the search's situations and the candidate ids it records; its changed units and candidate ids are the saved ones."""
    _, front, _ = ce4.pinned_bytes().split(b"---\n", 2)
    written, changed = driver.rewrite(json.loads(front))
    probe = read(PROBE)[0]
    found = copy.deepcopy(probe)
    for R in found["reading_sets"]:
        [sid] = R.pop("situations")
        for r in R["readings"]:
            assert r.pop("meaning_id") and set(r["admission"]["distinguishing_models"].values()) == {sid}
            r["admission"]["distinguishing_models"] = {o: "pending" for o in r["admission"]["distinguishing_models"]}
    for R in written["reading_sets"]:
        for r in R["readings"]:
            r.pop("meaning_id")
    assert found == written
    saved = json.loads((CARRY / "changed_units.json").read_text())
    assert saved["changed_units"] == changed and saved["probe"] == PROBE.name
    ids = json.loads((CARRY / "answers/meaning-ids.json").read_text())
    assert {f"{R['id']}:{r['id']}": r["meaning_id"] for R in probe["reading_sets"] for r in R["readings"]} == \
        {k: v["candidate"] for k, v in ids.items()}
    searched = json.loads((CARRY / "answers/search.json").read_text())
    assert searched["pairs_without_situation"] == [] and searched["search_limits"] == []
    assert searched["situations"] == {R["id"]: sorted(R["situations"]) for R in probe["reading_sets"]}


def test_rule_7_refuses_a_passage_it_cannot_cut(driver):
    """A start that is missing or occurs twice, an end missing after the start, or a legend the vocabulary lacks."""
    meta = read(PROBE)[0]
    source = ce4.pinned_bytes().split(b"---\n", 2)[2]
    for spans in ((("No such words in the source", "."),), (("Claude", "."),),
                  (("Deception involves attempting", "no such ending words."),)):
        with pytest.raises(ValueError):
            driver.carry_definitions(meta, source, {("predicates", "compliance_unsafe"): spans})
    with pytest.raises(ValueError):
        driver.carry_definitions(meta, source, {("predicates", "no_such_predicate"): driver.DECEPTION})


HASH = re.compile(r"[0-9a-f]{64}")


@pytest.mark.parametrize("document", ["after", "strict"])
def test_c9_point_status_is_the_old_runs_but_for_identities(document):
    """Saved evidence: the carried probe's C9 point statuses, measured by run-20261104T0716Z's measure.py, are the old
    run's record byte for byte once every 64-hex identity is masked; the same 80 statuses (UNDECIDED or SETTLED yes)."""
    old = (OLD_PROBE.parent / "answers" / document / "point-status-c9.out").read_text()
    new = (CARRY / "answers" / document / "point-status-c9.out").read_text()
    assert HASH.sub("#", new) == HASH.sub("#", old) and HASH.findall(new) != HASH.findall(old)
    statuses = [c["answer"]["inner"]["point_status"] for c in json.loads(new)["cases"]]
    assert len(statuses) == 80 and set(statuses) <= {"UNDECIDED", "SETTLED yes"}
    steps = json.loads((CARRY / "answers/measurements.json").read_text())["steps"]
    assert [(s["document"], s["step"], s["returncode"]) for s in steps] == [
        ("after", "point-status-c9", 0), ("strict", "point-status-c9", 0)]


def test_c9_point_status_records_are_bound_to_the_carried_probe(tmp_path, driver):
    """Each saved record's inner request is the case the carried probe gives (its environment, so its legends)."""
    from tests import lean_routes
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")
    spec = importlib.util.spec_from_file_location("defs_carry_c9_status", OLD_PROBE.parent / "c9_status.py")
    c9_status = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c9_status)
    meta, source = read(PROBE)
    strict = tmp_path / "strict.ve.md"
    driver.migrate_soft.pilot.write(strict, c9_status.strict_twin(meta), source)
    for document, path in (("after", PROBE), ("strict", strict)):
        cases, labels = c9_status.point_status_cases(path)
        saved = json.loads((CARRY / "answers" / document / "point-status-c9.out").read_text())["cases"]
        assert len(cases) == len(saved) == 80
        assert [r["inner_request"] for r in saved] == [c["inner"] for c in cases]
        assert [r["scenario"] for r in saved] == labels
