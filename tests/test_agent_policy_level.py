"""The policy family's requirement register and its level reader (apol-req)."""
import copy
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "usecases" / "agent-policy"
_spec = importlib.util.spec_from_file_location("agent_policy_level", CASE / "level.py")
level = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(level)


def _read(name):
    return json.loads((CASE / name).read_text(encoding="utf-8"))


REGISTER, KEY, RESULTS, MANIFEST = (_read(name) for name in
                                    ("requirements.json", "answer-key.json", "results.json", "policy.manifest.json"))
TESTS = {test for row in REGISTER["rows"] for test in row["decided_by"]["tests"]}


def passing(tests):
    return set(tests)


def measure(register=REGISTER, results=RESULTS, key=KEY, manifest=MANIFEST, run_tests=passing):
    return level.measure(register, key, results, manifest, run_tests)


def row_of(register, row_id):
    return next(row for row in register["rows"] + register["appended"] if row["id"] == row_id)


def edited(edit, row_id=None):
    """A copy of the register with one row edited and the frozen header re-hashed, so only the edit is judged."""
    register = copy.deepcopy(REGISTER)
    edit(row_of(register, row_id) if row_id else register)
    register["header"]["rows_sha256"] = level.rows_sha256(register["rows"])
    return register


def failed_rows(result):
    return {failure.split(":", 1)[0] for failure in result["failures"]}


BASE = measure()


def bytes_of(*row_ids):
    return sum(row_of(REGISTER, row_id)["bytes"] for row_id in row_ids)


# --- the live register --------------------------------------------------------

def test_live_register_passes_with_its_named_tests_run():
    live = level.measure(REGISTER, KEY, RESULTS, MANIFEST)
    assert live["failures"] == []
    assert live == BASE
    rows = REGISTER["rows"]
    assert live["source"] == sum(row["bytes"] for row in rows)
    assert live["verified"] == sum(row["bytes"] for row in rows if row["status"] == "VERIFIED")
    assert live["verified"] + sum(live["open"].values()) == live["source"]
    assert live["rows"] == {row["id"]: row["status"] for row in rows}


def test_header_holds_the_basis_and_the_hash_of_the_frozen_rows():
    header = REGISTER["header"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", header["frozen_utc"])
    assert header["rows_sha256"] == level.rows_sha256(REGISTER["rows"])
    assert header["basis"].startswith("a unit is one plain-English requirement statement of the family;")
    assert header["basis"].endswith("Source bytes = all units.")
    for family in level.FAMILIES:
        assert family in header["basis"]


def test_rows_are_taken_from_the_named_sources():
    rows = REGISTER["rows"]
    readme = (CASE / "README.md").read_text(encoding="utf-8")
    plain = dict(re.findall(r"^\| (\d+) \| [a-z-]+ \| (.+) \| CHECKED \|$", readme, re.M))
    rules = [row for row in rows if row["id"].startswith("rule-")]
    assert [row["statement"] for row in rules] == [plain[str(n)] for n in range(1, 27)]
    names = {block["number"]: block["name"] for block in MANIFEST["blocks"]}
    assert [row["ve_text"]["rules"] for row in rules] == [[names[n]] for n in range(1, 27)]
    plan = (CASE / "PLAN.md").read_text(encoding="utf-8")
    section7 = plan.split("## 7.")[1].split("## 8.")[0]
    section10 = plan.split("## 10.")[1].split("## 11.")[0]
    scope = plan.split("Out of scope, with the reason:")[1].split("## 3.")[0]
    count = {prefix: sum(row["id"].startswith(prefix) for row in rows)
             for prefix in ("finding-", "speech-", "scope-", "cedar-", "gatekeeper-")}
    assert count["finding-"] == len(re.findall(r"^\| (?!Finding|---)", section7, re.M))
    assert count["speech-"] == len(re.findall(r"^\| (?!Item|---)", section10, re.M))
    assert count["scope-"] == len(re.findall(r"^- ", scope, re.M))
    assert (count["cedar-"], count["gatekeeper-"]) == (1, 1)
    assert len(rows) == 26 + sum(count.values())


# --- (ii) linked answer-key cases ---------------------------------------------

def _results_with(edit):
    results = copy.deepcopy(RESULTS)
    edit(results)
    return results


def test_a_flipped_linked_case_does_not_count():
    def flip(results):
        results["actions"]["a01"]["permission"]["verdict"] = "REJECTED"
    result = measure(results=_results_with(flip))
    assert failed_rows(result) == {"rule-01"}
    assert result["verified"] == BASE["verified"] - bytes_of("rule-01")
    assert "rule-01" not in result["rows"]


def test_changed_deciding_rules_do_not_count_but_reordered_ones_do():
    def widen(results):
        results["actions"]["a02"]["permission"]["positive"] = [1, 2, 3]
    assert failed_rows(measure(results=_results_with(widen))) == {"rule-01", "rule-02"}

    def reorder(results):
        results["actions"]["a02"]["permission"]["positive"] = [2, 1]
    assert measure(results=_results_with(reorder)) == BASE


def test_a_flipped_unlinked_case_changes_nothing():
    linked = {case for row in REGISTER["rows"] for case in row["decided_by"]["cases"]}
    assert "action:a37" not in linked

    def flip(results):
        results["actions"]["a37"]["permission"]["verdict"] = "APPROVED"
    assert measure(results=_results_with(flip)) == BASE


def test_a_flipped_report_case_does_not_count():
    def flip(results):
        results["actions"]["a31"]["rule_25"] = "not covered"
    assert failed_rows(measure(results=_results_with(flip))) == {"rule-26"}


@pytest.mark.parametrize("field, value, rows", [
    ("never_deciding", [], {"rule-12", "finding-3"}),
    ("satisfiable_pairs", [[3, 14], [12, 24]], {"rule-14", "finding-2"}),
    ("pair_queries", 143, {"finding-2"}),
    ("conflict", {"permitted": "CONFLICT-FREE", "report_required": "CONFLICT-FREE"}, {"finding-1"}),
    ("gap_tools", ["(an undeclared tool)", "get_secret", "post_message", "schedule_task", "send_email"],
     {"finding-5"}),
    ("gap_tools", ["(an undeclared tool)", "get_secret", "post_message", "schedule_task", "send_email",
                   "spawn_agent", "shell"], {"finding-5"}),
    ("gap_tools", ["get_secret", "post_message", "schedule_task", "send_email", "spawn_agent"], set()),
    ("overlaps", [[1, 2], [6, 7], [6, 8], [7, 8], [20, 21]], {"finding-7"}),
    ("overlaps", [[1, 2], [6, 7], [6, 8], [7, 8], [20, 21], [23, 24], [9, 10]], set()),
])
def test_policy_cases_at_and_around_their_boundary(field, value, rows):
    def edit(results):
        results["policy_summary"][field] = value
    assert failed_rows(measure(results=_results_with(edit))) == rows


def test_obligation_and_default_cases():
    def drop(results):
        results["comparison"]["obligation"]["covered"].remove("a34")
    assert failed_rows(measure(results=_results_with(drop))) == {"finding-6"}

    def flip(results):
        results["comparison"]["M4_default_sensitive"] = ["a27"]
    register = edited(lambda row: row["decided_by"]["cases"].append("default:sensitive"), "finding-1")
    assert failed_rows(measure(register, results=_results_with(flip))) == {"finding-1"}
    assert measure(register)["failures"] == []


@pytest.mark.parametrize("case", ["action:a99", "report:a99", "policy:bogus", "bogus", "action:", "obligation:other"])
def test_a_case_outside_the_key_is_refused(case):
    register = edited(lambda row: row["decided_by"]["cases"].append(case), "rule-01")
    assert failed_rows(measure(register)) == {"rule-01"}


# --- row shape: bytes, links, families ----------------------------------------

@pytest.mark.parametrize("delta, refused", [(-1, True), (0, False), (1, True)])
def test_bytes_typed_wrong_are_refused(delta, refused):
    register = edited(lambda row: row.update(bytes=row["bytes"] + delta), "rule-01")
    assert failed_rows(measure(register)) == ({"rule-01"} if refused else set())


def test_multibyte_statement_bytes_are_utf8_bytes():
    statement = "An action may read a file in the workspace — café."
    register = edited(lambda row: row.update(statement=statement, bytes=len(statement)), "rule-01")
    assert failed_rows(measure(register)) == {"rule-01"}
    register = edited(lambda row: row.update(statement=statement, bytes=len(statement.encode())), "rule-01")
    assert measure(register)["failures"] == []


def test_a_verified_row_with_no_linked_case_is_refused():
    register = edited(lambda row: row["decided_by"].update(cases=[]), "rule-01")
    assert failed_rows(measure(register)) == {"rule-01"}
    register = edited(lambda row: row["decided_by"].update(cases=["action:a01"]), "rule-01")
    assert measure(register)["failures"] == []
    register = edited(lambda row: row["decided_by"].update(tests=[]), "cedar-1")
    assert failed_rows(measure(register)) == {"cedar-1"}


def test_an_open_row_with_no_feature_family_is_refused():
    for family in (None, "", "speech act", "Speech acts", 7):
        register = edited(lambda row: row.update(family=family), "speech-1")
        assert failed_rows(measure(register)) == {"speech-1"}
    register = edited(lambda row: row.update(family="time"), "speech-1")
    result = measure(register)
    assert result["failures"] == [] and result["open"]["time"] == BASE["open"]["time"] + bytes_of("speech-1")


def test_a_verified_row_naming_a_family_or_an_unknown_status_is_refused():
    assert failed_rows(measure(edited(lambda row: row.update(family="time"), "rule-01"))) == {"rule-01"}
    assert failed_rows(measure(edited(lambda row: row.update(status="CHECKED"), "rule-01"))) == {"rule-01"}


# --- (i) the VE text is the text VE checked -------------------------------------

def test_a_rule_name_outside_the_manifest_is_refused():
    register = edited(lambda row: row["ve_text"].update(rules=["absent"]), "rule-01")
    assert failed_rows(measure(register)) == {"rule-01"}


def test_a_policy_text_results_were_not_checked_on_is_refused():
    def stale(results):
        results["inputs"]["policy.ve"] = "0" * 64
    failed = failed_rows(measure(results=_results_with(stale)))
    assert failed == {row["id"] for row in REGISTER["rows"]
                      if "usecases/agent-policy/policy.ve" in row["ve_text"]["files"]}
    manifest = dict(MANIFEST, text_digest="0" * 64)
    assert failed_rows(measure(manifest=manifest)) == {f"rule-{n:02d}" for n in range(1, 27)}


@pytest.mark.parametrize("files", [
    ["usecases/agent-policy/policy.ve", "usecases/agent-policy/log.ve", "usecases/agent-policy/absent.ve"],
    ["usecases/agent-policy/policy.ve", "usecases/agent-policy/log.ve", "usecases/agent-policy/environment.lean.json"],
    ["usecases/agent-policy/policy.ve"],
    ["usecases/agent-policy/log.ve"],
])
def test_ve_text_files_that_are_not_the_checked_inputs_are_refused(files):
    register = edited(lambda row: row["ve_text"].update(files=files), "rule-01")
    assert failed_rows(measure(register)) == {"rule-01"}


def test_a_record_outside_the_log_is_refused():
    register = edited(lambda row: row["ve_text"]["records"].append("a99"), "rule-01")
    assert failed_rows(measure(register)) == {"rule-01"}


def test_a_cedar_or_gatekeeper_row_outside_its_use_case_is_refused():
    register = edited(lambda row: row["ve_text"]["files"].append("usecases/agent-policy/policy.ve"), "cedar-1")
    assert failed_rows(measure(register)) == {"cedar-1"}
    register = edited(lambda row: row["decided_by"]["cases"].append("action:a01"), "gatekeeper-1")
    assert failed_rows(measure(register)) == {"gatekeeper-1"}


def test_a_failing_named_test_does_not_count():
    gatekeeper = row_of(REGISTER, "gatekeeper-1")["decided_by"]["tests"]
    result = measure(run_tests=lambda tests: set(tests) - {gatekeeper[0]})
    assert failed_rows(result) == {"gatekeeper-1"}
    assert failed_rows(measure(run_tests=lambda tests: set())) == {"cedar-1", "gatekeeper-1"}


# --- the frozen header and appended rows ----------------------------------------

def test_an_edited_frozen_row_is_refused_as_a_whole():
    register = copy.deepcopy(REGISTER)
    row_of(register, "speech-1")["statement"] += " "
    result = measure(register)
    assert result["verified"] == result["source"] == 0
    assert failed_rows(result) == {"register"}


def test_appended_rows_need_a_date_and_a_new_id():
    new = dict(copy.deepcopy(row_of(REGISTER, "speech-1")), id="speech-7", date="2026-11-01")
    register = copy.deepcopy(REGISTER)
    register["appended"].append(new)
    result = measure(register)
    assert result["failures"] == [] and result["source"] == BASE["source"] + new["bytes"]
    for change in ({"date": ""}, {"date": None}, {"id": "speech-1"}):
        register["appended"] = [dict(new, **change)]
        assert measure(register)["failures"], change
    register["appended"] = [{k: v for k, v in new.items() if k != "date"}]
    assert failed_rows(measure(register)) == {"register"}


# --- malformed input -----------------------------------------------------------

BAD = [7, True, None, [], {}, 1.5, "\ud800", [[[[]]]]]


@pytest.mark.parametrize("field", sorted(level.ROW_KEYS))
@pytest.mark.parametrize("value", BAD)
def test_each_row_field_retyped_is_refused(field, value):
    register = edited(lambda row: row.update({field: value}), "rule-01")
    result = measure(register)
    if (field, value) == ("family", None):
        assert result == BASE
    else:
        assert failed_rows(result) == {value if field == "id" and value == "\ud800" else
                                       "?" if field == "id" else "rule-01"}
        assert result["verified"] == BASE["verified"] - bytes_of("rule-01")


@pytest.mark.parametrize("value", BAD + ["x"])
def test_malformed_register_results_key_or_manifest_fail_without_raising(value):
    assert measure(register=value)["failures"]
    assert measure(results=value)["failures"]
    assert measure(key=value)["failures"]
    assert measure(manifest=value)["failures"]
    deep = value
    for _ in range(10_000):
        deep = [deep]
    assert measure(results={**RESULTS, "actions": deep})["failures"]


def test_main_exits_one_on_a_failing_register_and_zero_on_the_live_one(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(level, "run_pytest", passing)
    assert level.main([]) == 0
    out = capsys.readouterr().out
    assert f"verified bytes: {BASE['verified']}\nsource bytes: {BASE['source']}\n" in out
    broken = tmp_path / "requirements.json"
    broken.write_text(json.dumps(edited(lambda row: row.update(bytes=0), "rule-01")), encoding="utf-8")
    assert level.main(["--register", str(broken)]) == 1
    assert "FAIL rule-01: bytes" in capsys.readouterr().err
    broken.write_text("[" * 100_000, encoding="utf-8")
    assert level.main(["--register", str(broken)]) == 1
    assert level.main(["--register", str(tmp_path / "absent.json")]) == 1
