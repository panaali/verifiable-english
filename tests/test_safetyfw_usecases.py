"""The anthropic-rsp and openai-preparedness use cases (usecases/<case>): the frozen answer keys and their
transcription.

Each PLAN's section 6 is the answer key, frozen before any VE run (KEY-FREEZE.md records its SHA-256). The
transcription in answer-key.json and cases.json is pinned here by hash, and its counts are checked against the
PLAN's own section 5 table and section 6 totals, so that neither the key nor its transcription can change unnoticed.
"""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
USECASES = REPO / "usecases"

# case -> (section-6 SHA-256 recorded at the freeze, total items of section 5)
FROZEN = {
    "anthropic-rsp": ("1a684c7276c98e80b6a2db2718b5af7ba702b933be846498f895ec28744af5a3", 126),
    "openai-preparedness": ("6d1dd2a7729f789ea26212783fd49355ff3256110dc879c18e9f794b955ac522", 239),
}
# The section-6 subsection of each family, in the PLANs' order.
FAMILY_SECTION = {"A": "6.1", "B": "6.2", "K": "6.3", "T": "6.4", "C": "6.5", "G": "6.6", "N": "6.7", "S": "6.8",
                  "D": "6.9"}
CASES = sorted(FROZEN)


def section(case, number):
    """PLAN.md section `number` as KEY-FREEZE.md defines it: from the line starting `## <n>. ` up to the next one,
    joined with newlines plus a final newline."""
    lines = (USECASES / case / "PLAN.md").read_text(encoding="utf-8").split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith(f"## {number}. "))
    stop = next(i for i, line in enumerate(lines) if line.startswith(f"## {number + 1}. "))
    return "\n".join(lines[start:stop]) + "\n"


def items(case):
    return json.loads((USECASES / case / "answer-key.json").read_text())["items"]


def family_totals(case):
    """The section 5 table: family letter -> scored items (the number ending the row), and the bold total."""
    totals, total = {}, None
    for line in section(case, 5).split("\n"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and re.fullmatch(r"[A-Z]: .+", cells[0]):
            totals[cells[0][0]] = int(re.search(r"(\d+)$", cells[2]).group(1))
        elif cells[0] == "**Total**":
            total = int(cells[2].strip("*"))
    return totals, total


@pytest.mark.parametrize("case", CASES)
def test_section_6_is_the_frozen_key(case):
    """(a) The answer key is section 6 as frozen: the SHA-256 KEY-FREEZE.md records, recomputed."""
    recorded = re.search(r"Section 6 SHA-256 \| `([0-9a-f]{64})` \((\d+) bytes\)",
                         (USECASES / case / "KEY-FREEZE.md").read_text()).groups()
    text = section(case, 6).encode()
    assert (hashlib.sha256(text).hexdigest(), str(len(text))) == recorded
    assert recorded[0] == FROZEN[case][0]


@pytest.mark.parametrize("case", CASES)
def test_answer_key_has_every_item_of_section_5(case):
    """(b) and (c): the transcription has the section 5 total and each family's count, and one item per id."""
    totals, total = family_totals(case)
    rows = items(case)
    assert total == FROZEN[case][1] == len(rows) == sum(totals.values())
    assert len({r["id"] for r in rows}) == len(rows)
    assert Counter(r["plan"] for r in rows) == {FAMILY_SECTION[f]: n for f, n in totals.items()}
    assert {r["id"][0] for r in rows if r["plan"] == FAMILY_SECTION[r["id"][0]]} == set(totals)
    assert all(r["plan"] == FAMILY_SECTION[r["id"][0]] for r in rows)


@pytest.mark.parametrize("case", CASES)
def test_verdict_totals_are_those_section_6_states(case):
    """Section 6 states the ALL/SOME/NONE totals of its tabulated families; the transcription has them."""
    stated = {}
    for subsection, text in re.findall(r"### (6\.\d) [^\n]*\n(.*?)(?=\n### |\Z)", section(case, 6), re.S):
        found = re.search(r"Totals: ((?:(?:ALL|SOME|NONE) \d+(?:, )?)+)\.", text)
        if found:
            stated[subsection] = {k: int(n) for k, n in re.findall(r"(ALL|SOME|NONE) (\d+)", found.group(1))}
    assert stated, case
    for subsection, expected in stated.items():
        got = Counter(r["key"].split("(")[0] for r in items(case) if r["plan"] == subsection)
        assert got == expected, subsection


@pytest.mark.parametrize("case", CASES)
def test_every_item_names_a_case_of_cases_json_or_none(case):
    cases = {c["id"]: c for c in json.loads((USECASES / case / "cases.json").read_text())["cases"]}
    named = {r["case"] for r in items(case)}
    assert named - {None} == set(cases)
    for r in items(case):
        if r["case"] is not None:
            assert cases[r["case"]]["family"] == r["id"][0], r["id"]
        else:
            assert r["plan"] in {"6.5", "6.7", "6.8", "6.9"}, r["id"]


TRANSCRIPTION_SHA256 = {
    "anthropic-rsp": {"answer-key.json": "fd00575d348f0917cc6aebd08ea21cb67c5f2f7f1540a2d970666a127f1d4a50",
                      "cases.json": "0ed79956454c30e12b7808bec6d0db7b94324a97a14daabf7e8272d5ec8a5405"},
    "openai-preparedness": {"answer-key.json": "2c8b27504eebd57bdb4953f5527fdc6373ce5e456fc5050bc8a840877b160ac2",
                            "cases.json": "a5b0d0c6a3bade39bd046e9434656231547237d06233651da909c34bd0704397"},
}


@pytest.mark.parametrize("case", CASES)
def test_transcription_is_pinned(case):
    """No key cell or case fact of the transcription changes without this pin changing in the same commit."""
    for name, digest in TRANSCRIPTION_SHA256[case].items():
        assert hashlib.sha256((USECASES / case / name).read_bytes()).hexdigest() == digest, name
