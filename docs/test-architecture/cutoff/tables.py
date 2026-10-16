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
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
EVIDENCE = HERE / "evidence"
REPORT = HERE / "REPORT.md"


def seconds() -> dict[str, float]:
    with gzip.open(EVIDENCE / "recording-map.json.gz", "rt") as handle:
        return {unit: status["seconds"] for unit, status in json.load(handle)["status"].items()}


def cost(units: list[str], timing: dict[str, float]) -> str:
    return f"{len(units)} / {round(sum(timing.get(unit, 0) for unit in units))} s"


def seeds_table(timing: dict[str, float]) -> str:
    import seeds
    rows = json.loads((EVIDENCE / "seeds.json").read_text())["seeds"]
    lines = ["| Seed | File | Edit | Outcome | Caught through the service by | Changed answers | Today | `modes` | "
             "`answers` (at least) |", "|---|---|---|---|---|---:|---|---|---|"]
    for row in rows:
        found = seeds.outcome(row)
        edit = (row["old"][:38] + "…") if len(row["old"]) > 40 else row["old"]
        edit = edit.replace("|", "\\|").replace("`", "'")
        if found == seeds.UNBUILT:
            lines.append(f"| {row['id']} | {row['file'].removeprefix('lean/')} | `{edit}` | {found} | | | | | |")
            continue
        caught = ""
        if found == seeds.CAUGHT:
            kept = seeds.kept_by(row)
            found += " (kept by " + ", ".join(name for name in ("today", "modes", "answers") if kept[name]) + ")"
            caught = ", ".join(sorted({test.split("::")[0].removeprefix("tests/")
                                       for test in row["verified"]["through_service"]}))
        lines.append(f"| {row['id']} | {row['file'].removeprefix('lean/')} | `{edit}` | {found} | {caught} | "
                     f"{row['changed_cases']} | {cost(row['today'], timing)} | {cost(row['modes_selected'], timing)} | "
                     f"{cost(row['answers_selected'], timing)} |")
    counts: dict[str, int] = {}
    for row in rows:
        counts[seeds.outcome(row)] = counts.get(seeds.outcome(row), 0) + 1
    lines.append("")
    lines.append(f"{len(rows)} seeds: " + "; ".join(f"{name} {count}" for name, count in counts.items()) + ".")
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


def recording_table(timing: dict[str, float]) -> str:
    data = json.loads((EVIDENCE / "recording.json").read_text())
    modes = ", ".join(f"{mode} {count:,}" for mode, count in list(data["cases_by_mode"].items())[:8])
    pins = ", ".join(f"{kind.replace(',', ' and ')}: {count}" for kind, count in data["pin_reads"].items())
    lines = ["| Measure | Value |", "|---|---|",
             f"| Commit recorded | `{data['commit'][:10]}` (main `dae12d5ff` and this batch's tools) |",
             f"| Units / `ve_service` users | {data['units']} / {data['service_users']} |",
             f"| Distinct cases recorded | {data['distinct_cases']:,} |",
             f"| Most cases, by mode | {modes} |",
             f"| Pin reads by unit (`lean/checkers.lock`) | {pins} |",
             f"| Units not recorded (failed or opaque) | {', '.join(unit.removeprefix('tests/') for unit in data['not_recorded'])} |",
             f"| Unknown units at the recording's own commit | {len(data['unknown'])}, {data['unknown_seconds']:,} s of "
             f"{data['service_user_seconds']:,} s of service users' recorded time |",
             f"| Mac job (record, replay, emit) | {data['job_seconds']:,} s |"]
    reasons: dict[str, int] = {}
    for reason in data["unknown"].values():
        key = (reason.split(",")[0] if reason.startswith("a request to another") else
               "property tests (hypothesis)" if reason.endswith("uses hypothesis") else reason)
        reasons[key] = reasons.get(key, 0) + 1
    lines.append("")
    lines.append("Why units are unknown there: " + "; ".join(f"{reason} ({count})" for reason, count in
                                                             sorted(reasons.items(), key=lambda item: -item[1])) + ".")
    return "\n".join(lines)


def costs_table(timing: dict[str, float]) -> str:
    data = json.loads((EVIDENCE / "costs.json").read_text())
    replays = data["replays_format_4"].values()
    seconds = sorted(row["job_seconds"] for row in replays)
    setups = sorted(row["runner_setup_seconds"] for row in replays if row["runner_setup_seconds"])
    lines = [f"Replay of all recorded cases on one build (format 4, 6 service processes, ve-mac-1): "
             f"{len(seconds)} builds, {seconds[0]:.0f}-{seconds[-1]:.0f} s, median {seconds[len(seconds) // 2]:.0f} s; the "
             f"runner's Lean build of each tree before it: {setups[0]}-{setups[-1]} s.", "",
             "| S01's selection | Test files | Mac pytest, 6 workers | Result |", "|---|---:|---:|---|"]
    for name, row in data["timing_S01"].items():
        lines.append(f"| {name} | {row['files']} | {row['pytest_seconds']:.0f} s | {row['summary']} |")
    return "\n".join(lines)


def mutants_table(timing: dict[str, float]) -> str:
    rows = json.loads((EVIDENCE / "mutants.json").read_text())["mutants"]
    lines = ["| Bug | File | Seeded fault | Failing test |", "|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['id']} | {row['file']} | {row['fault']} | `{row['test'].split('::')[-1]}` |")
    return "\n".join(lines)


TABLES = {"seeds": seeds_table, "shadow": shadow_table, "recording": recording_table, "costs": costs_table,
          "mutants": mutants_table}


def render(text: str) -> str:
    timing = seconds()
    for name, make in TABLES.items():
        pattern = re.compile(rf"(<!-- table:{name} -->\n)(?:.*?\n)?(<!-- /table:{name} -->)", re.S)
        if not pattern.search(text):
            raise ValueError(f"REPORT.md has no table:{name} markers")
        text = pattern.sub(lambda match: match.group(1) + make(timing) + "\n" + match.group(2), text)
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
