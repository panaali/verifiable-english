"""Write docs/trust-baseline.json in the AR-4 format from the base commit's file (run once by the batch).

    uv run python docs/arch/AR-4/migrate_baseline.py BASE

The budget is the base's measured K, S and untied [V] lines (`tools/trust_map.py`, the base's committed
`lean/` and side table): the starting budget of DRI decision D3. The allowances are the base file's
`history` and `signed` entries (`trust_map.from_history`: the duplicated entry once), each with the first
commit of BASE's history whose baseline recorded it. Saves evidence/migration.json beside this script.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import trust_map  # noqa: E402

FILE = "docs/trust-baseline.json"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def needle(change: str) -> str:
    """A prefix of the entry's text spelled the same in every JSON encoding of the file."""
    out = ""
    for char in change:
        if not char.isascii() or char in '"\\':
            break
        out += char
    return out[:80]


def first_recorded(base: str, change: str) -> str:
    # A merge that resolved the file can be the first to record an entry: its diff against the first parent counts.
    commits = git("log", "--format=%H", "--reverse", "--diff-merges=first-parent", "-S", needle(change), base,
                  "--", FILE).split()
    if not commits:
        raise SystemExit(f"no commit of {base} records {change[:60]!r}")
    return commits[0]


def main(base: str) -> int:
    base = git("rev-parse", f"{base}^{{commit}}").strip()
    old = json.loads(git("show", f"{base}:{FILE}"))
    files, problems, _ = trust_map.measure_rev(base, ROOT)
    if problems:
        raise SystemExit("\n".join(problems))
    measured = trust_map.budget(trust_map.totals(files))
    entries = [*old.get("history", []), *old.get("signed", [])]
    allowances = [{**a, "commit": first_recorded(base, a["reason"])} for a in trust_map.from_history(old)]
    trust_map.write_baseline(ROOT / FILE, measured, allowances)
    evidence = {
        "base": base,
        "recorded_budget": old["budget"],
        "measured_budget": measured,
        "old_lines": len(git("show", f"{base}:{FILE}").splitlines()),
        "new_lines": len((ROOT / FILE).read_text().splitlines()),
        "old_keys": list(old),
        "history_entries": len(entries),
        "distinct_entries": len({json.dumps({k: e.get(k) for k in ("change", "allow", "signed")}, sort_keys=True)
                                 for e in entries}),
        "allowances": len(allowances),
        "signed_allowances": sum(a["signature"] != trust_map.UNSIGNED for a in allowances),
        "per_file_modules": len(old["files"]),
        "section11_rows": len(old["section11"]),
    }
    out = Path(__file__).parent / "evidence/migration.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(evidence, indent=1) + "\n")
    print(json.dumps(evidence, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
