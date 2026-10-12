"""Render the AR-9 outcome block solely from saved evidence (`evidence/*.json`)."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
TARGET_LINES = 700
SPLITS = {"ve/assist/recovery.py": ("recovery", "recovery_journal", "recovery_replay", "recovery_commands"),
          "ve/assist/session.py": ("session", "session_state", "session_proposals", "session_views")}


def load(name: str):
    path = EVIDENCE / name
    return json.loads(path.read_text()) if path.exists() else None


def metrics() -> str:
    split, mutants = load("split.json"), load("mutants.json")
    selected = load("selected.json")
    gate, scope = load("gate.json"), load("scope.json")
    base, head = split["files"]["base"], split["files"]["head"]
    lines = [f"- Measured: base `{split['base'][:8]}`, head `{split['head'][:8]}` "
             f"({'dirty' if split['dirty'] else 'clean'} `ve/`)."]
    for old, parts in SPLITS.items():
        rows = [f"`{part}.py` {head[f've/assist/{part}.py']['lines']:,}" for part in parts]
        lines.append(f"- `{old}` {base[old]['lines']:,} lines -> " + ", ".join(rows) + ".")
    assist = {path: row for path, row in head.items() if path.startswith("ve/assist/")}
    largest = max(assist, key=lambda path: assist[path]["lines"])
    over = sorted(path for path, row in assist.items() if row["lines"] > TARGET_LINES)
    lines.append(f"- Largest assist file: `{largest}`, {assist[largest]['lines']:,} lines; "
                 f"files over {TARGET_LINES}: {len(over)}" + (f" ({', '.join(over)})" if over else "") + ".")
    rows = split["definitions"]
    changed = [row["name"] for row in rows if not row["identical"]]
    lines.append(f"- Base definitions syntax-identical at head: {sum(r['identical'] for r in rows)}/{len(rows)}; "
                 f"identical once seam calls are read as the module names: "
                 f"{sum(r['identical_up_to_seams'] for r in rows)}/{len(rows)}; "
                 f"through a seam: {len(changed)} (" + ", ".join(f"`{n}`" for n in changed) + ").")
    missing = sum(len(names) for names in split["missing_names"].values())
    lines.append(f"- Names the two modules defined that they no longer provide: {missing}.")
    lines.append(f"- Function-level imports in `ve/assist/`: {sum(r['function_imports'] for r in base.values())} "
                 f"before, {sum(r['function_imports'] for r in assist.values())} after.")
    caught = [m for m in mutants["mutants"] if m["runs"] and all(r["exit_code"] != 0 for r in m["runs"])]
    runs = sum(len(m["runs"]) for m in mutants["mutants"])
    restored = mutants["restored"]
    lines.append(f"- Seeded faults: {len(caught)}/{len(mutants['mutants'])} caught by every named test "
                 f"({runs} failing runs); after restoring, "
                 f"{sum(r['exit_code'] == 0 for r in restored)}/{len(restored)} runs pass.")
    relay, relay_mutants = load("relay-gate.json"), load("relay-mutants.json")
    if relay is not None:
        totals = relay["totals"]
        lines.append(f"- Relay mutation gate (picked readings-route fix): {len(relay['routes'])} routes, "
                     f"{totals['mutants']:,} mutants, {len(relay['failures'])} failures.")
    if relay_mutants is not None:
        rows = relay_mutants["mutants"]
        caught = [m for m in rows if m["runs"] and all(r["exit_code"] != 0 for r in m["runs"])]
        languages = sorted({m["language"] for m in rows})
        restored = relay_mutants["restored"]
        lines.append(f"- Relay-fix seeded faults ({', '.join(languages)}): {len(caught)}/{len(rows)} caught by "
                     f"every named test; after restoring, "
                     f"{sum(r['exit_code'] == 0 for r in restored)}/{len(restored)} runs pass.")
    if selected is not None:
        lines.append(f"- Selected test units at `{selected['head'][:8]}`: "
                     f"{sum(row['exit'] == 0 for row in selected['units'])}/{selected['unit_count']} passed.")
    if scope is None or gate is None:
        lines.append("- Full gate: not saved yet (it runs on the final code commit; its result is saved after it).")
    else:
        counts = gate["counts"]
        lines.append(f"- Saved scope: `{scope['base'][:8]}..{scope['head'][:8]} --no-merges`, "
                     f"{len(scope['commits'])} commit(s): "
                     + ", ".join(f"`{row['hash'][:8]}`" for row in scope["commits"]) + ".")
        lines.append(f"- Full gate at `{gate['commit_sha'][:8]}`: {gate['status']}; {counts['passed']:,} passed, "
                     f"{counts['skipped']} skipped, {counts['failed']} failed; "
                     f"{counts['rust_passed']} Rust tests passed.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(metrics())
