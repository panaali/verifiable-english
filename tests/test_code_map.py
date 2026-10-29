"""The committed code map depends only on source paths and first module doc sentences."""
from __future__ import annotations

from pathlib import Path

from tools import code_map

ROOT = Path(__file__).resolve().parents[1]


def _put(root: Path, name: str, content: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_synthetic_tree_extracts_first_sentences_and_is_deterministic(tmp_path):
    _put(tmp_path, "ve/alpha.py", '"""Alpha uses e.g. examples\nacross lines. Second sentence."""\n\ndef f():\n    return 1\n')
    _put(tmp_path, "lean/VE/Route/One.lean", "/-! Route one\ncontinues. Second sentence. -/\n")
    _put(tmp_path, "rust/src/lib.rs", "//! Rust first line\n//! continues. Next sentence.\nfn one() {}\n")
    _put(tmp_path, "ve/empty.py", "def f():\n    return 1\n")
    _put(tmp_path, "ve/README.md", "# VE\n\nFirst area sentence\nacross lines. Second sentence.\n")
    first, missing = code_map.render(tmp_path)
    second, _ = code_map.render(tmp_path)
    assert first == second
    assert missing == [Path("ve/empty.py")]
    contents = "\n".join(first.values())
    assert "- `ve/alpha.py` — Alpha uses e.g. examples across lines.\n" in contents
    assert "Alpha uses e.g. examples across lines." in contents
    assert "Route one continues." in contents
    assert "Rust first line continues." in contents
    assert "`ve/empty.py` — (no module docstring)" in contents
    assert "Second sentence" not in contents and "Next sentence" not in contents
    assert "Regenerated on every merge to main; on a branch it may lag that branch's own changes." in first[code_map.OUTPUT / "INDEX.md"]
    assert "— First area sentence across lines." in first[code_map.OUTPUT / "INDEX.md"]


def test_check_detects_stale_and_extra_files_then_accepts_write(tmp_path, capsys):
    _put(tmp_path, "ve/one.py", '"""One."""\n')
    assert code_map.run(tmp_path, "check") == 1
    assert "docs/codemap/INDEX.md" in capsys.readouterr().out
    assert code_map.run(tmp_path, "write") == 0
    assert code_map.run(tmp_path, "check") == 0
    _put(tmp_path, "ve/one.py", '"""Two."""\n')
    assert code_map.run(tmp_path, "check") == 1
    assert "docs/codemap/ve.md" in capsys.readouterr().out
    assert code_map.run(tmp_path, "write") == 0
    assert code_map.run(tmp_path, "check") == 0
    _put(tmp_path, "docs/codemap/obsolete.md", "stale\n")
    assert code_map.run(tmp_path, "check") == 1
    assert code_map.run(tmp_path, "write") == 0
    assert not (tmp_path / "docs/codemap/obsolete.md").exists()


def test_body_edit_does_not_change_output(tmp_path):
    _put(tmp_path, "tools/one.py", '"""A tool."""\ndef f():\n    return 1\n')
    before, _ = code_map.render(tmp_path)
    _put(tmp_path, "tools/one.py", '"""A tool."""\ndef f():\n    return 2\n')
    assert code_map.render(tmp_path)[0] == before


def test_missing_is_informational_and_sentences_are_capped(tmp_path, capsys):
    _put(tmp_path, "ve/long.py", '"""' + "x" * 180 + '."""\n')
    _put(tmp_path, "ve/empty.py", "pass\n")
    assert code_map.run(tmp_path, "missing") == 0
    assert capsys.readouterr().out == "ve/empty.py\n"
    output, _ = code_map.render(tmp_path)
    description = next(line.split(" — ", 1)[1] for line in output[code_map.OUTPUT / "ve.md"].splitlines()
                       if "ve/long.py" in line)
    assert len(description) == 160 and description.endswith("…")


def test_readme_table_is_not_an_area_sentence(tmp_path):
    _put(tmp_path, "ve/one.py", '"""One."""\n')
    _put(tmp_path, "ve/README.md", "# VE\n\n| Module | Purpose |\n|---|---|\n| one.py | One. |\n")
    output, _ = code_map.render(tmp_path)
    assert "[ve/](ve.md) — 1 modules — -\n" in output[code_map.OUTPUT / "INDEX.md"]


def test_real_tree_size_caps():
    result, _ = code_map.render(ROOT)
    assert len(result[code_map.OUTPUT / "INDEX.md"].encode()) < 16_000
    assert all(len(content.encode()) < 12_000 for path, content in result.items() if path.name != "INDEX.md")
