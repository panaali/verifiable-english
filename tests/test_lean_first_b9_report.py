"""Lean-first batch 9: the numbers of `docs/lean-first/b9/DELTA.md` are rendered from the evidence files
(build checklist 20), every A/B difference is a listed one, the differential fuzzer found nothing the base
lacked, and every seeded bug was caught (build checklist 13)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B9 = ROOT / "docs/lean-first/b9"


def _module(name):
    spec = importlib.util.spec_from_file_location(f"lean_first_b9_{name}", B9 / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _report():
    return _module("report")


def _evidence(name):
    return json.loads((B9 / "evidence" / name).read_text())


def test_delta_numbers_are_generated_from_the_evidence():
    report = _report()
    text = (B9 / "DELTA.md").read_text()
    assert report.BEGIN in text and report.END in text
    assert text.split(report.BEGIN, 1)[1].split(report.END, 1)[0] == report.render()


def test_every_ab_difference_is_listed_and_only_the_quantity_corpus_differs():
    delta = json.loads((B9 / "delta.json").read_text())
    pairs = {(pair["base"], pair["head"]) for pair in delta["wording"]}
    listed = {(row["corpus"], row["authority"], row["case"], row["op"]) for key in ("order", "verdict")
              for row in delta[key]}
    corpora = set()
    for name in ("quantity-compare.json", "core-compare.json", "pilots-compare.json", "layers-compare.json"):
        compare = _evidence(name)
        assert compare["unlisted"] == 0, name
        corpora |= {key.split("/")[0] for key in compare["records"]}
        for difference in compare["differences"]:
            assert difference["corpus"] == "quantity", difference
            key = (difference["corpus"], difference["authority"], difference["case"], difference["op"])
            if difference["class"] == "wording":
                base = difference["base"]["raised"]["message"]
                head = difference["head"]["raised"]["message"]
                assert (base, head) in pairs, (base, head)
            else:
                assert difference["class"] in ("order", "verdict") and key in listed, difference
    assert corpora == {"quantity", "probe", "conformance", "pilots", "readings", "discourse"}
    assert not delta["availability"] and not delta["unavailable"]


def test_the_fuzzer_found_nothing_the_base_lacked():
    fuzz = _evidence("difffuzz-ab.json")
    assert fuzz["ok"] is True
    assert [run["run"] for run in fuzz["runs"]][0] == "--ci" and len(fuzz["runs"]) == 15
    for run in fuzz["runs"]:
        assert run["head_only_new"] == [] and run["head_not_reproduced"] == [], run["run"]
        base, head = run["baseline"]
        assert head["entries"] <= base["entries"] and head["unreviewed"] == 0, run["run"]


def test_the_eligibility_harness_answers_alike_within_its_budget():
    eligibility = _evidence("eligibility.json")
    assert eligibility["base"]["stdout_sha256"] == eligibility["head"]["stdout_sha256"]
    assert eligibility["head"]["wall_s"] <= 1.25 * eligibility["base"]["wall_s"]


def test_every_seeded_bug_was_caught():
    lines = (B9 / "evidence" / "mutants.txt").read_text().splitlines()
    verdicts = [line for line in lines if line.startswith("M")]
    # Every seed the runner plants has its verdict, in the runner's order (build checklist 16).
    seeded = [name.split(" ", 1)[0] for name, *_ in _module("mutants").MUTANTS]
    assert [line.split(" ", 1)[0] for line in verdicts] == seeded
    assert all("failed=True" in line for line in verdicts), verdicts
    assert lines[-1].startswith("all mutants removed; ve_service rebuilt clean")
