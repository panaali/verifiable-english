"""`tools/lean_first_oracle.py`: the frozen pre-deletion Python (LEAN-FIRST-PLAN.md 6.2)."""
from __future__ import annotations

import json

from tools import lean_first_oracle as oracle
from ve.errors import UnknownSymbol


def test_the_freeze_is_intact():
    assert oracle.check() == []


def test_a_changed_frozen_file_or_tag_is_found(tmp_path, monkeypatch):
    manifest = json.loads(oracle.MANIFEST.read_text())
    tampered = tmp_path / "oracle.json"
    path = sorted(manifest["files"])[0]
    tampered.write_text(json.dumps({**manifest, "files": {**manifest["files"], path: "0" * 64}}))
    monkeypatch.setattr(oracle, "MANIFEST", tampered)
    assert any("frozen files differ" in problem for problem in oracle.check())
    tampered.write_text(json.dumps({**manifest, "tag": "lean-first/no-such-tag"}))
    assert oracle.check() == ["tag lean-first/no-such-tag does not exist"]


def test_the_oracle_runs_the_pre_deletion_python(tmp_path, capfd):
    """The oracle answers with the base commit's Python, in isolation: its `UnknownSymbol`
    text has no code prefix, which this checkout's has (batch 0's wording change)."""
    script = tmp_path / "probe.py"
    script.write_text("import ve\nfrom ve.errors import UnknownSymbol\n"
                      "print(ve.__file__)\nprint(UnknownSymbol('x').message)\n")
    assert oracle.run(script, scratch=tmp_path) == 0
    location, message = capfd.readouterr().out.splitlines()
    assert "ve-lean-first-oracle-" in location and message == "x"
    assert UnknownSymbol("x").message == "UnknownSymbol: x"
