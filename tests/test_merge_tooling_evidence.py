"""docs/merge-tooling.md against its saved evidence (docs/merge-tooling/*.json).

Every number in the document's tables is recomputed from the saved files, which were recorded once by the
tools (`relay_mutation_gate.py --json`, `mutants.py --evidence`, `docs/merge-tooling/survey.py`, the replay):
no test here runs git, a gate or a build, so the evidence holds after any sync with main. The generated-file
table names exactly the entries of `tools/regen_generated.py`.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/merge-tooling.md").read_text()
EVIDENCE = ROOT / "docs/merge-tooling"


def numbers() -> dict[str, int]:
    rows = re.findall(r"^\| ([^|]+?) \| (\d+) \|$", DOC, re.M)
    names = [name for name, _ in rows]
    assert len(names) == len(set(names)), "a number is stated twice"
    return {name: int(value) for name, value in rows}


def load(name):
    return json.loads((EVIDENCE / name).read_text())


def test_survey_numbers_come_from_the_saved_merges():
    survey = load("sync-merge-survey.json")
    merges = survey["merges"]
    recomputed = {"sync_merges": len(merges), "clean": sum(not m["conflicts"] for m in merges),
                  "only_generated": sum(bool(m["conflicts"]) and not m["other"] for m in merges),
                  "with_other": sum(bool(m["other"]) for m in merges)}
    assert recomputed == survey["summary"]
    for merge in merges:
        assert sorted(merge["generated"] + merge["other"]) == merge["conflicts"]
    n = numbers()
    assert (n["sync merges surveyed"], n["sync merges without conflicts"],
            n["sync merges with conflicts only in generated files"], n["sync merges with other conflicts"]) == \
        (recomputed["sync_merges"], recomputed["clean"], recomputed["only_generated"], recomputed["with_other"])


def test_replay_numbers_come_from_the_saved_replay():
    replay = load("replay-dddeb893.json")
    survey = {m["merge"]: m for m in load("sync-merge-survey.json")["merges"]}
    assert replay["git_conflicts_without_driver"] == survey[replay["merge"][:10]]["conflicts"]
    n = numbers()
    assert n["replay: files conflicted without the driver"] == len(replay["git_conflicts_without_driver"])
    assert n["replay: files conflicted with the driver"] == len(replay["unmerged_with_driver"]) == 0
    assert n["replay: failed checks"] == len(replay["resolve"]["checks_failed"]) == 1
    assert replay["resolve"]["checks_failed"] == ["trust-tables"] and "+21" in DOC.replace(" ", "")
    files = replay["driver_result_vs_agent_merge"]
    assert files["ve/assurance-manifest.json"] == files["tools/trust-classes.json"] == "same content, other order"
    assert files["lean/VE/Audit.lean"] == files["lean/ResponseShape/Audit.lean"] == "identical"
    assert replay["after_resolve_lock_vs_agent"]["ve_service"]["only_replay"] == []


def test_gate_numbers_come_from_the_saved_report():
    report = load("relay-gate-report.json")
    totals, routes = report["totals"], report["routes"]
    assert report["failures"] == [] and report["findings"] == []
    allowed = Counter({key.split(":", 1)[1]: value for key, value in totals.items() if key.startswith("allowed:")})
    assert sum(allowed.values()) == totals["allowed"] == totals["accepted"]
    assert totals["mutants"] == totals["refused"] + totals["accepted"]
    n = numbers()
    assert n["routes"] == len(routes)
    assert n["service modes"] == sum(route.startswith("service:") for route in routes)
    assert n["one-shot routes"] == n["routes"] - n["service modes"]
    assert (n["fixtures"], n["mutants"], n["refused"], n["accepted and listed"], n["untyped fields"]) == \
        (totals["fixtures"], totals["mutants"], totals["refused"], totals["accepted"], totals["untyped"])
    assert n["accepted by design"] == sum(v for k, v in allowed.items() if k.startswith("B"))
    assert n["accepted follow-ups"] == sum(v for k, v in allowed.items() if k.startswith("F"))
    assert n["unlisted findings"] == len(report["findings"])
    assert all(stats["ok_fixtures"] >= 1 for stats in routes.values())
    # The follow-up table: one row per follow-up with accepted mutants, with the saved count.
    table = dict(re.findall(r"^\| (F\d+) \| (\d+) \|", DOC, re.M))
    assert {key: int(value) for key, value in table.items()} == {k: v for k, v in allowed.items() if k.startswith("F")}


def test_mutant_numbers_come_from_the_saved_run():
    planted = load("mutants.json")["mutants"]
    ran = load("mutants-evidence.json")["mutants"]
    assert [m["id"] for m in ran] == [m["id"] for m in planted]
    for mutant, row in zip(planted, ran):
        assert row["killed"] and row["baseline_exit"] == 0 and row["mutant_exit"] == 1
        assert set(row["killed_by"]) <= set(mutant["tests"]) and row["killed_by"]
        assert mutant["claim"] and mutant["find"] != mutant["replace"]
    n = numbers()
    assert n["seeded mutants"] == len(planted) and n["killed"] == sum(row["killed"] for row in ran)
    # At least one mutant per tool this batch adds or changes.
    files = {m["file"] for m in planted}
    assert {"tools/regen_generated.py", "tools/relay_mutation_gate.py", "tools/mutants.py",
            "ve/backends/speech_source.py"} <= files


def test_the_generated_file_table_names_every_entry():
    sys.path.insert(0, str(ROOT / "tools"))
    import regen_generated
    section = DOC.split("## 1.", 1)[1].split("`python tools/regen_generated.py --list`", 1)[0]
    listed = re.findall(r"^\| ([a-z-]+) \|", section, re.M)
    assert listed == [entry.name for entry in regen_generated.GENERATED]
