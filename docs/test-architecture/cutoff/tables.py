"""The report's tables, from the saved evidence only (REPORT.md holds them between generated markers).

  python3 docs/test-architecture/cutoff/tables.py --write | --check

Seconds are the recording run's per-unit seconds on the Mac runner (evidence/recording-map.json.gz):
scheduling metadata for comparing selections, never a correctness criterion.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
REPORT = HERE / "REPORT.md"


def seconds() -> dict[str, float]:
    with gzip.open(EVIDENCE / "recording-map.json.gz", "rt") as handle:
        return {unit: status["seconds"] for unit, status in json.load(handle)["status"].items()}


def cost(units: list[str], timing: dict[str, float]) -> str:
    return f"{len(units)} / {round(sum(timing.get(unit, 0) for unit in units))} s"


def seeds_table(timing: dict[str, float]) -> str:
    rows = json.loads((EVIDENCE / "seeds.json").read_text())["seeds"]
    lines = ["| Seed | File | Edit | Result | Caught by | Changed answers | Today | `modes` | `answers` (at least) |",
             "|---|---|---|---|---|---:|---|---|---|"]
    for row in rows:
        if row["status"] != "caught" and row["status"] != "not caught":
            lines.append(f"| {row['id']} | {row['file'].removeprefix('lean/')} | | {row['status']} | | | | | |")
            continue
        caught = ", ".join(sorted({test.split("::")[0].removeprefix("tests/") for test in row["caught_by"]})) or "none"
        inside = "" if row["status"] != "caught" else " (" + ", ".join(
            name for name in ("today", "modes", "answers") if row["caught_in"][name]) + ")"
        edit = (row["old"][:38] + "…") if len(row["old"]) > 40 else row["old"]
        edit = edit.replace("|", "\\|").replace("`", "'")
        lines.append(f"| {row['id']} | {row['file'].removeprefix('lean/')} | `{edit}` | {row['status']}{inside} | "
                     f"{caught} | {row['changed_cases']} | {cost(row['today'], timing)} | "
                     f"{cost(row['modes_selected'], timing)} | {cost(row['answers_selected'], timing)} |")
    caught = [row for row in rows if row["status"] == "caught"]
    lines.append("")
    lines.append(f"{len(caught)} of {len(rows)} seeds caught; every caught seed's catching test is in today's, the "
                 f"`modes` and the `answers` selection: "
                 f"{all(all(row['caught_in'].values()) for row in caught)}.")
    return "\n".join(lines)


def shadow_table(timing: dict[str, float]) -> str:
    rows = json.loads((EVIDENCE / "shadow.json").read_text())["rows"]
    lines = ["| Change | Kind | Paths | Full run on the Mac | Failures | Today | `modes` | `answers` | Misses (today / modes / answers) |",
             "|---|---|---:|---|---:|---|---|---|---|"]
    for row in rows:
        run = re.sub(r",? *[0-9]+ warnings?", "", row["full_run"] or "").strip("= ")
        lines.append(f"| {row['label']} | {row['kind']} | {len(row['paths'])} | {run} | {len(row['full_failures'])} | "
                     f"{cost(row['today'], timing)} | {cost(row['modes'], timing)} | {cost(row['answers'], timing)} | "
                     f"{len(row['today_misses'])} / {len(row['modes_misses'])} / {len(row['answers_misses'])} |")
    return "\n".join(lines)


TABLES = {"seeds": seeds_table, "shadow": shadow_table}


def render(text: str) -> str:
    timing = seconds()
    for name, make in TABLES.items():
        pattern = re.compile(rf"(<!-- table:{name} -->\n).*?(\n<!-- /table:{name} -->)", re.S)
        if not pattern.search(text):
            raise ValueError(f"REPORT.md has no table:{name} markers")
        text = pattern.sub(lambda match: match.group(1) + make(timing) + match.group(2), text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = REPORT.read_text()
    rendered = render(text)
    if args.write:
        REPORT.write_text(rendered)
        return 0
    if rendered != text:
        print("REPORT.md tables are stale: run tables.py --write")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
