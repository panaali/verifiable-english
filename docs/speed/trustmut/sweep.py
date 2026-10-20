#!/usr/bin/env python3
"""speed-trustmut reviews F7 and F9: the DRI's sweeps over the truth tables of tests/test_trust_mutants.py.

    uv run python docs/speed/trustmut/sweep.py [--run] [--jobs 16]

The forms table (F7) is every command form `classify` can see, bare, under `#guard_msgs in` and with its docstring
too, in the mutated module (its proofs cut up front) and in another (a proof the mutant breaks is cut there),
reading a definition's value or a proof the tool cuts; since F9 it has a definition with a proof inside it (F8's
form), whose value reading must be UNKNOWN, never KILLED. Here each definition has the RICH body (every operator of
the test package but the arms). The lines table (F9) is `LINES`: every operator whose replacement can span lines,
with fewer, the same or more lines than what it replaces, read by a check that compares the value and by one that
reads nothing, in both settings (the arms and the list and `++` operators the RICH body has on one line). The tool
runs every mutant of both (no --max-mutants cut). With --run the packages are built under a temporary directory and
the evidence written to evidence/sweep.json; without, the tables are read from that evidence (D4). It exits 1 when
a forms row that is no check, or that reads a proof, has a KILLED mutant, when a row the table expects to kill (or
to be UNKNOWN) has none, when a mutant is UNKNOWN outside a row expecting it or NOT RUN, or when a lines row breaks
`lines_problems`. The forms counts are mutant verdicts summed over the rows that read each definition (rows that
must survive share one definition per wrapping and setting).
"""
from __future__ import annotations

import argparse
import hashlib
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent / "evidence" / "sweep.json"
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "tools")]


def tool(table, root: Path, out: Path, jobs: int, tmp: str) -> tuple[dict, int]:
    done = subprocess.run([sys.executable, str(ROOT / "tools/trust_mutants.py"), "--root", str(root), "--base",
                           "HEAD~1", "--jobs", str(jobs), "--max-mutants", "100000", "--json", str(out)],
                          env={**table.os.environ, **table.PATH, "TMPDIR": tmp, "VE_LEAN_SHARE": "off"},
                          text=True, capture_output=True)
    print(done.stdout[-2000:], done.stderr[-2000:])
    return json.loads(out.read_text()), done.returncode


def run(jobs: int) -> None:
    import test_trust_mutants as table
    with tempfile.TemporaryDirectory(prefix="trustmut-sweep-") as tmp:
        rows = table.table_package(Path(tmp) / "package", Path(tmp), rich=True)
        data, code = tool(table, Path(tmp) / "package", Path(tmp) / "run.json", jobs, tmp)
        (Path(tmp) / "lines-dump").mkdir()
        lines = table.lines_package(Path(tmp) / "lines", Path(tmp) / "lines-dump")
        data["lines"], data["lines_exit"] = tool(table, Path(tmp) / "lines", Path(tmp) / "lines.json", jobs, tmp)
    data["rows"] = [{k: v for k, v in row.items() if k not in ("key", "text")} for row in rows]
    data["lines"] = {"seconds": data["lines"]["seconds"], "counts": data["lines"]["counts"], "rows": lines,
                     "mutants": data["lines"]["mutants"]}
    data["exit"] = code
    data["sources"] = sources()
    EVIDENCE.write_text(compact(data))


def sources() -> dict[str, str]:
    """The sha256 of the files the sweep ran: the tool, trust_map and the tables."""
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in ("tools/trust_mutants.py", "tools/trust_map.py", "tests/test_trust_mutants.py")}


KEYS = ("definition", "operator", "line", "before", "after", "status", "detail")


def compact(data: dict) -> str:
    """One mutant per line: [definition, operator, line, before, after, status, where Lean failed] (the lines table
    keeps 100 characters of the detail: its rule reads the UNKNOWN reason)."""
    data = {k: v for k, v in data.items() if k != "definitions"}
    forms = [[m[k] for k in KEYS[:-1]] + [m["detail"].split(": ")[0]] for m in data.pop("mutants")]
    lines = data.pop("lines")
    cut = [[m[k] for k in KEYS[:-1]] + [m["detail"][:100]] for m in lines.pop("mutants")]
    rows, line_rows = data.pop("rows"), lines.pop("rows")

    def each(items: list) -> str:
        return ",\n".join(json.dumps(x, ensure_ascii=False) for x in items)
    return (f'{json.dumps(data, ensure_ascii=False)[:-1]}, "rows": [\n{each(rows)}\n], "mutants": [\n{each(forms)}\n],'
            f' "lines": {json.dumps(lines, ensure_ascii=False)[:-1]}, "rows": [\n{each(line_rows)}\n], "mutants": [\n'
            f'{each(cut)}\n]}}}}\n')


SPACE = {"mutated": "Demo.M", "other": "Demo.O"}


def load(text: str | None = None) -> dict:
    """The saved sweep (or `text`, a copy git keeps), each mutant a dict (`KEYS`), the lines rows' targets tuples."""
    data = json.loads(EVIDENCE.read_text() if text is None else text)
    data["mutants"] = [dict(zip(KEYS, m)) for m in data["mutants"]]
    data["lines"]["mutants"] = [dict(zip(KEYS, m)) for m in data["lines"]["mutants"]]
    for row in data["lines"]["rows"]:
        row["targets"] = [tuple(t) for t in row["targets"]]
    return data


def survivors_of(data: dict) -> tuple[dict[str, list[dict]], set[str], set[str], Counter]:
    """The forms' mutants by definition; the definitions a row expecting KILLED reads, and those a row expecting
    UNKNOWN reads; and their survivors, (operator, before, after) -> count (`report`, and `claims.py`'s counts)."""
    by_def: dict[str, list[dict]] = {}
    for m in data["mutants"]:
        by_def.setdefault(m["definition"], []).append(m)
    unknown = {f"{SPACE[row['setting']]}.{row['d']}" for row in data["rows"] if row["expected"] == "UNKNOWN"}
    kills = {m["definition"] for row in data["rows"] if row["expected"] == "KILLED"
             for m in by_def[f"{SPACE[row['setting']]}.{row['d']}"]}
    survivors = Counter((m["operator"], m["before"], m["after"]) for m in data["mutants"]
                        if m["definition"] in kills | unknown and m["status"] == "SURVIVOR")
    return by_def, kills, unknown, survivors


def report() -> int:
    import test_trust_mutants as table
    data = load()
    space = SPACE
    by_def, kills, unknown, survivors = survivors_of(data)
    bad = [m for m in data["mutants"] if m["status"] == "NOT RUN"
           or m["status"] == "UNKNOWN" and m["definition"] not in unknown]
    print(f"Forms: {len(data['mutants'])} mutants of {len(by_def)} definitions, {len(data['rows'])} rows, "
          f"{data['seconds']} s at {data['jobs']} jobs: {data['counts']}")
    print("| Form | Class | Reading | Rows | KILLED | SURVIVOR | UNKNOWN | INVALID |")
    print("|---|---|---|---|---|---|---|---|")
    seen: dict[tuple, Counter] = {}
    rows: Counter = Counter()
    for row in data["rows"]:
        key = (row["form"], row["class"], row["reads"])
        rows[key] += 1
        statuses = Counter(m["status"] for m in by_def[f"{space[row['setting']]}.{row['d']}"])
        seen.setdefault(key, Counter()).update(statuses)
        if statuses["KILLED"] and (row["reads"] == "proof" or row["class"] != "check"):
            bad += [m for m in by_def[f"{space[row['setting']]}.{row['d']}"] if m["status"] == "KILLED"]
        if row["expected"] in ("KILLED", "UNKNOWN") and not statuses[row["expected"]]:
            bad.append({"row": row, "statuses": dict(statuses)})
    for (form, cls, reads), counts in seen.items():
        print(f"| {form} | {cls} | {reads} | {rows[form, cls, reads]} | {counts['KILLED']} | {counts['SURVIVOR']} | "
              f"{counts['UNKNOWN']} | {counts['INVALID']} |")
    print("Survivors of the definitions a check or a definition reads (operator: before -> after, count):")
    for (op, before, after), n in sorted(survivors.items()):
        print(f"  {op}: {before} -> {after} ({n})")
    lines = data["lines"]
    print(f"Lines: {len(lines['mutants'])} mutants, {len(lines['rows'])} rows, {lines['seconds']} s: "
          f"{lines['counts']}")
    print("| Shape | Targets (operator: lines) | Setting | Check | KILLED | SURVIVOR | UNKNOWN | INVALID |")
    print("|---|---|---|---|---|---|---|---|")
    for row in lines["rows"]:
        statuses = Counter(m["status"] for m in lines["mutants"] if m["definition"] == f"{row['space']}.{row['d']}")
        targets = ", ".join(f"{op}: {n}" for op, _, n in row["targets"])
        print(f"| {row['shape']} | {targets} | {row['setting']} | {'compares' if row['reads'] else 'reads nothing'} "
              f"| {statuses['KILLED']} | {statuses['SURVIVOR']} | {statuses['UNKNOWN']} | {statuses['INVALID']} |")
    survivors = Counter((m["operator"], " ".join(m["before"].split()), " ".join(m["after"].split()))
                        for row in lines["rows"] if row["reads"] for m in lines["mutants"]
                        if m["definition"] == f"{row['space']}.{row['d']}" and m["status"] == "SURVIVOR")
    print("Survivors of the definitions a comparing check reads (operator: before -> after, count):")
    for (op, before, after), n in sorted(survivors.items()):
        print(f"  {op}: {before} -> {after} ({n})")
    bad += table.lines_problems(lines["rows"], lines["mutants"])
    for b in bad:
        print("FAIL", b)
    return 1 if bad else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--jobs", type=int, default=16)
    args = parser.parse_args()
    if args.run:
        run(args.jobs)
    return report()


if __name__ == "__main__":
    sys.exit(main())
