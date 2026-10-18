#!/usr/bin/env python3
"""Replay test selection on the merges to main since 2026-10-14 and on the cutoff report's ten shadow
changes, to find what still selects every unit (tarch-manifest-ops, test-architecture draft 2 rank 4 item 5).

Each row is the plan `tools/select_tests.py` makes for one change, run by the selector of a checkout
(`--selector`, default this one) in private caches (no shared map, no Lean build record, so no binary cutoff):

* `merges`: the 54 first-parent merges of main from 2026-10-14 00:00Z to `de9cfa84f` (this branch's base),
  each against its first parent, with the cutoff batch's recorded map (`../cutoff/evidence/recording-map.json.gz`,
  main `dae12d5ff`'s units recorded on ve-mac-1) taken as recorded at the parent (`--assume-fresh`): the
  "map after every merge" of rank 4, the same for every row. With `--drift` (label `before-drift`) the same
  map runs the selector's own drift check against each parent instead: the plan a real `--run` makes when
  that map is the nearest one, its uncertain units answered by the static graph.
* `shadow`: the ten changes of `../cutoff/changes.json`, each against its base, with the map that table
  pinned (`r1_map`, by name and SHA-256, in the shared cache `~/.cache/ve-testmap`) and its drift check.

Each plan is computed twice: `plan`, the plan a print or the gate's selection makes (`select_tests.select`),
and `r1`, the plan of a feedback `--run` (`answer_cutoff.R1_RULE`, ts-B2's `modes` rule). A row keeps the
selected units, the full-suite reasons, the units selected only through the checker pins
(`lean/checkers.lock`), how many units the other reasons still select without the manifest's reasons, without
the pins' and without both (`is_manifest`, `is_pin`), and the three reasons that select the most units. Seconds are the recorded Mac seconds of the selected units in the recorded map.

    python3 docs/test-architecture/manifest-ops/measure.py --label before --selector /tmp/main --write
    python3 docs/test-architecture/manifest-ops/measure.py --label after --write   # after a narrowing
    python3 docs/test-architecture/manifest-ops/measure.py --label before-drift --drift --write
    python3 docs/test-architecture/manifest-ops/measure.py --check     # the report's tables, every saved label recomputed
    python3 docs/test-architecture/manifest-ops/measure.py --check --only a4676c0b7,lf-14a   # those rows only
    python3 docs/test-architecture/manifest-ops/measure.py --table     # the report's tables, from the saved rows

A plan depends on the tree the selector runs in (its units, its static graph), so each label saves the
commit it ran at (`--write` needs a clean checkout) and `--check` recomputes it in a temporary worktree of
that commit, failing on any difference in a selected set or a reason: batch evidence (decision D4), checked
at the batch gate and by the merge train, not a permanent test.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVIDENCE = HERE / "evidence/replay.json.gz"
REPORT = HERE / "REPORT.md"
# The report's generated tables sit between these two lines, exactly as `--table` prints them.
BEGIN, END = "<!-- measure.py --table: begin -->", "<!-- measure.py --table: end -->"
RECORDED = HERE.parent / "cutoff/evidence/recording-map.json.gz"
CHANGES = HERE.parent / "cutoff/changes.json"
PINS = "lean/checkers.lock"
MANIFEST = "ve/assurance-manifest.json"
PIN_REASON = f"reads {PINS}"
MANIFEST_REASON = f"{MANIFEST}: no safe operation map"
# git log --first-parent main --since=2026-10-14T00:00:00Z, up to de9cfa84f, oldest first.
MERGES = ("dccd9cf5a", "4667e8de6", "8594f1d05", "9f40783b8", "f187e4e9a", "4ce477e18", "b96f04a5a",
          "4ea2ac47c", "f75082449", "b98d87947", "1cbd5ed1e", "16a02693a", "a650eeb63", "aaff77634",
          "c4fdd804a", "91858c032", "2a4fbf708", "dae12d5ff", "8cbb3049f", "3160fb800", "21029b86e",
          "c53117326", "bf6c03baf", "1cf82542d", "99f67a7a9", "ee4ae48ad", "d7ea7228b", "8bc65a907",
          "f59dde41e", "171faae80", "2578fd9ad", "5759be852", "f3046f7dc", "85b20fcba", "bc1936dd5",
          "3c6646151", "f811fa69c", "a747a9cf7", "4e2c73dec", "8a5b701b4", "de309d61c", "fb0590a63",
          "f130b8c07", "b5248038e", "bfa8c41f3", "109c7de1d", "2d4b93206", "8dc29ba68", "a4676c0b7",
          "ffb3155a5", "c4d7ea565", "05b85b631", "e7f6968d4", "de9cfa84f")

# Runs in the selector's checkout: one change in, its two plans out.
PLAN = r"""
import contextlib, io, json, sys
sys.path.insert(0, "tools")
import answer_cutoff, select_tests, test_map
job = json.loads(sys.argv[1])
paths = select_tests.git_lines("diff", "--no-renames", "--name-only", job["base"], job["head"])
def coverage():
    return select_tests.Coverage(test_map.load(job["map"]), None)
out = {"paths": paths}
for name, rule in (("plan", "off"), ("r1", answer_cutoff.R1_RULE)):
    with contextlib.redirect_stderr(io.StringIO()):
        plan = answer_cutoff.select(rule, paths, base=job["base"], after=job["head"], coverage=coverage(),
                                    assume_fresh=job["fresh"])
    out[name] = {"selected": plan["selected"], "full": plan["full"], "full_reasons": plan["full_reasons"],
                 "reasons": plan["reasons"], "uncertain": plan["map"]["uncertain_units"]}
print(json.dumps(out))
"""


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def shadow_jobs() -> list[dict]:
    cache = Path(os.environ.get("VE_SHADOW_MAPS") or Path.home() / ".cache/ve-testmap")
    jobs = []
    for change in json.loads(CHANGES.read_text()):
        path = cache / change["r1_map"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != change["r1_map_sha256"]:
            raise SystemExit(f"{path}: not the map the shadow table pinned")
        jobs.append({"label": change["label"], "base": change["base"], "head": change["head"],
                     "map": str(path), "fresh": False})
    return jobs


def merge_jobs(drift: bool) -> list[dict]:
    return [{"label": merge, "base": f"{merge}^", "head": merge, "map": str(RECORDED), "fresh": not drift}
            for merge in MERGES]


def weights() -> dict[str, float]:
    data = json.loads(gzip.decompress(RECORDED.read_bytes()))
    return {unit: float(status["seconds"]) for unit, status in data["status"].items()}


def is_pin(reason: str) -> bool:
    """A reason the pin file alone gives: its readers, the units that name it, its directory's listers."""
    return reason.split(" (", 1)[0] in (PIN_REASON, f"names {PINS}", f"lists the directory of {PINS}")


def is_manifest(reason: str) -> bool:
    """A reason `select_tests.manifest_impact` / `manifest_change` gives (the contract test included)."""
    return reason in ("manifest contract", "reads the whole manifest", "unmapped manifest reader") or \
        reason.startswith(("reads manifest operation ", "registers manifest operation ", "registers an entry of ",
                           "reads the whole manifest, shared field "))


def summarise(plan: dict, seconds: dict[str, float]) -> dict:
    reasons = plan["reasons"]
    def without(drop) -> int:
        return sum(1 for why in reasons.values() if not all(drop(reason) for reason in why))
    counts: dict[str, int] = {}
    for why in reasons.values():
        for reason in why:
            counts[reason] = counts.get(reason, 0) + 1
    pins_only = sorted(unit for unit, why in reasons.items() if all(map(is_pin, why)))
    return {"selected": plan["selected"], "units": len(plan["selected"]), "full": plan["full"],
            "full_reasons": plan["full_reasons"],
            "seconds": round(sum(seconds.get(unit, 0.0) for unit in plan["selected"]), 1),
            # Without the full-suite trigger, what the other paths select; and the pins' own share of it.
            "without_full": len(reasons), "pins_only": pins_only,
            # What the other paths select without the manifest's reasons, without the pins', and without both.
            "without_manifest": without(is_manifest), "without_pins": without(is_pin),
            "without_both": without(lambda reason: is_manifest(reason) or is_pin(reason)),
            # The three reasons that select the most units, the plan's reason lines.
            "top_reasons": [[reason, count] for reason, count in
                            sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:3]],
            "manifest": MANIFEST_REASON in plan["full_reasons"]}


def because(row: dict, total: int) -> list[str]:
    """Which of the manifest and the pins a plan that selects everything needs to select everything."""
    found = []
    if row["manifest"]:
        found.append("manifest (no safe map)")
    if not row["full"] and row["units"] == total:
        if row["without_manifest"] < total:
            found.append(f"manifest readers ({total - row['without_manifest']})")
        if row["without_pins"] < total:
            found.append(f"pin readers ({total - row['without_pins']})")
        if not found and row["without_both"] < total:
            found.append(f"manifest and pin readers together ({total - row['without_both']})")
    return found


def replay(selector: Path, drift: bool = False, only: set[str] | None = None) -> dict[str, dict[str, dict]]:
    seconds = weights()
    found: dict[str, dict[str, dict]] = {"merges": {}, "shadow": {}}
    with tempfile.TemporaryDirectory(prefix="ve-manifest-ops-") as directory:
        env = {**os.environ, "XDG_CACHE_HOME": f"{directory}/xdg", "VE_TESTMAP_CACHE": f"{directory}/no-maps",
               "VE_LEAN_BUILDS": f"{directory}/no-builds"}
        env.pop("VE_TESTMAP", None)
        for table, jobs in (("merges", merge_jobs(drift)), ("shadow", shadow_jobs())):
            for job in jobs:
                if only is not None and job["label"] not in only:
                    continue
                result = subprocess.run([sys.executable, "-c", PLAN, json.dumps(job)], cwd=selector, env=env,
                                        capture_output=True, text=True)
                if result.returncode:
                    raise SystemExit(f"{job['label']}: {result.stderr[-2000:]}")
                data = json.loads(result.stdout.splitlines()[-1])
                found[table][job["label"]] = {"paths": len(data["paths"]),
                                              **{name: summarise(data[name], seconds) for name in ("plan", "r1")}}
                row = found[table][job["label"]]["plan"]
                print(f"{table} {job['label']}: {row['units']} units{' FULL ' + str(row['full_reasons']) if row['full'] else ''}",
                      flush=True)
    return found


def load() -> dict:
    return json.loads(gzip.decompress(EVIDENCE.read_bytes())) if EVIDENCE.exists() else {}


def average(rows: dict[str, dict], column: str, key: str) -> float:
    return round(sum(row[column][key] for row in rows.values()) / len(rows), 1)


def table(saved: dict) -> str:
    """The report's tables, from the saved rows: per measured label, the plans that select every unit;
    then the averages of every label."""
    out = []
    for measured in (label for label in saved if label.startswith("before")):
        rows_of = saved[measured]["rows"]
        total = max(row["plan"]["units"] for rows in rows_of.values() for row in rows.values())
        for name, labels in (("merges", MERGES), ("shadow", list(rows_of["shadow"]))):
            if name == "shadow" and measured != "before":
                continue  # the shadow rows run the drift check in every label
            out.append(f"**{measured}, {name}**")
            out.append("")
            out.append(f"| {'Merge' if name == 'merges' else 'Change'} | Subject | Paths | Units | Full-suite reasons | "
                       "Top reasons (units) | Without manifest / pins / both | Because of |")
            out.append("|---|---|---:|---:|---|---|---|---|")
            everything = caused = 0
            for label in labels:
                row = rows_of[name][label]
                plan = row["plan"]
                if plan["units"] != total:
                    continue
                everything += 1
                cause = because(plan, total)
                caused += bool(cause)
                subject = (git("log", "-1", "--format=%s", label).removeprefix("Merge ").split(" (", 1)[0]
                           if name == "merges" else label)
                top = "; ".join(f"{reason} ({count})" for reason, count in plan["top_reasons"])
                out.append(f"| `{label}` | {subject} | {row['paths']} | {plan['units']} | "
                           f"{'; '.join(plan['full_reasons']) or '(none)'} | {top} | "
                           f"{plan['without_manifest']} / {plan['without_pins']} / {plan['without_both']} | "
                           f"{'; '.join(cause) or 'neither'} |")
            out.append("")
            out.append(f"{everything} of {len(labels)} plans select every unit ({total}); "
                       f"{caused} of them because of the manifest or the pins.")
            out.append("")
    labels = sorted(saved, key=lambda label: (not label.startswith("before"), label))
    out.append("Averages (minutes: the recorded Mac seconds of the selected units, summed, / 60):")
    out.append("")
    out.append("| Changes | Rule | " + " | ".join(f"{label}: units / minutes / full" for label in labels) + " |")
    out.append("|---|---|" + "---|" * len(labels))
    for name in ("merges", "shadow"):
        for column in ("plan", "r1"):
            cells = []
            for label in labels:
                rows = saved[label]["rows"][name]
                cells.append(f"{average(rows, column, 'units')} / {round(average(rows, column, 'seconds') / 60, 1)} / "
                             f"{sum(row[column]['full'] for row in rows.values())}")
            out.append(f"| {name} ({len(saved[labels[0]]['rows'][name])}) | {column} | " + " | ".join(cells) + " |")
    out.append("")
    out.append(f"The merges that edit `{MANIFEST}` or `{PINS}` (from the fixed merge commits), with the digests each "
               "adds to (+) or drops from (-) each pinned checker:")
    out.append("")
    out.append("| Merge | Manifest | Pins |")
    out.append("|---|---|---|")
    edits = {MANIFEST: 0, PINS: 0}
    for merge in MERGES:
        changed = git("diff", "--no-renames", "--name-only", f"{merge}^", merge, "--", MANIFEST, PINS).split()
        if not changed:
            continue
        edits.update({path: edits[path] + 1 for path in changed})
        pins = ""
        if PINS in changed:
            old, new = (json.loads(git("show", f"{rev}:{PINS}")) for rev in (f"{merge}^", merge))
            pins = ", ".join(f"{name} +{len(set(new.get(name, [])) - set(old.get(name, [])))}"
                             f" -{len(set(old.get(name, [])) - set(new.get(name, [])))}"
                             for name in sorted(old.keys() | new.keys())
                             if set(old.get(name, [])) != set(new.get(name, [])))
        out.append(f"| `{merge}` | {'edited' if MANIFEST in changed else ''} | {pins} |")
    out.append("")
    out.append(f"{edits[MANIFEST]} merges edit the manifest, {edits[PINS]} the pins.")
    out.append("")
    out.append("Upper bound of any narrowing of the manifest and pin rules: the units only their reasons select "
               "(plans without a full-suite reason), as if every one were dropped:")
    out.append("")
    out.append("| Label | Changes | Manifest only | Pins only | Either | Plans with any | Per plan |")
    out.append("|---|---|---:|---:|---:|---:|---:|")
    for label in labels:
        for name, rows in saved[label]["rows"].items():
            plans = [row["plan"] for row in rows.values() if not row["plan"]["full"]]
            gain = [plan["units"] - plan["without_both"] for plan in plans]
            out.append(f"| {label} | {name} ({len(rows)}) | "
                       f"{sum(plan['units'] - plan['without_manifest'] for plan in plans)} | "
                       f"{sum(plan['units'] - plan['without_pins'] for plan in plans)} | {sum(gain)} | "
                       f"{sum(1 for units in gain if units)} | {round(sum(gain) / len(rows), 1)} |")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selector", type=Path, default=ROOT, help="the checkout whose selector runs")
    parser.add_argument("--label", default="after", help="the name the rows are saved under")
    parser.add_argument("--drift", action="store_true",
                        help="merges: run the selector's drift check against the map's commit (no --assume-fresh)")
    parser.add_argument("--write", action="store_true", help="save the rows in evidence/replay.json.gz")
    parser.add_argument("--check", action="store_true", help="recompute every saved label")
    parser.add_argument("--table", action="store_true", help="print the report's tables")
    parser.add_argument("--only", help="--check: recompute only these comma-separated rows (a quick check)")
    args = parser.parse_args()
    saved = load()
    if args.table:
        print(table(saved))
        return 0
    if args.check:
        text = REPORT.read_text()
        if BEGIN not in text or END not in text or \
                text.split(BEGIN, 1)[1].split(END, 1)[0].strip() != table(saved).strip():
            print(f"{REPORT.name}: the tables between the markers are not what --table prints from the saved rows")
            return 1
        only = set(args.only.split(",")) if args.only else None
        differ = []
        for label, entry in saved.items():
            with tempfile.TemporaryDirectory(prefix="ve-manifest-ops-check-") as directory:
                tree = Path(directory) / "tree"
                git("worktree", "add", "--detach", str(tree), entry["commit"])
                try:
                    found = replay(tree, entry.get("drift", False), only)
                finally:
                    subprocess.run(["git", "worktree", "remove", "--force", str(tree)], cwd=ROOT, capture_output=True)
            differ += [f"{label} {name} {key}" for name, rows in entry["rows"].items() for key, row in rows.items()
                       if (only is None or key in only) and found[name].get(key) != row]
        print(f"replayed {len(saved)} labels: " + (f"{len(differ)} rows differ: {differ}" if differ
                                                    else "every row as saved"))
        return 1 if differ else 0
    selector = args.selector.resolve()
    if args.write and git("status", "--porcelain", "--untracked-files=no", cwd=selector):
        parser.error(f"{selector} has uncommitted changes: the saved commit would not be the tree replayed")
    found = replay(selector, args.drift)
    if args.write:
        saved[args.label] = {"commit": git("rev-parse", "HEAD", cwd=selector), "rows": found,
                             **({"drift": True} if args.drift else {})}
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_bytes(gzip.compress((json.dumps(saved, indent=1, sort_keys=True) + "\n").encode(), mtime=0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
