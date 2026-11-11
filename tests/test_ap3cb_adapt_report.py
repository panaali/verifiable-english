"""ap-3cb-adapt: the report's claims about the seeded bugs are read from the saved seed evidence (mutants.json).

Review finding F1 (record-only overclaim): the report said every split result is refused under the unmapped-`over`
bug, while E1, whose one rule has `over = []`, stays accepted. The class: a claim that a bug refuses every document,
or that every new guard has a seed, wider than what the seeds recorded. The seeds now record, per fixture, whether the
bugged `elaborateMap` accepts it, and the report's table is checked against that record. No Lean run: saved evidence.
"""
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parents[1] / "docs/act-phrases/ap-3cb-adapt"
REPORT = (HERE / "REPORT.md").read_text()
SEEDS = (HERE / "seed_bugs.py").read_text()
EVIDENCE = json.loads((HERE / "mutants.json").read_text())


def load_seed_bugs():
    spec = importlib.util.spec_from_file_location("ap3cb_seed_bugs", HERE / "seed_bugs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Universal claims about refusals or seeds that two fixtures cannot carry (F1's probe, widened to the class).
BLANKET = [
    r"every split (?:result|document)(?: is refused| with an .over.)",  # PROBE F1, as the review gives it
    r"refuses every (?:split )?(?:result|document)",
    r"every (?:split )?(?:result|document) is refused",
    r"statements hold\s+of every document",
    r"nothing is accepted",
    r"Each new guard has a seed",  # note F2: the `partAct` text pin has none
    r"Every new check can fail",
]


def test_no_blanket_claim_about_refusals_or_seeds():
    for name, text in (("REPORT.md", REPORT), ("seed_bugs.py", SEEDS)):
        for pattern in BLANKET:
            assert not re.search(pattern, text, re.I), (name, pattern)


def test_each_seed_records_which_fixture_it_refuses():
    seeds = load_seed_bugs()
    # One acceptance guard per fixture: a single `&&` over both cannot say which one a bug refuses.
    assert set(seeds.ACCEPT) == {"e1", "e4"}
    for fx, guard in seeds.ACCEPT.items():
        assert guard == f"#guard (elaborateMap {fx}).isOk"
    assert EVIDENCE["restored"] == "SURVIVOR"
    assert EVIDENCE["restored_accepted"] == {"e1": True, "e4": True}
    assert [b["id"] for b in EVIDENCE["bugs"]] == [b[0] for b in seeds.BUGS]
    for bug in EVIDENCE["bugs"]:
        assert bug["result"] == "KILLED", bug["id"]
        acc = bug["accepted"]
        assert set(acc) == set(seeds.ACCEPT) and all(type(v) is bool for v in acc.values()), bug["id"]
        # A refused fixture is one whose acceptance guard is among the failures, and only then.
        for fx, guard in seeds.ACCEPT.items():
            assert (not acc[fx]) == any(f == f"guard `{guard}`" for f in bug["failing"]), (bug["id"], fx)


def test_the_unmapped_over_bug_leaves_e1_accepted():
    """F1's example: E1's one rule has `over = []`, so the unmapped-`over` bug refuses E4 only."""
    bug = next(b for b in EVIDENCE["bugs"] if b["id"] == "split-node-over-unmapped")
    assert bug["accepted"] == {"e1": True, "e4": False}
    assert "proof mem_splitNode" in bug["failing"]


def report_table():
    """Bug id -> the "E1, E4 under the bug" cell of section 5's seed table."""
    lines = REPORT.splitlines()
    head = next(i for i, l in enumerate(lines) if l.startswith("| Bug |"))
    cols = [c.strip() for c in lines[head].strip("|").split("|")]
    col = cols.index("E1, E4 under the bug")
    rows = {}
    for line in lines[head + 2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        assert len(cells) == len(cols), line
        rows[re.match(r"`([^`]+)`", cells[0]).group(1)] = cells[col]
    return rows


def test_the_report_table_reads_the_saved_acceptance():
    rows = report_table()
    assert list(rows) == [b["id"] for b in EVIDENCE["bugs"]]
    for bug in EVIDENCE["bugs"]:
        want = ", ".join("accepted" if bug["accepted"][fx] else "refused" for fx in ("e1", "e4"))
        assert rows[bug["id"]] == want, bug["id"]
