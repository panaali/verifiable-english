"""The W1 delta's suite corpus and its tagging plugin (`docs/en-e3-norm/en-2/w1_delta.py`; en-e3bb review F1).

The suite corpus is derived from the coverage map (`derive_suite`), never listed by hand: review F1 found 10 test
files calling `parse_english` that a hand-kept list of 33 left out. The saved evidence's suite is checked by
`tests/test_english_statement_shadow.py`'s `check_suite`; this file tests the derivation on a map built here and the
plugin's tagging, and starts no git and no Lean.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from tests.test_norms import environment, permission

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def w1_delta():
    spec = importlib.util.spec_from_file_location("w1_delta_under_test", ROOT / "docs/en-e3-norm/en-2/w1_delta.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_delta_suite_is_every_unit_the_coverage_map_cannot_rule_out(monkeypatch, w1_delta):
    """A unit the map records running `parse_english` (or a function nested in it) is in; so is one the map has not
    recorded, one it recorded failing or opaque, and one whose run may have changed since the map; a unit that only
    imported the module or ran other functions of it is out."""
    monkeypatch.syspath_prepend(str(ROOT / "tools"))
    import select_tests
    units = ["tests/test_calls.py", "tests/test_nested.py", "tests/test_imports.py", "tests/test_opaque.py",
             "tests/test_failed.py", "tests/test_drifted.py", "tests/test_new.py", "tests/test_other.py",
             "tools/test_extra.py"]
    recorded = units[:6] + ["tests/test_other.py", "tools/test_extra.py"]
    status = {u: {"exit": 1 if u == "tests/test_failed.py" else 0, "seconds": 1.0,
                  "opaque": ["child left no record"] if u == "tests/test_opaque.py" else []} for u in recorded}
    tests = sorted(recorded)
    index = {u: i for i, u in enumerate(tests)}
    data = {"version": 7, "commit": "c" * 40, "tests": tests, "status": status, "reads": {}, "dirs": {},
            "programs": {}, "operations": {}, "presence": {}, "modes": {},
            "functions": {"ve/norm_english.py": {
                "parse_english": [index["tests/test_calls.py"]],
                "parse_english.<locals>.<genexpr>": [index["tests/test_nested.py"]],
                "<module>": [index[u] for u in tests],
                "render_english": [index["tests/test_imports.py"], index["tests/test_other.py"]]}}}
    plan = w1_delta.derive_suite(select_tests.Coverage(data), set(units), {"tests/test_drifted.py"})
    assert plan["reached"] == ["tests/test_calls.py", "tests/test_nested.py"]
    assert plan["unknown"] == ["tests/test_drifted.py", "tests/test_failed.py", "tests/test_new.py",
                               "tests/test_opaque.py"]
    assert plan["files"] == sorted(plan["reached"] + plan["unknown"]) and plan["map"] == "c" * 40
    assert plan["function"] == "ve/norm_english.py:parse_english"
    assert w1_delta.short("tests/test_rights.py") == "rights" and w1_delta.short(units[-1]) == units[-1]


def test_the_suite_run_deselects_exactly_the_tests_that_read_its_output(w1_delta):
    """The suite run deselects `READS_OUTPUT`: the tests of the shadow's test file whose body names `DELTA` or
    `REPORT` (the saved delta and the REPORT), and only those; none of them names `parse_english`, so no record is
    lost."""
    import ast
    tree = ast.parse((ROOT / w1_delta.SHADOW_TESTS).read_text())
    tests = {node.name: {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}
    reading = {name for name, names in tests.items() if names & {"DELTA", "REPORT"}}
    assert {test.split("::")[1] for test in w1_delta.READS_OUTPUT} == reading
    assert all("parse_english" not in tests[name] for name in reading)


def test_the_plugin_tags_only_the_records_of_its_own_log(monkeypatch, tmp_path, w1_delta):
    """The suite runs with `w1_delta` as a pytest plugin: a record written to the run's log carries its corpus and
    test, while a test's own `statement_record` call and a log the test names itself get the records they would get
    without the plugin (so the instrumented run passes the shadow's own tests)."""
    from ve import norm_english
    from ve.backends import relay
    from ve.errors import CheckerUnavailable
    monkeypatch.chdir(tmp_path)
    for name in ("_shadow", "statement_record"):  # restored after the test: `install` replaces both
        monkeypatch.setattr(norm_english, name, getattr(norm_english, name))

    real = relay.decide

    def unreachable(mode, cases, **kwargs):  # every shadow answer is `lean-unavailable`; Python's reader is unchanged
        if mode == "english.statement":
            raise CheckerUnavailable("CheckerUnavailable: the Lean service is not running")
        return real(mode, cases, **kwargs)
    monkeypatch.setattr(relay, "decide", unreachable)
    ours, theirs = tmp_path / "ours.jsonl", tmp_path / "theirs.jsonl"
    monkeypatch.setenv("VE_STATEMENT_COMPARATOR", "1")
    monkeypatch.setenv("VE_SHADOW_LOG", str(ours))
    w1_delta.install()
    monkeypatch.setattr(w1_delta, "TAG", w1_delta.TAG)
    w1_delta.TAG.clear()
    env, text = environment({"permitted": permission()}), "Rule 1. Every act may be done."
    norm_english.parse_english(env, text)
    plain = norm_english.statement_record(text, [], CheckerUnavailable("x"))
    assert "corpus" not in plain and "id" not in plain
    monkeypatch.setenv("VE_SHADOW_LOG", str(theirs))
    norm_english.parse_english(env, text)
    [tagged] = [json.loads(line) for line in ours.read_text().splitlines()]
    [untagged] = [json.loads(line) for line in theirs.read_text().splitlines()]
    assert tagged["corpus"] == "suite" and tagged["id"].endswith("test_the_plugin_tags_only_the_records_of_its_own_log")
    assert {k: v for k, v in tagged.items() if k not in ("corpus", "id")} == untagged
    assert "corpus" not in untagged and untagged["class"] == "lean-unavailable"
