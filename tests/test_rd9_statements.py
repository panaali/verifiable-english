"""RD-9's Lean declarations against the approved blocks of docs/spec/rd-9-soft-chain.md 6 (checklist 17).

Recheck rd-9-looprecheck1 (Astra A, Fable B2): `softX_wellFormed` was unbuilt, so SC-1's acceptance check could not
pass. The probe was `tools/check_rd9_sc1_statements.py | grep -q unbuilt && exit 1`; these tests are that probe
and the check's ability to fail on every batch's block.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _checker():
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("check_rd9", ROOT / "tools/check_rd9_sc1_statements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rd9_statements_match_the_approved_text_with_nothing_unbuilt(capsys):
    """PROBE A of rd-9-looprecheck1: no RD-9 statement is reported unbuilt, and every block matches."""
    checker = _checker()
    assert checker.main() == 0
    out = capsys.readouterr().out
    assert "unbuilt" not in out and "not built yet" not in out
    assert all(not section[5] for section in checker.SECTIONS)
    assert "softX_wellFormed" in {name for _, name in checker.approved_block("### 6.4", "### 6.5")}


def test_every_built_batch_block_is_compared():
    """The sections cover SC-1's three blocks and every later batch's block that is built."""
    titles = [section[0].split()[0] for section in _checker().SECTIONS]
    assert titles[:3] == ["SC-1", "SC-1", "SC-1"]
    assert "SC-2" in titles


def _mutated_sections(checker, tmp_path, section_index, name):
    """The checker's sections with one theorem of one section changed in a copy of its file."""
    title, start, stop, sources, expected, later = checker.SECTIONS[section_index]
    for source in sources:
        text = source.read_text()
        match = re.search(rf"^theorem {re.escape(name)}\b", text, re.M)
        if match:
            head, proof = text[match.start():].split(":=", 1)
            changed = text[:match.start()] + head.rstrip() + " ∧ True :=" + proof
            copy = tmp_path / source.name
            copy.write_text(changed)
            sources = [copy if s == source else s for s in sources]
            break
    else:
        raise AssertionError(f"{name} not found in {sources}")
    sections = list(checker.SECTIONS)
    sections[section_index] = (title, start, stop, sources, expected, later)
    return sections


@pytest.mark.parametrize("section_index, name", [
    (1, "softX_wellFormed"), (0, "acceptanceX"), (2, "foldG_all_sound"), (3, "separatesS_sound"),
    (3, "observeOn_sideOfS_sound"),
])
def test_the_check_fails_on_a_changed_statement(tmp_path, capsys, section_index, name):
    checker = _checker()
    assert checker.main(_mutated_sections(checker, tmp_path, section_index, name)) == 1
    assert f"{name}: theorem differs" in capsys.readouterr().out


def test_a_stale_not_built_marker_fails(capsys):
    checker = _checker()
    sections = list(checker.SECTIONS)
    title, start, stop, sources, expected, _ = sections[1]
    sections[1] = (title, start, stop, sources, expected, {"softX_wellFormed"})
    assert checker.main(sections) == 1
    assert "softX_wellFormed: not-built marker is stale" in capsys.readouterr().out
