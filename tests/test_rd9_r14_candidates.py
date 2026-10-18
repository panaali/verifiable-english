"""R14 on rd-9's constitution results (review F26 of rd-9, DRI condition B1(c); DRI-RULINGS R14).

VE proves conflicts in the translated text. Whether the constitution itself conflicts depends on the translation, so a
conflict the readings route reports about `CE4` (the pilot's translation of the constitution's four sets) is a
candidate until an independent source check has run (SC-9's EXTERNAL check, a FOLLOW-UP). No rd-9 report, spec,
docstring or golden may call such a conflict a conflict in the source unless the same paragraph, table row or
function carries the label `CANDIDATE (R14 source check pending: SC-9 external check, FOLLOW-UP)`. Answers are not
changed; only how they are presented.

The scan reads every rd-9 report and spec and the `CE4` tests' strings (docstrings, comments are not read, goldens).
A unit is about the source when it names `CE4`, the constitution or the pilot; it states a conflict when it uses the
route's conflict verdict (`CONFLICT`, not `CONFLICT-FREE`) or says that rules conflict, contradict or are in conflict.
The F-ND fixtures are synthetic documents with no source text, so R14 has nothing to check there.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LABEL = "CANDIDATE (R14 source check pending: SC-9 external check, FOLLOW-UP)"
REPORTS = ("docs/rd-9/**/*.md", "docs/readings-defaults/rd9-lean/*.md", "docs/spec/rd-9-*.md")
GOLDENS = ("tests/test_readings_sd_ce4.py", "tests/ce4.py")
SOURCE = re.compile(r"\bCE4\b|constitution|\bpilot\b", re.IGNORECASE)
CLAIM = re.compile(r"\bconflicts? (?:in the source|between|among|with)\b|\bcontradict"
                   r"|\bin conflict\b|\bconflicting\b|\bis a conflict\b|\breal conflict\b", re.IGNORECASE)
# Only the route's verdict word is upper case; in prose "conflict" alone names the question asked ("the conflict
# answer"), which states nothing about the source.
VERDICT = re.compile(r"\bCONFLICT\b(?![-_ ]FREE)")


def _markdown_units(text):
    """Paragraphs, with each table row and list item its own unit."""
    units, block = [], []
    for line in text.splitlines():
        if not line.strip():
            units.append("\n".join(block))
            block = []
        elif line.lstrip().startswith(("|", "- ", "* ")) or re.match(r"\s*\d+\. ", line):
            units.append("\n".join(block))
            block = [line]
        else:
            block.append(line)
    units.append("\n".join(block))
    return [u for u in units if u.strip()]


def _python_units(text):
    """Each function's strings (docstring and goldens) as one unit, and the module's own strings as another."""
    tree = ast.parse(text)
    units, inside = [], set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            strings = [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
            inside.update(id(n) for n in ast.walk(node))
            units.append("\n".join(strings))
    units.append("\n".join(n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)
                           and isinstance(n.value, str) and id(n) not in inside))
    return units


def unlabelled(unit, *, about_source=False):
    """True when `unit` states a conflict about the source without R14's candidate label."""
    if LABEL in unit or not (about_source or SOURCE.search(unit)):
        return False
    return bool(VERDICT.search(unit) or CLAIM.search(unit))


def _files(patterns):
    return sorted({p for pattern in patterns for p in ROOT.glob(pattern)})


def test_the_reports_and_specs_label_every_constitution_conflict():
    files = _files(REPORTS)
    assert files
    bad = [f"{path.relative_to(ROOT)}: {unit[:160]!r}" for path in files
           for unit in _markdown_units(path.read_text(encoding="utf-8")) if unlabelled(unit)]
    assert not bad, "\n".join(bad)


def test_the_ce4_goldens_and_docstrings_label_every_constitution_conflict():
    bad = [f"{path}: {unit[:160]!r}" for path in GOLDENS
           for unit in _python_units((ROOT / path).read_text(encoding="utf-8")) if unlabelled(unit, about_source=True)]
    assert not bad, "\n".join(bad)


def test_probe_f26_the_rd9_reports_record_r14():
    """PROBE F26: the rd-9 reports name R14 beside the word candidate."""
    lines = [line for path in _files(REPORTS[:2]) for line in path.read_text(encoding="utf-8").splitlines()
             if "R14" in line]
    assert any("candidate" in line.lower() for line in lines)


@pytest.mark.parametrize("unit,flagged", [
    ("On `CE4` the route reports CONFLICT: pair conflict on x_required->x_permitted at e0.", True),
    ("The constitution's u0125 and u0156 conflict with each other.", True),
    ("CE4's two sets contradict each other.", True),
    ("The pilot shows a real conflict between honesty and helpfulness.", True),
    ("The constitution's rules are in conflict here.", True),
    (f"On `CE4` the route reports CONFLICT. {LABEL}", False),
    ("| C5 | `CE4`, conflict | 16 choices, each CONFLICT-FREE, `conditional_on: []` |", False),
    ("C8: the conflict answer alone carries none on the constitution's path.", False),
    ("F-ND2: CONFLICT: pair conflict on x_required->x_permitted at act e0", False),
])
def test_the_scan_flags_exactly_unlabelled_source_conflicts(unit, flagged):
    """The scan can fail: each unlabelled conflict about the source is flagged, and a labelled one, a conflict-free
    answer, the question's name and a synthetic fixture are not."""
    assert unlabelled(unit) is flagged


def test_a_golden_that_asserts_a_ce4_conflict_needs_the_label():
    golden = 'def test_c5():\n    """C5 on the constitution."""\n    assert status == "CONFLICT"\n'
    assert any(unlabelled(u, about_source=True) for u in _python_units(golden))
    labelled = golden.replace('"""C5 on the constitution."""', f'"""C5. {LABEL}"""')
    assert not any(unlabelled(u, about_source=True) for u in _python_units(labelled))
