"""PC-3's Lean declarations against the approved blocks of docs/spec/profile-composition.md 1.2 to 1.5 (build
checklist 17), and the check's ability to fail."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _checker():
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("check_pc3", ROOT / "tools/check_pc3_statements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pc3_statements_equal_the_approved_text():
    checker = _checker()
    assert checker.main() == 0
    names = {name for _, name in checker.approved()}
    assert {"interface_slot", "pipeline_names", "checkDocSets_pipeline", "listed_evidence", "Interface"} <= names


def test_a_changed_statement_or_a_later_declaration_fails(tmp_path, capsys):
    checker = _checker()
    contract = ROOT / "lean/VE/Compose/Contract.lean"
    text = contract.read_text()
    cases = {
        "weakened": text.replace("(hD : WF D) (h : pipeline rs D = .ok D')", "(h : pipeline rs D = .ok D')"),
        "unstaged": text.replace("  | _ => False\n", '  | ["acts@0", "scope@0"] => False\n  | _ => False\n'),
        "later": text + "\ndef LayerFacts : String → List String → Prop\n  | _, _ => False\n",
    }
    for name, changed in cases.items():
        assert changed != text, name
        path = tmp_path / f"{name}.lean"
        path.write_text(changed)
        sources = [source for source in checker.SOURCES if source.name != "Contract.lean"] + [path]
        assert checker.main(sources) == 1, name
    out = capsys.readouterr().out
    assert "pipeline_preserves: theorem differs" in out and "LayerFacts: listed as a later batch's but built" in out
