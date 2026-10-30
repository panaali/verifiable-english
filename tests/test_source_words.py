"""The source-word table and every boundary fixture are checked by Lean."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

from tests.lean_build import lean_build
from ve.english_grammar import source_words

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("english_grammar_gen", ROOT / "tools/english_grammar_gen.py")
G = importlib.util.module_from_spec(spec)
sys.modules["english_grammar_gen"] = G
spec.loader.exec_module(G)


def test_lean_boundary_fixtures():
    lean_build("VE")
    assert (ROOT / "lean/.lake/build/lib/lean/VE/EnglishGrammar/SourceWordsExamples.olean").is_file()


def test_generated_json_equals_lean_table():
    expected = json.loads(G.source_words_blob(ROOT))
    assert json.loads((ROOT / G.SOURCE_WORDS_TARGET).read_bytes()) == expected
    assert source_words() == expected
    assert expected["format"] == "ve.source-words@1"


def test_source_word_export_uses_path_and_prebuilt_module(tmp_path, monkeypatch):
    module = tmp_path / "lean/.lake/build/lib/lean/VE/EnglishGrammar/SourceWords.olean"
    module.parent.mkdir(parents=True)
    module.write_bytes(b"prebuilt")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    lake = bin_dir / "lake"
    lake.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$LAKE_CALLS"\nprintf \'{"format":"ve.source-words@1","rows":[]}\\n\'\n')
    lake.chmod(0o755)
    calls = tmp_path / "lake-calls"
    monkeypatch.setenv("HOME", str(tmp_path / "no-home-shim"))
    monkeypatch.setenv("PATH", str(bin_dir))
    monkeypatch.setenv("LAKE_CALLS", str(calls))
    monkeypatch.setenv("VE_LEAN_PREBUILT", "1")

    assert json.loads(G.source_words_blob(tmp_path)) == {"format": "ve.source-words@1", "rows": []}
    assert calls.read_text().splitlines() == ["env lean --run ../tools/source_words_export.lean"]


def test_locked_view_refuses_drift():
    original = (ROOT / G.SOURCE_WORDS_TARGET).read_bytes()

    def changed(path):
        return b'{"format":"ve.source-words@1","rows":[7]}\n' if path == G.SOURCE_WORDS_TARGET else G.file_reader(ROOT)(path)

    errors = G.check(changed, G.file_listing(ROOT))
    assert any(G.SOURCE_WORDS_TARGET in error and "SHA-256" in error for error in errors)
    assert original != changed(G.SOURCE_WORDS_TARGET)
