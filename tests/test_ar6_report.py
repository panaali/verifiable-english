"""The AR-6 report is a view of saved evidence, independent of live git HEAD."""
from __future__ import annotations

from collections import Counter
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/arch/AR-6"
EVIDENCE = HERE / "evidence"
SPEC = importlib.util.spec_from_file_location("ar6_report", HERE / "report.py")
assert SPEC is not None and SPEC.loader is not None
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def _saved(name: str):
    return json.loads((EVIDENCE / name).read_text())


def test_report_is_generated_from_saved_evidence():
    text = (HERE / "REPORT.md").read_text()
    generated = text.split("<!-- BEGIN GENERATED AR-6 METRICS -->\n", 1)[1].split(
        "\n<!-- END GENERATED AR-6 METRICS -->", 1)[0]
    assert generated == REPORT.metrics()


def test_the_census_counts_follow_from_its_saved_sites_and_entries():
    census = _saved("census.json")
    entries, lines = census["entries"], census["lines"]
    assert census["sites"] == len(lines) == len(entries) == sum(census["by_domain"].values()) > 0
    assert census["modules"] == len({path for path, *_ in lines})
    assert Counter((path, scope, domain) for path, _, scope, domain in lines) == Counter(
        (e["path"], e["scope"], e["domain"]) for e in entries)
    lean = [e for e in entries if e["owner"] == "lean"]
    assert census["lean_owned"] == len(lean) == sum(census["by_remover"].values())
    assert census["python_owned"] == len(entries) - len(lean) == sum(census["by_record"].values())
    assert census["lean_modules"] == len({e["path"] for e in lean})
    assert 0 < census["relayed_sites"] <= census["lean_owned"]


def test_the_saved_lean_domain_search_covers_every_allowlisted_domain():
    census, lean = _saved("census.json"), _saved("lean-domains.json")
    assert lean["commit"] == census["commit"]
    assert set(lean["domains"]) == {e["domain"] for e in census["entries"]}
    assert all(f.startswith("lean/VE/") and f.endswith(".lean") for files in lean["domains"].values() for f in files)
    python = {e["domain"] for e in census["entries"] if e["owner"] == "python"}
    assert all(lean["domains"][d] == [] for d in python)


def test_scope_and_mutants_are_saved_and_named():
    scope, mutants = _saved("scope.json"), _saved("mutants.json")
    assert len(scope["base"]) == len(scope["head"]) == 40
    assert scope["commits"] and scope["commits"][0]["hash"] == scope["head"]
    assert not any(f.startswith(("ve/", "lean/")) for f in scope["files"])
    assert {"tools/identity_lint.py", "tools/identity-sites.json", "tests/test_identity_lint.py"} <= set(
        scope["files"])
    assert len(mutants) >= 3 and len({m["bug"] for m in mutants}) == len(mutants)
    assert all(m["exit_code"] != 0 and "1 failed" in m["failure_excerpt"] and m["test"].startswith("tests/")
               for m in mutants)
