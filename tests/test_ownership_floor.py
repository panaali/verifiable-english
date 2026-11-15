"""kb-10d step 3: the per-answer Lean ownership count of the five frozen keys is a floor.

docs/kernel/ownership.json (written by `tools/ownership_trace.py verdict` from one fresh traced process per unit)
judges every item of the five keys by the three criteria of manage-agents
reviews/lean-ownership-baseline-20261112.md section 2. docs/kernel/ownership-floor.json holds each key's floor: the
count may not fall below it, and the floor falls only with a row of docs/kernel/ALLOWANCES.md's "Ownership floor"
table signed by the architect seat. ownership.json must be of the tree's traced inputs (the git blob ids of
ve/norms.py, ve/evaluate.py, ve/softnorms.py, ve/soft_route.py and the five harness run files). The last test
traces three passing items per key again (first, middle and last) and fails if one stops passing.
"""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import ownership_trace as OT  # noqa: E402

KERNEL = ROOT / "docs/kernel"
OWNERSHIP = KERNEL / "ownership.json"
FLOOR = KERNEL / "ownership-floor.json"
ALLOWANCES = KERNEL / "ALLOWANCES.md"


def ownership() -> dict:
    return json.loads(OWNERSHIP.read_text())


def floors() -> dict:
    return json.loads(FLOOR.read_text())["floor"]


def allowance_rows(text: str) -> list[dict]:
    """The rows of ALLOWANCES.md's "Ownership floor" table: date, key, floor before, floor after, change, signed."""
    section = text.split("\n## Ownership floor\n", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.split("\n"):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not line.startswith("| ") or len(cells) != 6 or cells[0] in ("Date",) or set(cells[0]) <= {"-"}:
            continue
        rows.append({"date": cells[0], "key": cells[1].strip("`"), "before": cells[2], "after": cells[3],
                     "change": cells[4], "signed": cells[5]})
    return rows


def lowest_floors(rows: list[dict]) -> dict:
    """Each key's lowest permitted floor: its last row's floor after. A fall needs the architect seat's signature."""
    out = {}
    for row in rows:
        after = int(row["after"].replace(",", ""))
        before = None if row["before"] in ("-", "") else int(row["before"].replace(",", ""))
        if before is not None and after < before and "architect seat" not in row["signed"]:
            raise AssertionError(f"the floor of {row['key']} falls ({before} to {after}) without the architect "
                                 f"seat's signature: {row['signed']!r}")
        out[row["key"]] = after
    return out


def test_every_item_of_the_five_keys_is_accounted_for():
    data = ownership()
    assert set(data["keys"]) == set(OT.KEYS)
    for key, block in data["keys"].items():
        expected = {item for items in OT.ADAPTERS[key]().units().values() for item in items}
        assert set(block["items"]) == expected, key
        assert not [i for i, v in block["items"].items() if v["reason"] == "not traced"], key
        for item, verdict in block["items"].items():
            assert verdict["pass"] == (verdict["criterion"] is None), item
            assert verdict["pass"] == all(verdict["criteria"][n]["ok"] for n in ("1", "2", "3")), item


def test_the_totals_are_the_items_that_pass():
    data = ownership()
    for key, block in data["keys"].items():
        assert data["totals"][key] == block["totals"] == OT._totals(block["items"].values()), key
        assert block["families"] == OT._families(block["items"]), key


def test_no_key_falls_below_its_floor():
    data, floor = ownership(), floors()
    assert set(floor) == set(OT.KEYS)
    for key in OT.KEYS:
        assert data["totals"][key]["pass"] >= floor[key], (
            f"{key}: {data['totals'][key]['pass']} answers pass, below the floor {floor[key]}")


def test_the_floor_falls_only_with_a_signed_allowance():
    lowest = lowest_floors(allowance_rows(ALLOWANCES.read_text()))
    floor = floors()
    assert set(lowest) == set(OT.KEYS)
    for key in OT.KEYS:
        assert floor[key] >= lowest[key], f"{key}: floor {floor[key]} is below the signed {lowest[key]}"


def test_a_fall_without_the_architect_seat_is_refused_and_a_rise_needs_no_signature():
    rows = [{"key": "k", "before": "-", "after": "10", "signed": "not needed (the first measurement)"},
            {"key": "k", "before": "10", "after": "12", "signed": "not needed (a rise)"}]
    assert lowest_floors(rows) == {"k": 12}
    assert lowest_floors(rows + [{"key": "k", "before": "12", "after": "9", "signed": "architect seat, round 6"}]) == \
        {"k": 9}
    with pytest.raises(AssertionError, match="without the architect seat"):
        lowest_floors(rows + [{"key": "k", "before": "12", "after": "9", "signed": "the builder"}])


def test_ownership_json_is_of_the_traced_inputs():
    """A change to ve/norms.py, ve/evaluate.py, ve/softnorms.py, ve/soft_route.py or a harness run file needs a
    new trace (`tools/ownership_trace.py run` per key, then `verdict`)."""
    assert ownership()["inputs"] == OT.input_ids(), "docs/kernel/ownership.json is stale: trace the five keys again"


def test_a_changed_traced_input_makes_ownership_json_stale(tmp_path):
    for path in OT.TRACED_INPUTS:
        (tmp_path / path).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / path).write_bytes((ROOT / path).read_bytes())
    assert OT.input_ids(tmp_path) == OT.input_ids()
    (tmp_path / "ve/norms.py").write_bytes((ROOT / "ve/norms.py").read_bytes() + b"\n")
    changed = OT.input_ids(tmp_path)
    assert changed["ve/norms.py"] != OT.input_ids()["ve/norms.py"]
    assert {k: v for k, v in changed.items() if k != "ve/norms.py"} == \
        {k: v for k, v in OT.input_ids().items() if k != "ve/norms.py"}


def test_passing_items_still_pass_criterion_two_under_the_live_registry():
    """Each passing answer's value calls, judged again with today's tools/kernel-paths.json."""
    registry, names = json.loads(OT.REGISTRY_FILE.read_text()), OT.mode_names()
    for key, block in ownership()["keys"].items():
        for item, verdict in block["items"].items():
            if verdict["pass"]:
                c2 = verdict["criteria"]["2"]
                again = OT.criterion_two(c2["value_calls"], c2["unrelayed"], registry, names)
                assert again["ok"], (key, item, again["failed_by"])


def _scratch_registry(edit) -> dict:
    registry = copy.deepcopy(json.loads(OT.REGISTRY_FILE.read_text()))
    edit({path["name"]: path for path in registry["paths"]})
    return registry


@pytest.mark.parametrize("edit, words", [
    (lambda paths: paths["softNorms"]["uncovered"].append({"name": "scratch", "kinds": ["soft-selected"],
                                                           "why": "seeded"}), "listed uncovered"),
    (lambda paths: paths["softNorms"]["kinds"].__setitem__("soft-selected", {"nonverdict": "seeded"}),
     "listed nonverdict"),
    (lambda paths: paths["softNorms"].__setitem__("tier", "candidate"), "no kernel path lists a theorem"),
])
def test_a_kind_the_registry_no_longer_covers_fails_criterion_two(edit, words):
    """Seeded bug (b): soft-selected listed uncovered (or nonverdict, or its path a candidate) in a scratch copy of
    the registry fails criterion 2 for exactly the passing items whose value is a soft-selected answer."""
    registry, names = _scratch_registry(edit), OT.mode_names()
    hit = kept = 0
    for block in ownership()["keys"].values():
        for verdict in block["items"].values():
            if not verdict["pass"]:
                continue
            c2 = verdict["criteria"]["2"]
            again = OT.criterion_two(c2["value_calls"], c2["unrelayed"], registry, names)
            if "soft-norms/soft-selected" in c2["value_kinds"]:
                assert not again["ok"] and any(words in reason for reason in again["failed_by"]), verdict
                hit += 1
            else:
                assert again["ok"], verdict
                kept += 1
    assert hit and kept


def test_criterion_two_reads_kinds_families_and_the_relay():
    registry, names = json.loads(OT.REGISTRY_FILE.read_text()), OT.mode_names()
    call = {"mode": "route", "kind": "certificate", "caller": "f", "profiles": ["relational-fol@0"], "count": 1}
    assert OT.criterion_two([call], [], registry, names)["ok"]
    # The closureNary family is untied: a case that may be of it (nary@0 declared, or profiles unknown) fails.
    for profiles in (["closure@0", "nary@0", "relational-fol@0"], None):
        assert not OT.criterion_two([{**call, "profiles": profiles}], [], registry, names)["ok"], profiles
    for bad in ({"kind": None}, {"kind": "background"}, {"mode": "risk", "kind": "risk-decision"},
                {"mode": "soft-norms", "kind": "soft-elaborate"}, {"mode": "no-such-mode"}):
        assert not OT.criterion_two([{**call, **bad}], [], registry, names)["ok"], bad
    assert not OT.criterion_two([], [], registry, names)["ok"]
    assert not OT.criterion_two([call], ["ve/backends/lean.py:run"], registry, names)["ok"]


def test_every_registry_mode_has_one_wire_name():
    names = OT.mode_names()
    registry = json.loads(OT.REGISTRY_FILE.read_text())
    for path in registry["paths"]:
        for mode in path["modes"]:
            assert list(names.values()).count(mode) == 1, mode


def test_decision_functions_match_functions_and_their_nested_code_not_the_class_body():
    listed = OT.decision_functions()
    rows = [("norms.py", "NormDocument.selection"), ("norms.py", "NormDocument.selection.<locals>.subtree"),
            ("evaluate.py", "_Evaluator.formula"), ("norms.py", "_check_conflict_python"),
            ("evaluate.py", "_Evaluator"), ("softnorms.py", "SoftenedNormDocument.selected_rules"),
            ("norms.py", "NormDocument.selection_helper"), ("norms.py", "NormDocument.__init__")]
    assert OT.decision_hits([[f, q, 1, 2, "-"] for f, q in rows], listed) == sorted([
        "ve/norms.py:NormDocument.selection", "ve/norms.py:NormDocument.selection.<locals>.subtree",
        "ve/evaluate.py:_Evaluator.formula", "ve/norms.py:_check_conflict_python"])


def test_each_listed_decision_function_exists_and_has_a_reason():
    import importlib
    for entry in OT.decision_functions():
        assert entry["reason"].strip() and "\n" not in entry["reason"], entry
        module = importlib.import_module(entry["file"][:-3].replace("/", "."))
        target = module
        for part in entry["qualname"].split("."):
            target = getattr(target, part)
        assert callable(target), entry


def _chosen(data: dict) -> list:
    """Per key, the units of the first, middle and last passing items (in ownership.json's order)."""
    out = []
    for key, block in data["keys"].items():
        passing = [item for item, verdict in block["items"].items() if verdict["pass"]]
        if not passing:
            continue
        picks = sorted({passing[0], passing[len(passing) // 2], passing[-1]})
        for unit in sorted({block["items"][item]["unit"] for item in picks}):
            out.append((key, unit, [item for item in picks if block["items"][item]["unit"] == unit]))
    return out


def _service_built() -> bool:
    from ve.backends.lean_service import DEFAULT_EXECUTABLE
    return Path(os.environ.get("VE_LEAN_SERVICE") or DEFAULT_EXECUTABLE).exists()


@pytest.mark.skipif(not _service_built(), reason="the Lean service is not built")
def test_three_passing_items_per_key_still_pass(tmp_path):
    """Each chosen unit traced again in a fresh process (at most 4 at a time) and judged: its items still pass."""
    data = ownership()
    chosen = _chosen(data)
    assert {key for key, _, _ in chosen} == {k for k, t in data["totals"].items() if t["pass"]}

    def trace(job):
        key, unit, _ = job
        out = tmp_path / f"{key}-{OT._safe(unit)}.json"
        done = subprocess.run([sys.executable, str(ROOT / "tools/ownership_trace.py"), "trace", key, unit, str(out)],
                              cwd=ROOT, capture_output=True, text=True, timeout=HANG_TIMEOUT)
        assert done.returncode == 0, done.stdout[-2000:] + done.stderr[-2000:]
        return job, json.loads(out.read_text())

    listed, registry, names = OT.decision_functions(), json.loads(OT.REGISTRY_FILE.read_text()), OT.mode_names()
    with ThreadPoolExecutor(OT.MAX_JOBS) as pool:
        for (key, unit, items), record in pool.map(trace, chosen):
            adapter = OT.ADAPTERS[key]()
            for item in items:
                verdict = OT.judge(record, item, adapter, listed, registry, names)
                assert verdict["pass"], (key, item, verdict["criterion"], verdict["reason"])
                assert OT._canonical(verdict["value"]) == OT._canonical(data["keys"][key]["items"][item]["value"]), \
                    (key, item)
