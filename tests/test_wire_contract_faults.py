"""The fault catalogue and the oracle of the soft-norms gate (wire-contract.md 8.3), checked without Lean.

The full gate (`python -m conformance.wire_contract_gate`) runs both engines and both legacy validators;
these tests check, quickly, that the oracle is the catalogue's and not an engine's: each fault alone gives
its hand-written check and path in the Python engine, positions order as section 2.6 and section 6 say,
footprints keep interacting faults apart, and a combination is judged by its check, not only its code.
"""

from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

from conformance import wire_contract_gate
from conformance.wire_contract_gate import (_applied, all_checks, feasibility, gate_failures, record_problems,
                                            shape_problems)
from conformance.wire_contract_faults import (UNREACHED, catalogue, expected_first, expected_record,
                                              footprint, legacy_codes, overlaps, position, rendered, route)
from ve.errors import VEError
from ve.softnorms_contract import REGISTRY
from ve.wire_contract.engine import CLEAN, Fault, load, run

CONTRACT = load("soft-norms@0")
FAULTS = {fault.name: fault for fault in catalogue()}
REPORT = Path(__file__).resolve().parents[1] / "conformance/wire-contract/soft-norms@0-gate.json"
FIELDS = ("contract", "revision", "check", "phase", "code", "class", "path")


def python(faults, fields=FIELDS):
    outcome = run(CONTRACT, _applied(faults), registry=REGISTRY)
    assert isinstance(outcome, Fault)
    return {key: outcome.record[key] for key in fields}


@pytest.mark.parametrize("name", sorted(FAULTS))
def test_each_fault_alone_gives_its_hand_written_record(name):
    fault = FAULTS[name]
    expected = expected_record(CONTRACT, fault)
    assert python([fault], expected) == expected
    if name in legacy_codes():
        assert legacy_codes()[name] == expected_record(CONTRACT, fault)["code"]


def test_positions_follow_the_table_and_the_order_keys():
    pos = lambda name: position(CONTRACT, FAULTS[name])
    # Phase order, then item-major inside a group: rule 0's last field check before rule 1's first.
    assert pos("language") < pos("party-name") < pos("profile-unknown") < pos("r0-factors") < pos("r1-field")
    # Check-major across two groups over the same items: 2.1a on any predicate before 2.2a on any.
    assert pos("reserved-name-z") < pos("instruction-type")
    # Inside `rule_typing` (section 6): 5.8b on condition 0 comes before 5.8a on condition 1.
    assert pos("r0-condition") < pos("r0-necessary-budget")
    assert pos("r0-guard") < pos("r0-condition")


def test_footprints_keep_interacting_faults_apart():
    """Each pair here gave the gate a wrong expectation before footprints covered replaced values, reads
    and the shared document budget; the old code-only oracle could not see the first one at all."""
    prints = {name: footprint(fault) for name, fault in FAULTS.items()}
    for left, right in (("derived-depth", "derived-nodes"), ("outranking-field", "outranking-decider-type"),
                        ("vocabulary-limit", "stratification"), ("soft-over-hard", "long-decision-names"),
                        ("revision", "soft4-layers-strict-guard-4981")):
        assert overlaps(prints[left], prints[right]), (left, right)
    assert not overlaps(prints["language"], prints["r0-mode"])


# 2.11 and 4.10 share a code; the gate replays this pair whatever tier A samples.
SHARED_CODE_PAIR = ("r0-decider-type", "outranking-decider-type")


def test_the_oracle_judges_the_check_not_only_the_code():
    """2.11 and 4.10 share the code SOFT_INVALID_DECIDER; the expected record names 2.11."""
    combo = tuple(FAULTS[name] for name in SHARED_CODE_PAIR)
    first = expected_first(CONTRACT, combo)
    assert first.name == "outranking-decider-type"
    expected = expected_record(CONTRACT, first)
    assert python(combo, expected) == expected


def test_the_oracle_fixes_text_and_args_apart_from_the_engines():
    """Wire re-check (B): tier A judged `text` and `args` only by comparing the engines with each other, so an
    argument error shared by both passed. The expected record now carries the catalogue's args and the text
    rendered from the contract's template, and an inherited record is judged by the legacy text."""
    for name in sorted(FAULTS):
        member = route(CONTRACT, FAULTS[name].check)[1][-1][1]
        expected = expected_record(CONTRACT, FAULTS[name])
        assert ("text" in expected) == (not member.get("inherited")), name
    expected = expected_record(CONTRACT, FAULTS["r3-over-predicate"])
    assert expected["text"] == "PrecedenceAcrossPredicates: rule d3 on x_permitted, rule a0 on x_required"
    good = run(CONTRACT, _applied([FAULTS["r3-over-predicate"]]), registry=REGISTRY).record
    assert record_problems(good, expected, None) == []
    # Both engines swapping two arguments, or rendering one wrongly, is now a mismatch.
    swapped = {**good, "args": {**good["args"], "predicate": "x_required", "parent_predicate": "x_permitted"}}
    assert record_problems(swapped, expected, None)
    assert record_problems({**good, "text": good["text"] + "!"}, expected, None)
    # An inherited record: its text must be the legacy validator's, with the one argument `message`.
    inherited = run(CONTRACT, _applied([FAULTS["r0-guard"]]), registry=REGISTRY).record
    legacy = ("SOFT_INVALID_INPUT", inherited["text"])
    assert record_problems(inherited, expected_record(CONTRACT, FAULTS["r0-guard"]), legacy) == []
    assert record_problems(inherited, expected_record(CONTRACT, FAULTS["r0-guard"]), (legacy[0], "other"))
    assert record_problems({**inherited, "args": {}}, expected_record(CONTRACT, FAULTS["r0-guard"]), legacy)
    with pytest.raises(ValueError):
        rendered("ResourceLimit: decision predicate {name}", {})


def test_stored_gate_report_has_no_mismatch_and_explains_every_gap():
    report = json.loads(REPORT.read_text())
    assert report["revision"] == CONTRACT["revision"]
    assert report["mismatches"] == []
    assert report["residual"] == {"python": 0, "lean": 0}
    gaps = set(report["coverage_unmet"]["first"]) | set(report["coverage_unmet"]["masked"])
    assert gaps <= set(report["coverage_unmet_reasons"])
    assert set(UNREACHED) <= gaps
    # Wire re-check (B): coverage is met. 8.3 asks a masking witness of every check after the table's
    # first instance, and 6.10c, a member no input reached, is no longer in the table (revision 3).
    assert report["coverage_met"] and not gaps and UNREACHED == {}
    assert list(report["masking_not_required"]) == [all_checks(CONTRACT)[0]] == ["1.1"]
    assert report["legacy_verdict_differences"] == [] and report["s3_pre"].startswith("closed")
    assert report["oracle"].startswith("fault catalogue")


def test_record_shape_is_closed_on_every_tier():
    """Wire re-check 2 (C): `record_problems` read only the expected fields, so an extra top-level field,
    identical in both engines, passed the whole-record comparison. The fault record's members are the
    schema's closed set (2.7), checked on every record, with or without an expected record."""
    schema = json.loads((Path(wire_contract_gate.ROOT) / "ve/wire_contract/contract.schema.json").read_text())
    fault = schema["$defs"]["fault"]
    assert set(fault["required"]) == set(fault["properties"]) == wire_contract_gate.RECORD_FIELDS
    assert fault["additionalProperties"] is False
    good = run(CONTRACT, _applied([FAULTS["r3-over-predicate"]]), registry=REGISTRY).record
    expected = expected_record(CONTRACT, FAULTS["r3-over-predicate"])
    assert shape_problems(good) == [] and record_problems(good, expected, None) == []
    for bad in ({**good, "hint": "x"}, {key: value for key, value in good.items() if key != "args"},
                {**good, "args": []}, [good]):
        assert shape_problems(bad), bad
        assert record_problems(bad, expected, None), bad
    inherited = run(CONTRACT, _applied([FAULTS["r0-guard"]]), registry=REGISTRY).record
    legacy = ("SOFT_INVALID_INPUT", inherited["text"])
    assert record_problems({**inherited, "severity": 1}, expected_record(CONTRACT, FAULTS["r0-guard"]), legacy)


def test_gate_fails_below_the_feasibility_threshold(monkeypatch, tmp_path, capsys):
    """Wire re-check 2 (B): the gate's exit ignored feasibility, so a report with `n1 + n2` = 44 that matched
    the stored one passed. Every required row of spec 9 now fails the gate, judged from `n1` and `n2`
    against the spec's 45 of 67, not from the report's own `met` or `threshold`."""
    stored = json.loads(REPORT.read_text())
    assert stored["feasibility"] == feasibility(CONTRACT)
    assert gate_failures(stored) == []
    assert stored["feasibility"]["of"] == 67 and stored["feasibility"]["threshold"] == 45
    def broken(change):
        value = deepcopy(stored)
        change(value)
        return gate_failures(value)
    def at(n1, n2, **rest):
        """`n1` and `n2` moved, the coarse count taking up the difference so the tiers still partition 67."""
        def change(value):
            coarse = 67 - value["feasibility"]["t3"] - n1 - n2
            value["feasibility"].update({"n1": n1, "n2": n2, "coarse": coarse, "total": n1 + n2,
                                         "met": n1 + n2 >= 45, **rest})
        return change
    assert broken(at(36, 8))
    assert broken(at(37, 8)) == []
    assert broken(at(36, 8, met=True))                # the report's own verdict is not trusted
    assert broken(at(36, 8, threshold=44, met=True))  # nor its threshold
    assert broken(at(43, 8, of=60))                   # a table that lost numbered checks
    assert broken(at(43, 8, total=60))                # a total that is not n1 + n2
    # The other required rows, each alone.
    assert broken(lambda value: value.update(mismatches=[{"case": "x", "problems": ["p"]}]))
    assert broken(lambda value: value["residual"].update(lean=1))
    assert broken(lambda value: value["residual"].pop("python"))
    assert broken(lambda value: value.update(coverage_met=False))
    assert broken(lambda value: value.update(s3_pre="open: x"))
    # The probe of the finding: `--check` with a report at 44 that matches the stored one exits non-zero.
    value = deepcopy(stored)
    at(36, 8)(value)
    path = tmp_path / "gate.json"
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    monkeypatch.setattr(wire_contract_gate, "report", lambda: deepcopy(value))
    monkeypatch.setattr(wire_contract_gate, "REPORT", path)
    monkeypatch.setattr(sys, "argv", ["wire_contract_gate", "--check"])
    assert wire_contract_gate.main()
    assert "below 45" in capsys.readouterr().out
    monkeypatch.setattr(wire_contract_gate, "report", lambda: deepcopy(stored))
    path.write_text(json.dumps(stored, indent=2, sort_keys=True) + "\n")
    assert not wire_contract_gate.main()


def _broken(change):
    value = json.loads(REPORT.read_text())
    change(value)
    return gate_failures(value)


def test_s4_pre_and_public_code_rule_are_gate_rows():
    report = json.loads(REPORT.read_text())
    inherited = wire_contract_gate.inherited_checks(CONTRACT)
    assert sum(row["text_changes"] for row in report["public_diagnostic_changes"]
               if row["check"] not in inherited) == report["text_delta_count"]
    assert report["legacy_code_differences"] == []
    assert report["public_code_differences"] == 0
    assert _broken(lambda value: value.update(legacy_code_differences=[{"case": "L:speech-acts@0:env"}])) == [
        "legacy code differences [{'case': 'L:speech-acts@0:env'}]"]
    assert _broken(lambda value: value.update(public_code_differences=3)) == [
        "public delta: 3 code differences"]
    def before_s4_pre(value):
        value["legacy_code_differences"] = [{"case": name} for name in (
            "L:speech-acts@0:env", "L:speech-acts@0:base", "L:norm-defaults@0:unspecified")]
        value["public_code_differences"] = 3
    failures = _broken(before_s4_pre)
    assert any("legacy code differences" in failure for failure in failures)
    assert "public delta: 3 code differences" in failures


def test_delta_check_detects_an_unregenerated_contract_text(tmp_path, monkeypatch):
    from conformance import wire_contract_delta
    directory = tmp_path / "conformance/wire-contract"
    directory.mkdir(parents=True)
    contract_path = tmp_path / "ve/wire_contract/soft-norms@0.json"
    contract_path.parent.mkdir(parents=True)
    contract_path.write_text(json.dumps({"status": "shadow", "text": "old"}))
    source = wire_contract_delta.ROOT
    for name in ("soft-norms-python-delta.json", "soft-norms@0-gate.json"):
        (directory / name).write_bytes((source / name).read_bytes())
    monkeypatch.setattr(wire_contract_delta, "ROOT", directory)
    monkeypatch.setattr(wire_contract_delta, "OUTPUT", directory / "soft-norms@0-delta.json")
    monkeypatch.setattr(sys, "argv", ["wire_contract_delta"])
    assert wire_contract_delta.main() == 0
    contract_path.write_text(json.dumps({"status": "shadow", "text": "changed"}))
    monkeypatch.setattr(sys, "argv", ["wire_contract_delta", "--check"])
    assert wire_contract_delta.main() == 1


def test_public_gate_requires_exactly_the_measured_signatures(tmp_path, monkeypatch):
    report = json.loads(REPORT.read_text())
    assert report["status"] == "public"
    signatures = json.loads(wire_contract_gate.SWITCH.read_text())
    path = tmp_path / "switch.json"
    monkeypatch.setattr(wire_contract_gate, "SWITCH", path)
    missing = deepcopy(signatures)
    missing["signed"].pop("4.1c")
    path.write_text(json.dumps(missing))
    assert "public delta: check 4.1c changes text in 210 cases and is not signed" in gate_failures(report)
    extra = deepcopy(signatures)
    extra["signed"]["1.1"] = "No measured change."
    path.write_text(json.dumps(extra))
    assert "public delta: signed check 1.1 has no text change" in gate_failures(report)


def test_gate_fails_when_a_stated_summary_contradicts_its_data():
    """Wire loop final (B, B, C): `gate_failures` trusted the report's own summaries, so a report with a
    nonempty `coverage_unmet` and `coverage_met` true, one with legacy verdict differences under an S3-pre
    "closed", and one whose feasibility counts exceed the 67 numbered checks all passed. Each summary is now
    judged from the data it summarizes, and must also agree with it."""
    assert _broken(lambda value: None) == []
    # Coverage: an unmet row fails whatever `coverage_met` says; so does a gap the unmet lists omit.
    for row, gap in (("first", ["2.5"]), ("masked", ["2.5"]), ("adjacent_phase_pairs", [[0, 1]])):
        assert _broken(lambda value: value["coverage_unmet"].update({row: gap})), row
    assert _broken(lambda value: value["coverage_unmet"].pop("masked"))
    assert _broken(lambda value: value.update(coverage_met=1))
    assert _broken(lambda value: value["checks_without_first"].update(python=["2.5"]))
    assert _broken(lambda value: value["checks_without_masked"].update(python=["1.1", "2.5"]))
    assert _broken(lambda value: value["checks_without_first"].update(lean=["4.11b", "2.5"]))
    assert _broken(lambda value: value["first_check_count"].update(python=104))
    assert _broken(lambda value: value["masking_not_required"].update({"2.5": "x"}))
    assert _broken(lambda value: value.update(all_check_count=104))
    # A Lean-only gap that the reasons explain is the report's one accepted gap (4.11b, an explicit null).
    assert _broken(lambda value: value["coverage_unmet_reasons"].clear())
    # S3-pre: a recorded legacy verdict difference fails under any stated `s3_pre`; so does a run without
    # the legacy difference inputs.
    difference = {"case": "L:x", "python": None, "lean": ["SOFT_UNSUPPORTED_PROFILE", "x"]}
    assert _broken(lambda value: value["legacy_verdict_differences"].append(difference))
    assert _broken(lambda value: value["tiers"].update(legacy_differences=0))
    assert _broken(lambda value: value.update(s3_pre=None))
    # Feasibility: counts above the 67 checks, negative, or not integers fail, with a self-consistent
    # `total` and `met`.
    def counts(**change):
        def apply(value):
            value["feasibility"].update(change)
            feasible = value["feasibility"]
            if all(type(feasible[part]) is int for part in ("n1", "n2")):
                feasible.update(total=feasible["n1"] + feasible["n2"])
        return apply
    assert _broken(counts(n1=60, n2=10))
    assert _broken(counts(n1=43, n2=8, coarse=10))
    assert _broken(counts(n1=59, n2=8, coarse=-3, t3=3))
    assert _broken(counts(n1=43.0))
    assert _broken(counts(met=1))
    assert _broken(counts(n1=True))
    # The other required rows, against values that compare equal to zero without being the count zero.
    assert _broken(lambda value: value["residual"].update(lean=False))
    assert _broken(lambda value: value["tiers"].update(B=0))


def test_record_members_have_the_schema_types_on_every_tier():
    """Wire loop final (C): Tier B and replay records were checked only for their member names, so a
    non-string `text` both engines produced passed. Each member now has its type from the fault schema
    (`$defs/fault`), on records with and without an expected record."""
    schema = json.loads((Path(wire_contract_gate.ROOT) / "ve/wire_contract/contract.schema.json").read_text())
    types = {name: member["type"] for name, member in schema["$defs"]["fault"]["properties"].items()}
    assert wire_contract_gate.RECORD_TYPES == types
    good = run(CONTRACT, _applied([FAULTS["r3-over-predicate"]]), registry=REGISTRY).record
    expected = expected_record(CONTRACT, FAULTS["r3-over-predicate"])
    wrong = {"string": [None, 5, ["x"], {"x": 1}], "integer": ["3", 3.0, True, None], "object": [[], "x", None]}
    for name, kind in types.items():
        for bad in wrong[kind]:
            record = {**good, name: bad}
            assert shape_problems(record), (name, bad)
            assert record_problems(record, expected, None), (name, bad)
    inherited = run(CONTRACT, _applied([FAULTS["r0-guard"]]), registry=REGISTRY).record
    assert shape_problems({**inherited, "text": 7}) and shape_problems({**inherited, "text": None})


def test_soft_semantic_names_no_member_for_an_unknown_softened_failure(monkeypatch):
    """Rule 13 (revision 3): a rejection of `T′` that is neither a cycle nor a resource limit names no member,
    as rule 3a for the base, so it would show as a residual rather than as a member no input reaches."""
    from ve import softnorms_contract
    from ve.errors import VEError
    assert all(m["id"] != "6.10c" for phase in CONTRACT["phases"] for entry in phase["checks"]
               if entry.get("kind") == "classifier" for m in entry["emits"])
    root = _applied([])
    assert softnorms_contract.soft_semantic(root, []) is None
    def reject(environment, norms):
        raise VEError("InvalidInput: soft norm document is not stratified")
    monkeypatch.setattr(softnorms_contract.soft, "load_soft_document", reject)
    assert softnorms_contract.soft_semantic(root, []) is None
    assert run(CONTRACT, root, registry=REGISTRY) is CLEAN


def test_only_an_allowed_gap_of_8_3_exempts_a_missing_witness(monkeypatch, tmp_path):
    """Wire2 loop (B): any entry of `coverage_unmet_reasons` exempted a missing Lean witness, so check 2.5
    added to Lean's `checks_without_first`, its count adjusted, with the reason "x" passed. A gap is now
    exempt only under a row of 8.3's table of allowed gaps, read from the spec, whose applicability is judged
    from the fault catalogue, with the row's reason verbatim; any other entry fails."""
    gaps = wire_contract_gate.allowed_gaps()
    assert list(gaps) == ["G1"] and gaps["G1"][0] == "lean"
    null_reason = gaps["G1"][1]
    assert wire_contract_gate.exempt_gaps("lean") == {"4.11b": null_reason}
    assert wire_contract_gate.exempt_gaps("python") == {}
    assert {fault.check for fault in catalogue() if fault.readers == "python"} == {"4.11b"}
    assert json.loads(REPORT.read_text())["coverage_unmet_reasons"] == {"4.11b": null_reason}
    def lean_gap(row, reason, check="2.5"):
        def change(value):
            value[f"checks_without_{row}"]["lean"].append(check)
            if row == "first":
                value["first_check_count"]["lean"] -= 1
            value["coverage_unmet_reasons"][check] = reason
        return change
    assert _broken(lambda value: None) == []
    for row in ("first", "masked"):
        assert _broken(lean_gap(row, "x")), row             # the finding's probe
        assert _broken(lean_gap(row, null_reason)), row     # an allowed reason where its row does not apply
    # No row allows a Python gap, whatever its reason.
    def python_gap(value):
        value["checks_without_first"]["python"].append("4.11b")
        value["first_check_count"]["python"] -= 1
    assert _broken(python_gap)
    # The one allowed gap with another reason, and an entry that exempts nothing, fail as well.
    assert _broken(lambda value: value["coverage_unmet_reasons"].update({"4.11b": "x"}))
    assert _broken(lambda value: value["coverage_unmet_reasons"].update({"2.5": null_reason}))
    assert _broken(lambda value: value.update(coverage_unmet_reasons=[]))
    # A row without its applicability rule, or a malformed row, is refused rather than read.
    spec = tmp_path / "wire-contract.md"
    text = wire_contract_gate.SPEC.read_text()
    row = next(line for line in text.splitlines() if line.startswith("| G1 |"))
    for changed in (text.replace(row, row + "\n| G2 | Lean | anything | x |"), text.replace(row, row + " extra |")):
        spec.write_text(changed)
        monkeypatch.setattr(wire_contract_gate, "SPEC", spec)
        with pytest.raises(ValueError):
            wire_contract_gate.allowed_gaps()


def test_gate_judges_the_deferred_share_from_the_deferred_counts():
    """Wire2 loop (C): a report with no Lean deferral and `deferred_share.lean` 0.75 passed. Each share must
    be its language's deferred count over the cases run; each count is a non-negative integer within the
    cases, and Lean's is 0 (2.8: the Lean engine never defers)."""
    stored = json.loads(REPORT.read_text())
    cases = sum(stored["tiers"].values())
    assert stored["deferred"] == {"python": 0, "lean": 0} and stored["deferred_share"] == {"python": 0, "lean": 0}
    assert _broken(lambda value: value["deferred_share"].update(lean=0.75))   # the finding's probe
    assert _broken(lambda value: value["deferred_share"].update(python=0.5))
    assert _broken(lambda value: value["deferred_share"].update(python=False))
    assert _broken(lambda value: value["deferred_share"].pop("lean"))
    # A Python deferral is reported, not refused, when its share agrees with its count.
    assert _broken(lambda value: value["deferred"].update(python=3)) != []
    assert _broken(lambda value: (value["deferred"].update(python=3),
                                  value["deferred_share"].update(python=3 / cases))) == []
    assert _broken(lambda value: (value["deferred"].update(lean=1), value["deferred_share"].update(lean=1 / cases)))
    for bad in (-1, True, 1.0, None, cases + 1):
        assert _broken(lambda value: value["deferred"].update(python=bad)), bad


def test_report_counts_deferrals_apart_from_residuals_and_refuses_a_row_without_outcome(monkeypatch):
    """A deferred outcome counts under its language's deferred share and never as residual (2.8), and a
    `ve_diagnose` row with no outcome (an adapter or reader error) is a mismatch, not a clean outcome."""
    from ve.wire_contract.engine import Deferred
    raw, norms = _applied([FAULTS["language"]])["environment"], _applied([FAULTS["language"]])["norms"]
    monkeypatch.setattr(wire_contract_gate, "gate_cases",
                        lambda contract: [("R", "R:deferred", raw, norms, None, (), True)])
    monkeypatch.setattr(wire_contract_gate, "_python",
                        lambda contract, raw, norms: (("SOFT_UNSUPPORTED_PROFILE", "m"), Deferred("1.2"),
                                                     VEError("m"), False))
    rows = {"ve_diagnose": {"status": "ok", "outcome": "deferred"},
            "ve_soft_norms_route": {"status": "error", "code": "SOFT_UNSUPPORTED_PROFILE", "error": "m"}}
    monkeypatch.setattr(wire_contract_gate, "_lean_rows", lambda binary, unit, cases: [rows[binary]] * len(cases))
    value = wire_contract_gate.report()
    assert value["deferred"] == {"python": 1, "lean": 1} and value["residual"] == {"python": 0, "lean": 0}
    assert value["deferred_share"] == {"python": 1.0, "lean": 1.0}
    assert any("never defers" in failure for failure in gate_failures(value))
    rows["ve_diagnose"] = {"status": "error", "error": "ResourceLimit: JSON depth exceeds 256"}
    value = wire_contract_gate.report()
    assert any("without an outcome" in problem for problem in value["mismatches"][0]["problems"])
    assert value["deferred"]["lean"] == 0 and value["residual"]["lean"] == 1


def test_every_non_string_name_class_is_measured_and_signed():
    """Fable B1: checks 2.7a and 2.8c spell a name that is not a string as compact JSON, Python's legacy
    validator as Python's value. For each name list the corpus mutates an item to a Boolean, an array and an
    object, whose two spellings differ, and to an integer, whose spellings agree; so each check's text
    change is measured on the whole corpus and signed."""
    from conformance.soft_norms import generated_invalid_soft_blocks
    kinds = {"parties": set(), "ranks": set()}
    for raw, _ in generated_invalid_soft_blocks():
        block = raw["vocabulary"].get("soft")
        for field in kinds:
            values = block.get(field) if type(block) is dict else None
            if type(values) is list and values and type(values[0]) is not str:
                kinds[field].add(type(values[0]).__name__)
    assert kinds["parties"] >= {"bool", "list", "dict"} and kinds["ranks"] >= {"bool", "list", "dict", "int"}
    report = json.loads(REPORT.read_text())
    measured = {row["check"]: row["text_changes"] for row in report["public_diagnostic_changes"]}
    signed = json.loads(wire_contract_gate.SWITCH.read_text())["signed"]
    for check in ("2.7a", "2.8c"):
        assert measured.get(check, 0) > 0 and check in signed
