"""defs-repair-math-mini-paper-1119: the paper's own definitions are carried word for word in the legends its rules use.

Two P1 rows of the 'definitions carried' audit (defs-carried-1119, rows-math-mini-paper.tsv):

- defs-math-mini-paper-1-1119: D3 (paper.template.md, Definition D3 **Prose.**) on the `sim` legend of
  environment.json, the predicate T6, T7, T7a, T7b and T7mono use (T7's own premises hold no definition axiom).
- defs-math-mini-paper-2-1119: the closure-profile sentence of section 7 on the `r` legend of
  environment-closure.json, the relation every T9-family conclusion closes over (`tc[r]`, `rtc[r]`).

Each sentence is read from the source file, never copied into this test. Markdown emphasis (`*`, `**`) is markup, not
wording, and is dropped from the source before comparison; then both sides go through the project's quote
normalisation (`tests/omission_rule.py:omit_norm`, NFKC, quotes and dashes, case and whitespace).
"""

import json
import re
from pathlib import Path

import pytest

from tests.omission_rule import omit_norm

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "usecases/math-mini-paper"


def _section(heading):
    """Lines of paper.template.md from `heading` (exact line) to the next heading of the same or higher level."""
    lines = (PAPER / "paper.template.md").read_text(encoding="utf-8").splitlines()
    start = lines.index(heading)
    level = len(heading) - len(heading.lstrip("#"))
    end = next((i for i in range(start + 1, len(lines))
                if re.match(r"#{1,%d} " % level, lines[i])), len(lines))
    return lines[start + 1:end]


def _first_sentence(paragraph):
    text = re.sub(r"\s+", " ", paragraph.replace("*", "")).strip()
    return re.split(r"(?<=\.)\s+(?=[A-Z])", text)[0]


def source_d3():
    prose = [line for line in _section("### Definition D3 (symmetrisation)") if line.startswith("**Prose.**")]
    assert len(prose) == 1, prose
    return _first_sentence(prose[0][len("**Prose.**"):])


def source_closure():
    body = _section("## 7. Transitive closure (`closure@0`)")
    paragraph = []
    for line in body:
        if not line.strip():
            if paragraph:
                break
            continue
        paragraph.append(line)
    assert paragraph and paragraph[0].startswith("The closure profile adds"), paragraph
    return _first_sentence(" ".join(paragraph))


def legend(env_file, predicate):
    env = json.loads((PAPER / env_file).read_text(encoding="utf-8"))
    return env["vocabulary"]["predicates"][predicate]["description"]


ROWS = [
    ("defs-math-mini-paper-1-1119", source_d3, "environment.json", "sim",
     "For a preorder (X, ≤) put x ∼ y iff x ≤ y and y ≤ x."),
    ("defs-math-mini-paper-2-1119", source_closure, "environment-closure.json", "r",
     "The closure profile adds `tc[r](a, b)` and `rtc[r](a, b)` — the transitive and reflexive-transitive closures"
     " of a named homogeneous binary relation — with a least-fixed-point semantics over arbitrary, possibly infinite"
     " structures."),
]


@pytest.mark.parametrize("row,source,env_file,predicate,audit_quote", ROWS, ids=[r[0] for r in ROWS])
def test_source_definition_is_carried_in_the_rules_legend(row, source, env_file, predicate, audit_quote):
    sentence = source()
    # The span the audit row names is the span the source file holds (no truncation, no paraphrase).
    assert sentence == audit_quote, (row, sentence)
    assert omit_norm(sentence) in omit_norm(legend(env_file, predicate)), (row, legend(env_file, predicate))


def test_carrier_is_used_by_the_rules_it_serves():
    theorems = PAPER / "theorems"

    def text(tid):
        return (theorems / tid / "premises.ve").read_text() + (theorems / tid / "conclusion.ve").read_text()

    for tid in ("T6", "T7", "T7a", "T7b", "T7mono"):
        assert re.search(r"\bsim\b", text(tid)), tid
    # T7 states no definition axiom of `sim` in its own premises: the legend is its only carrier.
    assert " iff " not in (theorems / "T7" / "premises.ve").read_text()
    assert not any("(x0 sim x1), then ((x0 le x1) and (x1 le x0))" in line
                   for line in (theorems / "T7" / "premises.ve").read_text().splitlines())
    for tid in ("T9", "T9a", "T9b", "T9c", "T9d", "T9e"):
        assert re.search(r"\btc\[r\]|\brtc\[r\]", text(tid)), tid


def test_certificates_pin_the_carrier_environments():
    """Every committed certificate's environment_id is the id of the environment file it was proved in."""
    from ve import Environment

    ids = {name: Environment.from_dict(json.loads((PAPER / name).read_text())).environment_id
           for name in ("environment.json", "environment-closure.json")}
    seen = set()
    for path in sorted((PAPER / "theorems").glob("*/certificate.json")):
        if not path.read_bytes().strip():
            continue
        cert = json.loads(path.read_bytes())
        name = "environment-closure.json" if cert["checker_version"].startswith("ve-tableau-closure-") else "environment.json"
        assert cert["environment_id"] == ids[name], path
        seen.add(name)
    assert seen == set(ids)
    for case in ("T9_induction", "T9e_induction"):
        query = json.loads((ROOT / "usecases/closure-induction" / case / "query.json").read_text())
        assert legend("environment-closure.json", "r") == query["environment"]["vocabulary"]["predicates"]["r"]["description"]
        assert query["certificate"]["environment_id"] == ids["environment-closure.json"], case
