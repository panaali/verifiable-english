"""defs-repair-claude-constitution-excerpt-1119: the seven P1 definitions of the 'definitions carried' audit are carried.

Each row names a term a claims.ve rule depends on, the source definition (source.md's numbered sentences, read here
from the source file in the repository, never from a copy) and the legend that carries it: the description of the
sort or predicate the rule uses, in environment.json (the owner) and in definitions-environment.json (generated from
it by verify_definitions.py). Each carried description must contain the whole source span byte for byte, and also
after the omission counter's quote normalisation (tests/omission_rule.py `omit_norm`).
"""
import json
import re
from pathlib import Path

import pytest

from omission_rule import omit_norm

CASE = Path(__file__).resolve().parents[1] / "usecases/claude-constitution-excerpt"
CARRIERS = ("environment.json", "definitions-environment.json")

# (row id, vocabulary category, carrier key, source sentence numbers, claims.ve lines whose rule uses the key)
ROWS = (
    ("defs-claude-constitution-excerpt-1-1119", "sorts", "property", (4, 5, 6, 7), (7, 8)),
    ("defs-claude-constitution-excerpt-2-1119", "predicates", "ought_have_core_values", (4, 5, 6, 7), (1,)),
    ("defs-claude-constitution-excerpt-3-1119", "predicates", "appropriate", (4,), (2, 9)),
    ("defs-claude-constitution-excerpt-4-1119", "predicates", "undermines", (18,), (2, 9)),
    ("defs-claude-constitution-excerpt-5-1119", "predicates", "honest", (5,), (3,)),
    ("defs-claude-constitution-excerpt-8-1119", "predicates", "outranks", (9,), (6, 7, 8)),
    ("defs-claude-constitution-excerpt-9-1119", "sorts", "overseer", (20, 21), (11,)),
)

# The defined phrase each span opens with: a guard against reading the wrong sentence of the source.
OPENINGS = {
    4: "Broadly safe:", 5: "Broadly ethical:", 6: "Compliant with Anthropic's guidelines:", 7: "Genuinely helpful:",
    9: "Here, the notion of prioritization", 18: "Supporting human oversight", 20: "Being overseeable", 21: "Instead,",
}


def source_sentences():
    """{n: text} of source.md's 'Excerpt formalised' list (lines 'n. text')."""
    text = (CASE / "source.md").read_text(encoding="utf-8")
    section = text.split("## Excerpt formalised", 1)[1].split("\n## ", 1)[0]
    found = {int(m.group(1)): m.group(2) for m in re.finditer(r"^(\d+)\. (.+)$", section, re.M)}
    assert sorted(found) == list(range(1, 22)), sorted(found)
    return found


def source_span(numbers):
    sentences = source_sentences()
    for n in numbers:
        assert sentences[n].startswith(OPENINGS[n]), (n, sentences[n])
    return " ".join(sentences[n] for n in numbers)


def description(carrier, category, key):
    vocabulary = json.loads((CASE / carrier).read_text(encoding="utf-8"))["vocabulary"]
    return vocabulary[category][key]["description"]


@pytest.mark.parametrize("carrier", CARRIERS)
@pytest.mark.parametrize("row,category,key,numbers,rules", ROWS, ids=[r[0] for r in ROWS])
def test_the_source_definition_is_carried_word_for_word(row, category, key, numbers, rules, carrier):
    span = source_span(numbers)
    legend = description(carrier, category, key)
    assert span in legend, f"{row}: {carrier} {key} does not carry source sentences {numbers}"
    assert omit_norm(span) in omit_norm(legend)


@pytest.mark.parametrize("row,category,key,numbers,rules", ROWS, ids=[r[0] for r in ROWS])
def test_the_carrier_is_a_term_the_rule_uses(row, category, key, numbers, rules):
    """The legend carries for the rule only if the rule uses its key (directly, or as the sort of a constant or
    variable the rule names)."""
    lines = (CASE / "claims.ve").read_text(encoding="utf-8").splitlines()
    vocabulary = json.loads((CASE / "environment.json").read_text(encoding="utf-8"))["vocabulary"]
    for n in rules:
        words = set(re.findall(r"[A-Za-z_]+", lines[n - 1]))
        constant_sorts = {vocabulary["constants"][w[1:]]["sort"] for w in re.findall(r"@[a-z_]+", lines[n - 1])}
        assert key in words or key in constant_sorts, (row, n, lines[n - 1])


REPO = CASE.parents[1]
EVIDENCE = REPO / "docs/usecases/claude-constitution-excerpt/defs-repair-claude-constitution-excerpt-1119/evidence"
PRE_CHANGE_ENVIRONMENT_ID = "98dbed69e9ed29c573756d4658b1fae39223466f3cb525f994648b7a5d4622cb"
REVIEWED_OVERLAY_DIGEST = "8411f393465a93ed63fdb8de8ee1d78ce32efb7265660ae6458a986ab3062088"


def without_appends(raw):
    """environment.json with each carried source span (and its joining space) removed again."""
    data = json.loads(raw)
    for _, category, key, numbers, _ in ROWS:
        entry = data["vocabulary"][category][key]
        suffix = " " + source_span(numbers)
        assert entry["description"].endswith(suffix), key
        entry["description"] = entry["description"][:-len(suffix)]
    return data


def test_the_only_environment_change_is_the_appended_source_spans():
    """Removing the seven appended spans gives back the environment the 2026-09-21 overlay review was bound to."""
    from ve.environment import Environment
    raw = (CASE / "environment.json").read_text(encoding="utf-8")
    assert Environment(without_appends(raw)).environment_id == PRE_CHANGE_ENVIRONMENT_ID


def test_the_overlay_review_is_carried_only_by_the_environment_id_rebind():
    """DRI decision 2026-11-19 (defs-repair-claude-constitution-excerpt-1119, item 1): the rebound overlay differs
    from the reviewed one only in environment_id, and the new pinned record names the reviewed digest it carries."""
    from ve.environment import Environment
    from ve.english_vocabulary import overlay_provenance
    overlay = json.loads((CASE / "environment.english.json").read_text(encoding="utf-8"))
    reviewed = json.loads((EVIDENCE / "reviewed-overlay-20260921.json").read_text(encoding="utf-8"))
    assert overlay_provenance(reviewed)["overlay_digest"] == REVIEWED_OVERLAY_DIGEST
    env = Environment.from_json((CASE / "environment.json").read_bytes())
    assert overlay["environment_id"] == env.environment_id != PRE_CHANGE_ENVIRONMENT_ID
    assert reviewed["environment_id"] == PRE_CHANGE_ENVIRONMENT_ID
    assert set(overlay) == set(reviewed)
    assert [k for k in overlay if overlay[k] != reviewed[k]] == ["environment_id"]
    assert overlay_provenance(dict(overlay, environment_id=PRE_CHANGE_ENVIRONMENT_ID))["overlay_digest"] \
        == REVIEWED_OVERLAY_DIGEST
    provenance = overlay_provenance(overlay)
    assert provenance["review_status"] == "reviewed"
    records = json.loads((REPO / "ve/reviewed-overlays.json").read_text(encoding="utf-8"))
    mine = [r for r in records if r["overlay"] == "usecases/claude-constitution-excerpt/environment.english.json"]
    assert [r["overlay_digest"] for r in mine] == [REVIEWED_OVERLAY_DIGEST, provenance["overlay_digest"]]
    assert mine[0]["reviewer"] == "GPT-6 Astra (Worker X)" and mine[0]["date"] == "2026-09-21"
    assert mine[1]["carried_from"] == REVIEWED_OVERLAY_DIGEST
    assert "rebind" in mine[1]["reviewer"] and REVIEWED_OVERLAY_DIGEST in mine[1]["scope"]


def test_the_generated_environment_keeps_every_owner_description():
    """definitions-environment.json is verify_definitions.py's copy of environment.json plus the definitions: every
    sort, predicate and constant description of the owner reappears unchanged."""
    owner = json.loads((CASE / "environment.json").read_text(encoding="utf-8"))["vocabulary"]
    generated = json.loads((CASE / "definitions-environment.json").read_text(encoding="utf-8"))["vocabulary"]
    for category in ("sorts", "predicates", "constants"):
        for name, entry in owner[category].items():
            assert generated[category][name]["description"] == entry["description"], (category, name)
