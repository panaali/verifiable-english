"""The policy family's requirement register and its level reader (apol-req), on both sides of each check."""
import copy
import importlib.util
import json
import re
from pathlib import Path

import pytest

CASE = Path(__file__).resolve().parents[1] / "usecases" / "agent-policy"
_spec = importlib.util.spec_from_file_location("agent_policy_level", CASE / "level.py")
level = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(level)
REGISTER, KEY, RESULTS, MANIFEST = (json.loads((CASE / name).read_text(encoding="utf-8")) for name in
                                    ("requirements.json", "answer-key.json", "results.json", "policy.manifest.json"))
P, L = "usecases/agent-policy/policy.ve", "usecases/agent-policy/log.ve"


def passing(tests):
    return set(tests)


def measure(register=REGISTER, results=RESULTS, key=KEY, manifest=MANIFEST, run_tests=passing):
    return level.measure(register, key, results, manifest, run_tests)


def row_of(register, row_id):
    return next(row for row in register["rows"] + register["appended"] if row["id"] == row_id)


def edited(edit, row_id):
    """A copy of the register with one row edited and the frozen header re-hashed, so only the edit is judged."""
    register = copy.deepcopy(REGISTER)
    edit(row_of(register, row_id))
    register["header"]["rows_sha256"] = level.rows_sha256(register["rows"])
    return register


def with_results(edit):
    results = copy.deepcopy(RESULTS)
    edit(results)
    return results


def failed_rows(result):
    return {failure.split(":", 1)[0] for failure in result["failures"]}


def bytes_of(*row_ids):
    return sum(row_of(REGISTER, row_id)["bytes"] for row_id in row_ids)


BASE = measure()


def test_live_register_passes_with_its_named_tests_run():
    live, rows, header = level.measure(REGISTER, KEY, RESULTS, MANIFEST), REGISTER["rows"], REGISTER["header"]
    assert live["failures"] == [] and live == BASE
    assert live["source"] == sum(row["bytes"] for row in rows)
    assert live["verified"] == sum(row["bytes"] for row in rows if row["status"] == "VERIFIED")
    assert live["verified"] + sum(live["open"].values()) == live["source"]
    assert live["rows"] == {row["id"]: row["status"] for row in rows}
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", header["frozen_utc"])
    assert header["rows_sha256"] == level.rows_sha256(rows)
    assert header["basis"].startswith("a unit is one plain-English requirement statement of the family;")
    assert header["basis"].endswith("Source bytes = all units.")
    assert all(family in header["basis"] for family in level.FAMILIES)


def test_rows_are_taken_from_the_named_sources():
    rows = REGISTER["rows"]
    plain = dict(re.findall(r"^\| (\d+) \| [a-z-]+ \| (.+) \| CHECKED \|$",
                            (CASE / "README.md").read_text(encoding="utf-8"), re.M))
    rules = [row for row in rows if row["id"].startswith("rule-")]
    assert [row["statement"] for row in rules] == [plain[str(n)] for n in range(1, 27)]
    names = {block["number"]: block["name"] for block in MANIFEST["blocks"]}
    assert [row["ve_text"]["rules"] for row in rules] == [[names[n]] for n in range(1, 27)]
    plan = (CASE / "PLAN.md").read_text(encoding="utf-8")
    section = lambda start, end: plan.split(start)[1].split(end)[0]  # noqa: E731
    count = {prefix: sum(row["id"].startswith(prefix) for row in rows)
             for prefix in ("finding-", "speech-", "scope-", "cedar-", "gatekeeper-")}
    assert count["finding-"] == len(re.findall(r"^\| (?!Finding|---)", section("## 7.", "## 8."), re.M))
    assert count["speech-"] == len(re.findall(r"^\| (?!Item|---)", section("## 10.", "## 11."), re.M))
    assert count["scope-"] == len(re.findall(r"^- ", section("Out of scope, with the reason:", "## 3."), re.M))
    assert (count["cedar-"], count["gatekeeper-"]) == (1, 1) and len(rows) == 26 + sum(count.values())


def test_readme_states_the_measured_level():
    section = (CASE / "README.md").read_text(encoding="utf-8").split("## Measured level")[1].split("\n## ")[0]
    assert REGISTER["header"]["basis"] == " ".join(line[2:] for line in section.splitlines() if line.startswith("> "))
    verified = sum(row["status"] == "VERIFIED" for row in REGISTER["rows"])
    table = dict(re.findall(r"^\| (.+?) \| ([\d,]+) \|$", section, re.M))
    assert table.pop(f"Verified ({verified} rows)") == f"{BASE['verified']:,}"
    assert table.pop(f"Source ({len(REGISTER['rows'])} rows)") == f"{BASE['source']:,}"
    assert table == {f"OPEN, {family}": f"{size:,}" for family, size in BASE["open"].items()}


def _set(path, value):
    def edit(target):
        *parents, last = path
        for name in parents:
            target = target[name]
        target[last] = value(target[last]) if callable(value) else value
    return edit


GAPS = ["get_secret", "post_message", "schedule_task", "send_email", "spawn_agent"]
OVERLAPS = [[1, 2], [6, 7], [6, 8], [7, 8], [20, 21], [23, 24]]
MULTIBYTE = "An action may read a file in the workspace — café."
# (row edited, its edit, results edit, rows refused); every other row still counts.
CASES = {
    "flipped linked verdict": (None, None, _set(["actions", "a01", "permission", "verdict"], "REJECTED"), {"rule-01"}),
    "widened deciding rules": (None, None, _set(["actions", "a02", "permission", "positive"], [1, 2, 3]),
                               {"rule-01", "rule-02"}),
    "reordered deciding rules": (None, None, _set(["actions", "a02", "permission", "positive"], [2, 1]), set()),
    "flipped unlinked case": (None, None, _set(["actions", "a37", "permission", "verdict"], "APPROVED"), set()),
    "flipped report case": (None, None, _set(["actions", "a31", "rule_25"], "not covered"), {"rule-26"}),
    "never deciding emptied": (None, None, _set(["policy_summary", "never_deciding"], []), {"rule-12", "finding-3"}),
    "pair added": (None, None, _set(["policy_summary", "satisfiable_pairs"], [[3, 14], [12, 24]]),
                   {"rule-14", "finding-2"}),
    "pair queries 143": (None, None, _set(["policy_summary", "pair_queries"], 143), {"finding-2"}),
    "conflict freed": (None, None, _set(["policy_summary", "conflict", "permitted"], "CONFLICT-FREE"), {"finding-1"}),
    "gap missing": (None, None, _set(["policy_summary", "gap_tools"], [level.UNDECLARED_TOOL] + GAPS[:-1]),
                    {"finding-5"}),
    "gap extra": (None, None, _set(["policy_summary", "gap_tools"], [level.UNDECLARED_TOOL, "shell"] + GAPS),
                  {"finding-5"}),
    "gap without undeclared tool": (None, None, _set(["policy_summary", "gap_tools"], GAPS), set()),
    "overlap missing": (None, None, _set(["policy_summary", "overlaps"], OVERLAPS[:-1]), {"finding-7"}),
    "overlap extra": (None, None, _set(["policy_summary", "overlaps"], OVERLAPS + [[9, 10]]), set()),
    "obligation dropped": (None, None, _set(["comparison", "obligation", "covered"], lambda c: c[:-1]), {"finding-6"}),
    "default sensitive linked": ("finding-1", lambda r: r["decided_by"]["cases"].append("default:sensitive"),
                                 None, set()),
    "default sensitive flipped": ("finding-1", lambda r: r["decided_by"]["cases"].append("default:sensitive"),
                                  _set(["comparison", "M4_default_sensitive"], ["a27"]), {"finding-1"}),
    "bytes - 1": ("rule-01", _set(["bytes"], lambda b: b - 1), None, {"rule-01"}),
    "bytes + 1": ("rule-01", _set(["bytes"], lambda b: b + 1), None, {"rule-01"}),
    "bytes as characters": ("rule-01", lambda r: r.update(statement=MULTIBYTE, bytes=len(MULTIBYTE)), None,
                            {"rule-01"}),
    "bytes as UTF-8": ("rule-01", lambda r: r.update(statement=MULTIBYTE, bytes=len(MULTIBYTE.encode())), None,
                       set()),
    "verified, no case": ("rule-01", _set(["decided_by", "cases"], []), None, {"rule-01"}),
    "verified, one case": ("rule-01", _set(["decided_by", "cases"], ["action:a01"]), None, set()),
    "verified, no test": ("cedar-1", _set(["decided_by", "tests"], []), None, {"cedar-1"}),
    "verified with family": ("rule-01", _set(["family"], "time"), None, {"rule-01"}),
    "unknown status": ("rule-01", _set(["status"], "CHECKED"), None, {"rule-01"}),
    "open, other family": ("speech-1", _set(["family"], "time"), None, set()),
    "rule outside manifest": ("rule-01", _set(["ve_text", "rules"], ["absent"]), None, {"rule-01"}),
    "absent file": ("rule-01", _set(["ve_text", "files"], [P, L, "usecases/agent-policy/absent.ve"]), None,
                    {"rule-01"}),
    "unchecked file": ("rule-01", _set(["ve_text", "files"], [P, L, "usecases/agent-policy/environment.lean.json"]),
                       None, {"rule-01"}),
    "records without log": ("rule-01", _set(["ve_text", "files"], [P]), None, {"rule-01"}),
    "rules without policy": ("rule-01", _set(["ve_text", "files"], [L]), None, {"rule-01"}),
    "record outside log": ("rule-01", _set(["ve_text", "records"], lambda r: r + ["a99"]), None, {"rule-01"}),
    "cedar text outside": ("cedar-1", _set(["ve_text", "files"], lambda f: f + [P]), None, {"cedar-1"}),
    "gatekeeper with case": ("gatekeeper-1", _set(["decided_by", "cases"], ["action:a01"]), None, {"gatekeeper-1"}),
    **{f"case {case}": ("rule-01", _set(["decided_by", "cases"], lambda c, case=case: c + [case]), None, {"rule-01"})
       for case in ("action:a99", "report:a99", "policy:bogus", "bogus", "action:", "obligation:other")},
}


@pytest.mark.parametrize("name", CASES)
def test_each_check_at_and_around_its_boundary(name):
    row_id, edit, results_edit, refused = CASES[name]
    result = measure(edited(edit, row_id) if row_id else REGISTER, with_results(results_edit or (lambda r: None)))
    assert failed_rows(result) == refused
    moved = result["source"] - BASE["source"]  # a statement edit on an accepted row moves both totals
    assert result["verified"] == BASE["verified"] - bytes_of(*refused) + (moved if not refused else 0)


def test_an_open_row_with_no_feature_family_is_refused():
    for family in (None, "", "speech act", "Speech acts", 7):
        register = edited(_set(["family"], family), "speech-1")
        assert measure(register)["failures"] == ["speech-1: an OPEN row names no feature family of the basis"]


def test_a_policy_text_results_were_not_checked_on_is_refused():
    failed = failed_rows(measure(results=with_results(_set(["inputs", "policy.ve"], "0" * 64))))
    assert failed == {row["id"] for row in REGISTER["rows"] if P in row["ve_text"]["files"]}
    manifest = dict(MANIFEST, text_digest="0" * 64)
    assert failed_rows(measure(manifest=manifest)) == {f"rule-{n:02d}" for n in range(1, 27)}


def test_a_failing_named_test_does_not_count():
    first = row_of(REGISTER, "gatekeeper-1")["decided_by"]["tests"][0]
    assert failed_rows(measure(run_tests=lambda tests: set(tests) - {first})) == {"gatekeeper-1"}
    assert failed_rows(measure(run_tests=lambda tests: set())) == {"cedar-1", "gatekeeper-1"}


def test_an_edited_frozen_row_refuses_the_whole_register():
    register = copy.deepcopy(REGISTER)
    row_of(register, "speech-1")["statement"] += " "
    result = measure(register)
    assert (result["verified"], result["source"], failed_rows(result)) == (0, 0, {"register"})


def test_appended_rows_need_a_date_and_a_new_id():
    new = dict(copy.deepcopy(row_of(REGISTER, "speech-1")), id="speech-7", date="2026-11-01")
    register = copy.deepcopy(REGISTER)
    register["appended"].append(new)
    result = measure(register)
    assert result["failures"] == [] and result["source"] == BASE["source"] + new["bytes"]
    for change in ({"date": ""}, {"date": None}, {"id": "speech-1"}):
        register["appended"] = [dict(new, **change)]
        assert failed_rows(measure(register)) == {"register"}, change
    register["appended"] = [dict(new, extra=1)]
    assert failed_rows(measure(register)) == {"speech-7"}


BAD = [7, True, None, [], {}, 1.5, "\ud800", [[[[]]]]]


@pytest.mark.parametrize("field", sorted(level.ROW_KEYS))
@pytest.mark.parametrize("value", BAD)
def test_each_row_field_retyped_is_refused(field, value):
    result = measure(edited(_set([field], value), "rule-01"))
    if (field, value) == ("family", None):
        assert result == BASE
    else:
        assert failed_rows(result) == {value if field == "id" and value == "\ud800" else
                                       "?" if field == "id" else "rule-01"}
        assert result["verified"] == BASE["verified"] - bytes_of("rule-01")


@pytest.mark.parametrize("value", BAD + ["x"])
def test_malformed_register_results_key_or_manifest_fail_without_raising(value):
    for side in ("register", "results", "key", "manifest"):
        assert measure(**{side: value})["failures"], side
    deep = value
    for _ in range(10_000):
        deep = [deep]
    assert measure(results={**RESULTS, "actions": deep})["failures"]


def test_main_exits_one_on_a_failing_register_and_zero_on_the_live_one(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(level, "run_pytest", passing)
    assert level.main([]) == 0
    assert f"verified bytes: {BASE['verified']}\nsource bytes: {BASE['source']}\n" in capsys.readouterr().out
    broken = tmp_path / "requirements.json"
    broken.write_text(json.dumps(edited(_set(["bytes"], 0), "rule-01")), encoding="utf-8")
    assert level.main(["--register", str(broken)]) == 1
    assert "FAIL rule-01: bytes" in capsys.readouterr().err
    broken.write_text("[" * 100_000, encoding="utf-8")
    assert level.main(["--register", str(broken)]) == 1
    assert level.main(["--register", str(tmp_path / "absent.json")]) == 1
