"""speed-vocabpar's measurement and its stop rule, regenerated from the saved run logs.

    python3 docs/infra/speed-vocabpar/check.py            # exit 1 on any missing, failed or skipped row
    python3 docs/infra/speed-vocabpar/check.py --write    # (re)write evidence.json from logs/

Every number comes from a log in `logs/` (each a mac-pytest.sh run's whole output, as it streamed) or from
`logs/mac-pytest.jsonl` (the lines mac-pytest.sh logged for those runs, copied as they are), and from the two
memory measurements of `rss.py` (`logs/rss-*.json`). The check recomputes evidence.json from them, requires it to be
the committed file, and requires every row of the stop rule to be present and to pass:

- each run ran on ve-mac-1, collected every test of its files, and skipped none;
- the vocab file with the pool takes at most half the serial baseline's time (the mean of each pair);
- the whole selected run is at least 5 minutes shorter with the pool than at width 1; every unit of the pooled run
  passes, and the width-1 run fails only tests/test_lean_pool.py, whose tests pin `JOBS > 1` (that run's edit);
- every node id has the same outcome with and without the pool, for each file, unseeded and seeded, and the seeded
  runs (a `#guard` deleted) fail at least one test;
- the pooled run's process tree stays under 8 GB (measured on the VM, `rss.py`: the runner runs only pytest).
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
LOGS = HERE / "logs"
EVIDENCE = HERE / "evidence.json"
VOCAB, LEXICAL = "tests/test_acts_vocab_mutants.py", "tests/test_acts_lexical_mutants.py"
# The tests each file collects at the measured commits.
COLLECTED = {VOCAB: 643, LEXICAL: 84}
RATIO, SAVED, RSS = 0.5, 300, 8 * 1024 ** 3

# Each run: its log, the worktree mac-pytest.sh ran, what it measures, and the files whose outcomes it lists.
RUNS = {
    "file-serial-1": {"worktree": "ve-vocabpar-base", "what": "vocab file, serial (main ab010c3f0, today's code)",
                      "files": [VOCAB]},
    "file-serial-2": {"worktree": "ve-vocabpar-base", "what": "vocab file, serial (main ab010c3f0), again",
                      "files": [VOCAB]},
    "file-pool-1": {"worktree": "ve-vocabpar-pool", "what": "vocab file, pool at the default width",
                    "files": [VOCAB]},
    "file-pool-2": {"worktree": "ve-vocabpar-pool", "what": "vocab file, pool at the default width, again",
                    "files": [VOCAB]},
    "lexical-serial": {"worktree": "ve-vocabpar-base", "what": "lexical file, serial (main ab010c3f0)",
                       "files": [LEXICAL]},
    "lexical-pool": {"worktree": "ve-vocabpar-pool", "what": "lexical file, pool at the default width",
                     "files": [LEXICAL]},
    "seeded-serial": {"worktree": "ve-vocabpar-scratch", "what": "both files, one #guard deleted from each "
                      "examples file, today's test code", "files": [VOCAB, LEXICAL]},
    "seeded-pool": {"worktree": "ve-vocabpar-scratch", "what": "both files, the same #guards deleted, the pool",
                    "files": [VOCAB, LEXICAL]},
    "select-serial": {"worktree": "ve-vocabpar-pool", "what": "whole selected run at width 1 (`JOBS = 1` uncommitted: "
                      "the runner does not pass VE_TEST_LEAN_JOBS on)", "select": True},
    "select-pool": {"worktree": "ve-vocabpar-pool", "what": "whole selected run at the default width",
                    "select": True},
}
OUTCOMES = ("PASSED", "FAILED", "SKIPPED", "ERROR", "XFAIL", "XPASS")
STAMP = re.compile(r"^\[mac-pytest(@ve-mac-1)? (\d\d):(\d\d):(\d\d)Z\] (.*)$", re.M)


def _seconds(match: re.Match) -> int:
    return int(match[2]) * 3600 + int(match[3]) * 60 + int(match[4])


def outcomes(text: str) -> dict[str, str]:
    """`-v`'s outcome of each node id. Another process's output can land between a node id and its outcome
    (`ve: English comparator: ...`), so a node id alone on its line takes the next line that starts with one."""
    found, pending = {}, None
    for line in text.splitlines():
        words = line.split()
        if line.startswith("tests/") and "::" in line and len(words) >= 1:
            pending = words[0]
            words = words[1:]
        if pending and words and words[0] in OUTCOMES:
            found[pending], pending = words[0], None
    return found


def _jsonl(worktree: str, end: str) -> dict:
    """The line mac-pytest.sh logged when the run ended (`end`, HH:MM:SS): its 1/5/15-min Mac load at the probe."""
    for line in (LOGS / "mac-pytest.jsonl").read_text().splitlines():
        record = json.loads(line)
        if record["worktree"].endswith("/" + worktree) and record["t"][11:19] == end:
            return record
    raise ValueError(f"no mac-pytest.jsonl line for {worktree} at {end}")


def run(name: str, spec: dict) -> dict:
    text = (LOGS / f"{name}.log").read_text()
    stamps = list(STAMP.finditer(text))
    summary = next(m for m in stamps if m[5].startswith("summary: "))
    start = next(m for m in stamps if m[1] and (m[5].startswith("pytest on ve-mac-1")
                                               or m[5].startswith("select on ve-mac-1")))
    wall = (_seconds(summary) - _seconds(start)) % 86400
    record = _jsonl(spec["worktree"], summary[0][12:20])
    out = {"what": spec["what"], "worktree": spec["worktree"], "where": record["where"],
           "ran_on_mac": summary[5].startswith("summary: ran on ve-mac-1"),
           "exit": int(re.search(r"exit=(\d+)", summary[5])[1]), "mac_load": record["mac_load"],
           "wall_seconds": wall}
    if spec.get("select"):
        units = re.findall(r"^  (tests/\S+|tools/\S+): exit (\S+) in ([\d.]+) s", text, re.M)
        out["units"] = {unit: {"exit": code, "seconds": float(s)} for unit, code, s in units}
        out["selected"] = int(re.search(r"^(\d+)/\d+ test units", text, re.M)[1])
        out["failed_tests"] = sorted(set(re.findall(r"^FAILED (tests/\S+::\S+)", text, re.M)))
        return out
    final = re.search(r"^=+ (.*) in ([\d.]+)s(?: \([\d:]+\))? =+$", text, re.M)
    out["pytest_seconds"] = float(final[2])
    out["summary"] = final[1]
    found = outcomes(text)
    out["outcomes"] = {f: {node: o for node, o in sorted(found.items()) if node.startswith(f + "::")}
                       for f in spec["files"]}
    return out


def _same(a: dict, b: dict) -> bool:
    return a == b and len(a) > 0


def rows(runs: dict, rss: dict) -> list[dict]:
    """The stop rule's rows, each with its numbers and whether it passes."""
    found = []

    def row(name: str, ok: bool, **numbers) -> None:
        found.append({"row": name, "pass": bool(ok), **numbers})

    for name, r in runs.items():
        counts = {f: len(o) for f, o in r.get("outcomes", {}).items()}
        skipped = sorted(n for o in r.get("outcomes", {}).values() for n, v in o.items() if v == "SKIPPED")
        complete = all(counts[f] == COLLECTED[f] for f in counts)
        row(f"ran {name}", r["ran_on_mac"] and r["where"] == "ve-mac-1" and complete and not skipped,
            collected=counts, skipped=skipped)
    serial = [runs[f"file-serial-{i}"]["pytest_seconds"] for i in (1, 2)]
    pool = [runs[f"file-pool-{i}"]["pytest_seconds"] for i in (1, 2)]
    ratio = (sum(pool) / 2) / (sum(serial) / 2)
    row("vocab file: pool at most 50% of serial", ratio <= RATIO, serial_seconds=serial, pool_seconds=pool,
        ratio=round(ratio, 3))
    saved = runs["select-serial"]["wall_seconds"] - runs["select-pool"]["wall_seconds"]
    row("whole selected run: at least 5 min shorter", saved >= SAVED,
        serial_seconds=runs["select-serial"]["wall_seconds"], pool_seconds=runs["select-pool"]["wall_seconds"],
        saved_seconds=saved)
    for unit in (VOCAB, LEXICAL):
        for r in ("select-serial", "select-pool"):
            row(f"{r}: {unit} ran and passed", runs[r]["units"].get(unit, {}).get("exit") == "0",
                seconds=runs[r]["units"].get(unit, {}).get("seconds"))
    for r in ("select-serial", "select-pool"):
        row(f"{r}: every selected unit ran", len(runs[r]["units"]) == runs[r]["selected"] > 0,
            units=len(runs[r]["units"]))
    row("select-pool: every unit passed", all(u["exit"] == "0" for u in runs["select-pool"]["units"].values()))
    failed = sorted(u for u, x in runs["select-serial"]["units"].items() if x["exit"] != "0")
    pinned = {"tests/test_lean_pool.py::test_the_pool_elaborates_exactly_the_modules_items_that_will_run",
              "tests/test_lean_pool.py::test_the_width_is_the_setting_else_the_default"}
    row("select-serial: only the tests that pin JOBS > 1 fail",
        failed == ["tests/test_lean_pool.py"] and set(runs["select-serial"]["failed_tests"]) == pinned,
        failed_units=failed)
    v = [runs[n]["outcomes"][VOCAB] for n in ("file-serial-1", "file-serial-2", "file-pool-1", "file-pool-2")]
    row("vocab outcomes: pool == serial", all(_same(v[0], x) for x in v[1:]),
        differ=sorted(n for x in v[1:] for n in set(v[0]) | set(x) if v[0].get(n) != x.get(n)))
    lx = [runs[n]["outcomes"][LEXICAL] for n in ("lexical-serial", "lexical-pool")]
    row("lexical outcomes: pool == serial", _same(*lx), differ=sorted(n for n in set(lx[0]) | set(lx[1])
                                                                       if lx[0].get(n) != lx[1].get(n)))
    for f in (VOCAB, LEXICAL):
        a, b = runs["seeded-serial"]["outcomes"][f], runs["seeded-pool"]["outcomes"][f]
        failed = sorted(n for n, o in a.items() if o == "FAILED")
        row(f"seeded {f}: same outcomes, some test fails", _same(a, b) and len(failed) > 0, failed=failed)
    row("peak RSS of the pooled run under 8 GB", rss["pool"]["peak_tree_rss_bytes"] < RSS,
        pool_bytes=rss["pool"]["peak_tree_rss_bytes"], pool_lean=rss["pool"]["peak_lean"],
        serial_bytes=rss["serial"]["peak_tree_rss_bytes"])
    return found


def evidence() -> dict:
    runs = {name: run(name, spec) for name, spec in RUNS.items()}
    rss = {kind: json.loads((LOGS / f"rss-{kind}.json").read_text()) for kind in ("pool", "serial")}
    return {"batch": "speed-vocabpar", "runs": runs, "rss": rss, "rows": rows(runs, rss)}


def main(argv: list[str]) -> int:
    try:
        fresh = evidence()
    except (OSError, ValueError, KeyError, TypeError, StopIteration, ZeroDivisionError) as error:
        print(f"FAIL: a row cannot be computed: {type(error).__name__}: {error}")
        return 1
    if "--write" in argv:
        EVIDENCE.write_text(json.dumps(fresh, indent=1, sort_keys=True) + "\n")
    saved = json.loads(EVIDENCE.read_text()) if EVIDENCE.exists() else None
    bad = [] if saved == fresh else ["evidence.json is not what the logs give (run with --write)"]
    for row in fresh["rows"]:
        print(f"{'PASS' if row['pass'] else 'FAIL'}  {row['row']}  "
              f"{ {k: v for k, v in row.items() if k not in ('row', 'pass', 'differ', 'failed')} }")
        if not row["pass"]:
            bad.append(row["row"])
    for problem in bad:
        print(f"FAIL: {problem}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
