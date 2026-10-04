"""The tooling fixtures of docs/spec/wire-contract.md 8.2 (L1 to L13 and L15; L14 is in
tests/test_wire_contract_lean.py), and the lint rules the wire review found dead: an include with a view
inside an included phase, and a hook or member with no fault in the fault catalogue."""

from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess

import pytest

import tools.wire_contract as wire_tool
from tools.wire_contract import lint, process
from ve.wire import canonical_json, loads_json

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "conformance/wire-contract/contracts"
UNITS = ("inner@0", "demo@0", "defer@0", "mid@0", "forms@0")


def contracts():
    return {unit: loads_json((CORPUS / f"{unit}.json").read_bytes()) for unit in UNITS}


def codes(contract, known=None, catalogue=None):
    limits = loads_json((CORPUS / "limits.json").read_bytes())
    names = loads_json((CORPUS / "names.json").read_bytes())
    return {code for code, _ in lint(contract, limits=limits, names=names, known=known or contracts(),
                                     catalogue=catalogue)}


def entry(contract, eid):
    def find(entries):
        for e in entries:
            if e.get("id") == eid:
                return e
            if "each" in e:
                found = find(e["checks"])
                if found is not None:
                    return found
        return None
    for phase in contract["phases"]:
        found = find(phase["checks"])
        if found is not None:
            return found
    raise KeyError(eid)


def demo():
    return contracts()["demo@0"]


def test_clean_corpus_lints_clean():
    for unit, contract in contracts().items():
        assert codes(contract) == set(), unit


def test_l1_repeated_id():
    contract = demo()
    entry(contract, "2.1c")["id"] = "2.1a"
    assert "WC02" in codes(contract)


def test_l2_rows_out_of_order():
    contract = demo()
    checks = contract["phases"][0]["checks"]
    checks[2], checks[3] = checks[3], checks[2]
    assert [c["id"] for c in checks[2:4]] == ["1.4", "1.3"]
    assert "WC02" in codes(contract)


def test_l3_undeclared_code():
    contract = demo()
    entry(contract, "1.2")["code"] = "DEMO_OTHER"
    assert "WC03" in codes(contract)


def test_l4_unknown_placeholder():
    contract = demo()
    entry(contract, "2.1b")["text"] = "Name: {nome}"
    assert "WC04" in codes(contract)


def test_l5_unknown_limit():
    contract = demo()
    entry(contract, "1.3")["limit"] = "DEMO_NONE"
    assert "WC05" in codes(contract)


def test_l6_unbound_item_base():
    contract = demo()
    entry(contract, "2.2b")["args"]["name"] = "@2/name"
    assert "WC06" in codes(contract)


@pytest.mark.parametrize("word", ["partial", "sorry"])
def test_l7_forbidden_lean_word(word):
    contract = demo()
    entry(contract, "1.2")["text"] = f"Shape: a {word} document"
    assert "WC07" in codes(contract)


def test_l8_missing_says():
    contract = demo()
    entry(contract, "4.1").pop("says")
    assert "WC08" in codes(contract)
    contract = demo()
    entry(contract, "3.4").pop("says")
    assert "WC08" in codes(contract)


def test_l9_view_inside_an_included_phase(tmp_path):
    directory = tmp_path / "contracts"
    shutil.copytree(CORPUS, directory)
    demo_value = demo()
    include = deepcopy(entry(demo_value, "3.4"))
    inner = loads_json((CORPUS / "inner@0.json").read_bytes())
    inner["phases"][0]["checks"].append(include)
    (directory / "inner@0.json").write_text(json.dumps(inner))
    findings = process(directory)
    assert any(": WC09: " in finding and "view" in finding for finding in findings), findings


def test_view_nested_through_an_ordinary_include():
    """Wire review (Astra B, Fable B4): two nested views were accepted, because the lint never looked inside
    an included contract. Here the second view sits under an include without a view."""
    known = contracts()
    mid = deepcopy(known["mid@0"])
    entry(mid, "m2").update(view="same_view", says="The view gives the value at W unchanged.")
    known["mid@0"] = mid
    assert "WC09" in codes(known["forms@0"], known)
    plain = deepcopy(known["forms@0"])
    plain["phases"][1]["checks"] = [e for e in plain["phases"][1]["checks"] if e["id"] == "n2"]
    assert "WC09" in codes(plain, known)
    assert "WC09" not in codes(mid, known)


def test_hook_without_a_catalogue_fault():
    """Wire review (Fable B4): the `WC08` clause on the fault catalogue (8.3) was absent."""
    contract = demo()
    assert codes(contract, catalogue={"4.1", "4.3a", "4.3b"}) == set()
    assert "WC08" in codes(contract, catalogue={"4.1", "4.3a"})
    assert "WC08" in codes(contract, catalogue=set())


def test_catalogue_index_is_current():
    from conformance.wire_contract_faults import INDEX, catalogue_index
    assert json.loads(INDEX.read_text()) == catalogue_index()


def test_shipped_catalogue_covers_every_hook_and_member():
    from conformance.wire_contract_faults import UNREACHED, catalogue_checks
    checks = catalogue_checks()
    assert process(wire_tool.DATA) == []
    assert any(": WC08: " in f for f in process(wire_tool.DATA, catalogue={"soft-norms@0": checks - {"6.2"}}))
    assert set(UNREACHED) <= checks


def test_l10_edit_without_revision(tmp_path):
    directory = tmp_path / "contracts"
    shutil.copytree(CORPUS, directory)
    value = demo()
    entry(value, "1.2")["text"] = "Shape: items, changed"
    (directory / "demo@0.json").write_text(json.dumps(value))
    assert any(": WC10: " in finding for finding in process(directory))


def test_l15_null_literal(tmp_path):
    directory = tmp_path / "contracts"
    shutil.copytree(CORPUS, directory)
    text = (directory / "demo@0.json").read_text().replace('"value":"root"', '"value":null')
    assert '"value":null' in text
    (directory / "demo@0.json").write_text(text)
    assert any("demo@0.json: WC01: " in finding for finding in process(directory))


@pytest.fixture
def shipped_copy(tmp_path, monkeypatch):
    """A copy of every file `process` reads or writes for the shipped contracts, with the tool pointed at it."""
    for relative in ("ve/wire_contract", "conformance/wire-contract/contracts", "lean/VE/WireContract"):
        shutil.copytree(ROOT / relative, tmp_path / relative, ignore=shutil.ignore_patterns("__pycache__"))
    shipped = [str(path.relative_to(ROOT)) for pattern in ("docs/spec/*-wire-table.md",
                                                           "conformance/wire-contract/*-catalogue.json")
               for path in sorted(ROOT.glob(pattern))]
    for relative in ("lean/VE/Route/frozen-sources.sha256", "conformance/wire-contract/engine-golden.json",
                     *shipped):
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / relative, tmp_path / relative)
    monkeypatch.setattr(wire_tool, "ROOT", tmp_path)
    monkeypatch.setattr(wire_tool, "DATA", tmp_path / "ve/wire_contract")
    return tmp_path


def test_l11_hand_edited_generated_module(shipped_copy):
    assert process(wire_tool.DATA) == []
    module = shipped_copy / "lean/VE/WireContract/Tables/Corpus.lean"
    module.write_text(module.read_text().replace('"Inner: x is "', '"Inner: x was "'))
    findings = process(wire_tool.DATA)
    assert any("Tables/Corpus.lean: WC11: " in f for f in findings), findings


def test_l12_clean_tree_prints_nothing():
    done = subprocess.run([str(ROOT / ".venv/bin/python") if (ROOT / ".venv/bin/python").exists() else "python3",
                           "-m", "tools.wire_contract", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert (done.returncode, done.stdout) == (0, "")


def test_l13_write_after_a_revision_changes_only_generated_files(shipped_copy):
    def snapshot():
        return {str(p.relative_to(shipped_copy)): p.read_bytes() for p in shipped_copy.rglob("*") if p.is_file()}
    path = shipped_copy / "ve/wire_contract/soft-norms@0.json"
    value = json.loads(path.read_text())
    value["revision"] += 1
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    before = snapshot()
    assert process(wire_tool.DATA, write=True) == []
    after = snapshot()
    changed = {name for name in after if before.get(name) != after[name]}
    assert changed == {"ve/wire_contract/contracts.lock", "lean/VE/WireContract/Tables/SoftNorms.lean",
                       "lean/VE/Route/frozen-sources.sha256"}
    old = before["lean/VE/Route/frozen-sources.sha256"].decode().splitlines()
    new = after["lean/VE/Route/frozen-sources.sha256"].decode().splitlines()
    assert [(a, b) for a, b in zip(old, new) if a != b] == [
        (a, b) for a, b in zip(old, new) if a.endswith("VE/WireContract/Tables/SoftNorms.lean") and a != b]
    lock = loads_json(after["ve/wire_contract/contracts.lock"])
    assert lock["soft-norms@0.json"]["revision"] == value["revision"]
    assert process(wire_tool.DATA) == []
    assert canonical_json(lock) + b"\n" == after["ve/wire_contract/contracts.lock"]
