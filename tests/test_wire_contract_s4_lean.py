"""Stage S4 item 1, the Lean and tooling fixtures (docs/spec/wire-contract-s4.md section 8.4).

The switch of `soft-norms@0` from `shadow` to `public` is revision 4 and changes two members of the contract
(2.6). In Lean only the generated table's revision changes (D7, (B) of 2.9): `Table` has no `status` field,
and the engine reads a table's phases only. These tests hold before and after the switch commit: each one
derives the revision from the contract file rather than naming it.

- L1: `ve_diagnose soft-norms@0` on the source of fixture S1 prints the record of 4.1's first object.
- T2: `status` raised to `public` without a new revision is `WC10`.
- T3: the switch edit, written by `tools/wire_contract.py --write`, changes the generated module's header
  comment and the numeral of its `revision`, and nothing else; `status` alone changes no byte of its body.
- T4: `status` `open` is `WC01`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

import tools.wire_contract as wire_tool
from conformance.soft_norms import multi_fault_base, multi_faults
from tests.test_wire_contract_lint import shipped_copy  # noqa: F401  (a fixture)
from tools.wire_contract import process
from ve.wire import loads_json

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "lean/.lake/build/bin"
CONTRACT = "ve/wire_contract/soft-norms@0.json"
MODULE = "lean/VE/WireContract/Tables/SoftNorms.lean"
FROZEN = "lean/VE/Route/frozen-sources.sha256"
LOCK = "ve/wire_contract/contracts.lock"


def revision():
    return json.loads((ROOT / CONTRACT).read_text())["revision"]


@pytest.fixture(scope="module")
def diagnose():
    if not (BIN / "ve_diagnose").exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("lake is required for ve_diagnose")
        result = subprocess.run([lake, "build", "ve_diagnose"], cwd=ROOT / "lean", capture_output=True,
                                text=True, timeout=1200)
        assert result.returncode == 0, result.stdout + result.stderr
    return BIN / "ve_diagnose"


def s1_source():
    """Fixture S1: the base B with parties `["p", "Q!"]`, the tier-0 fault `party-name`."""
    raw, rules = multi_fault_base()
    fault = {f[0]: f for f in multi_faults()}["party-name"]
    fault[4](raw, rules)
    assert raw["vocabulary"]["soft"]["parties"] == ["p", "Q!"]
    return raw, rules


def test_l1_diagnose_prints_the_record_of_s1(diagnose):
    raw, rules = s1_source()
    case = {"id": "s1", "kind": "soft-elaborate", "environment": raw, "norms": rules}
    result = subprocess.run([str(diagnose), "soft-norms@0", "-"], input=json.dumps([case]), text=True,
                            capture_output=True, timeout=600)
    assert result.returncode in (0, 1), result.stderr
    record = {"contract": "soft-norms@0", "revision": revision(), "check": "2.7a", "phase": "declarations",
              "code": "SOFT_INVALID_NAME", "class": "InvalidInput", "path": "/environment/vocabulary/soft/parties/1",
              "text": "InvalidInput: invalid soft name Q!", "args": {"value": "Q!"}}
    assert json.loads(result.stdout) == [{"id": "s1", "status": "ok", "outcome": "fault", "diagnostic": record}]


def edit(copy, **members):
    path = copy / CONTRACT
    value = json.loads(path.read_text())
    value.update(members)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    return value


def findings_on_contract(copy):
    return [f.split(": ", 2)[1] for f in process(wire_tool.DATA) if f.startswith(str(copy / CONTRACT) + ":")]


def test_t2_status_without_a_revision_is_wc10(shipped_copy):  # noqa: F811
    value = json.loads((shipped_copy / CONTRACT).read_text())
    edit(shipped_copy, status="shadow" if value["status"] == "public" else "public")
    assert "WC10" in findings_on_contract(shipped_copy)


def test_t4_unknown_status_is_wc01(shipped_copy):  # noqa: F811
    value = json.loads((shipped_copy / CONTRACT).read_text())
    edit(shipped_copy, status="open", revision=value["revision"] + 1)
    assert "WC01" in findings_on_contract(shipped_copy)


def test_t3_the_switch_edit_changes_only_the_generated_revision(shipped_copy):  # noqa: F811
    def snapshot():
        return {str(p.relative_to(shipped_copy)): p.read_bytes() for p in shipped_copy.rglob("*") if p.is_file()}
    assert process(wire_tool.DATA) == []
    before = snapshot()
    old = json.loads(before[CONTRACT])
    new = edit(shipped_copy, revision=old["revision"] + 1,
               status="shadow" if old["status"] == "public" else "public")
    assert process(wire_tool.DATA, write=True) == []
    after = snapshot()
    assert process(wire_tool.DATA) == []
    # 2.6: the lock, the generated module and its frozen-sources line; the English table does not change.
    changed = {name for name in after if before.get(name) != after[name]}
    assert changed == {CONTRACT, LOCK, MODULE, FROZEN}
    assert [(a, b) for a, b in zip(before[FROZEN].decode().splitlines(), after[FROZEN].decode().splitlines())
            if a != b and not a.endswith("VE/WireContract/Tables/SoftNorms.lean")] == []
    assert loads_json(after[LOCK])["soft-norms@0.json"]["revision"] == new["revision"]
    # T3: the header comment (revision and hash) and the numeral of the table's `revision`, nothing else.
    head_old, body_old = before[MODULE].decode().split(" -/\n", 1)
    head_new, body_new = after[MODULE].decode().split(" -/\n", 1)
    assert f"revision {old['revision']}," in head_old and f"revision {new['revision']}," in head_new
    needle = 'contract := "soft-norms@0", revision := {}, '
    assert body_old.count(needle.format(old["revision"])) == 1
    assert body_new == body_old.replace(needle.format(old["revision"]), needle.format(new["revision"]))
    assert "status" not in body_new and old["status"] not in body_new and new["status"] not in body_new
