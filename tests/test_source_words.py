"""The source-word table and every boundary fixture are checked by Lean."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from ve.english_grammar import source_words

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("english_grammar_gen", ROOT / "tools/english_grammar_gen.py")
G = importlib.util.module_from_spec(spec)
sys.modules["english_grammar_gen"] = G
spec.loader.exec_module(G)


def test_lean_boundary_fixtures():
    lake = str(Path.home() / ".elan/bin/lake")
    done = subprocess.run([lake, "build", "VE.EnglishGrammar.SourceWordsExamples"],
                          cwd=ROOT / "lean", capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stdout + done.stderr


def test_generated_json_equals_lean_table():
    expected = json.loads(G.source_words_blob(ROOT))
    assert json.loads((ROOT / G.SOURCE_WORDS_TARGET).read_bytes()) == expected
    assert source_words() == expected
    assert expected["format"] == "ve.source-words@1"


def test_locked_view_refuses_drift():
    original = (ROOT / G.SOURCE_WORDS_TARGET).read_bytes()

    def changed(path):
        return b'{"format":"ve.source-words@1","rows":[7]}\n' if path == G.SOURCE_WORDS_TARGET else G.file_reader(ROOT)(path)

    errors = G.check(changed, G.file_listing(ROOT))
    assert any(G.SOURCE_WORDS_TARGET in error and "SHA-256" in error for error in errors)
    assert original != changed(G.SOURCE_WORDS_TARGET)
