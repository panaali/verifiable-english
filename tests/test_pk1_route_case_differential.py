"""pk-1-cfr-1b: the saved base-vs-head differential of the 33 norm-defaults route cases (premise-packs spec,
fixtures L1/L2) is valid. It reads the saved record only, never git or a build: the record names pk-1's base and
head, covers each of the 33 saved cases with its own session, invokes every executable rebuilt between them, and
ends exit 0 with 0 differences, 0 timeouts and no INVALID line."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/premise-packs/pk-1-cfr-1b/evidence"
RECORD = EVIDENCE / "ab_route_cases_valid.txt"
CASES = EVIDENCE / "route_cases_norm_defaults.jsonl"
PK1_INVALID = ROOT / "docs/premise-packs/pk-1/evidence/ab_route_cases.txt"
# pk-1's base (main before pk-1, the merge's first parent) and head (pk-1's merge on main).
BASE = "3cc70f557e988c08cca45827495f79749a3f001c"
HEAD = "cb033316a7cb0476e856065e4047efe411bbe43d"
# The 33 ["norm-defaults", case] lines of tests/data/route-cases.jsonl at BASE and HEAD (identical at both).
CASES_SHA256 = "df47679e39b000328f0918aca414c8470b5000f67912c5ca6a6fbd3cb1a9d107"
SUMMARY = re.compile(r"^(\d+) invocations, (\d+) run on both builds, \d+ skipped .*; (\d+) differences, (\d+) timed out$")


def case_lines(cases_text: str) -> list[str]:
    """`route-case` lines the record must hold, one per saved case, as `route_case_sessions.py` prints them."""
    lines = cases_text.splitlines()
    assert hashlib.sha256(cases_text.encode()).hexdigest() == CASES_SHA256 and len(lines) == 33
    expected = []
    for number, line in enumerate(lines, 1):
        mode, case = json.loads(line)
        assert mode == "norm-defaults"
        expected.append(f"route-case nd-{number:02d} id={case.get('id')} kind={case.get('kind')} "
                        f"sha256={hashlib.sha256(line.encode()).hexdigest()[:12]}")
    return expected


def differential_faults(record: str, cases_text: str) -> list[str]:
    lines = [line.rstrip() for line in record.strip().splitlines()] or [""]
    faults = [f"INVALID line: {line[:80]}" for line in lines if "INVALID" in line]
    if lines[-1] != "exit 0":
        faults.append(f"ends {lines[-1][:40]!r}, not 'exit 0'")
    for want in (f"base {BASE} ", f"head {HEAD} ", f"baseline manifest: {BASE}", f"sha256 {CASES_SHA256} "):
        if not any(want in line + " " for line in lines):
            faults.append(f"no {want.strip()!r}")
    faults += [f"case not run: {want}" for want in case_lines(cases_text) if want not in lines]
    if "recorded route-case ve_service sessions 33 (33 distinct)" not in record:
        faults.append("the 33 case sessions are not all in the invocation list")
    rebuilt = next((line.split(": ", 1)[1].split(", ") for line in lines
                    if line.startswith("baseline ") and "rebuilt with a different digest: " in line), [])
    counts = dict(re.findall(r"(ve_\w+) (\d+)", next((line for line in lines if line.startswith("ve_")), "")))
    if "ve_service" not in rebuilt:
        faults.append(f"ve_service not among the rebuilt executables {rebuilt}: the case sessions were not compared")
    faults += [f"rebuilt {exe} has no invocation" for exe in rebuilt if int(counts.get(exe, 0)) == 0]
    summary = [m for m in map(SUMMARY.match, lines) if m]
    if len(summary) != 1:
        faults.append("no single summary line")
    elif summary[0][3] != "0" or summary[0][4] != "0" or int(summary[0][2]) < 33:
        faults.append(f"summary: {summary[0][0]}")
    return faults


def test_pk1_required_route_case_differential_is_valid() -> None:
    assert differential_faults(RECORD.read_text(encoding="utf-8"), CASES.read_text(encoding="utf-8")) == []


def test_differential_check_refuses_invalid_records() -> None:
    record, cases = RECORD.read_text(encoding="utf-8"), CASES.read_text(encoding="utf-8")
    assert any("INVALID" in f for f in differential_faults(PK1_INVALID.read_text(encoding="utf-8"), cases))
    dropped = "\n".join(line for line in record.splitlines() if not line.startswith("route-case nd-17 "))
    assert [f for f in differential_faults(dropped, cases) if f.startswith("case not run: route-case nd-17 ")]
    assert differential_faults(record.replace("; 0 differences", "; 1 differences"), cases)
    assert differential_faults(record.replace("exit 0", "exit 1"), cases)
    assert differential_faults(record.replace("ve_speech_acts_route 17", "ve_speech_acts_route 0"), cases)
