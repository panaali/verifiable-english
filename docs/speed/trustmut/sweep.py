#!/usr/bin/env python3
"""speed-trustmut review F7: the DRI's sweep over the truth table of tests/test_trust_mutants.py.

    uv run python docs/speed/trustmut/sweep.py [--run] [--jobs 16]

The table is every command form `classify` can see, bare, under `#guard_msgs in` and with its docstring too, in the
mutated module (its proofs cut up front) and in another (a proof the mutant breaks is cut there), reading a
definition's value or a proof the tool cuts. Here each definition has the RICH body (every operator of the test
package but the arms) and the tool runs every mutant (no --max-mutants cut). With --run the package is built under
a temporary directory and the evidence written to evidence/sweep.json; without, the table is read from that
evidence (D4). It exits 1 when a row that is no check, or that reads a proof, has a KILLED mutant, when a row the
table expects to kill has none, or when a mutant is UNKNOWN or NOT RUN. The table's counts are mutant verdicts summed
over the rows that read each definition (rows that must not kill share one definition per wrapping and setting).
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


def run(jobs: int) -> None:
    import test_trust_mutants as table
    with tempfile.TemporaryDirectory(prefix="trustmut-sweep-") as tmp:
        root = Path(tmp) / "package"
        rows = table.table_package(root, Path(tmp), rich=True)
        out = Path(tmp) / "run.json"
        done = subprocess.run([sys.executable, str(ROOT / "tools/trust_mutants.py"), "--root", str(root), "--base",
                               "HEAD~1", "--jobs", str(jobs), "--max-mutants", "100000", "--json", str(out)],
                              env={**table.os.environ, **table.PATH, "TMPDIR": tmp, "VE_LEAN_SHARE": "off"},
                              text=True, capture_output=True)
        print(done.stdout[-2000:], done.stderr[-2000:])
        data = json.loads(out.read_text())
    data["rows"] = [{k: v for k, v in row.items() if k not in ("key", "text")} for row in rows]
    data["exit"] = done.returncode
    data["sources"] = sources()
    EVIDENCE.write_text(compact(data))


def sources() -> dict[str, str]:
    """The sha256 of the files the sweep ran: the tool, trust_map and the table."""
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in ("tools/trust_mutants.py", "tools/trust_map.py", "tests/test_trust_mutants.py")}


def compact(data: dict) -> str:
    """One mutant per line: [definition, operator, line, before, after, status, where Lean failed]."""
    data = {k: v for k, v in data.items() if k != "definitions"}
    data["mutants"] = [[m["definition"], m["operator"], m["line"], m["before"], m["after"], m["status"],
                        m["detail"].split(": ")[0]] for m in data["mutants"]]
    rows = ",\n".join(json.dumps(row, ensure_ascii=False) for row in data.pop("rows"))
    mutants = ",\n".join(json.dumps(m, ensure_ascii=False) for m in data.pop("mutants"))
    return f'{json.dumps(data, ensure_ascii=False)[:-1]}, "rows": [\n{rows}\n], "mutants": [\n{mutants}\n]}}\n'


def report() -> int:
    data = json.loads(EVIDENCE.read_text())
    keys = ("definition", "operator", "line", "before", "after", "status", "detail")
    data["mutants"] = [dict(zip(keys, m)) for m in data["mutants"]]
    space = {"mutated": "Demo.M", "other": "Demo.O"}
    by_def: dict[str, list[dict]] = {}
    for m in data["mutants"]:
        by_def.setdefault(m["definition"], []).append(m)
    bad = [m for m in data["mutants"] if m["status"] in ("UNKNOWN", "NOT RUN")]
    print(f"{len(data['mutants'])} mutants of {len(by_def)} definitions, {len(data['rows'])} rows, "
          f"{data['seconds']} s at {data['jobs']} jobs: {data['counts']}")
    print("| Form | Class | Reading | Rows | KILLED | SURVIVOR | INVALID |")
    print("|---|---|---|---|---|---|---|")
    seen: dict[tuple, Counter] = {}
    rows: Counter = Counter()
    for row in data["rows"]:
        key = (row["form"], row["class"], row["reads"])
        rows[key] += 1
        statuses = Counter(m["status"] for m in by_def[f"{space[row['setting']]}.{row['d']}"])
        seen.setdefault(key, Counter()).update(statuses)
        if statuses["KILLED"] and (row["reads"] == "proof" or row["class"] != "check"):
            bad += [m for m in by_def[f"{space[row['setting']]}.{row['d']}"] if m["status"] == "KILLED"]
        if row["expected"] == "KILLED" and not statuses["KILLED"]:
            bad.append({"row": row, "statuses": dict(statuses)})
    for (form, cls, reads), counts in seen.items():
        print(f"| {form} | {cls} | {reads} | {rows[form, cls, reads]} | {counts['KILLED']} | {counts['SURVIVOR']} | "
              f"{counts['INVALID']} |")
    kills = {m["definition"] for row in data["rows"] if row["expected"] == "KILLED"
             for m in by_def[f"{space[row['setting']]}.{row['d']}"]}
    survivors = Counter((m["operator"], m["before"], m["after"]) for m in data["mutants"]
                        if m["definition"] in kills and m["status"] == "SURVIVOR")
    print("Survivors of the definitions a check reads (operator: before -> after, count):")
    for (op, before, after), n in sorted(survivors.items()):
        print(f"  {op}: {before} -> {after} ({n})")
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
