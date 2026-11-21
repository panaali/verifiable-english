"""srccov-rl-safety-framework-1121: FSF 1.3.4's two mitigation-evaluation sentences, carried by rule lines.

The source-coverage map (manage-agents reviews/source-coverage-1119/rows-safety-framework.tsv, row
srccov-safety-framework-s10-36-1119) found S0083 and S0085 ABSENT, tagged 'none: translation omission': a plain line
of the document's own profile (soft-norms@0) carries each. At main both were spans.json records UNFORMALISED with
reason `unspecified_process` (s134-various, s134-deployment).

For each kept unit this checks what a reader is shown:
- the new rule block stands in rules.d1.ve with its one rule line;
- the unit's spans.json record covers the unit's bytes and routes to that rule (status CHECKED, no reason left);
- the legend of the predicate the rule uses (environment.d1.json, what a reader is shown) quotes the sentence, read
  from the pinned FSF 3.1 text at its UTF-8 byte span (tests/pinned_source.py), byte for byte after the project's
  quote normalisation (usecases/safetyfw_accounting.py `norm`);
- the counter (tests/omission_rule.py) shows that legend with the block: the predicate is used by the block, is no
  open term, and the legend's raw vocabulary.py lines hold the quote, so every content word of the sentence is in
  one shown segment.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

from tests import omission_rule as O
from tests.pinned_source import pinned_source

REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "usecases" / "safety-framework"


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


A = _module("safetyfw_accounting", REPO / "usecases" / "safetyfw_accounting.py")

# unit -> (spans.json record, its UTF-8 byte span, the cut before the sentence, rule block, rule line, predicate)
KEPT = {
    "S0083": ("s134-various", (15691, 15783), "", "f7-eval",
              "Rule 1. Every proposal must have its mitigations evaluated.", "mitigations_evaluated"),
    "S0085": ("s134-deployment", (16018, 16220), "● ", "f7-eval-dm",
              "Rule 1. Every proposal must have its deployment mitigations assessed.",
              "deployment_mitigations_evaluated"),
}
# The map's units (units-safety-framework.tsv): the sentence's bytes, which the record must cover.
UNIT_BYTES = {"S0083": (15660, 15782), "S0085": (16018, 16219)}


def _rules_text() -> str:
    return (CASE / "rules.d1.ve").read_text(encoding="utf-8")


def _environment() -> dict:
    return json.loads((CASE / "environment.d1.json").read_text(encoding="utf-8"))


def _spans() -> dict:
    return {u["id"]: u for u in json.loads((CASE / "spans.json").read_text(encoding="utf-8"))["units"]}


def _quoted(legend: str) -> list[str]:
    return legend.split('"')[1::2]


def _sentence(unit: str) -> str:
    _, (start, end), cut, *_ = KEPT[unit]
    text = A.norm(pinned_source("safety-framework").read_bytes()[start:end].decode("utf-8")).strip()
    assert text.startswith(cut), (unit, text)
    return text[len(cut):]


@pytest.mark.parametrize("unit", sorted(KEPT))
def test_the_rule_line_stands_in_the_carrier(unit):
    """The block of the kept unit is in rules.d1.ve, read always (every complete choice), with its one rule line."""
    _, _, _, block, line, _ = KEPT[unit]
    blocks = O.rule_blocks(_rules_text())
    assert block in blocks, block
    head, body = blocks[block]
    assert head.splitlines()[0].startswith(f"## {block} | always | F7, 1.3.4 "), head
    assert body.strip() == line


@pytest.mark.parametrize("unit", sorted(KEPT))
def test_the_span_record_routes_to_the_rule(unit):
    """The unit's spans.json record covers the sentence's bytes and routes to the new rule, CHECKED."""
    record_id, (start, end), _, block, _, _ = KEPT[unit]
    record = _spans()[record_id]
    assert record["span"] == [start, end]
    lo, hi = UNIT_BYTES[unit]
    assert hi <= end
    if lo < start:  # S0083 opens with its section heading, the meta record just before
        heading = _spans()["s134-heading"]
        assert heading["span"] == [lo, start] and heading["kind"] == "meta"
    assert record.get("rule") == block
    assert record["kind"] == "norm" and record["status"] == "CHECKED"
    assert "reason" not in record and not record.get("open_terms")


@pytest.mark.parametrize("unit", sorted(KEPT))
def test_the_legend_quotes_the_pinned_source_sentence(unit):
    """The legend a reader is shown quotes the sentence read from the pinned text, byte for byte after `norm`."""
    predicate = KEPT[unit][5]
    sentence = _sentence(unit)
    legend = _environment()["vocabulary"]["predicates"][predicate]["description"]
    assert sentence in [A.norm(q) for q in _quoted(legend)], (unit, sentence, legend)


@pytest.mark.parametrize("unit", sorted(KEPT))
def test_the_counter_shows_the_legend_with_the_block(unit):
    """Needs no source. The block uses the predicate, the predicate is no open term, and the legend's raw lines in
    vocabulary.py hold every content word of the quoted sentence in one segment the counter shows with the block."""
    _, _, _, block, _, predicate = KEPT[unit]
    env = _environment()
    body = O.rule_blocks(_rules_text())[block][1]
    assert O.used_predicates(body, env) == [predicate]
    vocabulary = _module("safety_framework_vocabulary", CASE / "vocabulary.py")
    assert predicate not in vocabulary.OPEN_PREDICATES
    entry = env["vocabulary"]["predicates"][predicate]
    assert "Open term" not in entry["description"]
    assert entry["regulated"]["role"] == "obligation"
    quote = _quoted(entry["description"])[-1]
    raw = "\n".join(O.strip_comments(O.legend_raw(predicate, (CASE / "vocabulary.py").read_text(
        encoding="utf-8").splitlines())))
    words = set(re.findall(r"[a-z0-9_]+", O.omit_norm(quote)))
    assert words and words <= set(re.findall(r"[a-z0-9_]+", O.omit_norm(raw)))
