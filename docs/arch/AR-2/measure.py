#!/usr/bin/env python3
"""AR-2's measured outcome, written to docs/arch/AR-2/evidence/freeze.json.

    python3 docs/arch/AR-2/measure.py BASE [HEAD]

Reads the frozen inventory, the question lock and the trust-class table at BASE (the batch's merge base with main)
and HEAD from git: the inventory's lines and files before and after, each file now frozen with its reason (K
declarations or a ve.core@0.1 decoder), the module hashes of the question lock before and after, and, over the
non-merge commits of BASE since 2026-09-26 that edit a `lean/**/*.lean` source (the plan's window, 2.5), how many
edited the inventory and how many touched a file now frozen: the share of Lean-source commits that would have
edited the short list, against the share that edited the full one.
"""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = Path(__file__).resolve().parent / "evidence/freeze.json"
INVENTORY = "lean/VE/Route/frozen-sources.sha256"
LOCK = "ve/question/LOCK.json"
TABLE = "tools/trust-classes.json"
SINCE = "2026-09-26"


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def listed(text: str) -> list[str]:
    return sorted(line.split()[1] for line in text.splitlines() if line.strip() and not line.startswith("#"))


def main(base: str, head: str = "HEAD") -> dict:
    sys.path.insert(0, str(ROOT / "lean/VE/Route"))
    import frozen
    base, head = git("rev-parse", base).strip(), git("rev-parse", head).strip()
    before, after = git("show", f"{base}:{INVENTORY}"), git("show", f"{head}:{INVENTORY}")
    kernel = {m for m, c in json.loads(git("show", f"{head}:{TABLE}"))["modules"].items() if c.get("K")}
    now = listed(after)
    # Commits are named by hash and their files listed after a marker line, so no subject is read as a path.
    log = git("log", "--no-merges", f"--since={SINCE}", "--format=@@%H", "--name-only", base, "--", "lean")
    commits, current = {}, None
    for line in log.splitlines():
        if line.startswith("@@"):
            current = commits.setdefault(line[2:], set())
        elif line and current is not None:
            current.add(line)
    lean_source = {c: files for c, files in commits.items() if any(f.endswith(".lean") for f in files)}
    full = sorted(c for c, files in lean_source.items() if INVENTORY in files)
    short = sorted(c for c, files in lean_source.items() if any(f"lean/{name}" in files for name in now))
    out = {
        "base": base, "head": head,
        "inventory": {"lines_before": len(before.splitlines()), "lines_after": len(after.splitlines()),
                      "files_before": len(listed(before)), "files_after": len(now),
                      "frozen": {name: "K declarations" if name in kernel else "ve.core@0.1 decoder" for name in now},
                      "k_files": len(kernel), "decoders": list(frozen.DECODERS),
                      "dropped": len(set(listed(before)) - set(now)), "added": sorted(set(now) - set(listed(before)))},
        "question_lock": {"module_hashes_before": len(json.loads(git("show", f"{base}:{LOCK}")).get("files", {})),
                          "module_hashes_after": len(json.loads(git("show", f"{head}:{LOCK}")).get("files", {}))},
        "commits": {"window": f"--no-merges --since={SINCE} {base[:8]} -- lean, with a .lean source",
                    "lean_source": len(lean_source), "edited_full_inventory": len(full),
                    "touched_a_file_now_frozen": len(short),
                    "share_full": round(len(full) / len(lean_source), 3),
                    "share_short": round(len(short) / len(lean_source), 3)},
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, indent=1) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps(main(*sys.argv[1:]), indent=1))
