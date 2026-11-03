"""PC-3's Lean declarations against the approved blocks of docs/spec/profile-composition.md 1.2 to 1.6 (build
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
    assert {"interface_slot", "pipeline_names", "checkDocSets_pipeline", "listed_evidence", "Interface",
            "composed_superpose_all", "acceptanceXV"} <= names


def test_a_changed_statement_or_a_later_declaration_fails(tmp_path, capsys):
    checker = _checker()
    contract = ROOT / "lean/VE/Compose/Contract.lean"
    text = contract.read_text()
    cases = {
        "weakened": text.replace("(hD : WF D) (h : pipeline rs D = .ok D')", "(h : pipeline rs D = .ok D')"),
        "no hQw": text.replace("    (hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) (VE.NormDefaults.Packs.X qs))\n", ""),
        "swapped": text.replace("(slotUnder D A ++ VE.NormDefaults.Packs.X qs))", "(VE.NormDefaults.Packs.X qs ++ slotUnder D A))"),
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
    assert "composed_superpose_all: theorem differs" in out


def test_a_theorem_is_cut_at_its_proofs_assignment_not_one_inside_the_statement():
    """Review sc-6 F1, as a class: the shared `proof_cut` keeps a record update's `:=` in the compared statement."""
    checker = _checker()
    text = "theorem t (N : Norm) : { N with guard := g }.guard = g := by\n  rfl\n"
    assert checker.declarations(text)[("theorem", "t")] == ["theorem t (N : Norm) : { N with guard := g }.guard = g"]
