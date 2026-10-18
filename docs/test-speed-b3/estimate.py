"""A retrospective ESTIMATE of B3's saving on fix rounds (not the activation evidence, which only shadow rows
written beside live full gates can give: tools/since_pass.py).

For 14 fixed pairs of consecutive fix-round commits (P, H) from the loop records, at most 5 first-parent steps
apart, it compares the selection for P..H (the rule, as if P had passed) with today's for merge-base..H, both by
tools/select_tests.py over B2's saved v7 coverage map with `assume_fresh` (the map treated as recorded at the
base, as docs/test-speed-b2/shadow.py does; an estimate, not a safe selection). Test time is the map's recorded
seconds per unit. Whether P's gate passed is not known: this measures the selection sizes only.

    uv run python docs/test-speed-b3/estimate.py --write    # evidence/estimate.json
    uv run python docs/test-speed-b3/estimate.py --check    # its totals and medians from its saved rows
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import select_tests  # noqa: E402
import test_map  # noqa: E402

MAP = ROOT / "docs/test-speed-b2/evidence/coverage-map.json.gz"
OUTPUT = Path(__file__).resolve().parent / "evidence/estimate.json"
# (loop, P = the commit the round before rechecked, H = the commit this round rechecked), from
# manage-agents/gate-records.jsonl on 2026-10-14: the 14 newest pairs with P an ancestor of H, 1 to 5 steps apart.
PAIRS = (
    ("lf-14b", "83d9478656fa024d5b427958ce7ff3308d11a0d4", "5253536de1670002a9d23ae0da64e2a9fbd802ce"),
    ("qa-q2b", "02f64efdacc40a244630c7bf4e7a0a8cc9218011", "f63522bef4ca24229fe3ec7da09cc29f200d2b31"),
    ("runner-portability", "41dea64a56c5005a7ba6d4613092c29369b8bc4c", "47a3a39bb9e89f6291db74cff6d7b8c3c96a7ea1"),
    ("runner-portability", "47a3a39bb9e89f6291db74cff6d7b8c3c96a7ea1", "ede39f762c4110c8e9f68a60e1060ec74c41f45b"),
    ("rd-9b", "b7cf02545f149f3940c8d31131de49f8f42b74af", "9e7f114e69cbcf82430acec5c486741925dfac67"),
    ("rd-9b", "9e7f114e69cbcf82430acec5c486741925dfac67", "fbb81599cb13e31938fca63b0f4b471f43611a1d"),
    ("lf-16e", "db5f419e1a9616198b91be94cc16ad65bd989307", "382fe5c6f2bade4f2d09491289bafc11796ddf0b"),
    ("lf-14d", "801808c1fc61c804108467d2a51a762b4eeeb47e", "505a09ab72b8a15ecd1a6430193a0724dfc0a7fa"),
    ("qa-q2c", "4d13c23db9eda82da0b6966696eac16b78686b81", "705b3c46fccf76b1b24932b51a5feeba2d21bedf"),
    ("rd-9-c140740", "3aba4dc100528bac96f9b0b80a1b3a66f884c60b", "0a8432de53997ba0b095f2f384d984b2b965cd5b"),
    ("lf-16e-c141121", "cb43ce7819144c803af65b150b498005f5a91a07", "cc880ffc47bb98c0611b2184e483be85f5028051"),
    ("rd-9-c141336", "cb2db7c696d2c15dc87b5f1906d5616b2d7696e4", "362b17c8ec66f94bd2d2a143257b23a93d17f9a3"),
    ("ts-B2", "0dd694dab33a5764701df57f8cc795de9a127fc5", "bed47b05894dfb95cb04e9ed1f5507005539ca2a"),
    ("arch-AR-4-c142031", "4d834a58e4c4c65defecd9780e9ab9e0b42f6572", "0fd93cc404cb40eb1522719999b8d0815b03118e"),
)


def git(*args: str) -> str:
    return subprocess.run(("git", *args), cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()


def todays_base(head: str) -> str:
    """The merge base today's command used at `head`: with main as it was when the branch merged (the first
    parent of the main commit that merged it), or with main now when it has not merged."""
    merged = git("rev-list", "--first-parent", "--ancestry-path", "--reverse", f"{head}..main").splitlines()
    main = f"{merged[0]}^1" if merged else "main"
    return git("merge-base", head, main)


def seconds(selected: list[str], status: dict) -> float:
    return round(sum(status.get(unit, {}).get("seconds", 0.0) for unit in selected), 1)


def plan(base: str, head: str, coverage: dict) -> dict:
    paths = git("diff", "--no-renames", "--name-only", f"{base}...{head}").splitlines()
    changes = select_tests.read_changes(paths, base=base, after=head)
    found = select_tests.select(changes=changes, base=coverage["commit"], coverage=coverage, assume_fresh=True)
    return {"paths": len(paths), "selected": sorted(found["selected"]), "full": found["full"],
            "full_reasons": found["full_reasons"]}


def write() -> dict:
    coverage = test_map.load(MAP)
    status = coverage["status"]
    total = round(sum(row.get("seconds", 0.0) for row in status.values()), 1)
    rows = []
    for loop, anchor, head in PAIRS:
        base = todays_base(head)
        rule, today = plan(anchor, head, coverage), plan(base, head, coverage)
        rows.append({"loop": loop, "pass": anchor, "head": head, "merge_base": base,
                     "steps": int(git("rev-list", "--count", "--first-parent", f"{anchor}..{head}")),
                     "rule": {**rule, "seconds": seconds(rule["selected"], status)},
                     "today": {**today, "seconds": seconds(today["selected"], status)}})
        print(f"{loop}: rule {len(rule['selected'])} units {rows[-1]['rule']['seconds']} s; today "
              f"{len(today['selected'])} units {rows[-1]['today']['seconds']} s", flush=True)
    return {"schema": 1, "method": "retrospective estimate: fixed fix-round pairs, B2 v7 map, assume_fresh",
            "map_sha256": hashlib.sha256(MAP.read_bytes()).hexdigest(), "map_commit": coverage["commit"],
            "suite_seconds": total, "rows": rows, "summary": summary(rows, total)}


def summary(rows: list[dict], total: float) -> dict:
    rule = [row["rule"]["seconds"] / total for row in rows]
    today = [row["today"]["seconds"] / total for row in rows]
    return {"pairs": len(rows), "rule_median_share": round(statistics.median(rule), 3),
            "today_median_share": round(statistics.median(today), 3),
            "rule_mean_share": round(statistics.mean(rule), 3), "today_mean_share": round(statistics.mean(today), 3),
            # Units the rule selects that today's selection does not: P..H can change code that merge-base..H
            # leaves as main has it (a round that undoes an earlier round's edit). Adding them is safe.
            "rule_units_outside_today": sum(len(set(row["rule"]["selected"]) - set(row["today"]["selected"]))
                                            for row in rows)}


def check() -> int:
    saved = json.loads(OUTPUT.read_text())
    if [(row["loop"], row["pass"], row["head"]) for row in saved["rows"]] != list(PAIRS):
        print("the saved rows are not the fixed pairs", file=sys.stderr)
        return 1
    if hashlib.sha256(MAP.read_bytes()).hexdigest() != saved["map_sha256"]:
        print("the saved map digest differs", file=sys.stderr)
        return 1
    status = test_map.load(MAP)["status"]
    for row in saved["rows"]:
        for side in ("rule", "today"):
            if seconds(row[side]["selected"], status) != row[side]["seconds"]:
                print(f"{row['loop']}: {side} seconds differ from the map's", file=sys.stderr)
                return 1
    if summary(saved["rows"], saved["suite_seconds"]) != saved["summary"]:
        print("the saved summary differs from its rows", file=sys.stderr)
        return 1
    print(json.dumps(saved["summary"]))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    if parser.parse_args().write:
        OUTPUT.write_text(json.dumps(write(), indent=1) + "\n")
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
