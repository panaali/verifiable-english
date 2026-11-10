"""at-1's report (docs/attitudes/at-1/REPORT.md): its trust shortfalls and sizes are recomputed from saved evidence.

Every input is pinned to the tree of one of the item's commits (the baseline rows, the measured tie move, `git diff --numstat` from the
merge base), so the test still passes after a sync with main and after the merge. The report text of the reviewed head
36a5944147, which subtracted the at-1a-tie's 15 lines twice (review F1), must be refused.
"""
from __future__ import annotations

import json
import re
import subprocess
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = "docs/attitudes/at-1/REPORT.md"
# Trees, not commits: the test runners hold an export of the history whose commits have other ids but the same trees.
# The commit each tree is from is the one the report names.
TREES = {
    "a3454b6ba5": "69441147486fcf8b994d76b207a2e1c526a78ad3",  # at-1's merge base with main
    "0de99986bf": "95cc3cdcbd123d707759c7634974297135dcf9c9",
    "fc9c1eb496": "a4c7f488bced893dd4e6ee0e2907b624beb2c5a1",
    "693048ded9": "9dc7d832ab431d2ccadf8c4c49c2e9f11718c7e0",
    "8294a8da2e": "9d975d3fec743426323e358302588689f9248419",
    "2d577d5fc4": "4165ae8a36e6e3a967707973cdc53d74f47f61c7",  # the final code
    # The final Lean with its regenerated inventories (2d577d5fc4's Lean and side table; its declarations.txt was stale).
    "223ba4c085": "ebb497326c8fdb38aab70669206b56fedc429115",
    "36a5944147": "b7baba91b31a93568b9e2e7bb2971cedfead7998",  # the head of the final review, report included
}
BASE, FINAL_LEAN, REVIEWED = (TREES[c] for c in ("a3454b6ba5", "223ba4c085", "36a5944147"))
CAP = 150  # R16 (DRI-RULINGS.md): trusted lines per item
SYNTAX = "VE/Attitudes/Syntax.lean"
TOOL_WRITTEN = {"docs/attitudes/at-1/trust-mutants.json"}  # tools/trust_mutants.py's evidence


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def flat(text: str) -> str:
    """The text with each run of whitespace (the report's line wrapping included) read as one space."""
    return " ".join(text.split())


def section(text: str, title: str) -> str:
    match = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, f"{REPORT} has no section {title!r}"
    return match.group(1)


@cache
def shortfalls() -> dict[str, int]:
    """The measured shortfalls that reviews/dri-decisions-20261105-at-1b-trust.md item 3 asks each row to report.

    at-1b's baseline row records its own growth net of the at-1a-tie's first half (item 2: those lines are at-1a's
    cut-back, not at-1b's), so at-1b's own lines are its gross growth less the at-1b-tie move measured here, and the
    at-1a-tie's lines come off at-1a's row alone."""
    from tools import trust_map

    rows = json.loads(git("show", f"{FINAL_LEAN}:docs/trust-baseline.json"))["allowances"]

    def row(item: str) -> dict:
        found = [r for r in rows if r["class"] == "S" and r["reason"].startswith(f"{item}: ")]
        assert len(found) == 1, (item, found)
        return found[0]

    def number(pattern: str, text: str) -> int:
        match = re.search(pattern, text)
        assert match, (pattern, text)
        return int(match.group(1))

    a, b, c = row("at-1a"), row("at-1b"), row("at-1c")
    gross = number(r"gross \+(\d+)", b["reason"])
    first_half = number(r"at-1a-tie first half -(\d+)", b["reason"])
    assert b["lines"] == gross - first_half  # the row already nets the at-1a-tie's first half
    base_env = number(r"Syntax\.lean -(\d+) \(baseEnvAtt S to D\[V\] tied", c["reason"])

    before, problems, _ = trust_map.measure_rev(BASE)
    after, after_problems, _ = trust_map.measure_rev(FINAL_LEAN)
    assert not problems and not after_problems, problems + after_problems
    move = {key: after[SYNTAX][key] - before[SYNTAX][key] for key in ("S", "tied", "trusted", "lines")}
    tie = move["tied"]
    assert tie > 0 and move == {"S": -tie, "tied": tie, "trusted": -tie, "lines": 0}, move

    own_b = gross - tie
    own_a = a["lines"] - first_half - base_env
    return {"gross_b": gross, "tie": tie, "own_b": own_b, "a": a["lines"], "first_half": first_half,
            "base_env": base_env, "own_a": own_a, "over": (own_b - CAP) + (own_a - CAP)}


def shortfall_problems(text: str) -> list[str]:
    """What the report's Trust section gets wrong about the shortfalls, or nothing."""
    n = shortfalls()
    trust = flat(section(text, "Trust"))
    expected = [
        f"at-1b's own trusted lines are +{n['gross_b']} - {n['tie']} = +{n['own_b']}, against {CAP}: "
        f"{n['own_b'] - CAP} over.",
        f"at-1a's are +{n['a']} - {n['first_half']} (at-1b's ties) - {n['base_env']} (at-1c's `baseEnvAtt`) = "
        f"+{n['own_a']}, against {CAP}: {n['own_a'] - CAP} over.",
        f"In all, {n['over']} lines stay above the two caps",
    ]
    problems = [f"missing: {line}" for line in expected if line not in trust]
    stated = [int(m) for m in re.findall(r"(\d+) over\b", trust)]
    if stated != [n["own_b"] - CAP, n["own_a"] - CAP]:
        problems.append(f"the 'over' figures are {stated}")
    totals = [int(m) for m in re.findall(r"= \+(\d+), against", trust)]
    if totals != [n["own_b"], n["own_a"]]:
        problems.append(f"the own-line totals are {totals}")
    return problems


def numstat(tree: str) -> tuple[int, int]:
    """Lines added and changed from the merge base to `tree`, as the report's section "Size" counts them: without
    the files a generator writes (tools/regen_generated.py, merge kind `regenerate`) and the tool-written evidence;
    the hand-entered ledgers (merge kind `json`, tools/trust-classes.json) count."""
    from tools import regen_generated

    added = changed = 0
    for line in git("diff", "--numstat", BASE, tree).splitlines():
        plus, minus, path = line.split("\t")
        owner = regen_generated.owner(path)
        if path in TOOL_WRITTEN or (owner is not None and owner.merge == "regenerate"):
            continue
        added, changed = added + int(plus), changed + int(minus)
    return added, changed


def size_problems(text: str) -> list[str]:
    """Every table row of the report that names a commit and a size, checked against `numstat`, and the total."""
    problems, rows = [], 0
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        commit = re.search(r"\| ([0-9a-f]{10})(?: \(final code\))? \|", line)
        size = (re.search(r"\| (\d+), (\d+) \|", line)
                or re.search(r"\d+ lines \((\d+) added and (\d+) changed\)", line))
        if commit and size:
            rows += 1
            if commit.group(1) not in TREES:
                problems.append(f"{commit.group(1)}: no pinned tree")
                continue
            measured = numstat(TREES[commit.group(1)])
            if measured != (int(size.group(1)), int(size.group(2))):
                problems.append(f"{commit.group(1)}: stated {size.groups()}, measured {measured}")
    if rows < 7:  # five rows of "Size" and the two "Size after" rows of "Deliverables"
        problems.append(f"only {rows} sized rows")
    added, changed = numstat(REVIEWED)
    if f"at 36a5944147, the total is {added} added and {changed} changed" not in flat(section(text, "Size")):
        problems.append(f"the total at 36a5944147 is {added} added and {changed} changed")
    return problems


def test_the_trust_shortfalls_are_the_measured_ones():
    assert shortfalls()["own_b"] == shortfalls()["gross_b"] - shortfalls()["tie"]
    assert shortfall_problems((ROOT / REPORT).read_text()) == []


def test_the_reviewed_report_text_with_the_tie_subtracted_twice_is_refused():
    """Review F1: 36a5944147 said +165 - 10 = +155 (5 over) and 54 in all."""
    problems = shortfall_problems(git("show", f"{REVIEWED}:{REPORT}"))
    assert any("170" in p for p in problems) and any("69" in p for p in problems), problems
    assert any("[5, 49]" in p for p in problems), problems


def test_the_sizes_are_the_measured_ones():
    assert size_problems((ROOT / REPORT).read_text()) == []


def test_the_reviewed_report_total_of_about_610_is_refused():
    """Review F4: 36a5944147 said "about 610"; it measures 667 added."""
    problems = size_problems(git("show", f"{REVIEWED}:{REPORT}"))
    assert any("667 added and 15 changed" in p for p in problems), problems
