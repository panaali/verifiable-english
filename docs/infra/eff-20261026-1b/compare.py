"""eff-20261026-1b's real-tree check, on saved evidence only (architecture decision D4): `python3
docs/infra/eff-20261026-1b/compare.py` exits 0 when, on df-1ad's HEAD, the built tool's default sweep gives the
mutants and verdicts eff-20261026-1 saved (cost/df-1ad-default.json, the merge base's tool), its `--classes all`
sweep gives the prototype's (cost/df-1ad-all.json), and the widened sweep's trusted mutants and verdicts are the
default sweep's. The HEAD, base, options and counts are pinned here, not read from the files checked."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SAVED = HERE.parent / "eff-20261026-1" / "cost"
HEAD, BASE = "b8f32f8f4f2f8cd76dee9774e5e786b44364fe95", "7855620f3e06be59bd94730ef404689d3a18e558"
RUNS = {"default": (["trusted"], 80), "all": (["all"], 114)}  # --classes as recorded, mutants
KEY = ("id", "file", "line", "definition", "operator", "before", "after", "raw_status")


def rows(data: dict, trusted_only: bool = False) -> list[tuple]:
    return [tuple(m[k] for k in KEY) for m in data["mutants"] if not trusted_only or m["trusted"] is True]


def main() -> int:
    problems = []
    built = {}
    for name, (classes, count) in RUNS.items():
        old = json.loads((SAVED / f"df-1ad-{name}.json").read_text())
        new = built[name] = json.loads((HERE / "cost" / f"df-1ad-{name}.json").read_text())
        for key, want in (("head", HEAD), ("base", BASE), ("max_mutants", 1000), ("jobs", 6), ("deep", False),
                          ("tests", []), ("classes", classes)):
            if new.get(key) != want:
                problems.append(f"{name}: {key} is {new.get(key)!r}, not {want!r}")
        if (old["head"], old["base"]) != (HEAD, BASE):
            problems.append(f"{name}: the saved sweep is not of {HEAD[:9]} over {BASE[:9]}")
        if not (len(old["mutants"]) == len(new["mutants"]) == count):
            problems.append(f"{name}: {len(old['mutants'])} saved and {len(new['mutants'])} new mutants, not {count}")
        if rows(old) != rows(new):
            problems.append(f"{name}: the mutants or verdicts differ from the saved sweep's")
        if new["counts"]["NOT RUN"] or any(m["raw_status"] == "NOT RUN" for m in new["mutants"]):
            problems.append(f"{name}: some mutants NOT RUN")
        if any(not {"trust_class", "trusted"} <= set(m) or not m["trust_class"] for m in new["mutants"]):
            problems.append(f"{name}: a mutant records no class")
    if not all(m["trusted"] for m in built["default"]["mutants"]):
        problems.append("default: a mutant of an untrusted declaration")
    strip = [r[1:] for r in rows(built["all"], True)]  # the ids follow the run order, which the wider plan changes
    if Counter(strip) != Counter(r[1:] for r in rows(built["default"])):
        problems.append("all: its trusted mutants and verdicts are not the default sweep's")
    print("\n".join(problems) or f"df-1ad {HEAD[:9]}: default {RUNS['default'][1]} and all {RUNS['all'][1]} mutants "
          f"equal the saved sweeps; all's {len(strip)} trusted ones equal the default's; times "
          f"{built['default']['seconds']} s and {built['all']['seconds']} s; 0 problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
